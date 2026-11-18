"""German date words over the numtag number layer."""
from __future__ import annotations

from typing import Tuple

from chronologia.extract.model import Token
from chronologia.extract.numlayer_germanic import (DateWords, count_words, fold,
                                                   locale_words)

_WORDS = DateWords(
    lang="de",
    fractions=locale_words("de", "clock_fraction_"),
    counts=count_words("de"))


#: The ASCII spellings of the umlaut number words, as written without an
#: umlaut key ("in fuenf Tagen"), with their value and whether they are the
#: ordinal.  numtag reads only the umlaut spelling.
_ASCII_TWINS = {
    "fuenf": (5, False), "fuenfzehn": (15, False), "fuenfzig": (50, False),
    "fuenfte": (5, True), "fuenften": (5, True),
    "zwoelf": (12, False), "zwoelfte": (12, True), "zwoelften": (12, True),
}


def fold_de(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """The German number fold."""
    return fold(tokens, _WORDS, table=_ASCII_TWINS)
