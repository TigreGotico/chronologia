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

from chronologia.extract.numfold import _lazy_germanic_fold
from chronologia.extract.numfold_ordinals import with_ordinals as _with_ordinals



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


