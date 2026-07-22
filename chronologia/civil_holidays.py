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
* :class:`NearestWeekdayRule` ``(month, day, weekday, direction)`` — the nearest
  ``weekday`` on or before (``direction=-1``) or on or after (``direction=+1``)
  a fixed ``(month, day)``, for "the Monday preceding 25 May" (Victoria Day) or
  "the next Monday on or after 6 Jan" (Colombia's Ley Emiliani) rules whose
  ordinal drifts year to year. Basis ``exact``.
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
  days). Basis ``tabulated``: the honest kind for rule-less realities. It knows
  its own :meth:`~DecreeTableRule.horizon` (the span of years it tabulates); a
  query past that horizon can be bridged by a :attr:`HolidayRule.predict`
  annotation naming a :data:`WELL_KNOWN` computable rule (an Islamic feast on
  the Umm al-Qura calendar, the Chinese lunisolar cluster) — the bridged date
  carries basis ``predicted``. Genuinely gazette-only holidays (调休-adjacent
  shifts, one-offs) have no computable mapping and stay honestly silent; the
  gap is reported by :func:`coverage`, never hidden.
* :class:`ExcludeRule` ``(target)`` — the engine's one *subtractive* kind: it
  removes a named inherited holiday for a subdivision (US-ND / US-UM do not
  observe Columbus Day). It emits no date; see :meth:`HolidayCalendar.holidays`.
* :class:`OneOffRule` ``(year, month, day, citation)`` — a single dated
  occurrence that happened *once* and carries no recurrence: a coronation, a
  jubilee, a state funeral, a one-time proclaimed bank holiday. It resolves to
  its date in exactly its ``year`` and to nothing in every other year, and its
  ``citation`` (an official source URL/reference) is **mandatory** — a one-off
  with no provenance cannot be constructed. Basis ``tabulated``: the honest kind
  for a decreed single event.

An :class:`ObservedShift` modifier is layered on top of any kind: a weekend
falling on a listed weekday shifts by a signed delta (the U.S. federal rule is
Saturday → preceding Friday, Sunday → following Monday) — it *relocates* the day.

A :class:`SubstitutePolicy` is the complementary mechanism: instead of moving the
nominal day it *adds* a separate substitute holiday when the nominal falls on a
listed weekday, keeping the nominal day too. This is the UK "in-lieu" convention
(gov.uk: a bank holiday on a weekend grants a substitute weekday — normally the
following Monday — and the Christmas/Boxing pair can cascade two substitutes when
25/26 December fall on a weekend) and Japan's 振替休日 furikae (a holiday on a
Sunday makes the following non-holiday weekday a holiday). Because the substitute
must land on the next day that is not *already* a holiday, the policy is resolved
at the :class:`HolidayCalendar` level (it needs the year's whole holiday set),
not inside a single rule. See :class:`SubstitutePolicy`.

Rule validity ranges
--------------------
A :class:`HolidayRule` may carry ``from_year`` / ``until_year`` bounds: a holiday
that only became statutory in a given year (Brazil's Consciência Negra national
from 2024 by Lei 14.759/2023; the U.S. Juneteenth federal holiday from 2021;
Japan's Mountain Day from 2016) resolves to *nothing* outside its effective range,
so the same fixed rule is honestly silent before it existed and present after.

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

Internationalisation — three layers
------------------------------------
The golden rule: *a holiday's real name is what its own government calls it.*
Names are therefore modelled in three layers, kept honestly distinct.

1. **Official native names (primary data).** A holiday's ``name`` is the
   jurisdiction's own official-language name (Portugal's ``"Implantação da
   República"``, Saudi Arabia's ``"عيد الفطر"``, China's ``"春节"``). A
   jurisdiction with *several* official languages carries all of them: the
   ``name`` cell of a ``.tab`` row may hold ``;;``-separated, ``lang:``-tagged
   alternates (``zh:春节 ;; en:Spring Festival``), which populate
   :attr:`CivilHoliday.names` (a BCP-47-ish ``lang -> name`` mapping); the first
   alternate is the primary ``name``. A plain, untagged single-name cell stays
   fully backward-compatible (empty ``names``). These are *citable facts*: each
   comes verbatim from the file's cited primary source.

2. **Display translations (renderings, not facts).** ``holiday_data/
   translations.tab`` supplies convenience *translations* (en/pt/es/de/fr …) for
   holidays whose display in another language is useful. They are marked
   ``source: translation`` precisely because they are renderings we authored, not
   official names a government published — an honesty distinction the format
   preserves. They land in :attr:`CivilHoliday.translations`.

3. **The resolution API.** :meth:`CivilHoliday.display_name` walks a documented
   fallback chain: an *official* name for ``lang`` if the jurisdiction has one,
   else a *translation*, else the primary ``name``. So the government's own word
   always wins where it exists, and a rendering fills in only where it does not.
"""
from __future__ import annotations

import os
import re
import threading
from dataclasses import dataclass, field
from datetime import timedelta
from types import MappingProxyType
from typing import (Dict, FrozenSet, Iterable, Mapping, Optional, Protocol,
                    Tuple, Union, runtime_checkable)

from chronologia.astrodate import (BASIS_EXACT, BASIS_PREDICTED,
                                   BASIS_TABULATED, AstroDate, DateSpan)
from chronologia.calendars import CALENDARS, CalendarRangeError, gregorian_to_jdn
from chronologia.computus import easter
from chronologia.equinoxes import equinox, solar_term
from chronologia.recurrence import (WEEKDAYS, nth_weekday_of_month,
                                    occurrences)

__all__ = [
    "CATEGORIES",
    "FixedRule",
    "NthWeekdayRule",
    "NearestWeekdayRule",
    "EasterOffsetRule",
    "CalendarDateRule",
    "DecreeTableRule",
    "OneOffRule",
    "ExcludeRule",
    "SolarEventRule",
    "ObservedShift",
    "US_OBSERVED_SHIFT",
    "SUNDAY_TO_MONDAY",
    "SATURDAY_SUNDAY_TO_MONDAY",
    "IL_INDEPENDENCE_SHIFT",
    "NL_KINGSDAY_SHIFT",
    "SubstitutePolicy",
    "GB_SUBSTITUTE",
    "JP_FURIKAE",
    "HolidayRule",
    "CivilHoliday",
    "HolidayCalendar",
    "holidays_for",
    "coverage",
    "COVERAGE_FULL",
    "COVERAGE_PARTIAL",
    "COVERAGE_PREDICTED",
    "COVERAGE_NONE",
    "WellKnownHoliday",
    "WELL_KNOWN",
    "WELL_KNOWN_BY_KEY",
    "JurisdictionKnownHoliday",
    "JURISDICTION_KNOWN",
    "JURISDICTION_KNOWN_BY_KEY_LANG",
    "JURISDICTION_KNOWN_KEYS",
    "load_well_known_aliases",
    "well_known_surfaces",
    "well_known_source",
    "is_civil_holiday",
    "load_calendar",
    "load_translations",
    "parse_name_cell",
]

#: The documented category schema (see the module docstring).
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
    exposed so the wrapping :class:`HolidayRule` can bridge past it via a
    ``predict`` annotation (see :meth:`HolidayRule.resolve`) and so
    :func:`coverage` can report the gap instead of trusting the silence.
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
    category) on its wrapping :class:`HolidayRule`: when that subdivision is the
    one being resolved, every inherited holiday whose name equals ``target`` is
    removed from the result. It produces no date of its own — ``observances`` is
    always empty — so it is invisible except through its subtractive effect,
    applied by :meth:`HolidayCalendar.holidays`.
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
#: Australian "weekend → next Monday" rule (Australia Day and, in most
#: states, Christmas/Boxing/ANZAC): Saturday → +2, Sunday → +1.
SATURDAY_SUNDAY_TO_MONDAY = ObservedShift(((5, 2), (6, 1)))
#: Israel's Yom Ha'atzmaut (Independence Day) postponement, keyed to the
#: weekday of the nominal Iyar 5. Under the 2004 amendment 5 Iyar can only be
#: Monday, Wednesday, Friday or Saturday: Monday → +1 (Tuesday, to keep the
#: preceding Yom HaZikaron off Sunday), Friday → −1 and Saturday → −2 (both to
#: Thursday, away from Shabbat); Wednesday is unshifted.
IL_INDEPENDENCE_SHIFT = ObservedShift(((0, 1), (4, -1), (5, -2)))
#: Netherlands Koningsdag (King's Day): celebrated 27 April, but when the 27th
#: is a Sunday it is brought forward to Saturday 26 April (never postponed).
NL_KINGSDAY_SHIFT = ObservedShift(((6, -1),))


# --------------------------------------------------------------------------
# Substitute-day (in-lieu) policy — ADDS a day, resolved calendar-wide.
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class SubstitutePolicy:
    """An in-lieu substitute-day policy: *adds* a holiday, never relocates.

    When a holiday's nominal date lands on one of ``trigger_weekdays`` (Monday==0
    .. Sunday==6), a separate substitute holiday is granted on the next day that
    is not *already* a holiday — and, when ``skip_weekends`` is set, not a
    Saturday or Sunday either. The nominal day stays a holiday in its own right;
    the substitute is emitted alongside it with ``label`` appended to the name.

    Unlike :class:`ObservedShift`, which each rule can apply on its own, a
    substitute must know the year's *whole* holiday set to skip days already
    taken (so the UK Christmas/Boxing pair cascades to two distinct Mondays/
    Tuesdays rather than colliding). It is therefore applied by
    :meth:`HolidayCalendar.holidays`, not by the rule in isolation.

    * UK bank holidays (:data:`GB_SUBSTITUTE`): a weekend bank holiday
      (Saturday or Sunday) → the next free weekday, gov.uk's "substitute day".
    * Japan 振替休日 (:data:`JP_FURIKAE`): a Sunday holiday → the following
      non-holiday day (Saturdays are eligible substitutes, so weekends are not
      skipped).
    """

    trigger_weekdays: Tuple[int, ...]
    skip_weekends: bool = True
    label: str = " (substitute)"

    def __post_init__(self) -> None:
        for wd in self.trigger_weekdays:
            if not 0 <= wd <= 6:
                raise ValueError(f"weekday out of range: {wd}")

    def substitute_for(self, nominal: AstroDate,
                       taken: FrozenSet[AstroDate]) -> Optional[AstroDate]:
        """The substitute day for ``nominal`` given already-``taken`` holidays.

        Returns ``None`` when ``nominal``'s weekday is not a trigger. Otherwise
        rolls forward one day at a time past any day already in ``taken`` (and,
        if ``skip_weekends``, past Saturdays and Sundays) and returns the first
        free day.
        """
        if nominal.weekday() not in self.trigger_weekdays:
            return None
        cand = nominal + timedelta(days=1)
        while cand in taken or (self.skip_weekends and cand.weekday() >= 5):
            cand = cand + timedelta(days=1)
        return cand


#: UK gov.uk substitute-day rule: a bank holiday on Saturday or Sunday grants a
#: substitute on the next weekday that is not already a bank holiday.
GB_SUBSTITUTE = SubstitutePolicy((5, 6), skip_weekends=True,
                                 label=" (substitute day)")
#: Japan 振替休日: a national holiday on a Sunday makes the following non-holiday
#: day a holiday (weekends are not skipped — a Saturday can be the substitute).
JP_FURIKAE = SubstitutePolicy((6,), skip_weekends=False, label=" (振替休日)")


# --------------------------------------------------------------------------
# One shift registry for the ``.tab`` ``observed`` column.
# --------------------------------------------------------------------------
#: A weekend-triggered date policy attached to a rule. There are two, kept as
#: distinct classes on purpose because they act at *different points* with
#: *different semantics* (the per-kind-class doctrine applied to shifts too):
#:
#: * :class:`ObservedShift` *relocates* the nominal day — applied per rule in
#:   :meth:`HolidayRule.resolve`, since it needs nothing but the date itself.
#: * :class:`SubstitutePolicy` *adds* a separate in-lieu day — applied
#:   calendar-wide in :meth:`HolidayCalendar.holidays`, since the substitute
#:   must skip days the rest of the year already took (the UK cascade).
#:
#: They are unified only where they were needlessly parallel: a single named
#: registry and a single :attr:`HolidayRule.shift` field carry either, dispatched
#: by type at the one point each applies — no twin dicts, no twin rule fields.
ShiftPolicy = Union[ObservedShift, SubstitutePolicy]

#: ``observed``-column name -> shift policy (relocating or in-lieu).
_SHIFT_POLICIES: Dict[str, ShiftPolicy] = {
    "us": US_OBSERVED_SHIFT,
    "sun_mon": SUNDAY_TO_MONDAY,
    "sat_sun_mon": SATURDAY_SUNDAY_TO_MONDAY,
    "il_independence": IL_INDEPENDENCE_SHIFT,
    "nl_kingsday": NL_KINGSDAY_SHIFT,
    "gb_substitute": GB_SUBSTITUTE,
    "jp_furikae": JP_FURIKAE,
}


# --------------------------------------------------------------------------
# The rule wrapper and the output object.
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class HolidayRule:
    """A named holiday rule: a date *kind* plus its civil metadata.

    The ``kind`` is one of the per-kind frozen classes above; ``categories`` is
    a subset of :data:`CATEGORIES`; ``subdiv`` scopes the rule to a subdivision
    (``None`` = jurisdiction-wide); ``shift`` optionally attaches a weekend
    policy — an :class:`ObservedShift` that relocates the computed date onto its
    observed day, or a :class:`SubstitutePolicy` that grants an in-lieu day
    (resolved calendar-wide, see :meth:`HolidayCalendar.holidays`); ``from_year``
    / ``until_year`` optionally bound the years the rule is in force (inclusive).
    """

    name: str
    kind: RuleKind
    categories: FrozenSet[str]
    subdiv: Optional[str] = None
    #: An optional weekend policy — either an :class:`ObservedShift` (relocates
    #: the nominal day, applied here in :meth:`resolve`) or a
    #: :class:`SubstitutePolicy` (adds an in-lieu day, applied calendar-wide in
    #: :meth:`HolidayCalendar.holidays`). One field for both; the applying site
    #: dispatches by type.
    shift: Optional[ShiftPolicy] = None
    from_year: Optional[int] = None
    until_year: Optional[int] = None
    span_shape: str = "day"
    #: Optional name of a :data:`WELL_KNOWN` holiday whose computable rule
    #: *predicts* this holiday's date in years beyond a :class:`DecreeTableRule`
    #: horizon. It bridges the silent time bomb: a decree table that tabulates
    #: 2024–2027 with ``predict="eid_al_fitr"`` resolves 2028 through the
    #: Umm al-Qura calendar with basis ``predicted`` instead of vanishing. Only
    #: honest where a genuine computable mapping exists — a decree row is
    #: annotated with a ``predict`` key only when the key's computed date
    #: matches the tabulated dates for *every* year the row tabulates (proven by
    #: construction, never guessed from the name). See :meth:`resolve`.
    predict: Optional[str] = None
    #: Official-language name alternates, ``lang -> name`` (see
    #: :func:`parse_name_cell`). ``name`` is the primary (first) official name;
    #: this maps *every* official-language rendering the source publishes, and is
    #: empty for a single-name rule. Excluded from equality/hash (it is derived
    #: metadata on the same rule identity, and keeps the rule hashable).
    names: Mapping[str, str] = field(default_factory=dict, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "names", MappingProxyType(dict(self.names)))
        bad = set(self.categories) - CATEGORIES
        if bad:
            raise ValueError(
                f"unknown categories {sorted(bad)}; schema is {sorted(CATEGORIES)}")
        if self.span_shape not in _SPAN_SHAPES:
            raise ValueError(
                f"unknown span shape {self.span_shape!r}; expected {_SPAN_SHAPES}")
        if (self.from_year is not None and self.until_year is not None
                and self.from_year > self.until_year):
            raise ValueError(
                f"from_year {self.from_year} > until_year {self.until_year}")
        if self.predict is not None and self.predict not in WELL_KNOWN_BY_KEY:
            raise ValueError(
                f"predict names unknown well-known key {self.predict!r}")

    def in_force(self, year: int) -> bool:
        """True when ``year`` is within this rule's validity range (inclusive)."""
        if self.from_year is not None and year < self.from_year:
            return False
        if self.until_year is not None and year > self.until_year:
            return False
        return True

    def past_horizon(self, year: int) -> bool:
        """True when ``year`` is outside this rule's :class:`DecreeTableRule` horizon.

        Only a decree-table kind has a horizon; any other kind (computable every
        year) is never "past" one, so this is ``False`` for it.
        """
        horizon = getattr(self.kind, "horizon", None)
        if horizon is None:
            return False
        bounds = horizon()
        if bounds is None:
            return False
        return year < bounds[0] or year > bounds[1]

    def resolve(self, year: int) -> Tuple[Tuple[AstroDate, str], ...]:
        if not self.in_force(year):
            return ()
        obs = self.kind.observances(year)
        # Bridge the horizon: a decree-tabulated holiday queried beyond the years
        # it tabulates resolves through its ``predict`` well-known rule (the same
        # computable calendar the feast really follows) with basis ``predicted``,
        # rather than silently vanishing.
        if not obs and self.predict is not None and self.past_horizon(year):
            wk = WELL_KNOWN_BY_KEY.get(self.predict)
            if wk is not None:
                obs = tuple((date, BASIS_PREDICTED)
                            for date, _ in wk.kind.observances(year))
        out = []
        for date, basis in obs:
            if isinstance(self.shift, ObservedShift):
                date = self.shift.apply(date)
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
    #: Official-language name alternates (``lang -> name``), copied from the
    #: rule. ``name`` is the primary (first) official name; empty for a
    #: single-name holiday. Excluded from equality/hash (derived display data).
    names: Mapping[str, str] = field(default_factory=dict, compare=False)
    #: Display *translations* (``lang -> text``) — renderings we authored, not
    #: official names (see ``holiday_data/translations.tab``). Distinct from
    #: :attr:`names` on purpose. Excluded from equality/hash.
    translations: Mapping[str, str] = field(default_factory=dict, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "names", MappingProxyType(dict(self.names)))
        object.__setattr__(
            self, "translations", MappingProxyType(dict(self.translations)))

    @property
    def date(self) -> AstroDate:
        """The holiday's day (the span's start)."""
        return self.span.start

    def display_name(self, lang: str) -> str:
        """The best name to *show* in ``lang``, along a documented fallback chain.

        The government's own word wins where it exists: an **official** name for
        ``lang`` (from :attr:`names`) is returned first; failing that a **display
        translation** (from :attr:`translations`); failing that the primary
        :attr:`name` itself. ``lang`` is matched exactly, then by its primary
        subtag (so ``"pt-BR"`` falls back to ``"pt"``).
        """
        for table in (self.names, self.translations):
            if lang in table:
                return table[lang]
        base = lang.split("-", 1)[0]
        if base != lang:
            for table in (self.names, self.translations):
                if base in table:
                    return table[base]
        return self.name

    def to_json(self) -> dict:
        """A ``json.dumps``-ready dict envelope (see :meth:`from_json`).

        ``categories`` serialize as a sorted list (deterministic output);
        :meth:`from_json` restores the :class:`frozenset`. ``names`` and
        ``translations`` serialize only when non-empty (backward-compatible with
        older single-name envelopes, which :meth:`from_json` reads too).
        """
        env = {"type": "CivilHoliday", "name": self.name,
               "span": self.span.to_json(), "jurisdiction": self.jurisdiction,
               "subdiv": self.subdiv, "categories": sorted(self.categories),
               "basis": self.basis}
        if self.names:
            env["names"] = dict(self.names)
        if self.translations:
            env["translations"] = dict(self.translations)
        return env

    @classmethod
    def from_json(cls, data: dict) -> "CivilHoliday":
        """Rebuild a :class:`CivilHoliday` from a :meth:`to_json` envelope."""
        if data.get("type") != "CivilHoliday":
            raise ValueError(
                f"not a CivilHoliday envelope: {data.get('type')!r}")
        return cls(data["name"], DateSpan.from_json(data["span"]),
                   data["jurisdiction"], data.get("subdiv"),
                   frozenset(data.get("categories", ())), data["basis"],
                   data.get("names", {}), data.get("translations", {}))


def _day_span(date: AstroDate, basis: str) -> DateSpan:
    start = AstroDate(date.year, date.month, date.day)
    return DateSpan(start, start + timedelta(days=1), basis)


#: Half-day span shapes. The engine's :class:`~chronologia.astrodate.DateSpan`
#: is span-native — its *width* IS the referent — so a half-day holiday is not a
#: flag bolted onto a day, it is a genuinely narrower span. ``half_pm`` (the
#: common "offices close at noon" pre-holiday afternoon) is the interval
#: ``[12:00, 24:00)`` of the day — the free afternoon; ``half_am`` is
#: ``[00:00, 12:00)``. ``day`` (the default) is the full ``[00:00, 24:00)``.
_SPAN_SHAPES = ("day", "half_pm", "half_am")


def _shape_span(date: AstroDate, basis: str, shape: str) -> DateSpan:
    """Build the resolved :class:`DateSpan` for ``shape``.

    A half-day is a real 12-hour-wide span, so ``span.width`` reports
    ``timedelta(hours=12)`` and ``span.contains`` is honest about which half of
    the civil day the holiday actually covers (a ``half_pm`` afternoon does not
    contain the morning). This is the first holiday whose width is not a whole
    day — the payoff of a span-native model over a date-plus-flag one.
    """
    day0 = AstroDate(date.year, date.month, date.day)
    if shape == "day":
        return DateSpan(day0, day0 + timedelta(days=1), basis)
    if shape == "half_pm":
        return DateSpan(day0.replace(hour=12), day0 + timedelta(days=1), basis)
    if shape == "half_am":
        return DateSpan(day0, day0.replace(hour=12), basis)
    raise ValueError(f"unknown span shape {shape!r}; expected {_SPAN_SHAPES}")


# --------------------------------------------------------------------------
# The calendar object and the data-file loader.
# --------------------------------------------------------------------------
_DATA_DIR = os.path.join(os.path.dirname(__file__), "holiday_data")
_REQUIRED_HEADERS = ("jurisdiction", "source", "retrieved")
_TRANSLATIONS_FILE = os.path.join(_DATA_DIR, "i18n", "translations.tab")


def load_translations(path: str = _TRANSLATIONS_FILE
                      ) -> Dict[Tuple[str, str], Dict[str, str]]:
    """Parse ``holiday_data/translations.tab`` into ``(JURIS, name) -> {lang: text}``.

    **File format** (``# civil-holidays-translations v1``). ``#``-lines are
    comments; each data row is pipe-delimited ``jurisdiction | name | lang |
    text``. ``jurisdiction`` is the upper-case code (``PT``); ``name`` is the
    holiday's **primary** ``name`` (its official native name — the join key back
    to the rule); ``lang`` is a BCP-47-ish code; ``text`` is the *translation*.

    These are display renderings, not official names — the honest distinction the
    header records with ``source: translation``. A missing file yields ``{}``.
    """
    out: Dict[Tuple[str, str], Dict[str, str]] = {}
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            cols = [c.strip() for c in line.split("|")]
            if len(cols) < 4:
                raise ValueError(
                    f"malformed translation line (need 4 columns): {line!r}")
            juris, name, lang, text = cols[0], cols[1], cols[2], cols[3]
            out.setdefault((juris.upper(), name), {})[lang] = text
    return out


_TRANSLATIONS: Optional[Dict[Tuple[str, str], Dict[str, str]]] = None
_TRANSLATIONS_LOCK = threading.Lock()


def _translations_for(jurisdiction: str, name: str) -> Dict[str, str]:
    global _TRANSLATIONS
    if _TRANSLATIONS is None:
        with _TRANSLATIONS_LOCK:
            if _TRANSLATIONS is None:
                _TRANSLATIONS = load_translations()
    return _TRANSLATIONS.get((jurisdiction.upper(), name), {})


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
        applicable = []
        # Subtractive pass: an ExcludeRule scoped to the requested subdivision
        # names an inherited holiday to drop (US-ND / US-UM omit Columbus Day).
        # It is collected here — never emitted — so the additive pass below skips
        # any holiday whose name it excludes.
        excluded: set = set()
        for rule in self.rules:
            if rule.subdiv is not None and rule.subdiv != subdiv:
                continue
            if isinstance(rule.kind, ExcludeRule):
                excluded.add(rule.kind.target)
                continue
            if want is not None and not (rule.categories & want):
                continue
            applicable.append(rule)
        applicable = [r for r in applicable if r.name not in excluded]

        out = []
        # Nominal (base) occurrences first — they populate the ``taken`` set the
        # substitute pass rolls forward past, so a substitute never collides with
        # another holiday (the UK Christmas/Boxing cascade, Japan furikae).
        subst_work = []  # (nominal_date, rule) awaiting a substitute day
        for rule in applicable:
            trans = _translations_for(self.jurisdiction, rule.name)
            for date, basis in rule.resolve(year):
                out.append(CivilHoliday(
                    name=rule.name,
                    span=_shape_span(date, basis, rule.span_shape),
                    jurisdiction=self.jurisdiction,
                    subdiv=rule.subdiv,
                    categories=rule.categories,
                    basis=basis,
                    names=rule.names,
                    translations=trans))
                if isinstance(rule.shift, SubstitutePolicy):
                    subst_work.append((date, basis, rule))

        taken = {h.span.start for h in out}
        for date, basis, rule in sorted(subst_work, key=lambda t: t[0]):
            sub = rule.shift.substitute_for(date, frozenset(taken))
            if sub is None:
                continue
            taken.add(sub)
            label = rule.shift.label
            trans = _translations_for(self.jurisdiction, rule.name)
            out.append(CivilHoliday(
                name=rule.name + label,
                span=_day_span(sub, basis),
                jurisdiction=self.jurisdiction,
                subdiv=rule.subdiv,
                categories=rule.categories,
                basis=basis,
                names={lang: text + label for lang, text in rule.names.items()},
                translations={lang: text + label
                              for lang, text in trans.items()}))
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
    if kind == "weekday_onbefore":
        return NearestWeekdayRule(int(parts[0]), int(parts[1]), int(parts[2]),
                                  direction=-1)
    if kind == "weekday_onafter":
        return NearestWeekdayRule(int(parts[0]), int(parts[1]), int(parts[2]),
                                  direction=+1)
    if kind == "easter":
        offset = int(parts[0])
        method = parts[1] if len(parts) > 1 else "gregorian"
        return EasterOffsetRule(offset, method)
    if kind == "calendar_date":
        return CalendarDateRule(parts[0], int(parts[1]), int(parts[2]))
    if kind in ("equinox", "solar_term"):
        tz = float(parts[1]) if len(parts) > 1 else 0.0
        return SolarEventRule(parts[0], tz)
    if kind == "decree":
        dates = []
        for token in parts:
            y, m, d = (int(x) for x in token.split("-"))
            dates.append((y, (m, d)))
        return DecreeTableRule(tuple(dates))
    if kind == "one_off":
        y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
        citation = " ".join(parts[3:])
        return OneOffRule(y, m, d, citation)
    if kind == "exclude":
        return ExcludeRule(args.strip())
    raise ValueError(f"unknown rule kind {kind!r}")


def _parse_valid(token: Optional[str]) -> Tuple[Optional[int], Optional[int]]:
    """Parse a ``valid`` column into ``(from_year, until_year)`` bounds.

    Grammar: ``"2024-"`` (from 2024 on), ``"-2015"`` (until 2015), ``"2016-2020"``
    (both bounds), ``"2024"`` (that single year only), empty/``None`` (unbounded).
    """
    if not token:
        return (None, None)
    if "-" in token:
        lo, hi = token.split("-", 1)
        return (int(lo) if lo.strip() else None,
                int(hi) if hi.strip() else None)
    y = int(token)
    return (y, y)


def load_calendar(path: str) -> HolidayCalendar:
    """Parse a ``holiday_data/*.tab`` file into a :class:`HolidayCalendar`.

    **File format** (``# civil-holidays v1``). ``#``-prefixed lines are comments;
    header metadata is written as ``# name: value`` and the loader **requires**
    ``jurisdiction``, ``source`` (official URL) and ``retrieved`` (date) to be
    present — provenance is mandatory. Each data row is pipe-delimited::

        kind | name | args | categories | subdiv | observed | valid | span | predict

    * ``kind`` — ``fixed`` / ``nth_weekday`` / ``easter`` / ``calendar_date`` /
      ``equinox`` / ``solar_term`` / ``decree`` / ``one_off`` / ``exclude``
      (see the per-kind classes for the ``args`` grammar). A ``one_off`` row's
      ``args`` is ``<year> <month> <day> <citation…>`` — the citation is the
      rest of the field and is mandatory. An ``exclude`` row's ``args`` is the
      exact ``name`` of the inherited holiday to *remove* for its ``subdiv``
      (the additive engine's one subtractive kind — see :class:`ExcludeRule`);
      its own ``name`` column repeats that target for readability.
    * ``name`` — the official holiday name(s), verbatim from the cited source. A
      single plain name is the common case; a multi-official jurisdiction may
      give ``;;``-separated ``lang:``-tagged alternates (``zh:春节 ;; en:Spring
      Festival``) — see :func:`parse_name_cell`. The first alternate is the
      primary ``name``; every tagged one populates :attr:`HolidayRule.names`.
      Display *translations* are a separate layer (``translations.tab``), never
      mixed into this column.
    * ``categories`` — space-separated subset of :data:`CATEGORIES`.
    * ``subdiv`` — optional subdivision code (empty = jurisdiction-wide).
    * ``observed`` — optional named policy: a relocating shift (``us`` /
      ``sun_mon`` / ``sat_sun_mon`` / ``il_independence``) OR an in-lieu
      substitute (``gb_substitute`` / ``jp_furikae``); empty = none.
    * ``valid`` — optional validity range (``"2024-"`` / ``"-2015"`` /
      ``"2016-2020"`` / ``"2024"``; empty = always in force).
    * ``span`` — optional span shape: ``day`` (default, a whole-day holiday),
      ``half_pm`` (the free afternoon ``[12:00, 24:00)`` — the "offices close at
      noon" pre-holiday half-day) or ``half_am`` (``[00:00, 12:00)``). The
      resolved :class:`CivilHoliday`'s span carries the real 12-hour width.
    * ``predict`` — optional :data:`WELL_KNOWN` key naming the computable rule
      that predicts a ``decree`` holiday's date beyond its tabulated horizon
      (basis ``predicted``); empty = honest silence past the horizon. See
      :attr:`HolidayRule.predict`.
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
            kind, name_cell, args, cats = cols[0], cols[1], cols[2], cols[3]
            name, names = parse_name_cell(name_cell)
            subdiv = cols[4] if len(cols) > 4 and cols[4] else None
            obs_name = cols[5] if len(cols) > 5 and cols[5] else None
            valid = cols[6] if len(cols) > 6 and cols[6] else None
            span_shape = cols[7] if len(cols) > 7 and cols[7] else "day"
            predict = cols[8] if len(cols) > 8 and cols[8] else None
            # The observed column names one shift policy — a relocating
            # ObservedShift or an in-lieu SubstitutePolicy; the applying site
            # dispatches by type.
            shift = None
            if obs_name is not None:
                shift = _SHIFT_POLICIES.get(obs_name)
                if shift is None:
                    raise ValueError(
                        f"unknown observed/substitute policy {obs_name!r}")
            from_year, until_year = _parse_valid(valid)
            categories = frozenset(cats.split())
            rules.append(HolidayRule(
                name=name,
                kind=_parse_kind(kind, args),
                categories=categories,
                subdiv=subdiv,
                shift=shift,
                from_year=from_year,
                until_year=until_year,
                span_shape=span_shape,
                predict=predict,
                names=names))
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
#: guards the lazy, per-jurisdiction ``.tab`` calendar cache so concurrent
#: first-lookups of different jurisdictions from separate threads each parse
#: their file exactly once.
_CACHE_LOCK = threading.Lock()

#: Financial-market jurisdiction codes are not ISO-3166-1 countries — they are
#: institutions (a stock exchange, a central bank's settlement system, a
#: futures exchange) that vacanza/holidays 0.101 registers under several
#: interchangeable codes for the *same* calendar (its MIC/ticker plus any
#: short-name aliases). Rather than duplicate one calendar's rules across
#: several identical ``.tab`` files, each alias here resolves to the single
#: canonical code that owns the shipped file. ``jurisdiction`` stays
#: free-form (no 2-letter assumption anywhere in the loader), so this is a
#: pure lookup layered in front of the ``.tab`` path resolution.
MARKET_ALIASES: Dict[str, str] = {
    # European Central Bank / TARGET2 settlement calendar -- vacanza's XECB.
    "ECB": "XECB",
    "TAR": "XECB",
    # New York Stock Exchange -- vacanza's XNYS.
    "NYSE": "XNYS",
    # Chicago Mercantile Exchange -- vacanza's XCME.
    "CME": "XCME",
    # Frankfurt Stock Exchange -- same calendar as Xetra, vacanza's XETR.
    "XFRA": "XETR",
    # SIX Swiss Exchange -- vacanza's XSWX.
    "SIX": "XSWX",
    # Toronto Stock Exchange -- vacanza's XTSE.
    "TSX": "XTSE",
    # Hong Kong Stock Exchange -- vacanza's XHKG.
    "HKEX": "XHKG",
    "SEHK": "XHKG",
    # Japan Exchange Group -- vacanza's XJPX.
    "JPX": "XJPX",
    "TSE": "XJPX",
    "OSE": "XJPX",
    # Shenzhen Stock Exchange -- same calendar as Shanghai, vacanza's XSHG.
    "XSHE": "XSHG",
    "SSE": "XSHG",
    "SZSE": "XSHG",
    # National Stock Exchange of India / Bombay Stock Exchange -- same
    # SEBI-gazetted calendar, vacanza's XBOM.
    "BSE": "XBOM",
    "XNSE": "XBOM",
    "NSE": "XBOM",
    # Brasil Bolsa Balcao -- vacanza's BVMF.
    "B3": "BVMF",
    # Bolsa Mexicana de Valores -- vacanza's XMEX.
    "BMV": "XMEX",
}


def _calendar_for(jurisdiction: str) -> HolidayCalendar:
    key = jurisdiction.upper()
    key = MARKET_ALIASES.get(key, key)
    cal = _CACHE.get(key)
    if cal is not None:
        return cal
    with _CACHE_LOCK:
        cal = _CACHE.get(key)
        if cal is None:
            path = os.path.join(_DATA_DIR, f"{key.lower()}.tab")
            if not os.path.exists(path):
                raise KeyError(
                    f"no holiday data for jurisdiction {jurisdiction!r}")
            cal = _CACHE[key] = load_calendar(path)
        return cal


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


#: The four coverage verdicts :func:`coverage` reports (see its docstring).
COVERAGE_FULL = "full"
COVERAGE_PARTIAL = "partial"
COVERAGE_PREDICTED = "predicted"
COVERAGE_NONE = "none"


def coverage(jurisdiction: str, year: int,
             subdiv: Optional[str] = None) -> str:
    """How well ``jurisdiction`` is covered for ``year`` — the horizon detector.

    Decree-tabulated holidays (Islamic feasts, the Chinese cluster, gazette-only
    shift days) are authoritative only across the years they tabulate. Past that
    horizon a bare :func:`holidays_for` call can silently drop them, so a caller
    who trusts the empty result is trusting a time bomb. ``coverage`` makes the
    horizon inspectable, returning one of:

    * ``"full"`` — no applicable decree rule is past its horizon this year
      (everything resolves from a tabulated table or a computable rule).
    * ``"predicted"`` — every applicable decree rule that *is* past its horizon
      carries a ``predict`` annotation, so the year is fully bridged through the
      calendars with basis ``predicted`` (no silent gap remains).
    * ``"partial"`` — at least one applicable decree rule is past its horizon
      with no prediction (a genuine gazette-only gap), while other holidays
      still resolve.
    * ``"none"`` — no holiday resolves for the year at all.

    ``subdiv`` / no ``categories`` scoping matches :func:`holidays_for`.
    """
    cal = _calendar_for(jurisdiction)
    resolved = cal.holidays(year, subdiv)
    if not resolved:
        return COVERAGE_NONE
    past_unpredicted = False
    past_predicted = False
    for rule in cal.rules:
        if rule.subdiv is not None and rule.subdiv != subdiv:
            continue
        if not rule.in_force(year):
            continue
        if not rule.past_horizon(year):
            continue
        if rule.predict is not None:
            past_predicted = True
        else:
            past_unpredicted = True
    if past_unpredicted:
        return COVERAGE_PARTIAL
    if past_predicted:
        return COVERAGE_PREDICTED
    return COVERAGE_FULL


# --------------------------------------------------------------------------
# Globally well-known holidays — the movable/religious/civil set a *language*
# binds for natural-language reference ("christmas", "when is easter", "next
# christmas").  This is deliberately NOT "every rule in all 45 jurisdictions":
# it is a small, curated set of holidays that are well-known *across* borders,
# each anchored to one jurisdiction whose data file already carries its rule
# and its official name.  Behaviour (the date math) stays in the rule kinds;
# the surfaces a language speaks are FACTS harvested at load time from the
# engine's existing i18n tables (official native names + ``translations.tab``)
# plus a curated spoken-alias table (``i18n/well_known.tab``) — never a giant
# hand-authored per-language vocabulary file.
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class _KnownHoliday:
    """The shared contract of both well-known tiers: a keyed, datable rule.

    Both the cross-border first tier (:class:`WellKnownHoliday`) and the
    locale-bound second tier (:class:`JurisdictionKnownHoliday`) are the same
    thing at heart — a language-neutral ``key`` bound to a date ``kind`` and a
    set of ``categories`` — differing only in their *binding* (one canonical
    rule vs one rule chosen per locale). The common ``date_for`` / ``span_for``
    resolution lives here once, so the resolver treats both tiers alike and
    neither subclass re-implements the date math. Subclasses supply the
    binding-specific provenance fields and their own ``span_shape``.
    """

    key: str
    kind: RuleKind
    categories: FrozenSet[str]

    def date_for(self, year: int) -> Optional[Tuple[AstroDate, str]]:
        """The ``(AstroDate, basis)`` of this holiday in ``year`` (or None)."""
        obs = self.kind.observances(year)
        return obs[0] if obs else None

    def span_for(self, year: int) -> Optional[Tuple[DateSpan, str]]:
        """The resolved ``(DateSpan, basis)`` for ``year`` (span shape applied)."""
        got = self.date_for(year)
        if got is None:
            return None
        date, basis = got
        return _shape_span(date, basis, self.span_shape), basis


@dataclass(frozen=True)
class WellKnownHoliday(_KnownHoliday):
    """A globally well-known holiday keyed for cross-language reference.

    ``key`` is a stable, language-neutral identifier (``christmas``,
    ``easter``); ``kind`` is the canonical (Western) date rule, reusing the
    same rule kinds every jurisdiction uses, so a movable holiday still
    resolves through :func:`~chronologia.computus.easter` and never re-derives
    date math.  ``anchor_jurisdiction`` / ``anchor_name`` name the real
    jurisdiction + official native name the surfaces are harvested from (the
    provenance ``explain`` traces); ``anchor_lang`` is the language of that
    native name (so it is offered as a surface for its own language).
    """

    anchor_jurisdiction: str
    anchor_name: str
    anchor_lang: str
    span_shape: str = "day"


#: The curated global well-known set.  Each entry anchors on a jurisdiction
#: whose ``.tab`` file already carries the same rule and the official name.
WELL_KNOWN: Tuple[WellKnownHoliday, ...] = (
    WellKnownHoliday("new_year", FixedRule(1, 1),
                     frozenset({"public"}), "PT", "Ano Novo", "pt"),
    WellKnownHoliday("new_year_eve", FixedRule(12, 31),
                     frozenset({"public"}), "US", "New Year's Eve", "en"),
    WellKnownHoliday("epiphany", FixedRule(1, 6),
                     frozenset({"public", "religious"}), "IT", "Epifania", "it"),
    WellKnownHoliday("carnival", EasterOffsetRule(-47),
                     frozenset({"public"}), "PT", "Carnaval", "pt"),
    WellKnownHoliday("good_friday", EasterOffsetRule(-2),
                     frozenset({"public", "religious"}),
                     "PT", "Sexta-feira Santa", "pt"),
    WellKnownHoliday("easter", EasterOffsetRule(0),
                     frozenset({"public", "religious"}),
                     "PT", "Domingo de Pascoa", "pt"),
    WellKnownHoliday("easter_monday", EasterOffsetRule(1),
                     frozenset({"public", "religious"}),
                     "FR", "Lundi de Pâques", "fr"),
    WellKnownHoliday("ascension", EasterOffsetRule(39),
                     frozenset({"public", "religious"}), "FR", "Ascension", "fr"),
    WellKnownHoliday("pentecost", EasterOffsetRule(49),
                     frozenset({"public", "religious"}),
                     "DE", "Pfingstsonntag", "de"),
    WellKnownHoliday("whit_monday", EasterOffsetRule(50),
                     frozenset({"public", "religious"}),
                     "FR", "Lundi de Pentecôte", "fr"),
    WellKnownHoliday("corpus_christi", EasterOffsetRule(60),
                     frozenset({"public", "religious"}),
                     "PT", "Corpo de Deus", "pt"),
    WellKnownHoliday("assumption", FixedRule(8, 15),
                     frozenset({"public", "religious"}),
                     "PT", "Assuncao de Nossa Senhora", "pt"),
    WellKnownHoliday("all_saints", FixedRule(11, 1),
                     frozenset({"public", "religious"}),
                     "PT", "Dia de Todos os Santos", "pt"),
    WellKnownHoliday("christmas_eve", FixedRule(12, 24),
                     frozenset({"public", "religious"}),
                     "US", "Christmas Eve", "en"),
    WellKnownHoliday("christmas", FixedRule(12, 25),
                     frozenset({"public", "religious"}), "PT", "Natal", "pt"),
    WellKnownHoliday("boxing_day", FixedRule(12, 26),
                     frozenset({"public", "religious"}),
                     "NL", "Tweede Kerstdag", "nl"),

    # ---- Orthodox-Easter cycle (Julian computus, already modelled) --------
    # The Orthodox Pascha rendered on the civil calendar via
    # ``EasterOffsetRule(..., "julian_gregorian_date")``.  Because Orthodox
    # Easter is a real Sunday, the whole cycle reduces to integer offsets, just
    # like the Western one — no new date math.  Basis ``exact``.
    WellKnownHoliday("orthodox_easter", EasterOffsetRule(0, "julian_gregorian_date"),
                     frozenset({"public", "religious", "orthodox"}),
                     "GR", "Πάσχα", "el"),
    WellKnownHoliday("orthodox_good_friday",
                     EasterOffsetRule(-2, "julian_gregorian_date"),
                     frozenset({"public", "religious", "orthodox"}),
                     "GR", "Μεγάλη Παρασκευή", "el"),
    WellKnownHoliday("orthodox_easter_monday",
                     EasterOffsetRule(1, "julian_gregorian_date"),
                     frozenset({"public", "religious", "orthodox"}),
                     "GR", "Δευτέρα του Πάσχα", "el"),

    # ---- Orthodox (Julian-calendar) Christmas -----------------------------
    # The Nativity fixed at Julian December 25, rendered on the civil calendar
    # through the registered ``julian`` calendar (NOT a hard-coded Gregorian
    # Jan 7): the Julian->Gregorian offset the calendar carries lands it on
    # Gregorian Jan 7 for 1900-2099 and Jan 6 in early 1900 — the repo's own
    # Julian arithmetic, never a magic constant. Basis ``exact``.
    # Bound to churches on the Julian calendar (RU/BG/UA/RS/GE ...). Greece and
    # the other New-Calendar churches keep Christmas on Gregorian Dec 25, i.e.
    # the plain ``christmas`` key — el is deliberately NOT an alias here.
    WellKnownHoliday("orthodox_christmas", CalendarDateRule("julian", 12, 25),
                     frozenset({"public", "religious", "orthodox"}),
                     "RU", "Рождество Христово", "ru"),
    WellKnownHoliday("orthodox_christmas_eve", CalendarDateRule("julian", 12, 24),
                     frozenset({"religious", "orthodox"}),
                     "RU", "Рождественский сочельник", "ru"),

    # ---- Movable Islamic feasts (Umm al-Qura table, ``calendar_date``) ----
    # These resolve through the tabulated Umm al-Qura calendar (basis
    # ``tabulated``): inside its published range (AH 1356..1500, roughly
    # 1937..2077 CE) the Gregorian date is looked up, never computed here; a
    # year whose occurrence falls outside the table contributes NO date, so the
    # reference is honestly silent out of range rather than fabricating one.
    WellKnownHoliday("eid_al_fitr", CalendarDateRule("umm_al_qura", 10, 1),
                     frozenset({"public", "religious", "islamic"}),
                     "SA", "عيد الفطر", "ar"),
    WellKnownHoliday("eid_al_adha", CalendarDateRule("umm_al_qura", 12, 10),
                     frozenset({"public", "religious", "islamic"}),
                     "SA", "عيد الأضحى", "ar"),
    WellKnownHoliday("ramadan", CalendarDateRule("umm_al_qura", 9, 1),
                     frozenset({"religious", "islamic"}),
                     "SA", "رمضان", "ar"),
    WellKnownHoliday("islamic_new_year", CalendarDateRule("umm_al_qura", 1, 1),
                     frozenset({"public", "religious", "islamic"}),
                     "SA", "رأس السنة الهجرية", "ar"),
    WellKnownHoliday("ashura", CalendarDateRule("umm_al_qura", 1, 10),
                     frozenset({"religious", "islamic"}),
                     "SA", "عاشوراء", "ar"),
    WellKnownHoliday("mawlid", CalendarDateRule("umm_al_qura", 3, 12),
                     frozenset({"public", "religious", "islamic"}),
                     "SA", "المولد النبوي", "ar"),

    # ---- Movable Jewish feasts (arithmetic Hebrew calendar, ``calendar_date``)
    # The Hebrew calendar here is the arithmetic (Hillel II) one, so its basis
    # is ``exact`` — the civil date is derived, not looked up.  Each feast is a
    # fixed Hebrew (month, day); a feast begins the preceding sunset, so the
    # date is the first *full* civil day (the convention the published Jewish
    # date tables tabulate).
    WellKnownHoliday("rosh_hashanah", CalendarDateRule("hebrew", 7, 1),
                     frozenset({"public", "religious", "hebrew"}),
                     "IL", "ראש השנה", "he"),
    WellKnownHoliday("yom_kippur", CalendarDateRule("hebrew", 7, 10),
                     frozenset({"public", "religious", "hebrew"}),
                     "IL", "יום כיפור", "he"),
    WellKnownHoliday("passover", CalendarDateRule("hebrew", 1, 15),
                     frozenset({"public", "religious", "hebrew"}),
                     "IL", "פסח", "he"),
    WellKnownHoliday("hanukkah", CalendarDateRule("hebrew", 9, 25),
                     frozenset({"religious", "hebrew"}),
                     "IL", "חנוכה", "he"),

    # ---- Movable East-Asian feasts (tabulated Chinese calendar) -----------
    # ``calendar_date`` against the tabulated Chinese lunisolar calendar
    # (basis ``tabulated``, published range lunar years 1901..2099); silent
    # outside the table, never computed here.
    WellKnownHoliday("chinese_new_year", CalendarDateRule("chinese", 1, 1),
                     frozenset({"public"}), "CN", "春节", "zh"),
    WellKnownHoliday("mid_autumn", CalendarDateRule("chinese", 8, 15),
                     frozenset({"public"}), "CN", "中秋节", "zh"),

    # ---- Nowruz (Persian New Year) ----------------------------------------
    # The March-equinox new year, taken here from the arithmetic Solar Hijri
    # calendar (1 Farvardin) — the same calendar the ``fa``/``az`` locales
    # already model, basis ``exact``.
    WellKnownHoliday("nowruz", CalendarDateRule("solar_hijri_arithmetic", 1, 1),
                     frozenset({"public"}), "IR", "نوروز", "fa"),

    # ---- Decree-tabulated feasts (no closed form modelled here) -----------
    # Diwali (Hindu, lunar Amanta/Purnimanta) and Vesak (Buddhist, full moon of
    # Vaisakha) have no arithmetic calendar in this engine, so — per house
    # style — they are ``DecreeTableRule`` with explicit published per-year
    # dates (Diwali = Lakshmi Puja main day; Vesak = the UN/observed full-moon
    # date).  Basis ``tabulated``; a year outside the listed range is honestly
    # silent (the reference simply does not resolve), so out-of-range corpus
    # cases are xfailed, not asserted to a fabricated date.
    WellKnownHoliday("diwali", DecreeTableRule((
        (2016, (10, 30)), (2017, (10, 19)), (2018, (11, 7)), (2019, (10, 27)),
        (2020, (11, 14)), (2021, (11, 4)), (2022, (10, 24)), (2023, (11, 12)),
        (2024, (10, 31)), (2025, (10, 20)), (2026, (11, 8)), (2027, (10, 29)),
    )), frozenset({"religious", "hindu"}), "IN", "दिवाली", "hi"),
    WellKnownHoliday("vesak", DecreeTableRule((
        (2016, (5, 21)), (2017, (5, 10)), (2018, (5, 29)), (2019, (5, 18)),
        (2020, (5, 7)), (2021, (5, 26)), (2022, (5, 16)), (2023, (5, 5)),
        (2024, (5, 23)), (2025, (5, 12)), (2026, (5, 31)), (2027, (5, 20)),
    )), frozenset({"religious"}), "LK", "Vesak", "en"),

    # ---- Jurisdiction-invariant secular / cross-anglosphere fixed days ----
    # These are the same rule everywhere they are spoken, so they need no
    # per-locale tier: Halloween (31 Oct), St Valentine's (14 Feb) and
    # St Patrick's (17 Mar, a statutory holiday in Ireland) are fixed Gregorian
    # dates; Thanksgiving here is the **U.S.** rule (4th Thursday of November).
    # Canada's Thanksgiving is the 2nd Monday of October — a genuinely
    # different rule — so the ``thanksgiving`` surface is offered for ``en``
    # only under the documented U.S. reading; a Canadian reference needs its own
    # jurisdiction-scoped resolution (out of scope here, and NOT silently
    # resolved to the U.S. date).
    WellKnownHoliday("halloween", FixedRule(10, 31),
                     frozenset({"unofficial"}), "US", "Halloween", "en"),
    WellKnownHoliday("valentines", FixedRule(2, 14),
                     frozenset({"unofficial"}), "US", "Valentine's Day", "en"),
    WellKnownHoliday("st_patricks", FixedRule(3, 17),
                     frozenset({"public", "religious"}),
                     "IE", "Saint Patrick's Day", "en"),
    WellKnownHoliday("thanksgiving", NthWeekdayRule(11, 4, 3),
                     frozenset({"public"}), "US", "Thanksgiving", "en"),
)

#: ``key -> WellKnownHoliday`` for O(1) lookup by the resolver.
WELL_KNOWN_BY_KEY: Dict[str, WellKnownHoliday] = {w.key: w for w in WELL_KNOWN}


# --------------------------------------------------------------------------
# Second tier — JURISDICTION-BOUND well-known holidays.
#
# Some holiday *names* only pick out a date once a jurisdiction is assumed: the
# same colloquial name resolves to a DIFFERENT rule in different countries.
# "Mother's Day" is the 2nd Sunday of May in the U.S./Germany/Italy/Netherlands,
# the 1st Sunday of May in Portugal/Spain, and the last Sunday of May in France;
# "Father's Day" is the 3rd Sunday of June in the U.S./France/Netherlands, but
# 19 March (St Joseph) in Portugal/Spain/Italy and Ascension Day in Germany.
# A single ``WELL_KNOWN`` entry (one key, one rule) cannot honestly carry that,
# so these live in a second tier keyed by ``(key, lang)``: the rule offered for
# a surface is chosen by the *locale's* documented jurisdiction default.
#
# Jurisdiction-default decisions (the fact each locale is bound to):
#   pt->PT  es->ES  ca->ES  gl->ES  de->DE  fr->FR  it->IT  nl->NL  en->US
# (``en`` is deliberately given the U.S. reading and no other; a multi-country
# anglosphere name like "independence day" is NOT added here — it is left
# unresolved because no single country is implied, and inventing one would be
# dishonest. A jurisdiction word would be required to disambiguate it.)
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class JurisdictionKnownHoliday(_KnownHoliday):
    """A well-known holiday whose rule depends on the speaking ``lang``'s country.

    ``key`` is the language-neutral base identifier (``mothers_day``);
    ``lang`` is the locale this binding serves; ``kind`` is the rule that
    locale's jurisdiction default fixes. ``jurisdiction`` records the country
    the default reflects (provenance for ``explain``). It shares
    :class:`_KnownHoliday`'s date/span interface, so the resolver treats both
    tiers alike.
    """

    lang: str
    jurisdiction: str
    span_shape: str = "day"


_MD_2SUN_MAY = NthWeekdayRule(5, 2, 6)   # 2nd Sunday of May
_MD_1SUN_MAY = NthWeekdayRule(5, 1, 6)   # 1st Sunday of May
_MD_LAST_SUN_MAY = NthWeekdayRule(5, -1, 6)  # last Sunday of May
_FD_3SUN_JUN = NthWeekdayRule(6, 3, 6)   # 3rd Sunday of June
_FD_MAR19 = FixedRule(3, 19)             # 19 March (St Joseph)
_FD_ASCENSION = EasterOffsetRule(39)     # Ascension Day (Germany, Vatertag)
_UNOFF = frozenset({"unofficial"})

#: The jurisdiction-bound second tier (see the block comment above).
JURISDICTION_KNOWN: Tuple[JurisdictionKnownHoliday, ...] = (
    # Mother's Day — rule per the locale's jurisdiction default.
    JurisdictionKnownHoliday("mothers_day", _MD_2SUN_MAY, _UNOFF, "en", "US"),
    JurisdictionKnownHoliday("mothers_day", _MD_2SUN_MAY, _UNOFF, "de", "DE"),
    JurisdictionKnownHoliday("mothers_day", _MD_2SUN_MAY, _UNOFF, "it", "IT"),
    JurisdictionKnownHoliday("mothers_day", _MD_2SUN_MAY, _UNOFF, "nl", "NL"),
    JurisdictionKnownHoliday("mothers_day", _MD_1SUN_MAY, _UNOFF, "pt", "PT"),
    JurisdictionKnownHoliday("mothers_day", _MD_1SUN_MAY, _UNOFF, "es", "ES"),
    JurisdictionKnownHoliday("mothers_day", _MD_1SUN_MAY, _UNOFF, "ca", "ES"),
    JurisdictionKnownHoliday("mothers_day", _MD_1SUN_MAY, _UNOFF, "gl", "ES"),
    JurisdictionKnownHoliday("mothers_day", _MD_LAST_SUN_MAY, _UNOFF, "fr", "FR"),
    # Father's Day — rule per the locale's jurisdiction default.
    JurisdictionKnownHoliday("fathers_day", _FD_3SUN_JUN, _UNOFF, "en", "US"),
    JurisdictionKnownHoliday("fathers_day", _FD_3SUN_JUN, _UNOFF, "fr", "FR"),
    JurisdictionKnownHoliday("fathers_day", _FD_3SUN_JUN, _UNOFF, "nl", "NL"),
    JurisdictionKnownHoliday("fathers_day", _FD_MAR19, _UNOFF, "pt", "PT"),
    JurisdictionKnownHoliday("fathers_day", _FD_MAR19, _UNOFF, "es", "ES"),
    JurisdictionKnownHoliday("fathers_day", _FD_MAR19, _UNOFF, "ca", "ES"),
    JurisdictionKnownHoliday("fathers_day", _FD_MAR19, _UNOFF, "gl", "ES"),
    JurisdictionKnownHoliday("fathers_day", _FD_MAR19, _UNOFF, "it", "IT"),
    JurisdictionKnownHoliday("fathers_day", _FD_ASCENSION, _UNOFF, "de", "DE"),
)

#: ``(key, lang) -> JurisdictionKnownHoliday`` for the resolver.
JURISDICTION_KNOWN_BY_KEY_LANG: Dict[Tuple[str, str], JurisdictionKnownHoliday] = {
    (j.key, j.lang): j for j in JURISDICTION_KNOWN}

#: The set of second-tier base keys (``well_known.tab`` may name these too).
JURISDICTION_KNOWN_KEYS: FrozenSet[str] = frozenset(
    j.key for j in JURISDICTION_KNOWN)

_WELL_KNOWN_FILE = os.path.join(_DATA_DIR, "i18n", "well_known.tab")


def load_well_known_aliases(path: str = _WELL_KNOWN_FILE
                            ) -> Dict[Tuple[str, str], Tuple[str, ...]]:
    """Parse ``i18n/well_known.tab`` into ``(key, lang) -> (surface, ...)``.

    **File format** (``# civil-holidays-well-known v1``).  ``#``-lines are
    comments; each data row is pipe-delimited ``key | lang | surfaces``, where
    ``surfaces`` is one or more ``;;``-separated spoken forms of the holiday in
    that language ("christmas ;; christmas day ;; xmas").  These are the
    curated *spoken aliases* — the colloquial names a person actually says —
    kept as data, distinct from the official native names (in the ``.tab``
    files) and the display translations (``translations.tab``).  A missing file
    yields ``{}``.
    """
    out: Dict[Tuple[str, str], Tuple[str, ...]] = {}
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            cols = [c.strip() for c in line.split("|")]
            if len(cols) < 3:
                raise ValueError(
                    f"malformed well-known line (need 3 columns): {line!r}")
            key, lang, cell = cols[0], cols[1], cols[2]
            if key not in WELL_KNOWN_BY_KEY and key not in JURISDICTION_KNOWN_KEYS:
                raise ValueError(
                    f"well_known.tab names unknown holiday key {key!r}")
            surfaces = tuple(s.strip() for s in cell.split(";;") if s.strip())
            out[(key, lang.lower())] = out.get((key, lang.lower()), ()) + surfaces
    return out


_WELL_KNOWN_ALIASES: Optional[Dict[Tuple[str, str], Tuple[str, ...]]] = None
_WELL_KNOWN_LOCK = threading.Lock()


def _well_known_aliases() -> Dict[Tuple[str, str], Tuple[str, ...]]:
    global _WELL_KNOWN_ALIASES
    if _WELL_KNOWN_ALIASES is None:
        with _WELL_KNOWN_LOCK:
            if _WELL_KNOWN_ALIASES is None:
                _WELL_KNOWN_ALIASES = load_well_known_aliases()
    return _WELL_KNOWN_ALIASES


def well_known_surfaces(lang: str) -> Dict[str, str]:
    """Every spoken surface -> well-known ``key`` for ``lang`` (lowercased).

    The surfaces are *derived* — never hand-listed per locale — by unioning the
    engine's existing i18n facts with the curated spoken-alias table:

    * the curated spoken aliases (``i18n/well_known.tab``) for ``(key, lang)``;
    * the anchor holiday's **display translation** for ``lang`` from
      ``translations.tab`` (an existing i18n fact);
    * the anchor holiday's **official native name** when ``lang`` is that
      name's own language (the government's own word).

    A language with no data for a holiday simply contributes no surface for it,
    so the reference is honestly scoped to what the locale's language actually
    names.
    """
    aliases = _well_known_aliases()
    out: Dict[str, str] = {}
    for wk in WELL_KNOWN:
        surfaces = set(aliases.get((wk.key, lang.lower()), ()))
        trans = _translations_for(wk.anchor_jurisdiction, wk.anchor_name)
        if lang in trans:
            surfaces.add(trans[lang])
        if wk.anchor_lang == lang:
            surfaces.add(wk.anchor_name)
        for surface in surfaces:
            out[surface.strip().lower()] = wk.key
    # Second tier: jurisdiction-bound holidays contribute a surface only in the
    # locale they are bound to (its surfaces live under the base key in
    # well_known.tab); the resolver picks the per-``(key, lang)`` rule.
    for j in JURISDICTION_KNOWN:
        if j.lang != lang.lower():
            continue
        for surface in aliases.get((j.key, lang.lower()), ()):
            out[surface.strip().lower()] = j.key
    return out


def well_known_source(key: str, lang: Optional[str] = None) -> str:
    """The provenance label ``"JURIS:name"`` for a well-known ``key``.

    First-tier keys resolve straight from :data:`WELL_KNOWN_BY_KEY`; a
    second-tier (jurisdiction-bound) key needs ``lang`` to pick the binding, and
    its label is the bound country plus the base key.
    """
    wk = WELL_KNOWN_BY_KEY.get(key)
    if wk is not None:
        return f"{wk.anchor_jurisdiction}:{wk.anchor_name}"
    if lang is not None:
        j = JURISDICTION_KNOWN_BY_KEY_LANG.get((key, lang.lower()))
        if j is not None:
            return f"{j.jurisdiction}:{j.key}"
    return f":{key}"


def is_civil_holiday(date, jurisdiction: str,
                     subdiv: Optional[str] = None,
                     categories: Optional[Iterable[str]] = None) -> bool:
    """True when ``date`` (AstroDate/date/datetime) is a civil holiday.

    Considers jurisdiction-wide holidays plus, when ``subdiv`` is given, that
    subdivision's holidays. ``categories`` filters the same way
    :func:`holidays_for` does (``None`` = every category, the historical
    default).
    """
    point = AstroDate(date.year, date.month, date.day)
    for holiday in holidays_for(jurisdiction, point.year, subdiv, categories):
        if holiday.span.contains(point):
            return True
    return False
