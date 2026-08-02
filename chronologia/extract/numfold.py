"""Spelled-number folding pre-pass.

The tokenizer only recognises *digit* runs as numbers; natural speech spells
them ("five days ago", "the twenty fifth", "the third week of june").  This
pass folds a maximal run of number-words into a single digit
:class:`~chronologia.extract.model.Token` so every ``NUM``/``DAY``/``YEAR``/
``ORD`` slot binds the same way whether the writer typed ``5`` or ``five``.

This module holds the English fold plus every locale whose fold does not
share a family engine with another language (``fa``, ``id``, ``kab``,
``ms``), and the primitives multiple family modules import rather than
duplicate: the ``_make_germanic_fold``/``_lazy_germanic_fold`` single-extractor
engine (also used by ``numfold_germanic`` and ``numfold_turkic``).  The
Romance family (an/ast/ca/es/fr/gl/it/mwl/oc/pt/ro) lives in
``numfold_romance``, the Continental/North Germanic family (da/de/fy/nb/nl/nn/
sv) in ``numfold_germanic``, and the Turkic family (az/tr) in
``numfold_turkic``.  The Slavic, Semitic and agglutinative families each have
their own sibling module already (``numfold_slavic``, ``numfold_semitic``,
``numfold_agglutinative``).

Wired as a language ``hook`` in each locale's ``lang.json`` and applied by
:meth:`DateTimeEngine.tokenize` after normalisation.  Every fold is a pure
``tuple[Token] -> tuple[Token]`` transform, re-indexed so ``Token.index``
stays contiguous.

The English value is read from
:func:`ovos_number_parser.numbers_en.extract_number_en` (``ordinals=True``);
the fold owns only *which* tokens form a run.  Clock fractions ("half",
"quarter") are deliberately **not** number-words here -- they are their own
``FRACTION`` slot vocabulary and must survive intact.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Tuple

from ovos_number_parser.numbers_en import extract_number_en

from chronologia.extract.matcher import GYEAR_MAX, GYEAR_MIN
from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import (NumberGrammar, make_fold,
                                                    reindex as _reindex)
from chronologia.extract.numfold_ordinals import with_ordinals as _with_ordinals


# closed class of English number-words the fold may absorb (cardinals +
# ordinals + a few colloquial multipliers).  "half"/"quarter" are excluded
# on purpose (clock fractions); "a"/"an" are excluded (article ambiguity).
_ONES = ["one", "two", "three", "four", "five", "six", "seven", "eight",
         "nine", "ten", "eleven", "twelve", "thirteen", "fourteen",
         "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
_TENS = ["twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty",
         "ninety"]
_SCALES = ["hundred", "thousand", "million", "billion", "trillion"]
_ORD_ONES = ["first", "second", "third", "fourth", "fifth", "sixth",
             "seventh", "eighth", "ninth", "tenth", "eleventh", "twelfth",
             "thirteenth", "fourteenth", "fifteenth", "sixteenth",
             "seventeenth", "eighteenth", "nineteenth"]
_ORD_TENS = ["twentieth", "thirtieth", "fortieth", "fiftieth", "sixtieth",
             "seventieth", "eightieth", "ninetieth"]
_ORD_SCALES = ["hundredth", "thousandth", "millionth", "billionth"]
_EXTRA = ["zero", "couple", "dozen", "score"]

# NOTE: multiplier scale-words (hundred/thousand/million/billion) are
# deliberately *not* folded -- they are the ``SCALE`` slot of the deep-time
# construction ("66 million years ago"), and folding them would erase the
# very token that separates deep time from a plain "N years ago" offset.
_NUMWORDS = frozenset(_ONES + _TENS + _ORD_ONES + _ORD_TENS
                      + _ORD_SCALES + _EXTRA)
_ORD_SUFFIXES = frozenset({"st", "nd", "rd", "th"})


def _is_numword(tok: Token) -> bool:
    return tok.is_number or tok.text in _NUMWORDS


def _merge_en_ord_suffix(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Pre-pass: merge a digit followed by a lone ordinal suffix (5 th -> 5)."""
    merged = []
    i = 0
    while i < len(tokens):
        t = tokens[i]
        nxt = tokens[i + 1] if i + 1 < len(tokens) else None
        if (t.is_number and nxt is not None and not nxt.is_number
                and nxt.text in _ORD_SUFFIXES):
            merged.append(replace(t, raw=t.raw + nxt.raw))
            i += 2
            continue
        merged.append(t)
        i += 1
    return tuple(merged)


# ---------------------------------------------------------------------------
# spelled calendar years ("two thousand and one", "nineteen ninety-nine")
# ---------------------------------------------------------------------------
#
# The generic fold above withholds the multiplier scale words on purpose, so a
# spoken year built on one ("two thousand and one") reaches the matcher as
# ``[2, thousand, and, 1]`` -- the year construction binds the leading 2000 and
# silently drops the rest.  And a spoken year *pair* ("nineteen ninety-nine")
# is one maximal run of number-words, which the back-end reads as the single
# number 99, destroying the century/decade structure.
#
# Neither can be fixed by widening the generic run (that would eat the SCALE
# token deep time depends on).  This pass is a dedicated pre-pass instead: it
# recognises the three English *year* shapes, emits one digit token for each,
# and leaves every other reading of the same words untouched.

_CARD_ONES = {w: i + 1 for i, w in enumerate(_ONES)}      # one..nineteen
_CARD_TENS = {w: (i + 2) * 10 for i, w in enumerate(_TENS)}  # twenty..ninety
_CARDINALS = frozenset(_CARD_ONES) | frozenset(_CARD_TENS)
_YEAR_SCALES = {"hundred": 100, "thousand": 1000}


def _en_voc(base):
    """Surfaces of an English ``.voc``, read from the locale data itself."""
    from pathlib import Path

    from ovos_spec_tools import expand, read_resource_file

    lang_dir = Path(__file__).resolve().parent.parent / "locale" / "en"
    out = set()
    for template in read_resource_file(lang_dir / (base + ".voc")):
        out.update(s.lower() for s in expand(template, {}))
    return out


def _year_cues():
    """Tokens that explicitly announce a calendar year -- the ``year`` marker
    behind "the year ..." and the ``in`` preposition, both read from the
    English locale vocabulary rather than hardcoded here."""
    return _en_voc("marker_year_word") | _en_voc("marker_in")


def _unit_words():
    """Every offset-unit surface ("years", "days", ...).  A scale construction
    followed by one of these is the deep-time / offset frame, not a year."""
    from pathlib import Path
    words = set()
    lang_dir = Path(__file__).resolve().parent.parent / "locale" / "en"
    for path in sorted(lang_dir.glob("unit_*.voc")):
        words |= _en_voc(path.name[:-len(".voc")])
    return words


_CUE_WORDS = None
_UNIT_WORDS = None


def _cue_words():
    global _CUE_WORDS
    if _CUE_WORDS is None:
        _CUE_WORDS = frozenset(_year_cues())
    return _CUE_WORDS


def _units():
    global _UNIT_WORDS
    if _UNIT_WORDS is None:
        _UNIT_WORDS = frozenset(_unit_words())
    return _UNIT_WORDS


def _card_run(tokens):
    """Value of a run of plain cardinal words, or ``None``.

    Only the two shapes English spells a 0-99 component with are accepted: a
    single word ("nine", "ninety", "nineteen") and tens+ones ("ninety nine").
    Anything else ("five five", "twenty twenty") is *not* a number component
    and is refused rather than guessed at."""
    words = [t.text for t in tokens]
    if len(words) == 1:
        w = words[0]
        if w in _CARD_ONES:
            return _CARD_ONES[w]
        return _CARD_TENS.get(w)
    if (len(words) == 2 and words[0] in _CARD_TENS
            and words[1] in _CARD_ONES and _CARD_ONES[words[1]] < 10):
        return _CARD_TENS[words[0]] + _CARD_ONES[words[1]]
    return None


def _take_cardinals(tokens, i, limit=2):
    """Longest run (<= ``limit`` tokens) of cardinal words starting at ``i``."""
    j = i
    while j < len(tokens) and j - i < limit and tokens[j].text in _CARDINALS:
        j += 1
    return j


def _year_token(value, first, last):
    return Token(text=str(value), raw=str(value), index=0, is_number=True,
                 value=value, char_start=first.char_start,
                 char_end=last.char_end)


def _fold_spelled_year(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Fold a spelled English calendar year into one digit token.

    Three shapes, all requiring the leading component to be *spelled* (a digit
    "10 thousand" is left alone -- it is the deep-time SCALE frame):

    ``<n> hundred [and] [<m>]``
        ``n`` in 10..99 -- "nineteen hundred" (1900), "nineteen hundred and
        five" (1905).  ``n`` below ten is not a century prefix, so "one
        hundred and five" keeps its plain-number reading.

    ``<n> thousand [and] [<m>]``
        "two thousand" (2000), "two thousand and one" (2001), "two thousand
        and twenty four" (2024).  Unambiguous: the digit form ``2001`` already
        reads as a year, so the spelled form must too -- no cue needed.
        ``n`` runs 1..99, so the composed year covers the same
        ``GYEAR_MIN..GYEAR_MAX`` window a digit year does: "twenty thousand"
        reads exactly as ``20000`` does, and a spelled year outside the
        window resolves to nothing just as the digits would.  The magnitude
        is never what tells a year from deep time -- a closing unit word is
        ("ninety nine thousand years ago" stays an offset, refused below).

    ``<c> <y>`` (year pair, **explicit year cue required**)
        "nineteen ninety-nine" (1999), "twenty twenty-four" (2024).  A bare
        pair is genuinely ambiguous with a plain number, so it only reads as a
        year after a cue word ("in ...", "the year ..." -- taken from the
        locale vocabulary).  ``c`` must be a single teen/tens word (10..99)
        and ``y`` must itself be 10..99: a bare ones suffix is refused, both
        because "in twenty five days" is a count and because English spells
        that year with "oh" ("nineteen oh five").

    Refusals are deliberate, never a guess: any component outside 0..99, a
    further scale word riding on the construction ("two thousand and one
    hundred thousand"), a run that is not a well-formed 0-99 component
    ("ninety nine ninety nine"), or a unit word closing the phrase ("two
    thousand years ago" -- deep time) all leave the tokens untouched, and the
    sentence resolves to nothing rather than to a fabricated year.
    """
    out = []
    i = 0
    n = len(tokens)
    cues = _cue_words()
    units = _units()
    while i < n:
        tok = tokens[i]
        if tok.text not in _CARDINALS or (out and out[-1].is_number):
            out.append(tok)
            i += 1
            continue
        head_end = _take_cardinals(tokens, i)
        head = _card_run(tokens[i:head_end])
        end = None
        value = None
        if head is not None and head_end < n and tokens[head_end].text in _YEAR_SCALES:
            scale = _YEAR_SCALES[tokens[head_end].text]
            # the century prefix must be a real one (10..99); the thousands
            # head is unrestricted because the window check below is what
            # bounds the composition, exactly as it bounds the digit form
            if scale == 1000 or 10 <= head <= 99:
                j = head_end + 1
                if j < n and tokens[j].text == "and" and j + 1 < n:
                    j += 1
                tail_end = _take_cardinals(tokens, j)
                tail = _card_run(tokens[j:tail_end]) if tail_end > j else 0
                if tail is not None and tail < scale:
                    composed = head * scale + tail
                    if GYEAR_MIN <= composed <= GYEAR_MAX:
                        value, end = composed, max(tail_end, head_end + 1)
        elif out and out[-1].text in cues:
            # year pair: the century prefix is a *single* teen/tens word, the
            # rest of the run is the 10..99 remainder
            century = _card_run(tokens[i:i + 1])
            if century is not None and 10 <= century <= 99:
                tail_end = _take_cardinals(tokens, i + 1)
                tail = (_card_run(tokens[i + 1:tail_end])
                        if tail_end > i + 1 else None)
                if tail is not None and 10 <= tail <= 99:
                    value, end = century * 100 + tail, tail_end
        if value is None:
            out.append(tok)
            i += 1
            continue
        # a scale word riding on the construction, or a unit word closing it,
        # means this was never a year -- refuse rather than fabricate one
        if end < n and (tokens[end].text in _SCALES
                        or tokens[end].text in units):
            out.append(tok)
            i += 1
            continue
        out.append(_year_token(value, tokens[i], tokens[end - 1]))
        i = end
    return _reindex(out)


# ---------------------------------------------------------------------------
# spelled multi-word cardinal *offsets* ("a hundred years ago")
# ---------------------------------------------------------------------------
#
# The generic fold withholds the scale words so the deep-time SCALE slot
# survives, and ``_fold_spelled_year`` deliberately refuses the offset frame (a
# scale construction closed by a unit word).  That leaves "a hundred years ago"
# reaching the matcher as ``[a, hundred, years, ago]`` -- the "hundred" stranded
# and the offset read as a bare one.  This pass is the exact complement: it
# folds a *spelled* hundred cardinal into one digit token **only** when a unit
# word closes it (the offset frame), so "a hundred years ago" reads like "100
# years ago".  Only the hundred scale composes: thousand and up are the SCALE
# slot of the deep-time / Before-Present offset ("two thousand years ago",
# "sixty-six million years ago"), which the resolver reads from the surviving
# scale word, so they are left untouched and keep reaching that span.
_SCALE_MULT = {"hundred": 100}
_EN_ARTICLES = frozenset({"a", "an", "the"})


def _card_value(tok: Token):
    """Value of a single *spelled* 0-99 cardinal word, or ``None``.

    Digit tokens are deliberately refused: "10 thousand years ago" is left to
    the deep-time SCALE path exactly as ``_fold_spelled_year`` leaves it."""
    if tok.is_number:
        return None
    return _CARD_ONES.get(tok.text, _CARD_TENS.get(tok.text))


def _read_scale_number(tokens, i):
    """Fold ``[a|an] [<0-99>] hundred [and] [<0-99>]`` starting at ``i`` into
    ``(value, end)``; ``(None, i)`` when it is not such a run.

    Only the hundred scale composes -- thousand, million and up are the
    deep-time / Before-Present SCALE and stop the run, so they never fold
    here."""
    n = len(tokens)
    j = i
    total = 0
    current = 0
    seen_scale = False
    started = False
    while j < n:
        t = tokens[j].text
        if (t in _EN_ARTICLES and not started
                and j + 1 < n and tokens[j + 1].text in _SCALE_MULT):
            current, started = 1, True
            j += 1
            continue
        cv = _card_value(tokens[j])
        if cv is not None:
            current = cv if current == 0 else current + cv
            started = True
            j += 1
            continue
        if t in _SCALE_MULT:
            scale = _SCALE_MULT[t]
            if current == 0:
                current = 1
            if scale >= 1000:
                total += current * scale
                current = 0
            else:
                current *= scale
            seen_scale = True
            started = True
            j += 1
            continue
        if t == "and" and started and j + 1 < n:
            j += 1
            continue
        break
    if not seen_scale:
        # No scale word in this cardinal run, so it can never fold here. Report
        # how far the scan reached (``j``) so the caller can skip the whole run
        # in one step instead of re-scanning from every start position -- a run
        # of pure cardinals ("ninety nine ...") was O(n^2) otherwise.
        return None, j
    return total + current, j


# ---------------------------------------------------------------------------
# indefinite-article deep-time magnitudes ("a million years ago")
# ---------------------------------------------------------------------------
#
# The generic fold withholds thousand/million/billion/trillion so the deep-time
# SCALE slot survives ("66 million years ago").  But an *indefinite article*
# leading that scale ("a million years ago", "a hundred thousand years ago")
# reaches the matcher as ``[a, million, years, ago]`` -- "a" is no numeral, so
# the deep-time order "NUM SCALE year_word ago" never binds, the scale strands,
# and the offset reads as a bare one year.  This pass supplies the missing
# count: it emits a single digit token (the article's implicit 1, times any
# interior "hundred") flagged ``article=True`` and *keeps the scale word* so the
# deep-time order binds.  The resolver reads the flag to resolve the article
# form as a colloquial count-from-now point rather than the numeral form's
# geological Before-Present span.  Only the indefinite article fires it: a
# spoken numeral ("two million", "sixty-six million") keeps its numeral reading
# and its Before-Present span.
_BP_SCALE_WORDS = {"thousand": 1_000, "million": 1_000_000,
                   "billion": 1_000_000_000, "trillion": 1_000_000_000_000}
_INDEF_ARTICLES = frozenset({"a", "an"})


def _fold_article_magnitude(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Fold ``[a|an] [<0-99>] [hundred] SCALE year_word`` into an article-count
    token plus the surviving SCALE word (thousand/million/billion/trillion)."""
    units = _units()
    out = []
    i = 0
    n = len(tokens)
    while i < n:
        if tokens[i].text in _INDEF_ARTICLES:
            j = i + 1
            count = 1
            # an optional interior "<0-99> [hundred]" multiplier ("a hundred
            # thousand", "a two hundred billion")
            cv = _card_value(tokens[j]) if j < n else None
            if cv is not None:
                count = cv
                j += 1
            if j < n and tokens[j].text == "hundred":
                count = (count or 1) * 100
                j += 1
            if (j < n and tokens[j].text in _BP_SCALE_WORDS
                    and j + 1 < n and tokens[j + 1].text in units):
                scale_tok = tokens[j]
                out.append(replace(
                    _year_token(count, tokens[i], tokens[j - 1]),
                    article=True))
                out.append(scale_tok)
                i = j + 1
                continue
        out.append(tokens[i])
        i += 1
    return _reindex(out)


def _fold_scale_offset(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Fold a spelled hundred/thousand cardinal into a digit token when a unit
    word closes it -- the plain-offset frame ("a hundred years ago")."""
    units = _units()
    out = []
    i = 0
    n = len(tokens)
    while i < n:
        if tokens[i].text in _CARDINALS or tokens[i].text in _EN_ARTICLES:
            value, end = _read_scale_number(tokens, i)
            if (value is not None and end < n
                    and tokens[end].text in units):
                out.append(_year_token(value, tokens[i], tokens[end - 1]))
                i = end
                continue
            if value is None and end > i:
                # a pure cardinal run with no scale word: nothing here can fold,
                # so pass it through in one step (avoids O(n^2) re-scanning of a
                # long spelled-number run).
                out.extend(tokens[i:end])
                i = end
                continue
        out.append(tokens[i])
        i += 1
    return _reindex(out)


# ---------------------------------------------------------------------------
# spelled fractions in the relative/duration frame ("two and a half hours ago")
# ---------------------------------------------------------------------------
#
# Fraction words ("half", "quarter") are excluded from the generic fold because
# they own the clock FRACTION slot ("half past three").  In the offset/duration
# frame -- a fraction bound to a length unit -- they must instead compose into
# the count: "two and a half hours" is 2.5 hours, "three quarters of an hour"
# 0.75, "half a year" half a year.  This pass folds exactly that frame (a unit
# word closes it) into one decimal count token; clock fractions, which are
# followed by "past"/"to"/a clock number rather than a unit, never match.
#
# A fractional *year* count has no decimal offset reading (the resolver steps
# whole months), so a year fraction that lands on a whole month is emitted as
# that month count instead: "half a year" -> "6 months".
_EN_FRACS = {"half": 0.5, "quarter": 0.25, "quarters": 0.25}


def _fraction_number(value, first, last):
    v = int(value) if float(value).is_integer() else value
    return Token(text=str(v), raw=str(v), index=0, is_number=True,
                 value=v, char_start=first.char_start, char_end=last.char_end)


def _read_plain_count(tokens, i):
    """A leading count at ``i``: a digit token or a spelled 0-99 run -> value,
    end.  ``(None, i)`` when neither."""
    n = len(tokens)
    if i < n and tokens[i].is_number:
        return float(tokens[i].value), i + 1
    end = _take_cardinals(tokens, i)
    if end > i:
        v = _card_run(tokens[i:end])
        if v is not None:
            return float(v), end
    return None, i


def _fold_offset_fraction(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    units = _units()
    year_words = _en_voc("unit_year")
    # only the *indefinite* article introduces a duration ("half a year", "an
    # hour and a half"); the definite "the" marks the partitive sub-span
    # construction ("the first half of *the* century"), which is not a length
    # and must be left for its own resolver.
    frac_articles = frozenset({"a", "an"})
    filler = frac_articles | {"of"}
    out = []
    i = 0
    n = len(tokens)

    def skip_filler(k):
        while k < n and tokens[k].text in filler:
            k += 1
        return k

    while i < n:
        count, j = _read_plain_count(tokens, i)
        lead_article = False
        if count is None and tokens[i].text in frac_articles:
            count, j, lead_article = 1.0, i + 1, True
        combined = None
        unit_pos = None
        end = None
        if count is not None:
            # count "and a half" ... unit  (additive, fraction before unit)
            if j < n and tokens[j].text == "and":
                k = j + 1
                while k < n and tokens[k].text in frac_articles:
                    k += 1
                if k < n and tokens[k].text in _EN_FRACS:
                    k2 = skip_filler(k + 1)
                    if k2 < n and tokens[k2].text in units:
                        combined, unit_pos, end = (
                            count + _EN_FRACS[tokens[k].text], k2, k2 + 1)
            # count fraction ... unit  (multiplicative, "three quarters of ...")
            if combined is None and j < n and tokens[j].text in _EN_FRACS:
                k2 = skip_filler(j + 1)
                if k2 < n and tokens[k2].text in units:
                    combined, unit_pos, end = (
                        count * _EN_FRACS[tokens[j].text], k2, k2 + 1)
            # count unit "and a half"  (fraction trails the unit)
            if combined is None:
                k2 = skip_filler(j)
                if k2 < n and tokens[k2].text in units:
                    m = k2 + 1
                    if m < n and tokens[m].text == "and":
                        m += 1
                        while m < n and tokens[m].text in frac_articles:
                            m += 1
                        if m < n and tokens[m].text in _EN_FRACS:
                            combined, unit_pos, end = (
                                count + _EN_FRACS[tokens[m].text], k2, m + 1)
        # bare fraction ... unit  ("half a year", "a quarter of an hour")
        if combined is None and tokens[i].text in _EN_FRACS:
            k2 = skip_filler(i + 1)
            if k2 < n and tokens[k2].text in units:
                combined, unit_pos, end = _EN_FRACS[tokens[i].text], k2, k2 + 1
        if combined is None:
            out.append(tokens[i])
            i += 1
            continue
        unit_tok = tokens[unit_pos]
        # a fractional year has no decimal offset -- express it in whole months
        if unit_tok.text in year_words and not float(combined).is_integer():
            months = combined * 12
            if not float(months).is_integer():
                out.append(tokens[i])
                i += 1
                continue
            out.append(_fraction_number(months, tokens[i], tokens[end - 1]))
            out.append(Token(text="months", raw="months", index=0,
                             char_start=unit_tok.char_start,
                             char_end=unit_tok.char_end))
        else:
            out.append(_fraction_number(combined, tokens[i], tokens[end - 1]))
            out.append(unit_tok)
        i = end
    return _reindex(out)


def _pre_en(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    folded = _fold_spelled_year(_merge_en_ord_suffix(tokens))
    folded = _fold_article_magnitude(folded)
    return _fold_offset_fraction(_fold_scale_offset(folded))


# English: closed-class membership, an internal "and" that continues a run but
# is dropped from the text the back-end reads ("one hundred and five").
# The additive "and" is only genuine after a magnitude of at least 100
# ("one hundred AND five" == 105, "two hundred and fifty", "a thousand and
# one").  Between two small numbers or two ordinals it is a LIST, not an
# additive ("first and third of June" is the 1st and the 3rd, never the 3rd),
# so the bridge is refused and the run is cut at the "and" -- each side folds on
# its own and the "and" survives, instead of the back-end silently reading the
# joined run as its last ordinal and erasing the first.
fold_en = make_fold(NumberGrammar(
    is_number=_is_numword,
    extract=lambda text: extract_number_en(text, ordinals=True),
    joiner=lambda tok: tok.text == "and",
    joiner_in_text=False,
    bridge_ok=lambda so_far, atom: so_far >= 100 and atom < so_far,
    pre=_pre_en))


# ---------------------------------------------------------------------------
# Continental / North Germanic spelled-number folding
#
# The Germanic languages build numbers as single compound words
# ("einundzwanzig" 21, "vijfentwintig" 25), so a spelled number is usually a
# *single* token rather than English's multi-word run.  ovos-number-parser
# resolves those compounds; the fold owns only which tokens are numbers.
#
# Two surfaces must survive the fold: clock fractions ("halb"/"viertel",
# "halv"/"kvart" -- their own FRACTION slot) and scale words
# ("million"/"milliard" -- the deep-time SCALE slot).  They are excluded by
# an explicit stop-set per language.
# ---------------------------------------------------------------------------

def _make_germanic_fold(extract_fn, stop_words, ord_suffixes=(), word_map=None):
    """Build a ``tuple[Token] -> tuple[Token]`` fold for a Germanic language.

    ``extract_fn`` is the language's ``ovos_number_parser`` extractor; the
    German-family extractors return ordinals only under ``ordinals=True`` and
    cardinals only under the default, so both are tried.  ``stop_words`` are
    surfaces that resolve as numbers but must stay their own token (clock
    fractions and scale words).
    """
    stop = frozenset(stop_words)
    suffixes = frozenset(ord_suffixes)
    wmap = dict(word_map or {})

    def value_of(text):
        v = extract_fn(text, ordinals=True)
        if v is False or v is None:
            v = extract_fn(text)
        return v

    def is_numword(tok):
        if tok.is_number:
            return True
        if tok.text in stop:
            return False
        v = value_of(tok.text)
        return v is not None and v is not False

    def pre(tokens):
        # pass -1: rewrite fixed word->value surfaces to digit tokens.  Used
        # for the Frisian inflected "coming-hour" forms ("fiven" -> 5,
        # "fjouweren" -> 4) that the number parser does not recognise but the
        # clock look-ahead ("healwei fiven" == 04:30) needs as a bare HOUR.
        if wmap:
            tokens = tuple(
                replace(t, text=str(wmap[t.text]), raw=t.raw,
                        is_number=True, value=wmap[t.text])
                if (not t.is_number and t.text in wmap) else t
                for t in tokens)

        # pass 0: merge a digit followed by a lone alphabetic ordinal suffix
        # ("21 e" -> 21, Dutch "21e"; "3 de" -> 3).  Digit-dot ordinals are
        # handled by the tokenizer (ordinal_dot); this covers the alpha form.
        if suffixes:
            merged = []
            i = 0
            while i < len(tokens):
                t = tokens[i]
                nxt = tokens[i + 1] if i + 1 < len(tokens) else None
                if (t.is_number and nxt is not None and not nxt.is_number
                        and nxt.text in suffixes):
                    merged.append(replace(t, raw=t.raw + nxt.raw))
                    i += 2
                    continue
                merged.append(t)
                i += 1
            tokens = tuple(merged)
        return tokens

    return make_fold(NumberGrammar(
        is_number=is_numword, extract=value_of, pre=pre))


def _lazy_germanic_fold(module_name, fn_name, stop_words, ord_suffixes=(),
                        word_map=None):
    """Defer the ``ovos_number_parser`` import to first call (keeps locale
    load cheap and import-order-independent)."""
    holder = {}

    def fold(tokens):
        f = holder.get("f")
        if f is None:
            import importlib
            extract_fn = getattr(importlib.import_module(module_name), fn_name)
            f = holder["f"] = _make_germanic_fold(extract_fn, stop_words,
                                                  ord_suffixes, word_map)
        return f(tokens)

    return fold

fold_id = _lazy_germanic_fold(
    "ovos_number_parser.numbers_id", "extract_number_id",
    {"setengah", "seperempat", "suku", "ribu", "juta", "miliar", "milyar"})
# Indonesian spelled ordinals ("ketiga" third) fold to their digit so the
# scoped_ordinal ``ORD`` slot binds ("Senin ketiga Maret" = the third Monday of
# March); from the model's ``pronounce_ordinal_id`` (ke- prefix), plus the
# alternative first-ordinal surface "kesatu" the pronouncer spells "pertama".
fold_id = _with_ordinals(fold_id, "id", {"kesatu": 1})
fold_ms = _lazy_germanic_fold(
    "ovos_number_parser.numbers_id", "extract_number_ms",
    {"setengah", "separuh", "suku", "ribu", "juta", "bilion", "miliar"})
fold_kab = _lazy_germanic_fold(
    "ovos_number_parser.numbers_kab", "extract_number_kab",
    {"azgen", "agim", "amelyun"})
# fa (Persian): single extractor extract_number_fa(text, ordinals=False);
# withhold the half/quarter clock words and the scale words.
fold_fa = _lazy_germanic_fold(
    "ovos_number_parser.numbers_fa", "extract_number_fa",
    {"نیم", "ربع", "چارک", "هزار", "میلیون", "میلیارد"})
# Persian spelled ordinals ("سوم" third) fold to their digit so the quarter's
# ``ORD`` slot binds; from the model's ``pronounce_ordinal_fa``.
fold_fa = _with_ordinals(fold_fa, "fa")



