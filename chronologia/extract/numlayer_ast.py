"""Asturian date words over the numtag number layer."""
from __future__ import annotations

from typing import Tuple

from chronologia.extract.model import Token
from chronologia.extract.numlayer import (collapse_phrase, elision_split,
                                          glue_abbreviations,
                                          with_marked_h_clock)
from chronologia.extract.numlayer_romance import (DateWords, count_words,
                                                  fold, locale_words)

_WORDS = DateWords(
    lang="ast",
    fractions=locale_words("ast", "clock_fraction_") | {"cuartos"},
    definite=frozenset({"el", "la", "los", "les", "l"}),
    quarter_articles=frozenset(),
    unit_nouns=frozenset({"segundos"}),
    unit_ordinals=frozenset({"segundu"}),
    counts=count_words("ast", locale_words("ast", "marker_since")))
_PROCLITICS = frozenset({"l", "d", "un", "n"})
_PHRASES = [
    (["enantes", "de", "cristu"], "adc"), (["antes", "de", "cristu"], "adc"),
    (["dempués", "de", "cristu"], "ddc"), (["despues", "de", "cristu"], "ddc"),
    # the areligious era wording: "cuartu mileniu enantes de la nuesa era"
    # (https://ast.wikipedia.org/wiki/Espada), "l'añu 28 de la nuesa era"
    # (https://ast.wikipedia.org/wiki/Xuan_Bautista).
    (["enantes", "de", "la", "nuesa", "era"], "adc"),
    (["de", "la", "nuesa", "era"], "ddc"),
    (["pasáu", "mañana"], "trasmañana"), (["pasao", "mañana"], "trasmañana"),
    (["que", "vien"], "quevien"),
    (["fin", "de", "selmana"], "findeselmana"),
]


def _fold_ast(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    tokens = elision_split(tokens, _PROCLITICS)
    for seq, surface in _PHRASES:
        tokens = collapse_phrase(tokens, seq, surface)
    return fold(glue_abbreviations(tokens), _WORDS)


# The hour-letter clock is written only where a clock marker announces one:
# "a les 21h30".  The markers are ast's own marker_at and marker_oclock
# surfaces.
fold_ast = with_marked_h_clock(_fold_ast, {"a", "les", "la", "hores", "hora"})
