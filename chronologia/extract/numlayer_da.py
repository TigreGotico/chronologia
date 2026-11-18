"""Danish date words over the numtag number layer."""
from __future__ import annotations

from typing import Tuple

from chronologia.extract.model import Token
from chronologia.extract.numlayer_germanic import (DateWords, count_words, fold,
                                                   locale_words)

_WORDS = DateWords(
    lang="da",
    fractions=locale_words("da", "clock_fraction_"),
    counts=count_words("da"))


def fold_da(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """The Danish number fold."""
    return fold(tokens, _WORDS)
