"""Continental / North Germanic spelled-number folding (da/de/fy/nb/nl/nn/sv).

The Germanic languages build numbers as single compound words
("einundzwanzig" 21, "vijfentwintig" 25), so a spelled number is usually a
*single* token rather than English's multi-word run.  ovos-number-parser
resolves those compounds; the fold owns only which tokens are numbers.

Split out of ``numfold.py`` verbatim (behaviour-preserving refactor).  The
``_make_germanic_fold``/``_lazy_germanic_fold`` engine primitives stay in
``numfold`` because the Turkic folds and the base-locale folds (id/kab/ms/fa)
share them too -- imported here rather than duplicated.
"""
from __future__ import annotations

from typing import Callable, Tuple

from chronologia.extract.model import Token
from chronologia.extract.numfold import _lazy_germanic_fold
from chronologia.extract.numfold_engine import reindex
from chronologia.extract.numfold_ordinals import with_ordinals as _with_ordinals


# Dutch writes rel-day/weekday + day-part as ONE word ("morgenochtend",
# "woensdagmiddag"), unlike the space-separated spelling ("morgen ochtend")
# the grammar already reads.  Both halves are independently known surfaces
# (``named_day_*.voc``, ``weekday_*.voc``, ``daypart_*_nl.voc``); the fused
# spelling is just one unrecognised word to the tokenizer, so it strands.
# This pass splits the compound back into its two known tokens, mirroring
# :func:`chronologia.extract.numfold_slavic._split_ru_pol_unit`'s shape.
#
# "gister" is the compounding stem but is not itself a standalone word --
# only the citation form "gisteren" (``named_day_-1.voc``) is -- so the stem
# rewrites to the citation form; every other stem already IS its own
# standalone token and passes through unchanged.
_NL_DAYPART_STEMS = {
    "overmorgen": "overmorgen",
    "morgen": "morgen",
    "gister": "gisteren",
    "maandag": "maandag",
    "dinsdag": "dinsdag",
    "woensdag": "woensdag",
    "donderdag": "donderdag",
    "vrijdag": "vrijdag",
    "zaterdag": "zaterdag",
    "zondag": "zondag",
}
# Longest stem first so "overmorgen" is tried before "morgen" would otherwise
# never get a chance to (it never does here -- no stem is a prefix of another
# -- but the sort keeps the pass correct if the table ever grows one).
_NL_DAYPART_STEMS_BY_LEN = sorted(_NL_DAYPART_STEMS, key=len, reverse=True)
_NL_DAYPARTS = {"ochtend", "middag", "avond", "nacht"}


def _split_nl_relday_daypart(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Split fused ``<relday|weekday>+<daypart>`` compounds into their two
    known tokens.  Only fires when the WHOLE token is exactly a known stem
    immediately followed by a known day-part word -- never a partial match --
    so words that merely start with "morgen" ("morgenstond") or "gister"
    pass through untouched."""
    out, changed = [], False
    for t in tokens:
        if t.is_number:
            out.append(t)
            continue
        for stem in _NL_DAYPART_STEMS_BY_LEN:
            if not t.text.startswith(stem):
                continue
            tail = t.text[len(stem):]
            if tail not in _NL_DAYPARTS:
                continue
            canonical = _NL_DAYPART_STEMS[stem]
            cs, ce = t.char_start, t.char_end
            mid = (cs + len(stem)) if cs is not None else None
            out.append(Token(text=canonical, raw=t.raw[:len(stem)],
                             index=t.index, is_number=False,
                             char_start=cs, char_end=mid, cap=t.cap))
            out.append(Token(text=tail, raw=t.raw[len(stem):],
                             index=t.index, is_number=False,
                             char_start=mid, char_end=ce))
            changed = True
            break
        else:
            out.append(t)
    return reindex(out) if changed else tokens


def _compose(*passes: Callable) -> Callable:
    def run(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
        for p in passes:
            tokens = p(tokens)
        return tokens
    return run


#: Frisian inflected "coming-hour" forms (the genitive hour used after
#: healwei/kertier/oer/foar), mapped to their hour value.
_FY_HOURS = {"ienen": 1, "twaen": 2, "trijen": 3, "fjouweren": 4, "fiven": 5,
             "seizen": 6, "sânen": 7, "achten": 8, "njoggenen": 9,
             "tsienen": 10, "alven": 11, "tolven": 12}


# Per-language stop-sets: clock fractions + scale words that must not fold.
# "anderthalb" (== "eineinhalb", 1.5) is a genuine synonym ovos-number-parser
# does not pronounce or read back (extract_number_de('anderthalb') is None),
# so it is supplied as a fixed word->value surface, mirroring the Frisian
# inflected-hour word_map above. Duden: "anderthalb" = "eineinhalb".
#
# The umlaut-bearing number words are ASCII-transliterated the same way the
# function words are ("naechster" for "nächster"): ovos-number-parser
# reads only the umlaut spelling (extract_number_de('fuenf') is None where
# extract_number_de('fünf') is 5), so "in fuenf tagen" silently failed to
# fold. Add the ASCII twins actually attested in temporal offsets -- cardinal
# and the two ordinal forms (nominative/dative "-e"/"-en") ovos-number-parser
# reads with ordinals=True for the umlaut spelling.
_DE_UMLAUT_ASCII = {
    "fuenf": 5, "fuenfzehn": 15, "fuenfzig": 50, "fuenfte": 5, "fuenften": 5,
    "zwoelf": 12, "zwoelfte": 12, "zwoelften": 12,
}
fold_de = _lazy_germanic_fold(
    "ovos_number_parser.numbers_de", "extract_number_de",
    # "billion"/"billionen" is the long-scale 10^12 word (German Billion); it is
    # withheld here so it survives as the deep-time SCALE slot instead of being
    # read as a plain number by the value-probe.
    {"halb", "viertel", "dreiviertel", "million", "millionen",
     "milliarde", "milliarden", "billion", "billionen", "tausend"},
    word_map={"anderthalb": 1.5, **_DE_UMLAUT_ASCII})
fold_nl = _lazy_germanic_fold(
    "ovos_number_parser.numbers_nl", "extract_number_nl",
    # "biljoen" = 10^12 (Dutch long scale), withheld so the SCALE slot survives.
    {"half", "kwart", "miljoen", "miljard", "biljoen", "duizend"},
    ord_suffixes={"e", "de", "ste", "te"})
fold_nl = _compose(_split_nl_relday_daypart, fold_nl)
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


