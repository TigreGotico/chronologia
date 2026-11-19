"""North Germanic spelled-number folding (nb/nn).

The Germanic languages build numbers as single compound words, so a spelled
number is usually a *single* token rather than English's multi-word run.
ovos-number-parser resolves those compounds; the fold owns only which tokens
are numbers.

German, Dutch, Danish, Swedish and Frisian read their numbers through numtag
(``numlayer_de``, ``numlayer_nl``, ``numlayer_da``, ``numlayer_sv``,
``numlayer_fy``).  Norwegian stays here: numtag 0.15.3a1 does not read the
Bokmål ordinal "annen" or the Nynorsk ordinal "fyrste".
The ``_make_germanic_fold``/``_lazy_germanic_fold`` engine primitives stay in
``numfold`` because the Turkic folds and the base-locale folds (id/kab/ms/fa)
share them too -- imported here rather than duplicated.
"""
from __future__ import annotations

from chronologia.extract.numfold import _lazy_germanic_fold


fold_nb = _lazy_germanic_fold(
    "ovos_number_parser.numbers_nb", "extract_number_nb",
    {"halv", "halvdel", "halvdelen", "kvart", "million", "millioner",
     "milliard", "milliarder", "tusen"})
fold_nn = _lazy_germanic_fold(
    "ovos_number_parser.numbers_nn", "extract_number_nn",
    {"halv", "halvdel", "halvdelen", "kvart", "million", "millionar",
     "milliard", "milliardar", "tusen"})
