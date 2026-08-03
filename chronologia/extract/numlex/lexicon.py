"""The native ``surface -> [Entry, ...]`` number-word table."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import FrozenSet, List, Mapping, Optional, Union

from chronologia.extract.numlex.roles import Role

Number = Union[int, float]


@dataclass(frozen=True)
class Entry:
    """One reading of a surface.

    ``value`` is ``None`` for a :attr:`Role.PARTICLE`/:attr:`Role.CONNECTOR`
    surface that carries no number of its own ("dozen", "and").  ``tags``
    carries cross-cutting metadata the role does not: ``"ordinal"`` (an
    ordinal-family surface, gated by ``read_run(..., ordinals=...)``),
    structural equivalence for an ordinal whose own role is generic
    (``"unit"``/``"ten"``/``"scale"`` -- which additive class the ordinal
    stands in for), plus locale-specific flags (gender, case) future
    languages need and this reader ignores.
    """
    value: Optional[Number]
    role: Role
    tags: FrozenSet[str] = field(default_factory=frozenset)


class NumberLexicon:
    """A locale's number-word table plus its family composition flags.

    ``__contains__`` is the run-membership test a :class:`NumberGrammar`
    wires as ``is_number``: a surface is a number-word iff the lexicon has an
    entry for it (a digit token is handled separately by the engine, never
    consulting the lexicon).
    """

    def __init__(self, entries: Mapping[str, List[Entry]], *,
                 join_word: Optional[str] = None,
                 hundred_particle: Optional[str] = None,
                 short_scale: bool = True,
                 vigesimal: bool = False,
                 fused_thousand: bool = False):
        self._entries: Mapping[str, List[Entry]] = dict(entries)
        #: the additive internal connector ("and", Romance ``e``); ``None``
        #: when the family has none.
        self.join_word = join_word
        #: a bare hundred-particle surface that multiplies without its own
        #: HUNDRED entry (unused by English P0; future agglutinative/Slavic
        #: families).
        self.hundred_particle = hundred_particle
        #: short-scale (1e9 == billion, English/most) vs long-scale.
        self.short_scale = short_scale
        #: French-style base-20 composition (soixante-dix, quatre-vingts).
        self.vigesimal = vigesimal
        #: Italian-style ``mille``/``mila`` fused thousand forms.
        self.fused_thousand = fused_thousand

    def __contains__(self, word: str) -> bool:
        return word in self._entries

    def get(self, word: str) -> List[Entry]:
        return self._entries.get(word, [])

    def __repr__(self) -> str:  # pragma: no cover - debug aid only
        return f"NumberLexicon({len(self._entries)} surfaces)"
