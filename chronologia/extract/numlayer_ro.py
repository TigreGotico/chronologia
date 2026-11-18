"""Romanian date words over the numtag number layer."""
from __future__ import annotations

from typing import Tuple

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import with_marked_h_clock
from chronologia.extract.numfold_romance import (_collapse_phrase, _glue,
                                                 _merge_digit_ordinal)
from chronologia.extract.numlayer_germanic import word_numbers
from chronologia.extract.numlayer_romance import (DateWords, count_words,
                                                  fold, locale_words)

_WORDS = DateWords(
    lang="ro",
    fractions=locale_words("ro", "clock_fraction_"),
    definite=frozenset(),
    quarter_articles=frozenset({"un"}),
    unit_nouns=frozenset(),
    unit_ordinals=frozenset(),
    counts=count_words("ro", locale_words("ro", "marker_since")))
_PHRASES = [
    (["înainte", "de", "hristos"], "ihr"), (["inainte", "de", "hristos"], "ihr"),
    (["după", "hristos"], "dhr"), (["dupa", "hristos"], "dhr"),
    (["î", "hr"], "ihr"), (["i", "hr"], "ihr"), (["d", "hr"], "dhr"),
    (["miezul", "nopții"], "miezulnoptii"), (["miezul", "noptii"], "miezulnoptii"),
    (["week", "end"], "weekend"),
]
#: The cardinals "două" (2) and "nouă" (9) written without diacritics, which
#: numtag does not read: "doua minute".  After "a" the same spelling is the
#: ordinal ("a doua zi"), which numtag reads (DOOM 3, "doilea" and "doi").
_NO_DIACRITICS = {"doua": (2, False), "noua": (9, False)}
#: The endings a digit ordinal takes: "al 2-lea", "a 3-a".
_ORD_SUFFIXES = frozenset({"lea", "a", "ea", "le"})


def _fold_ro(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    for seq, surface in _PHRASES:
        tokens = _collapse_phrase(tokens, seq, surface)
    tokens = word_numbers(_merge_digit_ordinal(tokens, _ORD_SUFFIXES),
                          _NO_DIACRITICS)
    return fold(_glue(tokens), _WORDS)


# The hour-letter clock is written only where a clock marker announces one:
# "la ora 21h30".  The markers are ro's own marker_at and marker_oclock
# surfaces.
fold_ro = with_marked_h_clock(_fold_ro, {"la", "ora", "ore"})
