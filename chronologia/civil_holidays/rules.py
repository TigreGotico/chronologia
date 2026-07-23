"""Per-kind frozen rule classes — a tagged union of holiday date kinds.

Each *kind* of rule is its own frozen dataclass exposing one method,
``observances(year) -> tuple[(AstroDate, basis), ...]``. Per-kind classes are
preferred over a single class with a ``kind`` tag and a bag of optional fields:
every field a kind carries is mandatory *for that kind* and self-validating, so
an ill-formed rule cannot be constructed, and dispatch is ordinary Python
polymorphism rather than a ``match`` on a string tag.

This module also carries the documented :data:`CATEGORIES` schema and
:func:`parse_name_cell` (the ``.tab`` name-cell splitter), the lowest-dependency
facts every other part of the engine builds on.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import timedelta
from typing import (Dict, FrozenSet, Optional, Protocol, Tuple,
                    runtime_checkable)

from chronologia.astrodate import BASIS_EXACT, BASIS_TABULATED, AstroDate
from chronologia.calendars import CALENDARS, CalendarRangeError, gregorian_to_jdn
from chronologia.computus import easter
from chronologia.equinoxes import equinox, solar_term
from chronologia.recurrence import nth_weekday_of_month, occurrences

#: The documented category schema (see the package docstring).
#:
#: The base five (``public``/``regional``/``municipal``/``religious``/
#: ``school``) are this project's own taxonomy. The remainder mirror
#: vacanza/holidays 0.101's per-country ``supported_categories`` labels
#: verbatim (lower-cased, as vacanza already emits them) for the countries
#: whose non-default categories this project has adopted parity rows for
#: (see ``test/test_holiday_categories.py``) — ``workday`` (bridge/working-day
#: markers) is deliberately excluded as out of scope, same as bridge days.
CATEGORIES: FrozenSet[str] = frozenset({
    "public", "regional", "municipal", "religious", "school",
    # vacanza-parity labels (country-specific denominational/administrative
    # subsets; see per-country .tab headers for citations)
    "armenian", "bank", "government", "half_day", "optional",
    "albanian", "bosnian", "roma", "serbian", "turkish", "vlach",
    "armed_forces", "hebrew", "islamic", "catholic", "orthodox", "unofficial",
    "christian", "sabian", "yazidi", "hindu", "de_facto",
})

_EASTER_METHODS = ("gregorian", "julian_gregorian_date")

#: A ``lang:`` tag at the start of a ``;;``-separated name alternate. The tag is
#: a short BCP-47-ish code (``en``, ``zh``, ``pt-BR``, ``ca``); anything else —
#: including a name that merely contains a colon — is treated as an untagged
#: name, so plain single-name rows stay backward-compatible.
_LANG_TAG = re.compile(r"^([A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})?):(.+)$", re.S)


def parse_name_cell(cell: str) -> Tuple[str, Dict[str, str]]:
    """Split a ``.tab`` ``name`` cell into ``(primary_name, names_by_lang)``.

    The cell is one or more official-language names separated by ``;;``. Each
    alternate is either ``lang:text`` (a BCP-47-ish tag) or a plain ``text``.
    The **primary** name is the first alternate's text; ``names_by_lang`` maps
    every *tagged* alternate's language to its text. A plain single-name cell
    (the common, backward-compatible case) yields that name and an empty map::

        parse_name_cell("New Year's Day")        -> ("New Year's Day", {})
        parse_name_cell("zh:春节 ;; en:Spring Festival")
            -> ("春节", {"zh": "春节", "en": "Spring Festival"})
    """
    primary = None
    names: Dict[str, str] = {}
    for part in cell.split(";;"):
        part = part.strip()
        if not part:
            continue
        m = _LANG_TAG.match(part)
        if m:
            lang, text = m.group(1), m.group(2).strip()
            names[lang] = text
            text_val = text
        else:
            text_val = part
        if primary is None:
            primary = text_val
    if primary is None:
        raise ValueError("empty name cell")
    return primary, names


# --------------------------------------------------------------------------
# Rule kinds — each exposes ``observances(year) -> ((AstroDate, basis), ...)``.
# --------------------------------------------------------------------------
@runtime_checkable
class RuleKind(Protocol):
    """The structural contract every holiday rule kind satisfies."""

    def observances(self, year: int) -> Tuple[Tuple[AstroDate, str], ...]:
        ...


@dataclass(frozen=True)
class FixedRule:
    """A constant Gregorian ``(month, day)`` — the same date every year."""

    month: int
    day: int

    def __post_init__(self) -> None:
        if not 1 <= self.month <= 12:
            raise ValueError(f"month out of range: {self.month}")
        if not 1 <= self.day <= 31:
            raise ValueError(f"day out of range: {self.day}")

    def observances(self, year: int) -> Tuple[Tuple[AstroDate, str], ...]:
        return ((AstroDate(year, self.month, self.day), BASIS_EXACT),)


@dataclass(frozen=True)
class NthWeekdayRule:
    """The ``n``-th (``-1`` = last) ``weekday`` of ``month``, plus ``post_offset``.

    ``weekday`` is Monday==0 .. Sunday==6 (the :class:`AstroDate` convention).
    ``post_offset`` shifts the result by a whole number of days, which expresses
    "the Monday *after* the 2nd Sunday of July" as ``n=2, weekday=6,
    post_offset=1``. Evaluated through the RRULE engine so the arithmetic is the
    same one the recurrence layer already trusts.
    """

    month: int
    n: int
    weekday: int
    post_offset: int = 0

    def __post_init__(self) -> None:
        if not 1 <= self.month <= 12:
            raise ValueError(f"month out of range: {self.month}")
        if self.n == 0:
            raise ValueError("n must be a non-zero ordinal (-1 = last)")
        if not 0 <= self.weekday <= 6:
            raise ValueError(f"weekday out of range: {self.weekday}")

    def observances(self, year: int) -> Tuple[Tuple[AstroDate, str], ...]:
        rec = nth_weekday_of_month(self.n, self.weekday, month=self.month)
        got = list(occurrences(rec, AstroDate(year, 1, 1),
                               until=AstroDate(year, 12, 31)))
        if not got:
            return ()
        base = got[0].start
        return ((base + timedelta(days=self.post_offset), BASIS_EXACT),)


@dataclass(frozen=True)
class NearestWeekdayRule:
    """The nearest ``weekday`` on or before/after a fixed ``(month, day)``.

    The minimal kind for "the Monday preceding/following a fixed date" rules
    that no ``n``-th-weekday count can express, because the ordinal drifts year
    to year. ``direction`` is ``-1`` for *on or before* (the anchor's own
    weekday counts) and ``+1`` for *on or after* — the two are exact mirrors, so
    they share one kind with a signed direction rather than two near-identical
    classes.

    * ``direction == -1`` (on or before): Canada's Victoria Day is "the Monday
      preceding 25 May" — the Monday on or before 24 May,
      ``NearestWeekdayRule(5, 24, 0, -1)``. Quebec's National Patriots' Day
      shares that anchor; Saxony's Buß- und Bettag is the Wednesday on or before
      22 November, ``NearestWeekdayRule(11, 22, 2, -1)``.
    * ``direction == +1`` (on or after): Colombia's Ley 51 de 1983 ("Ley
      Emiliani") relocates a fixed list of holidays to the *next Monday on or
      after* their nominal date (Reyes Magos, San José, …) —
      ``NearestWeekdayRule(1, 6, 0, +1)`` and kin. When the nominal date is
      already that weekday it is unmoved (Reyes 2025 stays 6 Jan).

    ``weekday`` is Monday==0 .. Sunday==6 (the :class:`AstroDate` convention).
    Basis ``exact``.
    """

    month: int
    day: int
    weekday: int
    direction: int = -1

    def __post_init__(self) -> None:
        if not 1 <= self.month <= 12:
            raise ValueError(f"month out of range: {self.month}")
        if not 1 <= self.day <= 31:
            raise ValueError(f"day out of range: {self.day}")
        if not 0 <= self.weekday <= 6:
            raise ValueError(f"weekday out of range: {self.weekday}")
        if self.direction not in (-1, 1):
            raise ValueError(
                f"direction must be -1 (on/before) or +1 (on/after), "
                f"got {self.direction}")

    def observances(self, year: int) -> Tuple[Tuple[AstroDate, str], ...]:
        anchor = AstroDate(year, self.month, self.day)
        if self.direction < 0:
            delta = (anchor.weekday() - self.weekday) % 7
        else:
            delta = (self.weekday - anchor.weekday()) % 7
        return ((anchor + timedelta(days=self.direction * delta), BASIS_EXACT),)


@dataclass(frozen=True)
class EasterOffsetRule:
    """A whole-day ``offset_days`` from Easter Sunday (see :mod:`chronologia.computus`).

    ``method`` is ``"gregorian"`` (Western) or ``"julian_gregorian_date"``
    (Orthodox Easter rendered on the civil calendar). Both yield a real Sunday
    instant, so the offset lands on an actual civil date.
    """

    offset_days: int
    method: str = "gregorian"

    def __post_init__(self) -> None:
        if self.method not in _EASTER_METHODS:
            raise ValueError(
                f"unknown Easter method {self.method!r}; expected one of "
                f"{list(_EASTER_METHODS)}")

    def observances(self, year: int) -> Tuple[Tuple[AstroDate, str], ...]:
        sunday = easter(year, self.method)
        return ((sunday + timedelta(days=self.offset_days), BASIS_EXACT),)


@dataclass(frozen=True)
class CalendarDateRule:
    """A fixed ``(month, day)`` in another registered calendar (``calendar_key``).

    Resolves through :data:`~chronologia.calendars.CALENDARS`, so it inherits
    that calendar's range limits. A tabulated calendar (``umm_al_qura``) yields
    ``tabulated`` basis inside its published range; a year whose occurrence
    would fall outside the table is **omitted** rather than fabricated — the
    honest failure mode. Because the other calendar's year is shorter or longer
    than the Gregorian one, a single Gregorian ``year`` may hold zero, one, or
    two occurrences.
    """

    calendar_key: str
    month: int
    day: int

    def __post_init__(self) -> None:
        if self.calendar_key not in CALENDARS:
            raise ValueError(f"unknown calendar {self.calendar_key!r}")

    def _basis(self) -> str:
        cal = CALENDARS[self.calendar_key]
        return getattr(cal, "basis", BASIS_TABULATED)

    def observances(self, year: int) -> Tuple[Tuple[AstroDate, str], ...]:
        cal = CALENDARS[self.calendar_key]
        lo = gregorian_to_jdn(year, 1, 1)
        hi = gregorian_to_jdn(year, 12, 31)
        # Derive the *candidate* calendar years by asking the calendar itself
        # which of its years straddle this Gregorian year's two boundaries, then
        # sweep one year either side. This is calendar-agnostic — it works for a
        # lunar year numbered off the Hijri epoch (``umm_al_qura``), a lunisolar
        # year numbered off the Gregorian one it opens in (``chinese``) and a
        # ~3760-offset year (``hebrew``) alike — where a fixed arithmetic guess
        # keyed to one epoch would silently miss the others. A year whose
        # boundary falls outside the calendar's range simply contributes no
        # candidate (honest silence, never a fabricated date).
        cyears = set()
        for gm, gd in ((1, 1), (12, 31)):
            try:
                cyears.add(cal.from_astro(AstroDate(year, gm, gd)).year)
            except (CalendarRangeError, KeyError, ValueError):
                continue
        if not cyears:
            return ()
        basis = self._basis()
        out = []
        for cyear in range(min(cyears) - 1, max(cyears) + 2):
            try:
                jdn = cal.to_jdn(cyear, self.month, self.day)
            except (CalendarRangeError, KeyError, ValueError):
                continue
            if lo <= jdn <= hi:
                out.append((AstroDate.from_calendar(
                    self.calendar_key, cyear, self.month, self.day), basis))
        out.sort(key=lambda t: t[0])
        return tuple(out)


@dataclass(frozen=True)
class DecreeTableRule:
    """Explicit per-year dates for a holiday with no computable rule.

    ``dates`` maps a Gregorian ``year`` to its ``(month, day)`` — the honest
    kind for decree-driven realities (China's 调休 shift days, ad-hoc one-off
    observances). Basis ``tabulated``.

    A decree table is authoritative only across the *span of years it
    tabulates* — its :meth:`horizon`. A query outside that horizon is a silent
    time bomb (asking a 2024–2027 table for 2028 yields nothing, and a bare
    empty result is indistinguishable from "no such holiday"). The horizon is
    exposed so the wrapping :class:`~chronologia.civil_holidays.model.HolidayRule`
    can bridge past it via a ``predict`` annotation (see
    :meth:`~chronologia.civil_holidays.model.HolidayRule.resolve`) and so
    :func:`~chronologia.civil_holidays.registry.coverage` can report the gap
    instead of trusting the silence.
    """

    dates: Tuple[Tuple[int, Tuple[int, int]], ...]

    def observances(self, year: int) -> Tuple[Tuple[AstroDate, str], ...]:
        out = []
        for y, (m, d) in self.dates:
            if y == year:
                out.append((AstroDate(y, m, d), BASIS_TABULATED))
        return tuple(out)

    def horizon(self) -> Optional[Tuple[int, int]]:
        """The ``(min_year, max_year)`` this table tabulates (``None`` if empty)."""
        years = [y for y, _ in self.dates]
        return (min(years), max(years)) if years else None


@dataclass(frozen=True)
class OneOffRule:
    """A single dated occurrence in exactly ``year`` — a decreed one-time event.

    Coronations, jubilees, state funerals and one-time proclaimed bank holidays
    are not rules: they happened once, on a documented date, and recur never.
    ``OneOffRule`` models exactly that — it yields ``(year, month, day)`` when
    asked for its own ``year`` and an empty tuple for every other year, so a
    recurring-rule engine stays honest about a non-recurring event instead of
    fabricating it annually.

    ``citation`` is **mandatory**: a one-off asserts a specific historical fact,
    so it must carry the official source (a gov/legal URL or reference) that
    establishes it. An empty citation is a construction error. Basis
    ``tabulated`` — the honest footing for a decreed single date.
    """

    year: int
    month: int
    day: int
    citation: str

    def __post_init__(self) -> None:
        if not 1 <= self.month <= 12:
            raise ValueError(f"month out of range: {self.month}")
        if not 1 <= self.day <= 31:
            raise ValueError(f"day out of range: {self.day}")
        if not self.citation.strip():
            raise ValueError(
                "OneOffRule requires a citation (official source for the event)")

    def observances(self, year: int) -> Tuple[Tuple[AstroDate, str], ...]:
        if year != self.year:
            return ()
        return ((AstroDate(self.year, self.month, self.day), BASIS_TABULATED),)


@dataclass(frozen=True)
class ExcludeRule:
    """A subtractive rule: it *removes* an inherited holiday, never adds a date.

    The engine is otherwise additive — a subdivision row can only *add* a
    holiday to the jurisdiction-wide set. But a real subdivision may observe
    *fewer* holidays than its nation: North Dakota and the U.S. Minor Outlying
    Islands do not observe Columbus Day, a federal holiday. That is
    inexpressible with additive rules alone.

    An ``ExcludeRule`` names the ``target`` holiday (by its exact ``name``) to
    drop. It is meaningful only when scoped to a ``subdiv`` (or, in principle, a
    category) on its wrapping
    :class:`~chronologia.civil_holidays.model.HolidayRule`: when that
    subdivision is the one being resolved, every inherited holiday whose name
    equals ``target`` is removed from the result. It produces no date of its own
    — ``observances`` is always empty — so it is invisible except through its
    subtractive effect, applied by
    :meth:`~chronologia.civil_holidays.loader.HolidayCalendar.holidays`.
    """

    target: str

    def __post_init__(self) -> None:
        if not self.target.strip():
            raise ValueError("ExcludeRule requires a target holiday name")

    def observances(self, year: int) -> Tuple[Tuple[AstroDate, str], ...]:
        return ()


_EQUINOX_EVENTS = ("march", "september")


@dataclass(frozen=True)
class SolarEventRule:
    """A solar-instant holiday of ``year``, taken on its date in a civil timezone.

    An equinox or a solar term is the same thing to this engine: an astronomical
    instant the Sun reaches, read as a civil day in a given timezone. Both feed
    ``instant = span.start + span.width/2 + tz`` identically, so they share one
    kind rather than two classes that differ only in which almanac function they
    call. ``event`` selects it: ``"march"`` / ``"september"`` route through
    :func:`~chronologia.equinoxes.equinox` (the two equinoxes — solstices are
    not civil holidays here), any other name through
    :func:`~chronologia.equinoxes.solar_term` (e.g. ``"qingming"``).
    ``tz_offset_hours`` is the civil offset the date is read in. Basis ``exact``.

    * Japan's Shunbun no Hi / Shūbun no Hi (``"march"`` / ``"september"``,
      JST UTC+9) are gazetted from the Meeus ch.27 equinox instant; the ``.tab``
      header cites the Cabinet Office gazette and the golds assert its published
      dates, this arithmetic only reproduces them.
    * China's Qingming (``"qingming"``, CST UTC+8) is the day the Sun reaches
      ecliptic longitude 15°; the State Council announcement stays the cited
      legal authority in the ``.tab`` header.
    """

    event: str
    tz_offset_hours: float = 0.0

    def observances(self, year: int) -> Tuple[Tuple[AstroDate, str], ...]:
        if self.event in _EQUINOX_EVENTS:
            span = equinox(year, self.event)
        else:
            span = solar_term(year, self.event)
        instant = span.start + span.width / 2 + timedelta(
            hours=self.tz_offset_hours)
        return ((AstroDate(instant.year, instant.month, instant.day),
                 BASIS_EXACT),)
