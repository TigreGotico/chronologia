"""LangSpec -> compiled matcher table, cached per language.

Compilation is cheap here (the heavy lifting is the loader's vocab read),
but the contract from the design doc is that a language compiles **once**
and every later parse reuses the cached table.  The cache is keyed by
language code; :meth:`ConstructionCompiler.compile` returns the *same*
object on repeat calls (identity-stable, so callers may cache derived
state safely).

Construction precedence (era > scoped > calendar, per the doc) is baked
into the compiled ordering so the matcher's tie-break is a plain lookup.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

from chronologia.extract.model import LangSpec, SlotElement, SlotOrder

# lower rank == higher priority (era before scoped before calendar)
PRECEDENCE: Dict[str, int] = {
    "era_date": 0,
    "named_period": 0,
    "deep_time": 0,
    "era_bc": 1,
    "era_ad": 1,
    "era_bp": 1,
    # a scoped period carrying an explicit era marker ("the 3rd century bc",
    # "2nd century ad") is an era construction: it must outrank the plain
    # scoped_ordinal that would otherwise claim the bare "3rd century" and
    # strand the era marker in the remainder
    "scoped_bc": 1,
    "scoped_ad": 1,
    # a base-number decade carrying a BC marker ("the 300s bc") is an era
    # construction: it must outrank the bare decade/year reading and consume
    # the marker so it never strands in the remainder
    "decade_bc": 1,
    # regnal / roman constructions carry the most specific vocabulary, so
    # they win over the generic scoped/calendar families
    "regnal_date": 1,
    "roman_date": 1,
    # a holiday reference ("christmas", "next easter", "natal 2020") carries the
    # most specific vocabulary of all — a named holiday surface — so it wins the
    # tie against any generic calendar/year construction over the same tokens
    "holiday_ref": 1,
    # a bare "HHMM hours" would otherwise read as an "N-th hour" scoped
    # ordinal, so military time wins the same-span tie
    "military_time": 1,
    "scoped_ordinal": 2,
    "month_fuzzy": 2,
    "half_period": 2,
    "month_day_ref": 2,
    # a decade phrase ("the 1990s", "the nineties") carries the plural/word
    # marker that a bare year lacks, so it outranks year_ref for the same digits
    "decade_ref": 2,
    "season_ref": 3,
    "iso_date": 4,
    # reckoned_date (and its legacy alias nongregorian_date) -- the unified
    # calendar/era family; more specific vocabulary wins over calendar_date
    "hebrew_new_year": 1,
    "reckoned_date": 5,
    "nongregorian_date": 5,
    "calendar_date": 6,
    "subdivision_time": 6,
    # a bare year is the least specific calendar reference: any more specific
    # construction that also covers the digits (era_ad "44 ad", decade
    # "1990s") must win the tie, so year_ref sits just below calendar_date
    "year_ref": 6,
    "clock_time": 7,
    "weekday_ref": 8,
    "cycle_ref": 8,
    # "next week"/"this month"/"last year": the whole calendar period,
    # same tier as the weekday reference it generalises to coarser units
    "rel_period": 8,
    # "this/next/last weekend": the named two-day span, a specific
    # subdivision of the week that outranks a bare rel_period week
    "weekend_ref": 8,
    # compound named-day / weekday offsets carry the 'after'/'from' connector
    # that a bare relative offset lacks, so they win the longer span
    "named_day_after": 8,
    "named_day_before": 8,
    "weekday_offset": 8,
    "relative_offset": 9,
    "named_day": 10,
}

# constructions this phase declares but does not resolve
UNIMPLEMENTED = frozenset({"era_date"})


def parse_order(construction: str, raw: str) -> SlotOrder:
    """Parse an order string (``"MONTH DAY? YEAR?"``) into a SlotOrder."""
    elements = []
    for tok in raw.split():
        optional = tok.endswith("?")
        name = tok[:-1] if optional else tok
        elements.append(SlotElement(name=name, optional=optional,
                                    is_slot=name.isupper()))
    return SlotOrder(construction=construction,
                     elements=tuple(elements), raw=raw)


@dataclass(frozen=True)
class CompiledSpec:
    """A language's matcher table: precedence-sorted construction orders."""
    spec: LangSpec
    # (precedence, construction, order) sorted by precedence
    table: Tuple[Tuple[int, str, SlotOrder], ...]


class ConstructionCompiler:
    """Compiles and caches a :class:`CompiledSpec` per language."""

    def __init__(self):
        self._cache: Dict[str, CompiledSpec] = {}

    def compile(self, spec: LangSpec) -> CompiledSpec:
        if spec.lang in self._cache:
            return self._cache[spec.lang]
        entries = [(PRECEDENCE.get(name, 99), name, order)
                   for name, orders in spec.orders.items()
                   for order in orders]
        entries.sort(key=lambda e: e[0])
        compiled = CompiledSpec(spec=spec, table=tuple(entries))
        self._cache[spec.lang] = compiled
        return compiled
