"""Spanish date words over the numtag number layer."""
from __future__ import annotations

from typing import Tuple

from chronologia.extract.model import Token
from chronologia.extract.numfold_romance import _collapse_h_clock, _glue
from chronologia.extract.numlayer_romance import (DateWords, count_words,
                                                  fold, locale_words)

_WORDS = DateWords(
    lang="es",
    fractions=locale_words("es", "clock_fraction_") | {"cuartos"},
    definite=frozenset({"el", "la", "los", "las"}),
    quarter_articles=frozenset(),
    unit_nouns=frozenset({"segundos"}),
    unit_ordinals=frozenset({"segundo"}),
    counts=count_words("es", locale_words("es", "marker_since")))


def fold_es(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """The Spanish number fold."""
    return fold(_glue(_collapse_h_clock(tokens)), _WORDS)
