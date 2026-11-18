"""Swedish date words over the numtag number layer."""
from __future__ import annotations

from typing import Tuple

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import reindex, with_marked_h_clock
from chronologia.extract.numlayer_germanic import (DateWords, count_words, fold,
                                                   locale_words)

# Swedish counts a fraction of an hour as a length with the article and the
# bare fraction word, or with the compound noun: "om en halv timme" / "om en
# halvtimme" (in half an hour), "om en kvart" (in a quarter of an hour).
# Wiktionary: halvtimme "half an hour, a half-hour"; kvart "a quarter of an
# hour, 15 minutes".  "halv" and "kvart" are kept out of the cardinal fold
# because the clock reads them as FRACTION ("halv tre" = 02:30, "kvart över
# tre" = 03:15), so the length reading is rewritten here instead, and only
# where a unit noun follows or the phrase is the bare "en kvart" with no clock
# direction after it: the count 1 and the fraction word become one 0.5 / 0.25
# count, and the compound splits into its two words first.
_SV_HALF_COMPOUNDS = {"halvtimme": "timme", "halvtimmen": "timmen"}
_SV_CLOCK_DIRS = frozenset({"över", "i"})


def split_sv_half_compound(tokens):
    out = []
    for t in tokens:
        if not t.is_number and t.text in _SV_HALF_COMPOUNDS:
            cs, ce = t.char_start, t.char_end
            mid = cs + 4 if cs is not None else None
            out.append(Token(text="halv", raw=t.raw[:4], index=t.index,
                             char_start=cs, char_end=mid))
            out.append(Token(text=_SV_HALF_COMPOUNDS[t.text], raw=t.raw[4:],
                             index=t.index, char_start=mid, char_end=ce))
        else:
            out.append(t)
    return reindex(tuple(out))


def _sv_fraction_length(tokens):
    out = []
    i = 0
    n = len(tokens)
    while i < n:
        t = tokens[i]
        nxt = tokens[i + 1] if i + 1 < n else None
        if (t.is_number and t.value == 1 and nxt is not None
                and not nxt.is_number and nxt.text in ("halv", "kvart")):
            after = tokens[i + 2] if i + 2 < n else None
            if nxt.text == "halv" and after is not None and not after.is_number:
                out.append(Token(text="0.5", raw=t.raw + " " + nxt.raw,
                                 index=t.index, is_number=True, value=0.5,
                                 char_start=t.char_start, char_end=nxt.char_end))
                i += 2
                continue
            if nxt.text == "kvart" and (after is None or (
                    not after.is_number and after.text not in _SV_CLOCK_DIRS)):
                out.append(Token(text="0.25", raw=t.raw + " " + nxt.raw,
                                 index=t.index, is_number=True, value=0.25,
                                 char_start=t.char_start, char_end=nxt.char_start))
                out.append(Token(text="timme", raw=nxt.raw, index=t.index,
                                 char_start=nxt.char_start, char_end=nxt.char_end))
                i += 2
                continue
        out.append(t)
        i += 1
    return reindex(tuple(out))

_WORDS = DateWords(
    lang="sv",
    fractions=locale_words("sv", "clock_fraction_"),
    counts=count_words("sv"))


def _fold_sv(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    return _sv_fraction_length(fold(tokens, _WORDS))


# Swedish writes "21h30" only behind the clock marker ("kl 21h30", "klockan
# 21h30"); a bare "21h30" is a duration.  The marker set is sv's own
# marker_at surfaces.  The h-clock reads a digit pair that the fraction
# rewrite never sees, and the marker has to be found in the original tokens.
fold_sv = with_marked_h_clock(_fold_sv, {"klockan", "kl"})
