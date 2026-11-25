"""Occitan date words over the numtag number layer."""
from __future__ import annotations

from typing import Tuple

from chronologia.extract.model import Token
from chronologia.extract.numlayer import (collapse_h_clock, collapse_phrase,
                                          drop_digit_suffix, elision_split,
                                          glue_abbreviations)
from chronologia.extract.numlayer_romance import (DateWords, count_words,
                                                  fold, locale_words)

_WORDS = DateWords(
    lang="oc",
    fractions=locale_words("oc", "clock_fraction_"),
    definite=frozenset({"lo", "la", "los", "las", "l"}),
    quarter_articles=frozenset({"un"}),
    unit_nouns=frozenset({"segondas"}),
    unit_ordinals=frozenset({"segonda"}),
    counts=count_words("oc", locale_words("oc", "marker_since")),
    articles_are_words=True)
_PROCLITICS = frozenset({"l", "d", "un", "qu", "n", "s"})
_PHRASES = [
    (["abans", "jèsus", "crist"], "acn"), (["abans", "jesus", "crist"], "acn"),
    (["abans", "nòstra", "èra"], "acn"), (["abans", "nostra", "era"], "acn"),
    (["aprèp", "jèsus", "crist"], "apc"), (["aprep", "jesus", "crist"], "apc"),
    (["de", "nòstra", "èra"], "apc"), (["de", "nostra", "era"], "apc"),
    (["abans", "ièr"], "abansièr"), (["abans", "ier"], "abansièr"),
    (["passat", "deman"], "passatdeman"), (["delà", "deman"], "passatdeman"),
    (["que", "ven"], "queven"),
    (["week", "end"], "weekend"),
    # the future-offset marker survives the elision split as one token, the
    # way "dins" does, so the offset grammar binds it ("d'aquí un moment",
    # oc.wiktionary s.v. "lèu").
    (["d", "aquí"], "d'aquí"), (["d", "aicí"], "d'aicí"),
]
#: The endings a digit ordinal takes: "1èr", "2nd", "3en", "3ena".
_ORD_SUFFIXES = frozenset({"èr", "er", "n", "nd", "en", "ena", "a", "d"})


def fold_oc(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """The Occitan number fold."""
    tokens = elision_split(tokens, _PROCLITICS)
    for seq, surface in _PHRASES:
        tokens = collapse_phrase(tokens, seq, surface)
    tokens = drop_digit_suffix(collapse_h_clock(tokens), _ORD_SUFFIXES)
    return fold(glue_abbreviations(tokens), _WORDS)
