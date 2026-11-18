"""Dutch date words over the numtag number layer."""
from __future__ import annotations

from typing import Tuple

from chronologia.extract.model import Token
from chronologia.extract.numfold_engine import reindex
from chronologia.extract.numlayer_germanic import (DateWords, count_words, fold,
                                                   locale_words)

# Dutch writes rel-day/weekday + day-part as ONE word ("morgenochtend",
# "woensdagmiddag"), unlike the space-separated spelling ("morgen ochtend")
# the grammar already reads.  Both halves are independently known surfaces
# (``named_day_*.voc``, ``weekday_*.voc``, ``daypart_*_nl.voc``); the fused
# spelling is just one unrecognised word to the tokenizer, so it strands.
# This pass splits the compound back into its two known tokens, mirroring
# :func:`chronologia.extract.numfold_slavic._split_ru_pol_unit`'s shape.
#
# "gister" is the compounding stem but is not itself a standalone word --
# only the citation form "gisteren" (``named_day_-1.voc``) is -- so the stem
# rewrites to the citation form; every other stem already IS its own
# standalone token and passes through unchanged.
_NL_DAYPART_STEMS = {
    "overmorgen": "overmorgen",
    "morgen": "morgen",
    "gister": "gisteren",
    "maandag": "maandag",
    "dinsdag": "dinsdag",
    "woensdag": "woensdag",
    "donderdag": "donderdag",
    "vrijdag": "vrijdag",
    "zaterdag": "zaterdag",
    "zondag": "zondag",
}
# Longest stem first so "overmorgen" is tried before "morgen" would otherwise
# never get a chance to (it never does here -- no stem is a prefix of another
# -- but the sort keeps the pass correct if the table ever grows one).
_NL_DAYPART_STEMS_BY_LEN = sorted(_NL_DAYPART_STEMS, key=len, reverse=True)
_NL_DAYPARTS = {"ochtend", "middag", "avond", "nacht"}


def split_nl_relday_daypart(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Split fused ``<relday|weekday>+<daypart>`` compounds into their two
    known tokens.  Only fires when the WHOLE token is exactly a known stem
    immediately followed by a known day-part word -- never a partial match --
    so words that merely start with "morgen" ("morgenstond") or "gister"
    pass through untouched."""
    out, changed = [], False
    for t in tokens:
        if t.is_number:
            out.append(t)
            continue
        for stem in _NL_DAYPART_STEMS_BY_LEN:
            if not t.text.startswith(stem):
                continue
            tail = t.text[len(stem):]
            if tail not in _NL_DAYPARTS:
                continue
            canonical = _NL_DAYPART_STEMS[stem]
            cs, ce = t.char_start, t.char_end
            mid = (cs + len(stem)) if cs is not None else None
            out.append(Token(text=canonical, raw=t.raw[:len(stem)],
                             index=t.index, is_number=False,
                             char_start=cs, char_end=mid, cap=t.cap))
            out.append(Token(text=tail, raw=t.raw[len(stem):],
                             index=t.index, is_number=False,
                             char_start=mid, char_end=ce))
            changed = True
            break
        else:
            out.append(t)
    return reindex(out) if changed else tokens


#: The hour words Dutch writes after "half" as one word: Team Taaladvies,
#: "Kloklezen, kloktijden lezen", writes 6.30 uur as "halfzeven" and 6.40 uur
#: as "tien over halfzeven".
_NL_HALF_HOURS = {
    "een": 1, "één": 1, "twee": 2, "drie": 3, "vier": 4, "vijf": 5, "zes": 6,
    "zeven": 7, "acht": 8, "negen": 9, "tien": 10, "elf": 11, "twaalf": 12}


def split_nl_half_hour(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """Split "halfzeven" into "half" and the hour 7, the spelling the clock
    grammar reads.  Only "half" followed by a whole hour word splits, so
    "halfjaar" or "halfvol" pass through.  numtag reads the input text, where
    the hour word is inside a longer word, so the hour token carries its
    value here."""
    out, changed = [], False
    for t in tokens:
        tail = t.text[4:]
        if t.is_number or not t.text.startswith("half") \
                or tail not in _NL_HALF_HOURS:
            out.append(t)
            continue
        cs, ce = t.char_start, t.char_end
        mid = cs + 4 if cs is not None else None
        out.append(Token(text="half", raw=t.raw[:4], index=t.index,
                         char_start=cs, char_end=mid, cap=t.cap))
        hour = _NL_HALF_HOURS[tail]
        out.append(Token(text=str(hour), raw=t.raw[4:], index=t.index,
                         is_number=True, value=float(hour),
                         char_start=mid, char_end=ce))
        changed = True
    return reindex(out) if changed else tokens


def split_nl_compounds(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """The Dutch one-word compounds the grammar reads as two words."""
    return split_nl_half_hour(split_nl_relday_daypart(tokens))


_WORDS = DateWords(
    lang="nl",
    fractions=locale_words("nl", "clock_fraction_"),
    counts=count_words("nl"))


#: "anderhalve" is the form of "anderhalf" before a de-word ("anderhalve
#: week"); numtag reads only "anderhalf".  Van Dale: both are 1,5.
_TABLE = {"anderhalve": (1.5, False)}
#: The lone suffixes of a digit ordinal: "21e", "5de", "1ste".
_ORDINAL_SUFFIXES = frozenset({"e", "de", "ste", "te"})


#: "een paar" is "a couple": two.  Van Dale, "paar": "een paar: twee, enkele".
_PHRASES = {("een", "paar"): 2}


def fold_nl(tokens: Tuple[Token, ...]) -> Tuple[Token, ...]:
    """The Dutch number fold."""
    return fold(tokens, _WORDS, table=_TABLE,
                ordinal_suffixes=_ORDINAL_SUFFIXES, phrases=_PHRASES)
