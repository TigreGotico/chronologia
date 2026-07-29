"""Spelled-number folding pre-pass (English).

The tokenizer only recognises *digit* runs as numbers; natural English
speech spells them ("five days ago", "the twenty fifth", "the third week
of june").  This pass folds a maximal run of English number-words into a
single digit :class:`~chronologia.extract.model.Token` so every
``NUM``/``DAY``/``YEAR``/``ORD`` slot binds the same way whether the writer
typed ``5`` or ``five``.

Wired as a language ``hook`` in ``locale/en/lang.json`` and applied by
:meth:`DateTimeEngine.tokenize` after normalisation.  It is a pure
``tuple[Token] -> tuple[Token]`` transform, re-indexed so ``Token.index``
stays contiguous.

The value is read from :func:`ovos_number_parser.numbers_en.extract_number_en`
(``ordinals=True``); the fold owns only *which* tokens form a run.  Clock
fractions ("half", "quarter") are deliberately **not** number-words here --
they are their own ``FRACTION`` slot vocabulary and must survive intact.
"""
from __future__ import annotations

import os
from dataclasses import replace
from typing import Tuple

from ovos_number_parser.numbers_en import extract_number_en
from ovos_number_parser.numbers_fr import extract_number_fr

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
        return None, i
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
fold_en = make_fold(NumberGrammar(
    is_number=_is_numword,
    extract=lambda text: extract_number_en(text, ordinals=True),
    joiner=lambda tok: tok.text == "and",
    joiner_in_text=False,
    pre=_pre_en))


# ---------------------------------------------------------------------------
# Romance spelled-number folding (pt / es / gl / ca)
# ---------------------------------------------------------------------------
#
# The English fold above carries its own closed-class word list.  The Romance
# languages share one mechanism: the number-word set is read straight from
# ``ovos_number_parser``'s ``NumberVocabulary`` for the language, and a
# maximal run of those words (joined by the language's "and" word) is folded
# to a single digit token via ``extract_number_<lang>`` (ordinals included).
#
# Two classes of word are deliberately *withheld* from the run so the token
# that distinguishes a construction survives intact:
#
#   * clock fractions (``meia`` / ``media`` / ``mig`` ...) -- their own
#     ``FRACTION`` slot ("as tres e meia");
#   * multiplier scale words (``mil`` / ``milhao`` / ``bilhao`` ...) -- the
#     ``SCALE`` slot of deep time ("66 milhoes de anos atras").
#
# A per-language weekday blacklist keeps a feminine-ordinal surface that
# doubles as a weekday name (pt "segunda"/"quarta"/"quinta"/"sexta") from
# ever being read as a number.
from importlib import import_module


def _fem_forms(surf):
    """Feminine ordinal surfaces of a masculine ordinal: ``o``->``a``
    (primeiro->primeira) and a bare ``+a`` (tercer->tercera, segon->segona)
    cover pt/es/gl and ca respectively.  Spurious candidates are harmless --
    they never occur in real text."""
    s = surf.lower()
    forms = {s + "a"}
    if s.endswith("o"):
        forms.add(s[:-1] + "a")
    return forms


def _romance_numwords(vocab, blacklist):
    """The closed set of spelled number-words the fold may absorb, built from
    a ``NumberVocabulary``.  Cardinals, tens, hundreds and ordinals are in;
    fractions, multiplier scales and the language's hundred particle stay in
    but only when they are not scale words; blacklisted weekday-homographs
    are removed."""
    words = set()
    for table in (vocab.UNITS, vocab.TENS, vocab.HUNDREDS,
                  vocab.ORDINAL_UNITS, vocab.ORDINAL_TENS,
                  vocab.ORDINAL_HUNDREDS):
        words.update(v.lower() for v in table.values() if v)
    words.update(k.lower() for k in vocab.ALT_SPELLINGS)
    for gmap in vocab.GENDERED_SPELLINGS.values():
        words.update(v.lower() for v in gmap.values() if v)
    # feminine ordinals ("primeira", "terceira") -- generated o->a, then the
    # weekday-homograph blacklist is applied below
    for v in list(vocab.ORDINAL_UNITS.values()):
        if v:
            words.update(_fem_forms(v))
    if vocab.HUNDRED_PARTICLE:
        words.add(vocab.HUNDRED_PARTICLE.lower())
    # withhold multiplier scale words (mil/milhao/bilhao...) and clock
    # fractions so deep-time SCALE and clock FRACTION tokens survive
    scales = set()
    for table in (vocab.SHORT_SCALE, vocab.LONG_SCALE):
        scales.update(v.lower() for v in table.values() if v)
    fractions = set()
    for table in (vocab.FRACTION, vocab.FRACTION_FEMALE):
        fractions.update(v.lower() for v in table.values() if v)
    words -= scales
    words -= fractions
    words -= {w.lower() for w in blacklist}
    return frozenset(words)


#: definite articles (incl. elided "l") *per locale* -- the position that
#: licenses the *ordinal* reading of an ordinal-fraction homograph.  The scoped
#: ordinal is always "il/el/o/la <ordinal> <weekday|unit>"; the clock fraction
#: is "un/e <quarto>", never introduced by a definite article, so keying the
#: fold off a preceding definite article leaves every clock fraction byte-
#: identical.  Kept per-locale on purpose: a surface that is a definite article
#: in one Romance language ("i" = Italian masculine plural article) is the
#: coordinator "and" in another (Catalan "les tres **i** quart"), so a merged
#: set would mis-license a clock fraction.  A fact of the languages, kept tiny.
_ROMANCE_DEFINITE = {
    "it": frozenset({"il", "lo", "la", "i", "gli", "le", "l"}),
    "es": frozenset({"el", "la", "los", "las"}),
    "ca": frozenset({"el", "la", "els", "les", "l"}),
    "gl": frozenset({"o", "a", "os", "as"}),
    "pt": frozenset({"o", "a", "os", "as"}),
    "fr": frozenset({"le", "la", "les", "l"}),
    "oc": frozenset({"lo", "la", "los", "las", "les", "l"}),
    "an": frozenset({"o", "a", "os", "as", "lo", "la", "los", "las", "l"}),
    "ast": frozenset({"el", "la", "lo", "los", "les", "l"}),
    "mwl": frozenset({"l", "la", "lo", "ls", "las", "los"}),
    "ro": frozenset(),
}


def _homograph_ordinal_map(vocab, blacklist):
    """Surface -> value for the *ordinal* reading of every ordinal-unit
    surface that is also a *fraction* word ("terzo"/"quarto"/"cuarto" =
    third/fourth *and* a-third/a-quarter).  These are dropped from the
    number-fold's word set (see :func:`_romance_numwords`) so the clock
    FRACTION slot keeps them, which silently disabled the ``scoped_ordinal``
    ("il quarto giovedì di novembre") reading for every ordinal a language
    happens to spell like its fraction.  A blacklisted weekday-homograph
    (Portuguese feminine "quarta" = Wednesday) is excluded -- its ordinal /
    weekday ambiguity is a separate, positionally-licensed concern."""
    fractions = set()
    for table in (vocab.FRACTION, vocab.FRACTION_FEMALE):
        fractions.update(v.lower() for v in table.values() if v)
    black = {w.lower() for w in blacklist}
    out = {}
    for val, surf in vocab.ORDINAL_UNITS.items():
        if not surf:
            continue
        for s in {surf.lower()} | _fem_forms(surf):
            if s in fractions and s not in black:
                out[s] = val
    return out


#: locale root, for reading a language's ``marker_quarter_word.voc`` (the
#: calendar-quarter noun -- "trimestre") at fold-build time.
_LOCALE_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "locale")


def _quarter_word_surfaces(lang_code):
    """The calendar-quarter noun surfaces ("trimestre"/"trimestres") of a
    language, read from ``locale/<lang>/marker_quarter_word.voc``.

    This is the *second* position (besides a preceding definite article) that
    licenses the ordinal reading of an ordinal-fraction homograph: an ordinal
    number-word directly before the quarter noun is the quarter selector
    ("cuarto **trimestre**" = fourth quarter), never the clock/duration
    fraction, which is never followed by "trimestre".  Read from the same
    vocabulary the ``quarter_ref`` construction binds so the two never drift."""
    path = os.path.join(_LOCALE_ROOT, lang_code, "marker_quarter_word.voc")
    if not os.path.exists(path):
        return frozenset()
    out = set()
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            surf = line.strip()
            if surf and not surf.startswith("#"):
                out.add(surf.lower())
    return frozenset(out)


def _license_ordinal_fraction(tokens, homomap, definite, quarter_words=frozenset()):
    """Positionally read an ordinal-fraction homograph ("quarto"/"cuarto").

    The surface is the scoped ordinal ("**il quarto** giovedì", "**la cuarta**
    semana") directly after a definite article, the quarter selector ("**cuarto
    trimestre** de 2040" = fourth quarter) directly before the calendar-quarter
    noun, and the clock quarter ("tre **e quarto**", "un **quarto** d'ora")
    everywhere else.  Only the two ordinal frames -- a preceding definite
    article, or a following quarter noun -- fold to the digit so
    ``scoped_ordinal`` / ``quarter_ref`` bind it; every clock-fraction frame
    keeps the bare word for the FRACTION slot, so the fold is byte-identical
    there (a fraction word is never followed by "trimestre" nor, in the
    duration frame "un quarto de hora", introduced by a definite article).  The
    positive licence also survives a fold that segments the stream around a
    protected article (Portuguese "um quarto"): a segment stripped of its
    article no longer sees the definite article and correctly stays the
    fraction word."""
    if not homomap or (not definite and not quarter_words):
        return tokens
    out = list(tokens)
    changed = False
    n = len(out)
    for i, t in enumerate(out):
        if t.is_number or t.text not in homomap:
            continue
        prev = out[i - 1] if i - 1 >= 0 else None
        nxt = out[i + 1] if i + 1 < n else None
        after_article = prev is not None and prev.text in definite
        before_quarter = nxt is not None and nxt.text in quarter_words
        if not after_article and not before_quarter:
            continue  # not an ordinal frame -- leave for FRACTION
        val = homomap[t.text]
        out[i] = Token(text=str(val), raw=t.raw, index=0, is_number=True,
                       value=val, char_start=t.char_start,
                       char_end=t.char_end)
        changed = True
    return _reindex(tuple(out)) if changed else tokens


# abbreviations the tokenizer shatters on their dots/hyphens ("a.c." -> a,c;
# "meio-dia" -> meio,dia).  The fold glues the fragments back into the single
# token a marker/landmark slot binds.  Keyed by the fragment tuple, longest
# match first; shared across the Romance locales (surfaces are the same).
_ROMANCE_GLUE = {
    ("a", "e", "c"): "aec", ("a", "c"): "ac", ("d", "c"): "dc",
    ("e", "c"): "ec", ("a", "p"): "ap",
    ("meio", "dia"): "meiodia", ("meia", "noite"): "meianoite",
    ("migdia",): "migdia",
}


def _glue(tokens):
    seqs = sorted(_ROMANCE_GLUE, key=len, reverse=True)
    out = []
    i = 0
    n = len(tokens)
    while i < n:
        for seq in seqs:
            k = len(seq)
            if tuple(t.text for t in tokens[i:i + k]) == seq:
                raw = "".join(t.raw for t in tokens[i:i + k])
                out.append(Token(text=_ROMANCE_GLUE[seq], raw=raw, index=0))
                i += k
                break
        else:
            out.append(tokens[i])
            i += 1
    return tuple(out)


def _romance_additive_join(left, right):
    """Is ``left e right`` a genuine additive continuation of one Romance
    numeral (``vinte e cinco`` == 25), rather than two separate numbers the
    ``e`` merely stands between (``sete e vinte`` == seven, *e* twenty)?

    The connective ``e`` fills the next place of a *round* base: a tens word
    from twenty up ("vinte e cinco"), or a hundred/thousand ("cento e vinte",
    "mil e quinhentos").  The rule, in place-value terms: the running value is
    a multiple of ten of at least twenty, and the joined atom is smaller than
    the base's lowest occupied place -- so a unit (< 10) may follow a ten, a
    two-digit remainder (< 100) may follow a hundred, and so on.  Teen bases
    (``dez e cinco``) and unit bases (``sete e vinte``) are excluded, which is
    exactly what leaves a spoken clock minute for the MINUTE slot.
    """
    if left < 20 or left % 10 != 0 or right <= 0:
        return False
    place = 10
    while left % (place * 10) == 0:
        place *= 10
    return right < place


def _make_romance_fold(lang_code, blacklist, reader=None,
                       extra_numwords=frozenset(), extra_homograph=None):
    from ovos_number_parser.util import RomanceNumberExtractor
    numbers_mod = import_module("ovos_number_parser.numbers_" + lang_code)
    vocab = next(v for v in vars(numbers_mod).values()
                 if type(v).__name__ == "NumberVocabulary")
    # the shared spoken-number reader; for most Romance languages
    # ``extract_number_<lang>`` is a thin wrapper over exactly this, and a
    # language whose wrapper adds a real hook passes that wrapper as ``reader``.
    extractor = RomanceNumberExtractor(vocab)

    def extract_fn(text, ordinals=True):
        if reader is not None:
            return reader(text, ordinals=ordinals)
        return extractor.extract_number(text, ordinals=ordinals)
    numwords = _romance_numwords(vocab, blacklist) | frozenset(extra_numwords)
    joins = frozenset(j.lower() for j in vocab.JOIN_WORD)
    # some ``extract_number_<lang>`` back-ends do not recognise the feminine
    # ordinal surface ("tercera", "segona"); a direct surface->value map,
    # built from the masculine ordinals plus their generated feminine forms,
    # is the fallback for a single-token run the back-end rejects.
    ordinal_value = {}
    for table in (vocab.ORDINAL_UNITS, vocab.ORDINAL_TENS):
        for val, surf in table.items():
            if surf:
                ordinal_value[surf.lower()] = val
                for fem in _fem_forms(surf):
                    ordinal_value[fem] = val
    ordinal_value = {k: v for k, v in ordinal_value.items()
                     if k in numwords}

    # the a.c./d.c. glue runs first, then the shared engine: run membership
    # from the vocab-derived word set, the language's JOIN_WORD as the internal
    # connector (kept in the back-end text), and the feminine-ordinal map as the
    # single-token fallback the back-end rejects.
    base = make_fold(NumberGrammar(
        is_number=lambda tok: tok.is_number or tok.text in numwords,
        extract=lambda text: extract_fn(text, ordinals=True),
        joiner=lambda tok: tok.text in joins,
        single_fallback=ordinal_value.get,
        pre=_glue,
        bridge_ok=_romance_additive_join))
    # ordinal-fraction homographs ("quarto" = fourth *and* a-quarter) are held
    # out of ``numwords`` above so the clock FRACTION slot keeps them; license
    # the ordinal reading back positionally (outside the "un quarto" fraction
    # frame) so the scoped_ordinal construction can bind higher ordinals.
    homomap = dict(_homograph_ordinal_map(vocab, blacklist))
    # some languages spell the quarter ordinal with a surface their own number
    # vocabulary does not list as an ordinal ("quarto" in Aragonese, whose
    # ordinal-4 is "cuatreno" and whose fraction-4 is "cuarto"); an explicit
    # homograph entry licenses that surface in the ordinal frames only.
    if extra_homograph:
        homomap.update(extra_homograph)
    definite = _ROMANCE_DEFINITE.get(lang_code, frozenset())
    quarter_words = _quarter_word_surfaces(lang_code)
    if not homomap or (not definite and not quarter_words):
        return base

    def folded(tokens):
        return base(_license_ordinal_fraction(tokens, homomap, definite,
                                              quarter_words))
    return folded


# ---------------------------------------------------------------------------
# deep-time SCALE-frame licensing for the Romance folds
# ---------------------------------------------------------------------------
#
# Two surfaces the general Romance fold deliberately leaves alone must become
# numbers in the one frame that precedes a deep-time SCALE word:
#
#   * the INDEFINITE ARTICLE ("un"/"une"/"um") -- blacklisted from the fold
#     because it is the everyday article ("un jour", "um dia"); directly before
#     a scale word it is the number one ("un milliard", "un billón d'anos"), the
#     same positional licensing English does in ``_fold_article_magnitude``;
#   * the THOUSAND word ("mil") directly before a MILLION word -- the long-scale
#     languages spell 10^9 as a multiword "mil millones"/"mil milhões"; folding
#     "mil" to the numeral 1000 lets the deep-time order read it as NUM=1000
#     SCALE=million (1000 Ma = 10^9), reusing the numeral machinery whole.
#
# Both fire ONLY in the scale frame (the very next token is a scale word), so
# every other "un"/"mil" reading is untouched.
def _romance_scale_frame(lang_code, article_ones,
                         million_extra=frozenset(), scale_extra=frozenset()):
    """Wrap a Romance fold with the deep-time SCALE-frame number licensing.

    ``article_ones`` are the language's indefinite-article surfaces (the
    number one before a scale word).  The thousand/million/scale word sets are
    read from the language's ``NumberVocabulary`` (short + long scale); the
    vocabulary lists only singular scale words, so ``million_extra`` supplies
    the plural million surfaces the multiword 10^9 ("mil millones", "mil
    milhões") actually uses, and ``scale_extra`` any further billion-cognate
    surfaces the article-one frame must recognise.
    """
    numbers_mod = import_module("ovos_number_parser.numbers_" + lang_code)
    vocab = next(v for v in vars(numbers_mod).values()
                 if type(v).__name__ == "NumberVocabulary")
    thousand, million, scale_all = set(), set(million_extra), set(scale_extra)
    scale_all |= set(million_extra)
    for table in (vocab.SHORT_SCALE, vocab.LONG_SCALE):
        for factor, surf in table.items():
            if not surf:
                continue
            s = surf.lower()
            scale_all.add(s)
            if factor == 1_000:
                thousand.add(s)
            elif factor == 1_000_000:
                million.add(s)

    def prepass(tokens):
        out = []
        n = len(tokens)
        i = 0
        while i < n:
            t = tokens[i]
            nxt = tokens[i + 1] if i + 1 < n else None
            nxt_txt = nxt.text if nxt is not None else None
            if (not t.is_number and nxt is not None and not nxt.is_number
                    and t.text in article_ones and nxt_txt in scale_all):
                out.append(_scale_num_token(1, t))
                i += 1
                continue
            if (not t.is_number and nxt is not None and not nxt.is_number
                    and t.text in thousand and nxt_txt in million):
                out.append(_scale_num_token(1_000, t))
                i += 1
                continue
            out.append(t)
            i += 1
        return _reindex(tuple(out))

    return prepass


def _scale_num_token(value, like):
    """A numeral token of ``value`` carrying ``like``'s character extent."""
    return Token(text=str(value), raw=like.raw, index=0, is_number=True,
                 value=value, char_start=like.char_start,
                 char_end=like.char_end)


def _with_scale_frame(fold, lang_code, article_ones,
                      million_extra=frozenset(), scale_extra=frozenset()):
    prepass = _romance_scale_frame(lang_code, article_ones,
                                   million_extra, scale_extra)
    return lambda tokens: fold(prepass(tokens))


# pt: feminine ordinals "segunda/quarta/quinta/sexta" are weekday names
_fold_pt_base = _make_romance_fold("pt", {"segunda", "quarta", "quinta", "sexta",
                                          "terca", "terça"})


def _license_weekday_ordinal(tokens, mapping, units):
    """Read a weekday-homograph ordinal as its digit before a period noun.

    The feminine ordinals a Romance language blacklists from the number fold
    are blacklisted because each is also the name of a weekday -- Portuguese
    "segunda" is at once the ordinal "second" and Monday (segunda-feira).  The
    blacklist protects the weekday reading everywhere, but directly before the
    week noun the weekday reading is not available: "a segunda semana de março"
    is the second week of March, never Monday, because a weekday name does not
    take a following "semana".  In that one position the homograph is licensed
    to its digit so the "nth week of a month" composition can bind it, the same
    positional licensing that lets the plural weekday surface be read only in
    the syntactic slot that disambiguates it.
    """
    out = []
    n = len(tokens)
    for i, tok in enumerate(tokens):
        nxt = tokens[i + 1] if i + 1 < n else None
        if (not tok.is_number and tok.text in mapping
                and nxt is not None and nxt.text in units):
            value = mapping[tok.text]
            out.append(Token(text=str(value), raw=tok.raw, index=0,
                             is_number=True, value=value))
        else:
            out.append(tok)
    return _reindex(tuple(out))


#: The week nouns of Portuguese, the position that licenses the ordinal
#: reading of a weekday-homograph ordinal.
_PT_WEEK_UNITS = frozenset({"semana", "semanas"})
#: weekday-homograph feminine ordinal -> its value.  "terça" (Tuesday) is not
#: listed: the third ordinal is "terceira", no homograph, and it already folds.
_PT_ORDINAL_BEFORE_WEEK = {"segunda": 2, "quarta": 4, "quinta": 5, "sexta": 6}

# Portuguese writes the clock quarter with an explicit article -- "quatro e um
# quarto" == 4:15, "duas menos um quarto" == 1:45 -- where the "um"/"uma" is the
# article of "um quarto" (a quarter), not a number.  The spelled-number fold
# would otherwise read "quatro e um" as 5 (the JOIN_WORD "e") or fold the lone
# "um" to the digit 1, both of which lose the article the clock grammar needs.
# Unlike Italian/French (which blacklist "un" outright), Portuguese still spells
# "vinte e um" == 21 with a standalone "um", so the article cannot be removed
# from the number vocabulary wholesale -- it is protected only in the one place
# it is unambiguously an article: directly before the "quarto" fraction word.
# The stream is folded around such an "um", leaving "vinte e um dias" == 21
# untouched.  Source: Ciberdúvidas da Língua Portuguesa, "as horas".
_PT_QUARTER_SURFACES = frozenset({"quarto", "quartos"})


def fold_pt(tokens):
    tokens = _license_weekday_ordinal(tokens, _PT_ORDINAL_BEFORE_WEEK,
                                      _PT_WEEK_UNITS)
    protected = {
        i for i, t in enumerate(tokens)
        if t.text in ("um", "uma") and i + 1 < len(tokens)
        and tokens[i + 1].text in _PT_QUARTER_SURFACES
    }
    if not protected:
        return _fold_pt_base(tokens)
    out = []
    segment = []
    for i, t in enumerate(tokens):
        if i in protected:
            if segment:
                out.extend(_fold_pt_base(tuple(segment)))
                segment = []
            out.append(t)
        else:
            segment.append(t)
    if segment:
        out.extend(_fold_pt_base(tuple(segment)))
    return _reindex(tuple(out))


# Portuguese marks a *recurring set* with the plural throughout: "todas as
# terceiras quintas-feiras do mes" (every third thursday of the month) carries
# a plural article, a plural ordinal and a plural weekday, where the singular
# would name one particular occasion.  The plural feminine ordinal is the same
# closed morphological class as its singular, so it is derived from the number
# vocabulary (feminine form + "s") rather than listed by hand.
#
# Both genders are folded, because the weekday the ordinal agrees with picks
# the gender: "as terceiras quintas-feiras" (feminine, a weekday in -feira)
# against "os primeiros sabados" (masculine, saturday/sunday).
#
# Two classes of surface are held back.  The weekday homographs are skipped in
# the plural for exactly the reason they are blacklisted in the singular --
# "quintas" is Thursday, never five -- which also leaves "segundas" alone so
# "todas as segundas-feiras" stays a weekday.  And the masculine plurals that
# are ordinary nouns the fold must not eat are excluded by name: "segundos" is
# seconds and "quartos" is the clock quarter, both of which other constructions
# in this engine bind as words.
_PT_WEEKDAY_ORDINALS = frozenset({"segunda", "terca", "terça", "quarta",
                                  "quinta", "sexta"})
#: masculine plural ordinals that are homographs of a noun this engine reads.
_PT_ORDINAL_NOUN_HOMOGRAPHS = frozenset({"segundos", "quartos"})
#: plural feminine ordinals that are homographs of a Roman-calendar anchor.
#: "nonas" is at once the ninth-plural ordinal and the vernacular Nones; it is
#: held back from the plural-ordinal fold and licensed to the digit 9 by
#: :func:`_license_pt_nonas` everywhere except the anchor frame ("as nonas de
#: julho"), where it must survive as the word so ``roman_date`` binds it.
_PT_ANCHOR_ORDINAL_HOMOGRAPHS = frozenset({"nonas"})
#: pt "of" prepositions (plain and article-fused) that introduce the month in
#: the Roman-anchor frame -- the position that licenses the Nones reading.
_PT_OF_PREP = frozenset({"de", "do", "da", "dos", "das", "d"})


def _license_pt_nonas(tokens):
    """Positionally read the homograph "nonas".

    Portuguese "nonas" is at once the feminine plural ordinal "ninth" and the
    vernacular name of the Roman *Nones*.  The two readings split by position:
    the anchor is followed by an "of" preposition introducing the month ("as
    nonas **de** julho"), the ordinal is not ("as nonas semanas").  "nonas" is
    withheld from the plural-ordinal fold (see :data:`_PT_ANCHOR_ORDINAL_HOMOGRAPHS`)
    and licensed back to the digit 9 here in every position that is **not** the
    anchor frame, so ``roman_date`` binds the Nones while the plain ordinal
    still folds.
    """
    out = list(tokens)
    n = len(out)
    for i, t in enumerate(out):
        if t.is_number or t.text != "nonas":
            continue
        nxt = out[i + 1] if i + 1 < n else None
        if nxt is not None and nxt.text in _PT_OF_PREP:
            continue
        out[i] = Token(text="9", raw=t.raw, index=0, is_number=True,
                       value=9, char_start=t.char_start, char_end=t.char_end)
    return _reindex(tuple(out))


def _pt_plural_ordinals():
    from ovos_number_parser import numbers_pt
    vocab = next(v for v in vars(numbers_pt).values()
                 if type(v).__name__ == "NumberVocabulary")
    out = {}
    for val, surf in vocab.ORDINAL_UNITS.items():
        if not surf:
            continue
        for form in _fem_forms(surf) | {surf.lower()}:
            if form in _PT_WEEKDAY_ORDINALS:
                continue
            plural = form + "s"
            if plural in _PT_ORDINAL_NOUN_HOMOGRAPHS:
                continue
            if plural in _PT_ANCHOR_ORDINAL_HOMOGRAPHS:
                continue
            out[plural] = val
    return out


def _pt_ordinal_fold(fold):
    """Wrap ``fold`` so *only* the plural ordinals above are pre-folded.

    ``with_ordinals`` merges the model-derived ``pronounce_ordinal_pt`` map by
    default, whose **singular** entries are homographs this engine binds as
    words -- "quarto" is the clock quarter ("as tres e quarto", "um quarto de
    hora") and "segundo" is a second.  Folding those to digits would take the
    clock fraction and duration constructions apart, so every model-derived
    surface is excluded and the plural table is the whole contribution.
    """
    plurals = _pt_plural_ordinals()
    from chronologia.extract.numfold_ordinals import _pron_ordinal_map
    exclude = set(_pron_ordinal_map("pt")) - set(plurals)
    return _with_ordinals(fold, "pt", plurals, exclude=exclude)


fold_pt = _pt_ordinal_fold(fold_pt)
_fold_pt_ordinal = fold_pt


def fold_pt(tokens):  # noqa: F811 -- final wrap adds Nones licensing
    return _license_pt_nonas(_fold_pt_ordinal(tokens))


# deep-time SCALE-frame licensing: "um bilião"/"mil milhões de anos"
fold_pt = _with_scale_frame(fold_pt, "pt", frozenset({"um", "uma"}),
                            million_extra=frozenset({"milhões", "milhoes",
                                                     "milhão", "milhao"}))


fold_es = _make_romance_fold("es", set())
fold_gl = _make_romance_fold("gl", set())
fold_ca = _make_romance_fold("ca", set())
# deep-time SCALE-frame licensing (article-one + multiword "mil <million>")
fold_es = _with_scale_frame(fold_es, "es", frozenset({"un", "una"}),
                            million_extra=frozenset({"millones", "millon",
                                                     "millón"}))
fold_gl = _with_scale_frame(fold_gl, "gl", frozenset({"un", "unha"}),
                            million_extra=frozenset({"millóns", "millons",
                                                     "millón", "millon"}))
fold_ca = _with_scale_frame(fold_ca, "ca", frozenset({"un", "una"}),
                            million_extra=frozenset({"milions", "milió"}))
# an: "martes" (Tuesday) must never be read as a number; the Romance factory
# folds via numbers_an's NumberVocabulary and the shared a.c./d.c. glue.
# an: "quarto" (the qu- spelling) is the idiomatic masculine ordinal 4th before
# "trimestre", but numbers_an lists ordinal-4 only as "cuatreno" and fraction-4
# as "cuarto", so "quarto" is unknown to the vocabulary; an explicit homograph
# entry licenses it to the digit 4 in the ordinal frames (definite article /
# before the quarter noun) only, leaving the "cuarto" quarter-hour fraction
# ("un cuarto de hora") untouched.
fold_an = _make_romance_fold("an", {"martes"}, extra_homograph={"quarto": 4})
# Aragonese apocopated ordinals ("primer", "tercer") the NumberVocabulary lists
# only in their full form ("primero", "tercero"); the apocope is the surface a
# noun phrase attests ("o tercer trimestre").  numbers_an carries no ordinal
# pronouncer, so this is an explicit closed table.
fold_an = _with_ordinals(fold_an, "an", {"primer": 1, "tercer": 3})
# mwl (Mirandese): the feminine ordinals segunda/terça/quarta/quinta/sesta
# are weekday names (segunda-feira ...) and sábado is Saturday -- none may be
# read as a number.
fold_mwl = _make_romance_fold(
    "mwl", {"segunda", "terça", "terca", "quarta", "quinta", "sesta",
            "sabado", "sábado"})



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


#: Frisian inflected "coming-hour" forms (the genitive hour used after
#: healwei/kertier/oer/foar), mapped to their hour value.
_FY_HOURS = {"ienen": 1, "twaen": 2, "trijen": 3, "fjouweren": 4, "fiven": 5,
             "seizen": 6, "sânen": 7, "achten": 8, "njoggenen": 9,
             "tsienen": 10, "alven": 11, "tolven": 12}


# Per-language stop-sets: clock fractions + scale words that must not fold.
fold_de = _lazy_germanic_fold(
    "ovos_number_parser.numbers_de", "extract_number_de",
    # "billion"/"billionen" is the long-scale 10^12 word (German Billion); it is
    # withheld here so it survives as the deep-time SCALE slot instead of being
    # read as a plain number by the value-probe.
    {"halb", "viertel", "dreiviertel", "million", "millionen",
     "milliarde", "milliarden", "billion", "billionen", "tausend"})
fold_nl = _lazy_germanic_fold(
    "ovos_number_parser.numbers_nl", "extract_number_nl",
    # "biljoen" = 10^12 (Dutch long scale), withheld so the SCALE slot survives.
    {"half", "kwart", "miljoen", "miljard", "biljoen", "duizend"},
    ord_suffixes={"e", "de", "ste", "te"})
fold_sv = _lazy_germanic_fold(
    "ovos_number_parser.numbers_sv", "extract_number_sv",
    {"halv", "kvart", "miljon", "miljoner", "miljard", "miljarder", "tusen"})
# Swedish spells the day-of-month with a single-token ordinal that
# ``extract_number_sv`` does not read (it returns False for "femtonde",
# "tjugotredje" ...), so the Germanic value-probe fold leaves it stranded and
# the whole month is returned.  ``pronounce_ordinal_sv`` DOES emit every 1..31
# as one word (första, femtonde, tjugoförsta, tjugotredje, trettioförsta ...),
# so chronologia owns the ordinal locally by inverting that pronouncer.  SAOL
# (Svenska Akademiens ordlista): ordningstal.
fold_sv = _with_ordinals(fold_sv, "sv")
fold_da = _lazy_germanic_fold(
    "ovos_number_parser.numbers_da", "extract_number_da",
    {"halv", "halvdel", "halvdelen", "kvart", "million", "millioner",
     "milliard", "milliarder", "tusind"})
# Danish: ``extract_number_da`` returns False for the spelled ordinals
# ("femtende", "enogtyvende" ...) -- the release-blocked ovos-number-parser
# path -- so chronologia owns them by inverting ``pronounce_ordinal_da``, which
# emits every 1..31 as one word (første, femtende, enogtyvende, treogtyvende,
# enogtredivte ...).  Retskrivningsordbogen (Dansk Sprognævn): ordenstal.
fold_da = _with_ordinals(fold_da, "da")
fold_nb = _lazy_germanic_fold(
    "ovos_number_parser.numbers_nb", "extract_number_nb",
    {"halv", "halvdel", "halvdelen", "kvart", "million", "millioner",
     "milliard", "milliarder", "tusen"})
fold_nn = _lazy_germanic_fold(
    "ovos_number_parser.numbers_nn", "extract_number_nn",
    {"halv", "halvdel", "halvdelen", "kvart", "million", "millionar",
     "milliard", "milliardar", "tusen"})
fold_fy = _lazy_germanic_fold(
    "ovos_number_parser.numbers_fy", "extract_number_fy",
    {"heal", "healwei", "kertier", "miljoen", "miljard", "tûzen"},
    ord_suffixes={"e", "de", "te"}, word_map=_FY_HOURS)


# ---------------------------------------------------------------------------
# Turkic / isolating spelled-number folding (tr / az / id / ms / kab)
#
# These families expose a single ``extract_number_<lang>`` reader (no
# ``NumberVocabulary``), so the Germanic single-extractor fold applies
# verbatim: a maximal run of number-words is joined and read to one digit
# token, with clock-fraction and scale words withheld so the token that
# distinguishes a construction survives.  ``extract_number_<lang>`` here has
# signature ``(text, short_scale=True, ordinals=False)`` -- the fold's
# ``value_of`` tries ``ordinals=True`` then the cardinal default, which the
# extra ``short_scale`` positional default leaves untouched.
# ---------------------------------------------------------------------------
# Turkish spoken-clock hours carry the case suffix the direction word agrees
# with -- accusative (-ı/-i/-u/-ü) before "geçe" (past), dative (-e/-a) before
# "kala" (to).  ``extract_number_tr`` reads only the bare cardinal, so these
# inflected surfaces (which the pronounce side never emits) are mapped back to
# their hour value here; the accusative/dative distinction is redundant with
# the mandatory geçe/kala word and so is safely collapsed to the digit.
# 1..10 as single tokens ("saat dokuzu beş geçe" = 9:05, "yediye çeyrek kala"
# = 6:45); 11/12 ("on bir"/"on iki") inflect their final word (biri/ikiyi),
# so the "on" + mapped-final-word run folds through the cardinal reader.
_TR_HOURS = {
    "biri": 1, "ikiyi": 2, "üçü": 3, "dördü": 4, "beşi": 5,
    "altıyı": 6, "yediyi": 7, "sekizi": 8, "dokuzu": 9, "onu": 10,
    "bire": 1, "ikiye": 2, "üçe": 3, "dörde": 4, "beşe": 5,
    "altıya": 6, "yediye": 7, "sekize": 8, "dokuza": 9, "ona": 10,
}
_tr_numfold = _lazy_germanic_fold(
    "ovos_number_parser.numbers_tr", "extract_number_tr",
    # "buçuk" (=30, the additive half-past word) and "çeyrek" (=15) are held
    # out of the number run so the FRACTION slot binds them ("üç buçuk" =
    # 3:30) instead of folding to 3.5.
    {"yarım", "çeyrek", "buçuk", "bin", "milyon", "milyar"})


# Turkic locative case marks "at <hour>" on the clock numeral: Turkish "saat
# üçte" (at three), Azerbaijani "saat üçdə".  The suffix harmonises for
# backness and preceding-consonant voicing -- tr -te/-ta/-de/-da, az
# -tə/-ta/-də/-da -- and ``extract_number_<lang>`` does not read the inflected
# surface: it silently mis-reads "üçte"/"üçdə" as the fraction 1/3 (0.333), so
# the HOUR slot never binds and the whole span is dropped.  This mirrors the
# fi ablative ("kello kolmelta"), eu inessive ("hiruretan") and hu temporal
# ("háromkor") clock folds already in the agglutinative batch, and the
# accusative/dative geçe/kala fold just below: fold the case-suffixed hour
# back to its bare cardinal so the ordinary number path binds it.  Sources:
# Wiktionary, -də/-da (Azerbaijani) and -de/-te (Turkish) locative case; the
# suffixed numeral is the everyday telling-time form (TDK Güncel Türkçe
# Sözlük "saat"; Azərbaycan dilinin izahlı lüğəti "saat").
#
# Fired only in the clock frame (a "saat" hour-noun token present) and only
# when the stripped stem reads as a bare 0..23 cardinal, so bare numbers,
# dates and any non-clock word ending in these letters stay byte-identical.
# The strip runs *before* the cardinal run-fold so a compound hour folds
# through it: "on birde" -> "on" + "bir" -> 11, "on ikide" -> 12.
_TR_LOCATIVE_SUFFIXES = ("tə", "də", "te", "ta", "de", "da")


def _strip_locative_hour(tokens, lang):
    if not any(t.text == "saat" for t in tokens):
        return tokens
    import importlib
    extract = getattr(importlib.import_module(
        "ovos_number_parser.numbers_" + lang), "extract_number_" + lang)
    out = []
    for t in tokens:
        if not t.is_number:
            w = t.text
            for suf in _TR_LOCATIVE_SUFFIXES:
                if w.endswith(suf) and len(w) > len(suf):
                    stem = w[:-len(suf)]
                    try:
                        val = extract(stem)
                    except Exception:
                        val = False
                    if (isinstance(val, (int, float))
                            and not isinstance(val, bool)
                            and float(val) == int(val) and 0 <= val <= 23):
                        t = replace(t, text=stem)
                    break
        out.append(t)
    return tuple(out)


def fold_tr(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Turkish fold: strip a locative-case clock hour ("saat üçte" -> "üç"),
    cardinal run fold, then map the case-marked spoken-clock hour to its digit.
    The hour map runs *after* the cardinal fold so the mapped hour does not
    merge with a following bare-minute cardinal: "dokuzu beş geçe" must stay
    [9][5][geçe] (9:05), not fold to one number.
    """
    tokens = _strip_locative_hour(tokens, "tr")
    folded = _tr_numfold(tokens)
    out = [replace(t, text=str(_TR_HOURS[t.text]), is_number=True,
                   value=_TR_HOURS[t.text])
           if (not t.is_number and t.text in _TR_HOURS) else t
           for t in folded]
    return _reindex(tuple(out))
# Turkish ordinals so the ``NUM`` slot of "2020'nin ilk/ikinci yarısı" binds:
# ``pronounce_ordinal_tr`` emits birinci/ikinci ..., and "ilk" -- the ordinary
# word for "first/initial" that the half phrase actually uses -- is added as the
# one surface the pronouncer does not cover.  TDK Güncel Türkçe Sözlük: "ilk" =
# birinci; "ikinci" = sıra sayı sıfatı.  https://sozluk.gov.tr
fold_tr = _with_ordinals(fold_tr, "tr", {"ilk": 1})
_az_numfold = _lazy_germanic_fold(
    "ovos_number_parser.numbers_az", "extract_number_az",
    {"yarım", "min", "milyon", "milyard"})


def fold_az(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Azerbaijani fold: strip the locative-case clock hour ("saat üçdə" ->
    "üç") before the cardinal run-fold, then fold as usual."""
    return _az_numfold(_strip_locative_hour(tokens, "az"))
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



# ---------------------------------------------------------------------------
# fr / it / ro / oc / ast: language-specific pre-passes layered on the shared
# Romance fold factory.
#
# ``_make_romance_fold`` already owns spelled-number folding (compound
# numbers, JOIN_WORD bridging, feminine ordinals, and the a.c./d.c. glue).
# These five locales need small token-surgery pre-passes it does not provide:
# elided proclitics split so a bare year-word binds ("d'annees" -> d annees),
# fixed idiom phrases collapse to one connector ("il y a", "avanti cristo"),
# French/Occitan "NhMM" clock notation folds to an HH:MM literal, and a digit
# followed by an ordinal-suffix word merges ("1er" -> 1, "20-lea" -> 20).
# "un/una" are blacklisted from folding so the clock fraction "meno un
# quarto" keeps its article token.
# ---------------------------------------------------------------------------

def _elision_split(tokens, proclitics):
    """Split a leading elided proclitic ("d'annees" -> "d", "annees").

    Only the closed proclitic set splits, so a lexical apostrophe inside a
    word ("aujourd'hui") stays whole."""
    out = []
    for t in tokens:
        head, sep, tail = t.text.partition("'")
        if not sep:
            head, sep, tail = t.text.partition("’")
        if sep and head in proclitics and tail:
            # keep each half's character extent into the original utterance --
            # the proclitic occupies the head chars, the elided word the tail
            # chars past the apostrophe -- so a mention built on the split word
            # ("d'abril") still recovers a char span instead of ``None``.
            cs, ce = t.char_start, t.char_end
            if cs is None or ce is None:
                h_start = h_end = w_start = None
            else:
                h_start, h_end, w_start = cs, cs + len(head), ce - len(tail)
            out.append(Token(text=head, raw=head, index=0,
                             char_start=h_start, char_end=h_end))
            out.append(Token(text=tail, raw=tail, index=0,
                             char_start=w_start, char_end=ce if cs is not None
                             else None))
        else:
            out.append(t)
    return _reindex(out)


def _collapse_phrase(tokens, words, surface):
    """Collapse a fixed multiword sequence ("il y a") to one token."""
    n = len(words)
    out = []
    i = 0
    while i < len(tokens):
        if [t.text for t in tokens[i:i + n]] == words:
            raw = " ".join(t.raw for t in tokens[i:i + n])
            out.append(Token(text=surface, raw=raw, index=0))
            i += n
        else:
            out.append(tokens[i])
            i += 1
    return _reindex(out)


def _collapse_h_clock(tokens):
    """Fold French/Occitan "20h30"/"20h" into one ``HH:MM`` clock literal."""
    out = []
    i = 0
    n = len(tokens)
    while i < n:
        t = tokens[i]
        nxt = tokens[i + 1] if i + 1 < n else None
        nn = tokens[i + 2] if i + 2 < n else None
        if (t.is_number and t.value is not None and 0 <= t.value <= 24
                and float(t.value).is_integer() and nxt is not None
                and nxt.text == "h"):
            if (nn is not None and nn.is_number and nn.value is not None
                    and 0 <= nn.value <= 59 and float(nn.value).is_integer()):
                lit = "%d:%02d" % (int(t.value), int(nn.value))
                out.append(Token(text=lit, raw=lit, index=0))
                i += 3
                continue
            lit = "%d:00" % int(t.value)
            out.append(Token(text=lit, raw=lit, index=0))
            i += 2
            continue
        out.append(t)
        i += 1
    return _reindex(out)


def _merge_digit_ordinal(tokens, suffixes):
    """Drop a lone ordinal-suffix word after a digit ("1 er" -> 1)."""
    out = []
    i = 0
    n = len(tokens)
    while i < n:
        t = tokens[i]
        nxt = tokens[i + 1] if i + 1 < n else None
        if (t.is_number and nxt is not None and not nxt.is_number
                and nxt.text in suffixes):
            out.append(t)
            i += 2
            continue
        out.append(t)
        i += 1
    return _reindex(out)


def _romance_prepass_fold(lang_code, blacklist, proclitics=frozenset(),
                          phrases=(), h_clock=False, ord_suffixes=frozenset(),
                          fem_ord=None, reader=None,
                          extra_numwords=frozenset()):
    base = _make_romance_fold(lang_code, blacklist, reader=reader,
                              extra_numwords=extra_numwords)
    fem_ord = fem_ord or {}

    def fold(tokens):
        if proclitics:
            tokens = _elision_split(tokens, proclitics)
        for seq, surface in phrases:
            tokens = _collapse_phrase(tokens, seq, surface)
        if h_clock:
            tokens = _collapse_h_clock(tokens)
        if ord_suffixes:
            tokens = _merge_digit_ordinal(tokens, ord_suffixes)
        if fem_ord:
            # feminine ordinals the number back-end rejects ("a doua",
            # "la segunda") -- map the surface straight to its digit.
            tokens = _reindex(tuple(
                Token(text=str(fem_ord[t.text]), raw=t.raw, index=0,
                      is_number=True, value=fem_ord[t.text])
                if (not t.is_number and t.text in fem_ord) else t
                for t in tokens))
        return base(tokens)

    return fold


# -- French -----------------------------------------------------------------
_FR_PHRASES = [
    (["avant", "jésus", "christ"], "avjc"), (["avant", "jesus", "christ"], "avjc"),
    (["avant", "notre", "ère"], "avjc"), (["avant", "notre", "ere"], "avjc"),
    (["av", "j", "c"], "avjc"), (["av", "jc"], "avjc"),
    (["après", "jésus", "christ"], "apjc"), (["apres", "jesus", "christ"], "apjc"),
    (["de", "notre", "ère"], "apjc"), (["de", "notre", "ere"], "apjc"),
    (["ap", "j", "c"], "apjc"), (["ap", "jc"], "apjc"),
    (["il", "y", "a"], "ilya"),
    (["avant", "hier"], "avanthier"),
    (["apres", "demain"], "apresdemain"), (["après", "demain"], "apresdemain"),
    (["week", "end"], "weekend"),
]
#: the oclock surfaces that turn a preceding "un"/"une" into the hour 1.
_FR_HEURE = frozenset({"heure", "heures"})


def _license_fr_une_heure(tokens):
    """Read "un"/"une" as the hour 1 directly before "heure(s)".

    French "une" is at once the feminine indefinite article ("une semaine" =
    a week) and the feminine cardinal one, and the shared number back-end
    leaves both "un" and "une" unfolded so the article reading survives
    ("il y a une semaine").  On the clock, though, the hour name is spoken
    exactly like the article -- "une heure" is one o'clock, and every
    fraction/meridiem/subtractive frame built on it ("une heure et quart",
    "une heure moins le quart", "une heure du matin") needs the 1 to bind the
    HOUR slot the way "deux heures" already does.  The two readings are
    distinguishable by position: the cardinal is the "un"/"une" immediately
    before the oclock word "heure(s)", and the article everywhere else.  Only
    that position is licensed to the digit 1, so "une semaine" and every other
    article use stays byte-identical.
    """
    out = list(tokens)
    n = len(out)
    for i, t in enumerate(out):
        if t.is_number or t.text not in ("un", "une"):
            continue
        nxt = out[i + 1] if i + 1 < n else None
        if nxt is not None and nxt.text in _FR_HEURE:
            out[i] = replace(t, text="1", is_number=True, value=1)
    return _reindex(tuple(out))


# French composes its tens above sixty rather than naming them: eighty is
# four twenties ("quatre-vingts") and ninety is eighty plus ten
# ("quatre-vingt-dix"), a vigesimal reading the shared Romance extractor does
# not perform -- it adds the components instead and returns 24 and 34.  The
# French wrapper is the one that carries the vigesimal collapse, so French
# reads its numbers through the wrapper.  Without it every French phrase built
# on 80 or 90 -- "les années quatre-vingt", "quatre-vingts ans" -- parsed as a
# different number or not at all.  Source: Académie française, "quatre-vingts"
# (9e éd.), https://www.dictionnaire-academie.fr/article/A9Q0152
fold_fr = _romance_prepass_fold(
    "fr", {"un", "une"},
    reader=lambda text, ordinals=True: extract_number_fr(
        text, ordinals=ordinals),
    # "vingt" and "cent" take the plural -s exactly when they close a round
    # number -- "quatre-vingts", "deux cents", but "quatre-vingt-un" and "deux
    # cent un" -- and the shared vocabulary lists only the singular, so the
    # prescribed spelling of 80 and 200 fell out of the run and left the
    # leading "quatre"/"deux" behind as the whole number.
    extra_numwords=frozenset({"vingts", "cents"}),
    proclitics=frozenset({"d", "l", "j", "n", "s", "c", "m", "t", "qu"}),
    # feminine ordinals the number back-end rejects but that agree with a
    # feminine noun the constructions bind ("la premiere/première moitié",
    # "la seconde moitié").  "seconde" is unambiguous in French date text --
    # French has no time-unit "seconde" vocabulary here -- so it maps straight to
    # 2 like the Spanish/Romanian feminine tables above.
    fem_ord={"première": 1, "premiere": 1, "seconde": 2},
    phrases=_FR_PHRASES, h_clock=True,
    ord_suffixes=frozenset({"er", "ere", "ère", "e", "eme", "ème",
                            "nd", "nde", "d", "re", "es", "emes", "èmes"}))
# deep-time SCALE-frame licensing: "un milliard/un billion d'années"
fold_fr = _with_scale_frame(fold_fr, "fr", frozenset({"un", "une"}))
# clock-frame licensing: "une heure" (one o'clock) and every fraction/meridiem/
# subtractive frame built on it -- "un"/"une" reads as the hour 1 before
# "heure(s)", the article everywhere else.
_fold_fr_scaled = fold_fr


def fold_fr(tokens):  # noqa: F811 -- final wrap adds une-heure licensing
    return _fold_fr_scaled(_license_fr_une_heure(tokens))


# -- Italian ----------------------------------------------------------------
_IT_PHRASES = [
    (["avanti", "cristo"], "ac"), (["dopo", "cristo"], "dc"),
    (["avanti", "l", "era", "volgare"], "ac"), (["era", "volgare"], "dc"),
    (["altro", "ieri"], "altroieri"), (["avanti", "ieri"], "avantieri"),
    (["dopo", "domani"], "dopodomani"),
    (["fine", "settimana"], "finesettimana"),
]
#: the di-family prepositions (plain and article-fused) that introduce the
#: reference date after the before-marker "prima" -- "prima di gennaio",
#: "prima del 5 aprile".  "d"/"dell" are the elision-split heads of "d'"/
#: "dell'".
_IT_OFFSET_PREP = frozenset({"di", "del", "dello", "della", "dell", "dei",
                             "degli", "delle", "d"})


def _license_it_prima(tokens):
    """Positionally read the homograph "prima".

    Italian "prima" is at once the feminine ordinal "first" and the
    directional marker "before"; a blanket number-fold would erase the
    marker, a blanket blacklist would erase the ordinal.  The two readings
    are distinguishable by position, so "prima" is blacklisted from the
    general fold (see :func:`fold_it`) and licensed to the digit 1 *only*
    where it is the ordinal -- i.e. everywhere it is **not** in the offset
    frame.  It is the before-marker when it either

    * is immediately followed by a di-family preposition introducing the
      reference date ("prima **di** gennaio", "prima **del** 5 aprile"), or
    * closes a ``[NUM] UNIT`` duration ("3 giorni **prima** del ...",
      "tre giorni **prima** ...") -- the token before it a (non-number) unit
      word, the one before that a number;

    and the ordinal "first" otherwise ("**prima** settimana", "la **prima**
    domenica", "**prima** quindicina"), where it folds to 1 so the ordinal
    constructions bind it.  The rule keys off the preposition and the
    NUM+UNIT shape, never a hard-coded month or unit list, so it generalises.
    """
    out = list(tokens)
    n = len(out)
    for i, t in enumerate(out):
        if t.is_number or t.text != "prima":
            continue
        nxt = out[i + 1] if i + 1 < n else None
        prev = out[i - 1] if i - 1 >= 0 else None
        prev2 = out[i - 2] if i - 2 >= 0 else None
        is_before_marker = (
            (nxt is not None and nxt.text in _IT_OFFSET_PREP)
            or (prev is not None and not prev.is_number
                and prev2 is not None and prev2.is_number))
        if not is_before_marker:
            out[i] = Token(text="1", raw=t.raw, index=0, is_number=True,
                           value=1, char_start=t.char_start,
                           char_end=t.char_end)
    return _reindex(tuple(out))


# "prima" is the feminine ordinal "first" *and* the directional marker
# "before"; it is blacklisted from the general number fold (so the offset
# composition can read the marker) and positionally licensed back to the digit
# 1 in ordinal position by ``_license_it_prima``.  The unambiguous masculine
# "primo" still folds to 1 in the general pass.
_fold_it_base = _romance_prepass_fold(
    "it", {"un", "uno", "una", "milioni", "miliardi", "mila", "prima"},
    proclitics=frozenset({"l", "un", "d", "dell", "all", "nell", "dall",
                          "sull", "quest", "quell", "c"}),
    phrases=_IT_PHRASES)


def fold_it(tokens):
    return _license_it_prima(_fold_it_base(tokens))


# deep-time SCALE-frame licensing: "un miliardo/un bilione di anni fa"
fold_it = _with_scale_frame(fold_it, "it", frozenset({"un", "uno", "una"}))


# -- Romanian ---------------------------------------------------------------
_RO_PHRASES = [
    (["înainte", "de", "hristos"], "ihr"), (["inainte", "de", "hristos"], "ihr"),
    (["după", "hristos"], "dhr"), (["dupa", "hristos"], "dhr"),
    (["î", "hr"], "ihr"), (["i", "hr"], "ihr"), (["d", "hr"], "dhr"),
    (["miezul", "nopții"], "miezulnoptii"), (["miezul", "noptii"], "miezulnoptii"),
    (["week", "end"], "weekend"),
]
fold_ro = _romance_prepass_fold(
    "ro", {"un", "unu", "una", "o"},
    phrases=_RO_PHRASES,
    ord_suffixes=frozenset({"lea", "a", "ea", "le"}),
    fem_ord={"doua": 2, "două": 2, "treia": 3, "patra": 4, "cincea": 5,
             "șasea": 6, "sasea": 6, "șaptea": 7, "saptea": 7, "opta": 8,
             "noua": 9, "zecea": 10})
# deep-time SCALE-frame licensing: "un miliard/un bilion de ani în urmă"
fold_ro = _with_scale_frame(fold_ro, "ro", frozenset({"un", "unu", "una", "o"}))


# -- Occitan ----------------------------------------------------------------
_OC_PHRASES = [
    (["abans", "jèsus", "crist"], "acn"), (["abans", "jesus", "crist"], "acn"),
    (["aprèp", "jèsus", "crist"], "apc"), (["aprep", "jesus", "crist"], "apc"),
    (["abans", "ièr"], "abansièr"), (["abans", "ier"], "abansièr"),
    (["passat", "deman"], "passatdeman"), (["delà", "deman"], "passatdeman"),
    (["que", "ven"], "queven"),
    (["week", "end"], "weekend"),
]
fold_oc = _romance_prepass_fold(
    "oc", {"un", "una"},
    proclitics=frozenset({"l", "d", "un", "qu", "n", "s"}),
    phrases=_OC_PHRASES, h_clock=True,
    ord_suffixes=frozenset({"èr", "er", "n", "nd", "en", "ena", "a", "d"}))


# -- Asturian ---------------------------------------------------------------
_AST_PHRASES = [
    (["enantes", "de", "cristu"], "adc"), (["antes", "de", "cristu"], "adc"),
    (["dempués", "de", "cristu"], "ddc"), (["despues", "de", "cristu"], "ddc"),
    (["pasáu", "mañana"], "trasmañana"), (["pasao", "mañana"], "trasmañana"),
    (["que", "vien"], "quevien"),
    (["fin", "de", "selmana"], "findeselmana"),
]
fold_ast = _romance_prepass_fold(
    "ast", {"un", "una"},
    proclitics=frozenset({"l", "d", "un", "n"}),
    phrases=_AST_PHRASES,
    fem_ord={"primera": 1, "segunda": 2, "tercera": 3, "cuarta": 4,
             "quinta": 5, "sexta": 6, "séptima": 7, "septima": 7,
             "octava": 8, "novena": 9, "décima": 10, "decima": 10})
