"""Aragonese date words over the numtag number layer."""
from __future__ import annotations

from typing import Tuple

from chronologia.extract.model import Token
from chronologia.extract.numlayer import (glue_abbreviations)
from chronologia.extract.numlayer_romance import (DateWords, count_words,
                                                  fold, locale_words)

_WORDS = DateWords(
    lang="an",
    fractions=locale_words("an", "clock_fraction_"),
    definite=frozenset({"o", "a", "os", "as", "lo", "la", "los", "las"}),
    quarter_articles=frozenset(),
    unit_nouns=frozenset({"segundos"}),
    unit_ordinals=frozenset({"segundo"}),
    counts=count_words("an", locale_words("an", "marker_since")))


def fold_an(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """The Aragonese number fold."""
    return fold(glue_abbreviations(tokens), _WORDS)
