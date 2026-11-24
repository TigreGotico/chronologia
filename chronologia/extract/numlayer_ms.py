"""Malay date words over the numtag number layer."""
from __future__ import annotations

from typing import Tuple

from chronologia.extract.model import Token
from chronologia.extract.numlayer_germanic import (DateWords, count_words, fold,
                                                   locale_words)

_WORDS = DateWords(
    lang="ms",
    fractions=locale_words("ms", "clock_fraction_"),
    counts=count_words("ms"))


def fold_ms(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """The Malay number fold."""
    return fold(tokens, _WORDS)
