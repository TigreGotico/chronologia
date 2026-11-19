"""West Frisian date words over the numtag number layer."""
from __future__ import annotations

from typing import Tuple

from chronologia.extract.model import Token
from chronologia.extract.numlayer_germanic import (DateWords, count_words, fold,
                                                   locale_words)

_WORDS = DateWords(
    lang="fy",
    fractions=locale_words("fy", "clock_fraction_"),
    counts=count_words("fy"))


#: After "healwei", "kertier", "oer" and "foar" the hour takes the genitive
#: form, which numtag does not read; https://github.com/TigreGotico/numtag/issues/143
_TABLE = {word: (hour, False) for hour, word in enumerate(
    ("ienen", "twaen", "trijen", "fjouweren", "fiven", "seizen", "sânen",
     "achten", "njoggenen", "tsienen", "alven", "tolven"), 1)}
#: The lone suffixes of a digit ordinal: "21e", "5de", "6te".
_ORDINAL_SUFFIXES = frozenset({"e", "de", "te"})


def fold_fy(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """The West Frisian number fold."""
    return fold(tokens, _WORDS, table=_TABLE,
                ordinal_suffixes=_ORDINAL_SUFFIXES)
