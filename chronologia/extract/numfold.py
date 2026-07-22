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

from dataclasses import replace
from typing import Tuple

from ovos_number_parser.numbers_en import extract_number_en

from chronologia.extract.model import Token

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


def _reindex(tokens) -> Tuple[Token, ...]:
    return tuple(replace(t, index=i) for i, t in enumerate(tokens))


def fold_en(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    # -- pass 1: merge a digit followed by a lone ordinal suffix (5 th -> 5)
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

    # -- pass 2: fold maximal runs of spelled number-words to a digit token
    out = []
    i = 0
    n = len(merged)
    while i < n:
        if not _is_numword(merged[i]):
            out.append(merged[i])
            i += 1
            continue
        j = i
        run = []
        while j < n:
            if _is_numword(merged[j]):
                run.append(merged[j])
                j += 1
            elif (merged[j].text == "and" and run and j + 1 < n
                  and _is_numword(merged[j + 1])):
                run.append(merged[j])   # internal "and": one hundred and five
                j += 1
            else:
                break
        # a run that is a single already-digit token needs no folding
        spelled = [t for t in run if not t.is_number]
        if not spelled:
            out.extend(run)
            i = j
            continue
        text = " ".join(t.text for t in run if t.text != "and")
        value = extract_number_en(text, ordinals=True)
        if value is False or value is None:
            out.extend(run)
            i = j
            continue
        num = int(value) if float(value).is_integer() else float(value)
        raw = str(num)
        out.append(Token(text=str(num), raw=raw, index=0,
                         is_number=True, value=num,
                         char_start=run[0].char_start,
                         char_end=run[-1].char_end))
        i = j
    return _reindex(out)


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


def _make_romance_fold(lang_code, blacklist):
    from ovos_number_parser.util import RomanceNumberExtractor
    numbers_mod = import_module("ovos_number_parser.numbers_" + lang_code)
    vocab = next(v for v in vars(numbers_mod).values()
                 if type(v).__name__ == "NumberVocabulary")
    # the non-deprecated spoken-number reader; ``extract_number_<lang>`` is a
    # thin deprecated wrapper over exactly this.
    extractor = RomanceNumberExtractor(vocab)

    def extract_fn(text, ordinals=True):
        return extractor.extract_number(text, ordinals=ordinals)
    numwords = _romance_numwords(vocab, blacklist)
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

    def _is_numword(tok):
        return tok.is_number or tok.text in numwords

    def fold(tokens):
        tokens = _glue(tokens)
        out = []
        i = 0
        n = len(tokens)
        while i < n:
            if not _is_numword(tokens[i]):
                out.append(tokens[i])
                i += 1
                continue
            j = i
            run = []
            while j < n:
                if _is_numword(tokens[j]):
                    run.append(tokens[j])
                    j += 1
                elif (tokens[j].text in joins and run and j + 1 < n
                      and _is_numword(tokens[j + 1])):
                    run.append(tokens[j])
                    j += 1
                else:
                    break
            spelled = [t for t in run if not t.is_number]
            if not spelled:
                out.extend(run)
                i = j
                continue
            text = " ".join(t.text for t in run)
            value = extract_fn(text, ordinals=True)
            if (value is False or value is None) and len(run) == 1:
                value = ordinal_value.get(run[0].text, value)
            if value is False or value is None:
                out.extend(run)
                i = j
                continue
            num = int(value) if float(value).is_integer() else float(value)
            out.append(Token(text=str(num), raw=str(num), index=0,
                             is_number=True, value=num,
                             char_start=run[0].char_start,
                             char_end=run[-1].char_end))
            i = j
        return _reindex(out)

    return fold


# pt: feminine ordinals "segunda/quarta/quinta/sexta" are weekday names
fold_pt = _make_romance_fold("pt", {"segunda", "quarta", "quinta", "sexta",
                                    "terca", "terça"})
fold_es = _make_romance_fold("es", set())
fold_gl = _make_romance_fold("gl", set())
fold_ca = _make_romance_fold("ca", set())
# an: "martes" (Tuesday) must never be read as a number; the Romance factory
# folds via numbers_an's NumberVocabulary and the shared a.c./d.c. glue.
fold_an = _make_romance_fold("an", {"martes"})
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

    def fold(tokens):
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

        out = []
        i = 0
        n = len(tokens)
        while i < n:
            if not is_numword(tokens[i]):
                out.append(tokens[i])
                i += 1
                continue
            j = i
            run = []
            while j < n and is_numword(tokens[j]):
                run.append(tokens[j])
                j += 1
            spelled = [t for t in run if not t.is_number]
            if not spelled:
                out.extend(run)
                i = j
                continue
            text = " ".join(t.text for t in run)
            value = value_of(text)
            if value is None or value is False:
                out.extend(run)
                i = j
                continue
            num = int(value) if float(value).is_integer() else float(value)
            out.append(Token(text=str(num), raw=str(num), index=0,
                             is_number=True, value=num,
                             char_start=run[0].char_start,
                             char_end=run[-1].char_end))
            i = j
        return _reindex(out)

    return fold


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
    {"halb", "viertel", "dreiviertel", "million", "millionen",
     "milliarde", "milliarden", "tausend"})
fold_nl = _lazy_germanic_fold(
    "ovos_number_parser.numbers_nl", "extract_number_nl",
    {"half", "kwart", "miljoen", "miljard", "duizend"},
    ord_suffixes={"e", "de", "ste", "te"})
fold_sv = _lazy_germanic_fold(
    "ovos_number_parser.numbers_sv", "extract_number_sv",
    {"halv", "kvart", "miljon", "miljoner", "miljard", "miljarder", "tusen"})
fold_da = _lazy_germanic_fold(
    "ovos_number_parser.numbers_da", "extract_number_da",
    {"halv", "halvdel", "halvdelen", "kvart", "million", "millioner",
     "milliard", "milliarder", "tusind"})
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
fold_tr = _lazy_germanic_fold(
    "ovos_number_parser.numbers_tr", "extract_number_tr",
    {"yarım", "çeyrek", "bin", "milyon", "milyar"})
fold_az = _lazy_germanic_fold(
    "ovos_number_parser.numbers_az", "extract_number_az",
    {"yarım", "min", "milyon", "milyard"})
fold_id = _lazy_germanic_fold(
    "ovos_number_parser.numbers_id", "extract_number_id",
    {"setengah", "seperempat", "suku", "ribu", "juta", "miliar", "milyar"})
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
            out.append(Token(text=head, raw=head, index=0))
            out.append(Token(text=tail, raw=tail, index=0))
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
                          fem_ord=None):
    base = _make_romance_fold(lang_code, blacklist)
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
fold_fr = _romance_prepass_fold(
    "fr", {"un", "une"},
    proclitics=frozenset({"d", "l", "j", "n", "s", "c", "m", "t", "qu"}),
    phrases=_FR_PHRASES, h_clock=True,
    ord_suffixes=frozenset({"er", "ere", "ère", "e", "eme", "ème",
                            "nd", "nde", "d", "re", "es", "emes", "èmes"}))


# -- Italian ----------------------------------------------------------------
_IT_PHRASES = [
    (["avanti", "cristo"], "ac"), (["dopo", "cristo"], "dc"),
    (["avanti", "l", "era", "volgare"], "ac"), (["era", "volgare"], "dc"),
    (["altro", "ieri"], "altroieri"), (["avanti", "ieri"], "avantieri"),
    (["dopo", "domani"], "dopodomani"),
    (["fine", "settimana"], "finesettimana"),
]
fold_it = _romance_prepass_fold(
    "it", {"un", "uno", "una", "milioni", "miliardi", "mila"},
    proclitics=frozenset({"l", "un", "d", "dell", "all", "nell", "dall",
                          "sull", "quest", "quell", "c"}),
    phrases=_IT_PHRASES)


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
