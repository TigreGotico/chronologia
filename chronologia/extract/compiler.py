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
    # AUC / Olympiad / archon: specific era vocabulary, wins its span like the
    # other era families
    "era_auc": 1,
    # calendar-backed era-year surfaces: resolve through the era registry's
    # epoch (Saka/Byzantine Anno Mundi/Holocene), so they win the era tie and
    # consume the era name rather than stranding it for a bare year_ref
    "era_saka": 1,
    "era_byzantine": 1,
    "era_holocene": 1,
    "era_buddhist": 1,
    # "eve of <Roman anchor>" must outrank the bare roman_date it wraps
    "roman_eve": 1,
    "olympiad_ref": 1,
    "archon_ref": 1,
    "roman_classical": 1,
    # a holiday reference ("christmas", "next easter", "natal 2020") carries a
    # named holiday surface, so on a LONGER span it wins ("christmas 2020" beats
    # a bare year_ref on "2020"). But some holiday surfaces are *also* calendar
    # month names (Ramadan is both the holiday and the Hijri month) or overlap a
    # calendar construction ("ramadan 1446" is a Hijri month+year, not a holiday
    # in year 1446). On an EQUAL-length span the calendar family must win, so
    # holiday_ref sits just below the reckoned/nongregorian and calendar_date
    # tiers: a same-span calendar reading is preferred, a longer holiday span is
    # not (the holiday surface has no calendar competitor of equal length there).
    "holiday_ref": 6,
    # a bare "HHMM hours" would otherwise read as an "N-th hour" scoped
    # ordinal, so military time wins the same-span tie
    "military_time": 1,
    "scoped_ordinal": 2,
    "month_fuzzy": 2,
    "half_period": 2,
    "month_day_ref": 2,
    # a quarter ("Q3 2026") and an ISO week ("week 32") carry their own marker
    # vocabulary, so they win the same-span tie over a bare year_ref on the digits
    "quarter_ref": 2,
    "iso_week_ref": 2,
    # early/mid/late over a calendar UNIT ("early next week") must outrank the
    # bare rel_period it wraps, which it does on span length; tier keeps it with
    # the other fuzzy families
    "fuzzy_period": 2,
    # a decade phrase ("the 1990s", "the nineties") carries the plural/word
    # marker that a bare year lacks, so it outranks year_ref for the same digits
    "decade_ref": 2,
    # a solar event ("the summer solstice", "march equinox 2000") carries the
    # event word on top of the season/month qualifier, so on its longer span it
    # wins over the bare season_ref that would otherwise claim just the season
    # word and strand "solstice"/"equinox" in the remainder
    "solar_event": 2,
    "season_ref": 3,
    "iso_date": 4,
    # the ISO-8601 week designator literal ("2024-W10", "2024-W10-1"): a full
    # literal like the ISO date it sits beside, and it must outrank any bare
    # year_ref reading of its leading digits
    "iso_week_date": 4,
    # a numeric slash/dash date ("12/11/2024") is a full literal date, same
    # tier as the ISO literal it sits beside
    "numeric_date": 4,
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
    # "<hour> this <daypart>": a clock reading whose daypart word supplies the
    # am/pm meridiem, carrying the extra "this <daypart>" vocabulary over a bare
    # clock_time, so it wins the longer span ("3 this afternoon" over "3").
    "clock_this_daypart": 7,
    "weekday_ref": 8,
    "cycle_ref": 8,
    # "next week"/"this month"/"last year": the whole calendar period,
    # same tier as the weekday reference it generalises to coarser units
    "rel_period": 8,
    # "this morning"/"tonight"/"yesterday morning": a time-of-day band on a
    # deictically-selected day.  Same tier as the weekday/period references it
    # sits beside; a bare daypart composes onto a same-text date construction
    # (narrowing it to the band) exactly as a lone clock_time does.
    "daypart_ref": 8,
    # "this/next/last weekend": the named two-day span, a specific
    # subdivision of the week that outranks a bare rel_period week
    "weekend_ref": 8,
    # compound named-day / weekday offsets carry the 'after'/'from' connector
    # that a bare relative offset lacks, so they win the longer span
    "named_day_after": 8,
    "named_day_before": 8,
    "weekday_offset": 8,
    # "a week today"/"a month from tomorrow"/"this time last year": composed
    # offsets onto a named day or the anchor instant.  They carry the extra
    # unit/"from"/"this time" vocabulary a bare named_day or relative_offset
    # lacks, so on the longer span they win the same-anchor tie.
    "named_day_span_idiom": 8,
    "named_day_offset_from": 8,
    "sametime_shift": 8,
    # backward relative-day idioms -- "the <X> before last" / "the <X> after
    # next" / "a <weekday> ago" / "<N-unit> ago <weekday>".  Each carries the
    # trailing "before last"/"after next"/"ago" vocabulary a bare weekday_ref or
    # relative_offset lacks, so on the longer span it wins the same-anchor tie.
    "before_last": 8,
    "after_next": 8,
    "weekday_ago": 8,
    "unit_ago_weekday": 8,
    # "the eve of christmas": the day before a named holiday.  Carries the
    # "eve of" vocabulary on top of the holiday surface, so it outranks the
    # bare holiday_ref that would otherwise claim just the holiday and strand
    # "eve of" in the remainder.
    "holiday_eve": 5,
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
