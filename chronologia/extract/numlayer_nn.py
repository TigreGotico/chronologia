"""Nynorsk date words over the numtag number layer."""
from __future__ import annotations

from typing import Tuple

from chronologia.extract.model import Token
from chronologia.extract.numlayer_germanic import (DateWords, count_words, fold,
                                                   locale_words)

_WORDS = DateWords(
    lang="nn",
    fractions=locale_words("nn", "clock_fraction_"),
    counts=count_words("nn"))


#: numtag reads no number in "fyrste" and its compounds (numtag#141)
_TABLE = {"fyrste": (1, True), "tjuefyrste": (21, True),
          "trettifyrste": (31, True)}


def fold_nn(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """The Nynorsk number fold."""
    return fold(tokens, _WORDS, table=_TABLE)
