"""Indonesian date words over the numtag number layer."""
from __future__ import annotations

from typing import Tuple

from chronologia.extract.model import Token
from chronologia.extract.numlayer_germanic import (DateWords, count_words, fold,
                                                   locale_words)

_WORDS = DateWords(
    lang="id",
    fractions=locale_words("id", "clock_fraction_"),
    counts=count_words("id"))


def fold_id(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """The Indonesian number fold."""
    return fold(tokens, _WORDS)
