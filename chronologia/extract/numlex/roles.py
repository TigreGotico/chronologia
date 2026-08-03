"""The closed set of structural jobs a number-word surface can play.

A surface's :class:`Role` says what part of a composed number it names; the
same value can be spelled by a cardinal ("twenty") or an ordinal ("twentieth")
surface, so ordinal-ness is carried as the ``"ordinal"`` tag on the entry
rather than folded into the role -- the role still says *where* the word
sits (a TEN either way), the tag says *which surface family* it belongs to.
"""
from __future__ import annotations

from enum import Enum, auto


class Role(Enum):
    #: 1-9 ("one".."nine") -- a bare additive unit.
    UNIT = auto()
    #: 10-19 as a single atomic word ("eleven".."nineteen") -- English (and
    #: most Germanic languages) do not compose these from UNIT + TEN.
    TEEN = auto()
    #: 20, 30, .. 90 -- a multiple of ten that may take a trailing UNIT.
    TEN = auto()
    #: the "hundred" particle -- multiplies the group accumulated so far by
    #: 100 without starting a new additive group (unlike SCALE).
    HUNDRED = auto()
    #: 1000 and up ("thousand", "million", ...) -- multiplies the group so
    #: far and then closes it into the running total (a new additive group
    #: starts after a SCALE word).
    SCALE = auto()
    #: an ordinal-only surface with no cardinal counterpart in the table
    #: (used when a language has no distinct structural slot for it; English
    #: gives every ordinal a normal UNIT/TEN/SCALE tag instead and reserves
    #: this role for the rare cases that fit no other class).
    ORDINAL = auto()
    #: a fractional idiom ("half", "quarter") -- terminal, returns a float.
    FRACTION = auto()
    #: an internal connector ("and", waw) that continues a run without
    #: contributing a value of its own.
    CONNECTOR = auto()
    #: a bare multiplier morpheme with no standalone value of its own
    #: (Indonesian "puluh"/"ratus"/"belas") -- admits its host token to a run
    #: but is only meaningful composed with a neighbour.
    MULTIPLIER = auto()
    #: a closed-class word that is a *known* number-adjacent surface but
    #: carries no numeric value the reader can compose on its own ("dozen",
    #: "score" in English -- ``extract_number_en`` itself refuses them
    #: standalone).  Present so run-membership stays a pure lexicon lookup;
    #: the reader refuses to fold a run containing one.
    PARTICLE = auto()
