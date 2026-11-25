"""Mirandese date words over the numtag number layer."""
from __future__ import annotations

from typing import Tuple

from chronologia.extract.model import Token
from chronologia.extract.numlayer import (glue_abbreviations)
from chronologia.extract.numlayer_romance import (DateWords, count_words,
                                                  fold, locale_words)

_WORDS = DateWords(
    lang="mwl",
    fractions=locale_words("mwl", "clock_fraction_"),
    definite=frozenset({"l", "la", "ls", "las"}),
    quarter_articles=frozenset(),
    unit_nouns=frozenset({"segundos"}),
    unit_ordinals=frozenset({"segundo"}),
    counts=count_words("mwl", locale_words("mwl", "marker_since")))
#: The feminine ordinals that name a weekday: "segunda feira" is Monday,
#: "sesta feira" is Friday.
_WEEKDAY_ORDINALS = frozenset(
    w.split()[0] for w in locale_words("mwl", "weekday_") if " " in w)


def _weekdays(tokens: Tuple[Token, ...]):
    """Claim an ordinal that "feira" follows: the weekday name."""
    claimed = {i for i, t in enumerate(tokens)
               if t.mention is not None and t.text in _WEEKDAY_ORDINALS
               and i + 1 < len(tokens) and tokens[i + 1].text == "feira"}
    return claimed, set(), {}


def fold_mwl(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """The Mirandese number fold."""
    return fold(glue_abbreviations(tokens), _WORDS, extra=_weekdays)
