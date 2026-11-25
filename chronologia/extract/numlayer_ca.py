"""Catalan date words over the numtag number layer."""
from __future__ import annotations

from typing import Tuple

from chronologia.extract.model import Token
from chronologia.extract.numlayer import (collapse_h_clock, collapse_phrase,
                                          glue_abbreviations)
from chronologia.extract.numlayer_romance import (DateWords, count_words,
                                                  fold, locale_words)

_WORDS = DateWords(
    lang="ca",
    fractions=locale_words("ca", "clock_fraction_") | {"quarts"},
    definite=frozenset({"el", "la", "els", "les", "l"}),
    quarter_articles=frozenset(),
    unit_nouns=frozenset({"segons"}),
    unit_ordinals=frozenset({"segon"}),
    counts=count_words("ca", locale_words("ca", "marker_since")))


def fold_ca(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """The Catalan number fold.

    The elided "d'aquí" that the tokenizer splits into "d" and "aquí" is
    joined again, so the future-offset marker "d'aquí a" is one word.
    """
    tokens = collapse_phrase(tokens, ["d", "aquí"], "d'aquí")
    return fold(glue_abbreviations(collapse_h_clock(tokens)), _WORDS)
