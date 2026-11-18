"""North Germanic and Frisian spelled-number folding (fy/nb/nn).

The Germanic languages build numbers as single compound words, so a spelled
number is usually a *single* token rather than English's multi-word run.
ovos-number-parser resolves those compounds; the fold owns only which tokens
are numbers.

German, Dutch, Danish and Swedish read their numbers through numtag
(``numlayer_de``, ``numlayer_nl``, ``numlayer_da``, ``numlayer_sv``).  Norwegian
and Frisian stay here: numtag 0.15.3a1 does not read the Bokmål ordinal
"annen", the Nynorsk ordinal "fyrste" or the Frisian clock hours ("fiven").
The ``_make_germanic_fold``/``_lazy_germanic_fold`` engine primitives stay in
``numfold`` because the Turkic folds and the base-locale folds (id/kab/ms/fa)
share them too -- imported here rather than duplicated.
"""
from __future__ import annotations

from chronologia.extract.numfold import _lazy_germanic_fold


#: Frisian inflected "coming-hour" forms (the genitive hour used after
#: healwei/kertier/oer/foar), mapped to their hour value.
_FY_HOURS = {"ienen": 1, "twaen": 2, "trijen": 3, "fjouweren": 4, "fiven": 5,
             "seizen": 6, "sânen": 7, "achten": 8, "njoggenen": 9,
             "tsienen": 10, "alven": 11, "tolven": 12}


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


