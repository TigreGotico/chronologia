"""Persian date words over the numtag number layer."""
from __future__ import annotations

from dataclasses import replace
from typing import Tuple

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import reindex
from chronologia.extract.numlayer_germanic import (DateWords, count_words, fold,
                                                   locale_words)

_WORDS = DateWords(
    lang="fa",
    fractions=locale_words("fa", "clock_fraction_"),
    counts=count_words("fa"))


def _fold_fa(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    return fold(tokens, _WORDS)


#: the Persian length nouns, from ``locale/fa/unit_*.voc``.  A half word
#: directly before one of these closes a length ("نیم ساعت" half an hour,
#: "نیم قرن" half a century); anywhere else "نیم" keeps the clock FRACTION
#: slot it is withheld from the fold for ("سه و نیم" is half past three).
_FA_UNITS = frozenset({"ساعت", "دقیقه", "ثانیه", "روز", "هفته", "ماه",
                       "سال", "دهه", "قرن"})
_FA_HALF = "نیم"


def _fa_half_before_unit(fold):
    """Fold the Persian half word to 0.5 when a length noun closes it.

    Persian counts an offset with a number and a unit ("دو ساعت دیگه" in two
    hours).  The fold keeps the half word a word for the clock, so without
    this pass the half-length frame has no count.
    """
    def pre(tokens):
        out = []
        for i, t in enumerate(tokens):
            nxt = tokens[i + 1] if i + 1 < len(tokens) else None
            if (t.text == _FA_HALF and nxt is not None
                    and nxt.text in _FA_UNITS):
                out.append(replace(t, text="0.5", is_number=True, value=0.5))
                continue
            out.append(t)
        return fold(reindex(tuple(out)))

    return pre


fold_fa = _fa_half_before_unit(_fold_fa)
