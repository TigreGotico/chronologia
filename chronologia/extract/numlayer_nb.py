"""Bokmål date words over the numtag number layer."""
from __future__ import annotations

from typing import Tuple

from chronologia.extract.model import Token
from chronologia.extract.numlayer_germanic import (DateWords, count_words, fold,
                                                   locale_words)

_WORDS = DateWords(
    lang="nb",
    fractions=locale_words("nb", "clock_fraction_"),
    counts=count_words("nb"))


#: numtag reads no number in "annen" (numtag#140) or "annet" (numtag#246)
_TABLE = {"annen": (2, True), "annet": (2, True)}


def fold_nb(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """The Bokmål number fold."""
    return fold(tokens, _WORDS, table=_TABLE)
