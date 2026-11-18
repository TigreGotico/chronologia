"""Galician date words over the numtag number layer."""
from __future__ import annotations

from typing import Tuple

from chronologia.extract.model import Token
from chronologia.extract.numfold_romance import _collapse_h_clock, _glue
from chronologia.extract.numlayer_romance import (DateWords, count_words,
                                                  fold, locale_words)

_WORDS = DateWords(
    lang="gl",
    fractions=locale_words("gl", "clock_fraction_") | {"cuartos"},
    definite=frozenset({"o", "a", "os", "as"}),
    quarter_articles=frozenset(),
    unit_nouns=frozenset({"segundos"}),
    unit_ordinals=frozenset({"segundo"}),
    counts=count_words("gl", locale_words("gl", "marker_since")))


def fold_gl(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """The Galician number fold."""
    return fold(_glue(_collapse_h_clock(tokens)), _WORDS)
