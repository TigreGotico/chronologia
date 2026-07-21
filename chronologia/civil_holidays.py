"""Civil (public / regional / municipal) holidays as computed calendar rules.

A civil holiday is a *rule*, not a date: "New Year's Day" is "1 January every
year", "U.S. Labor Day" is "the first Monday of September", "Corpo de Deus" is
"the 60th day after Easter", "Eid al-Fitr" is "1 Shawwal on the Umm al-Qura
table". This module reduces each such rule to :mod:`chronologia`'s existing
machinery — :func:`~chronologia.recurrence.nth_weekday_of_month`,
:func:`~chronologia.computus.easter`, and the tabulated calendars in
:data:`~chronologia.calendars.CALENDARS` — so a holiday for the year -500 falls
out of the same integer arithmetic as one for 2024, with no ``datetime`` window.

Design — per-kind frozen rule classes (a tagged union by type)
--------------------------------------------------------------
Each *kind* of rule is its own frozen dataclass exposing one method,
``observances(year) -> tuple[(AstroDate, basis), ...]``. Per-kind classes are
preferred over a single class with a ``kind`` tag and a bag of optional fields:
every field a kind carries is mandatory *for that kind* and self-validating, so
an ill-formed rule cannot be constructed, and dispatch is ordinary Python
polymorphism rather than a ``match`` on a string tag.

The kinds:

* :class:`FixedRule` ``(month, day)`` — a constant Gregorian date; basis
  ``exact``.
* :class:`NthWeekdayRule` ``(month, n, weekday, post_offset)`` — the ``n``-th
  (``-1`` = last) ``weekday`` of ``month``, optionally shifted ``post_offset``
  days (so "the Monday after the 2nd Sunday of July" is ``n=2, weekday=SUN,
  post_offset=1``); evaluated through the RRULE engine. Basis ``exact``.
* :class:`EasterOffsetRule` ``(offset_days, method)`` — a whole-day offset from
  the computed Easter Sunday (``method`` ∈ ``gregorian`` | ``julian_gregorian_date``).
  Because Easter is always a Sunday, every "n-th Monday/Thursday after Easter"
  reduces to an exact integer offset. Basis ``exact``.
* :class:`CalendarDateRule` ``(calendar_key, month, day)`` — a fixed date *in
  another calendar* (``umm_al_qura``, ``hebrew`` …), resolved through
  :data:`~chronologia.calendars.CALENDARS`. It inherits that calendar's range
  limits: inside the tabulated range the basis is ``tabulated``; a year whose
  occurrence falls outside the table is simply **omitted** (honest silence, not
  a wrong fabricated date — see :class:`CalendarRangeError`). One Gregorian year
  may contain zero, one, or two occurrences (a short lunar year can fit two).
* :class:`DecreeTableRule` ``(dates)`` — explicit per-year dates for holidays
  that have *no* rule (announced by decree each year, e.g. China's 调休 shift
  days). Basis ``tabulated``: the honest kind for rule-less realities.

An :class:`ObservedShift` modifier is layered on top of any kind: a weekend
falling on a listed weekday shifts by a signed delta (the U.S. federal rule is
Saturday → preceding Friday, Sunday → following Monday).

Category schema
---------------
Every rule carries a set of :data:`CATEGORIES`:

* ``public`` — a nationwide statutory holiday.
* ``regional`` — observed in an autonomous region / first-level subdivision.
* ``municipal`` — a single municipality's holiday (the flagship depth here:
  Portugal's ~300 concelho holidays).
* ``religious`` — a holiday of religious origin (often *also* ``public``).
* ``school`` — a school-calendar holiday that is not a work holiday.

The schema is deliberately small and orthogonal; a holiday may hold several
categories at once (Sexta-feira Santa is ``public`` + ``religious``). This fills
the category gap the observed reference database acknowledges by *pinning* a
documented schema rather than leaving classification implicit.

Data files
----------
Rules live in ``chronologia/holiday_data/<country>.tab`` — a documented text
format (see :func:`load_calendar`) with a provenance header (official source
URL + retrieval date) per file, one rule per line, an optional subdivision
column. The engine loads them lazily and caches per file.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import timedelta
from typing import (Dict, FrozenSet, Iterable, Optional, Protocol, Tuple,
                    runtime_checkable)

from chronologia.astrodate import (BASIS_EXACT, BASIS_TABULATED, AstroDate,
                                   DateSpan)
from chronologia.calendars import CALENDARS, CalendarRangeError, gregorian_to_jdn
from chronologia.computus import easter
from chronologia.recurrence import (WEEKDAYS, nth_weekday_of_month,
                                    occurrences)

__all__ = [
    "CATEGORIES",
    "FixedRule",
    "NthWeekdayRule",
    "EasterOffsetRule",
    "CalendarDateRule",
    "DecreeTableRule",
    "ObservedShift",
    "US_OBSERVED_SHIFT",
    "SUNDAY_TO_MONDAY",
    "HolidayRule",
    "CivilHoliday",
    "HolidayCalendar",
    "holidays_for",
    "is_civil_holiday",
    "load_calendar",
]

#: The documented category schema (see the module docstring).
CATEGORIES: FrozenSet[str] = frozenset(
    {"public", "regional", "municipal", "religious", "school"})

_EASTER_METHODS = ("gregorian", "julian_gregorian_date")


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
        # Estimate the other calendar's year that maps here, then sweep a small
        # window around it (a lunar year is ~11 days short of a solar one).
        est = int((year - 622) * 33 / 32) + 1
        basis = self._basis()
        out = []
        for cyear in range(est - 2, est + 3):
            try:
                jdn = cal.to_jdn(cyear, self.month, self.day)
            except CalendarRangeError:
                continue
            except (KeyError, ValueError):
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
    """

    dates: Tuple[Tuple[int, Tuple[int, int]], ...]

    def observances(self, year: int) -> Tuple[Tuple[AstroDate, str], ...]:
        out = []
        for y, (m, d) in self.dates:
            if y == year:
                out.append((AstroDate(y, m, d), BASIS_TABULATED))
        return tuple(out)


# --------------------------------------------------------------------------
# Observed-shift modifier (weekend / in-lieu policies).
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class ObservedShift:
    """A parameterized weekend-shift policy.

    ``shifts`` is a tuple of ``(weekday, delta_days)``: a holiday landing on
    ``weekday`` (Monday==0 .. Sunday==6) is *observed* ``delta_days`` away. The
    first matching entry wins. The U.S. federal rule is Saturday → −1 (Friday),
    Sunday → +1 (Monday); many "next Monday" jurisdictions use just Sunday → +1.
    """

    shifts: Tuple[Tuple[int, int], ...]

    def apply(self, date: AstroDate) -> AstroDate:
        wd = date.weekday()
        for weekday, delta in self.shifts:
            if wd == weekday:
                return date + timedelta(days=delta)
        return date


#: U.S. federal rule (5 U.S.C. 6103): Saturday observed the preceding Friday,
#: Sunday observed the following Monday.
US_OBSERVED_SHIFT = ObservedShift(((5, -1), (6, 1)))
#: "If it falls on a Sunday, observe the next Monday."
SUNDAY_TO_MONDAY = ObservedShift(((6, 1),))

_OBSERVED_POLICIES: Dict[str, ObservedShift] = {
    "us": US_OBSERVED_SHIFT,
    "sun_mon": SUNDAY_TO_MONDAY,
}


# --------------------------------------------------------------------------
# The rule wrapper and the output object.
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class HolidayRule:
    """A named holiday rule: a date *kind* plus its civil metadata.

    The ``kind`` is one of the per-kind frozen classes above; ``categories`` is
    a subset of :data:`CATEGORIES`; ``subdiv`` scopes the rule to a subdivision
    (``None`` = jurisdiction-wide); ``observed`` optionally shifts the computed
    date onto its observed day.
    """

    name: str
    kind: RuleKind
    categories: FrozenSet[str]
    subdiv: Optional[str] = None
    observed: Optional[ObservedShift] = None

    def __post_init__(self) -> None:
        bad = set(self.categories) - CATEGORIES
        if bad:
            raise ValueError(
                f"unknown categories {sorted(bad)}; schema is {sorted(CATEGORIES)}")

    def resolve(self, year: int) -> Tuple[Tuple[AstroDate, str], ...]:
        out = []
        for date, basis in self.kind.observances(year):
            if self.observed is not None:
                date = self.observed.apply(date)
            out.append((date, basis))
        return tuple(out)


@dataclass(frozen=True)
class CivilHoliday:
    """A resolved holiday: a day-wide span with its civil metadata (objects out).

    ``span`` is a day-wide :class:`~chronologia.astrodate.DateSpan`; ``basis``
    records how the date was established (``exact`` for computed dates,
    ``tabulated`` for calendar-table / decree dates).
    """

    name: str
    span: DateSpan
    jurisdiction: str
    subdiv: Optional[str]
    categories: FrozenSet[str]
    basis: str

    @property
    def date(self) -> AstroDate:
        """The holiday's day (the span's start)."""
        return self.span.start

    def to_json(self) -> dict:
        """A ``json.dumps``-ready dict envelope (see :meth:`from_json`).

        ``categories`` serialize as a sorted list (deterministic output);
        :meth:`from_json` restores the :class:`frozenset`.
        """
        return {"type": "CivilHoliday", "name": self.name,
                "span": self.span.to_json(), "jurisdiction": self.jurisdiction,
                "subdiv": self.subdiv, "categories": sorted(self.categories),
                "basis": self.basis}

    @classmethod
    def from_json(cls, data: dict) -> "CivilHoliday":
        """Rebuild a :class:`CivilHoliday` from a :meth:`to_json` envelope."""
        if data.get("type") != "CivilHoliday":
            raise ValueError(
                f"not a CivilHoliday envelope: {data.get('type')!r}")
        return cls(data["name"], DateSpan.from_json(data["span"]),
                   data["jurisdiction"], data.get("subdiv"),
                   frozenset(data.get("categories", ())), data["basis"])


def _day_span(date: AstroDate, basis: str) -> DateSpan:
    start = AstroDate(date.year, date.month, date.day)
    return DateSpan(start, start + timedelta(days=1), basis)


# --------------------------------------------------------------------------
# The calendar object and the data-file loader.
# --------------------------------------------------------------------------
_DATA_DIR = os.path.join(os.path.dirname(__file__), "holiday_data")
_REQUIRED_HEADERS = ("jurisdiction", "source", "retrieved")


@dataclass(frozen=True)
class HolidayCalendar:
    """The set of holiday rules for one jurisdiction, loaded from a data file."""

    jurisdiction: str
    rules: Tuple[HolidayRule, ...]
    source: str = ""
    retrieved: str = ""

    def holidays(self, year: int, subdiv: Optional[str] = None,
                 categories: Optional[Iterable[str]] = None
                 ) -> Tuple[CivilHoliday, ...]:
        """Resolve every applicable rule for ``year`` into :class:`CivilHoliday`.

        ``subdiv`` selects a subdivision: a rule applies when it is
        jurisdiction-wide (``subdiv is None``) *or* its ``subdiv`` matches the
        requested one. ``categories`` keeps only holidays sharing at least one
        of the requested categories.
        """
        want = frozenset(categories) if categories is not None else None
        out = []
        for rule in self.rules:
            if rule.subdiv is not None and rule.subdiv != subdiv:
                continue
            if want is not None and not (rule.categories & want):
                continue
            for date, basis in rule.resolve(year):
                out.append(CivilHoliday(
                    name=rule.name,
                    span=_day_span(date, basis),
                    jurisdiction=self.jurisdiction,
                    subdiv=rule.subdiv,
                    categories=rule.categories,
                    basis=basis))
        out.sort(key=lambda h: (h.span.start, h.name))
        return tuple(out)


def _parse_kind(kind: str, args: str) -> RuleKind:
    parts = args.split()
    if kind == "fixed":
        m, d = int(parts[0]), int(parts[1])
        return FixedRule(m, d)
    if kind == "nth_weekday":
        month, n, wd = int(parts[0]), int(parts[1]), int(parts[2])
        post = int(parts[3]) if len(parts) > 3 else 0
        return NthWeekdayRule(month, n, wd, post)
    if kind == "easter":
        offset = int(parts[0])
        method = parts[1] if len(parts) > 1 else "gregorian"
        return EasterOffsetRule(offset, method)
    if kind == "calendar_date":
        return CalendarDateRule(parts[0], int(parts[1]), int(parts[2]))
    if kind == "decree":
        dates = []
        for token in parts:
            y, m, d = (int(x) for x in token.split("-"))
            dates.append((y, (m, d)))
        return DecreeTableRule(tuple(dates))
    raise ValueError(f"unknown rule kind {kind!r}")


def load_calendar(path: str) -> HolidayCalendar:
    """Parse a ``holiday_data/*.tab`` file into a :class:`HolidayCalendar`.

    **File format** (``# civil-holidays v1``). ``#``-prefixed lines are comments;
    header metadata is written as ``# name: value`` and the loader **requires**
    ``jurisdiction``, ``source`` (official URL) and ``retrieved`` (date) to be
    present — provenance is mandatory. Each data row is pipe-delimited::

        kind | name | args | categories | subdiv | observed

    * ``kind`` — ``fixed`` / ``nth_weekday`` / ``easter`` / ``calendar_date`` /
      ``decree`` (see the per-kind classes for ``args`` grammar).
    * ``name`` — the official holiday name (data, verbatim; no translation).
    * ``categories`` — space-separated subset of :data:`CATEGORIES`.
    * ``subdiv`` — optional subdivision code (empty = jurisdiction-wide).
    * ``observed`` — optional named policy (``us`` / ``sun_mon``; empty = none).
    """
    meta: Dict[str, str] = {}
    rules = []
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            if not line.strip():
                continue
            if line.lstrip().startswith("#"):
                body = line.lstrip()[1:].strip()
                if ":" in body:
                    k, v = body.split(":", 1)
                    meta.setdefault(k.strip(), v.strip())
                continue
            cols = [c.strip() for c in line.split("|")]
            if len(cols) < 4:
                raise ValueError(
                    f"malformed rule line (need >=4 columns): {line!r}")
            kind, name, args, cats = cols[0], cols[1], cols[2], cols[3]
            subdiv = cols[4] if len(cols) > 4 and cols[4] else None
            obs_name = cols[5] if len(cols) > 5 and cols[5] else None
            observed = _OBSERVED_POLICIES[obs_name] if obs_name else None
            categories = frozenset(cats.split())
            rules.append(HolidayRule(
                name=name,
                kind=_parse_kind(kind, args),
                categories=categories,
                subdiv=subdiv,
                observed=observed))
    missing = [h for h in _REQUIRED_HEADERS if h not in meta]
    if missing:
        raise ValueError(
            f"{os.path.basename(path)}: missing provenance header(s) {missing}")
    return HolidayCalendar(
        jurisdiction=meta["jurisdiction"],
        rules=tuple(rules),
        source=meta.get("source", ""),
        retrieved=meta.get("retrieved", ""))


_CACHE: Dict[str, HolidayCalendar] = {}


def _calendar_for(jurisdiction: str) -> HolidayCalendar:
    key = jurisdiction.upper()
    if key not in _CACHE:
        path = os.path.join(_DATA_DIR, f"{key.lower()}.tab")
        if not os.path.exists(path):
            raise KeyError(f"no holiday data for jurisdiction {jurisdiction!r}")
        _CACHE[key] = load_calendar(path)
    return _CACHE[key]


def holidays_for(jurisdiction: str, year: int, subdiv: Optional[str] = None,
                 categories: Optional[Iterable[str]] = None
                 ) -> Tuple[CivilHoliday, ...]:
    """Every civil holiday in ``jurisdiction`` for ``year`` (objects out).

    ``subdiv`` (e.g. ``"PT-LIS"``) adds that subdivision's holidays to the
    jurisdiction-wide set; ``categories`` filters to holidays sharing at least
    one requested category. Returns a chronologically sorted tuple of
    :class:`CivilHoliday`.

    :raises KeyError: no data file for ``jurisdiction``.
    """
    return _calendar_for(jurisdiction).holidays(year, subdiv, categories)


def is_civil_holiday(date, jurisdiction: str,
                     subdiv: Optional[str] = None) -> bool:
    """True when ``date`` (AstroDate/date/datetime) is a civil holiday.

    Considers jurisdiction-wide holidays plus, when ``subdiv`` is given, that
    subdivision's holidays.
    """
    point = AstroDate(date.year, date.month, date.day)
    for holiday in holidays_for(jurisdiction, point.year, subdiv):
        if holiday.span.contains(point):
            return True
    return False
