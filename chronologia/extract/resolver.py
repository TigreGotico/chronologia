"""Match + anchor + Conventions -> Resolution.  All date math lives here.

Every construction's semantics are computed once, engine-side, shared by
every language.  Notably the *sign* of a ``relative_offset`` is read from
the marker's declared direction (``spec.directions``); a language cannot
get the ago/hence direction wrong because it never writes the sign.

Resolution conventions (chosen once, documented, asserted in tests):

* pure-calendar constructions (``named_day``, ``weekday_ref``,
  ``calendar_date``, ``iso_date``) return midnight of the resolved date;
* ``relative_offset`` shifts the full anchor datetime, preserving its
  time-of-day.

An impossible or unrepresentable date never raises: :meth:`resolve`
returns ``None`` (the matcher offered a span the calendar rejects, so the
construction simply did not fire).

The adopted-extension constructions land their resolvers here:
``clock_time`` (with date composition), ``subdivision_time`` (alternative
day subdivisions), ``scoped_ordinal``, ``season_ref``, ``cycle_ref``
(named day cycles), ``regnal_date`` and ``roman_date``.  ``era_date``
remains declared-but-unimplemented (era phrasing resolves through
``reckoned_date`` / the eras layer) and raises ``NotImplementedError``.
"""
from __future__ import annotations

import calendar
import math
import re
from datetime import date, datetime, timedelta
from typing import Optional

from chronologia.astrodate import AstroDate, BASIS_RECONSTRUCTED, DateSpan
from chronologia.dayparts import daypart_span
from chronologia.calendars import (CALENDARS, gregorian_to_jdn,
                                        jdn_to_gregorian)
from chronologia.cycles import (DAY_CYCLES, DAY_SUBDIVISIONS, US_PER_DAY,
                                     resolve_cycle_day)
from chronologia.regnal import REGNAL_SEQUENCES
from chronologia.roman import roman_to_julian
from chronologia.extract.compiler import UNIMPLEMENTED
from chronologia.extract.matcher import GYEAR_MAX, GYEAR_MIN
from chronologia.extract.model import (Conventions, LangSpec, Match,
                                           Resolution)
from chronologia.extract.ranges import (_ABSOLUTE, _UNIT_OF_CENTURY,
                                        _UNIT_OF_MILLENNIUM, _UNIT_OF_MONTH,
                                        _UNIT_OF_YEAR,
                                        Hemisphere, Season, get_date_ordinal,
                                        current_season_date,
                                        last_season_date, next_season_date,
                                        season_to_date)


def _window_two_digit_year(n: int, anchor_year: int) -> int:
    """Resolve a bare two-digit year ``n`` (00-99) to a full year via an
    **anchor-relative sliding-window pivot**.

    A two-digit written year is inherently ambiguous ("the summer of 69" could
    be 1969 or 2069).  Rather than the fixed POSIX ``%y`` cut at 68/69 (which
    ages badly and mis-centuries recent years -- "'42" -> 2042, "'20" would
    read the wrong century), we adopt the anchor-relative window used by
    :mod:`email.utils` and ``dateutil``: the two-digit year resolves into the
    100-year span ``[anchor_year - 80, anchor_year + 19]``.  Exactly one of
    ``1900 + n`` / ``2000 + n`` lands inside that span, and that one wins, so
    the reading tracks the anchor and ages correctly (for anchor 2017 the
    window is 1937..2036: "'42" -> 1942, "'20" -> 2020, "'69" -> 1969).
    """
    candidate = 2000 + n
    if anchor_year - 80 <= candidate <= anchor_year + 19:
        return candidate
    return 1900 + n


def _pivot_two_digit_year(tok, anchor_year: int) -> int:
    """Read a ``YEAR`` slot token as an integer year, pivoting a *bare
    two-digit* run through the anchor-relative window of
    :func:`_window_two_digit_year`.

    The pivot fires **only** when the raw digit run is exactly two characters,
    so an explicit three-or-more-digit year ("summer of 500", "in 2024") and
    an era-marked year (handled by the separate era resolvers, e.g. "44 BC")
    are never rewritten.  A single-digit surface never reaches this slot at
    all -- the ``YEAR`` matcher only binds a bare number when its value is
    >= 32, it has >= 4 digits, or it carries the apostrophe cue ("'08") -- so
    no one-digit pivot is possible here.
    """
    n = int(tok.value)
    raw = tok.raw.lstrip("'").rstrip(".")
    if raw.isdigit() and len(raw) == 2:
        return _window_two_digit_year(n, anchor_year)
    return n


#: ``ERA`` slot surface -> era registry key, for the OFFSET eras a bare
#: Gregorian YEAR slot may compose with (see the ``ERA`` slot's docstring in
#: :mod:`chronologia.extract.matcher` for why this is BC/AD only).
_YEAR_ERA_KEYS = ("before_christ", "common_era")
_YEAR_ERA_CONNECTORS = {"before_christ": "bc", "common_era": "ad"}


def _era_key_for_token(spec, tok) -> Optional[str]:
    """Which era registry key an ``ERA`` slot token names, or ``None``."""
    for key in _YEAR_ERA_KEYS:
        if tok.text in spec.connectors.get(_YEAR_ERA_CONNECTORS[key],
                                           frozenset()):
            return key
    return None


def _year_with_era(year_tok, era_tok, spec) -> int:
    """Read an era-qualified ``YEAR`` slot as an astronomical year ("500 BC"
    -> -499, "44 AD" -> 44, "2560 BE" -> 2017).

    Only call this when ``era_tok is not None``; a bare (unqualified) YEAR
    goes through :func:`_pivot_two_digit_year` instead, which also handles
    the anchor-relative two-digit pivot.  An era-qualified year is never
    two-digit-pivoted -- the marker itself disambiguates the century -- so
    the literal digit run is read as-is, exactly as the dedicated
    era_bc/era_ad/era_buddhist_be constructions already do.
    """
    n = int(year_tok.value)
    from chronologia.eras import ERAS, EraCounting
    key = _era_key_for_token(spec, era_tok)
    if key is None:
        return n
    era = ERAS[key]
    if era.counting == EraCounting.YEARS_BEFORE:
        return era.epoch.year - n
    return era.epoch.year + n - 1


def _nth_weekday_of_month_astro(year: int, month: int, weekday: int,
                                n: int) -> Optional["AstroDate"]:
    """Same as :func:`_nth_weekday_of_month` but returns an
    :class:`~chronologia.astrodate.AstroDate` and supports years outside
    ``datetime.date``'s 1..9999 range (BC years) -- needed so an
    era-qualified "the last weekend of june 500 BC" can compose without
    routing through stdlib ``date``, which cannot represent astronomical
    year -499 at all."""
    from chronologia.astrodate import _days_in_month
    last = _days_in_month(year, month)
    days = [d for d in range(1, last + 1)
            if AstroDate(year, month, d).weekday() == weekday]
    idx = n if n < 0 else n - 1
    if not -len(days) <= idx < len(days):
        return None
    return AstroDate(year, month, days[idx])


def _pivot_year_str(raw: str, anchor_year: int) -> int:
    """The same anchor-relative window pivot as :func:`_pivot_two_digit_year`,
    but for a bare digit *substring* (the year component of a numeric
    slash/dash date) rather than a slot token: exactly two digits pivot through
    the window; three or four digits are the explicit year as written.
    """
    n = int(raw)
    if len(raw) == 2:
        return _window_two_digit_year(n, anchor_year)
    return n


def _nth_weekday_of_month(year: int, month: int, weekday: int,
                          n: int) -> Optional[date]:
    """The ``n``-th ``weekday`` (Mon=0) of ``month``/``year``; ``n < 0`` counts
    from the end (``-1`` = last).  Returns ``None`` when the month has no such
    occurrence (e.g. a 5th Monday of a February with only four) -- a
    non-existent day is vetoed, never fabricated, and the API never raises."""
    last = calendar.monthrange(year, month)[1]
    days = [d for d in range(1, last + 1)
            if date(year, month, d).weekday() == weekday]
    idx = n if n < 0 else n - 1
    if not -len(days) <= idx < len(days):
        return None
    return date(year, month, days[idx])


def _nth_weekday_of_year(year: int, weekday: int, n: int) -> Optional[date]:
    """The ``n``-th ``weekday`` (Mon=0) WITHIN calendar ``year`` (Jan 1 through
    Dec 31); ``n < 0`` counts from the end (``-1`` = last). Sibling to
    :func:`_nth_weekday_of_month` but scoped to the whole year rather than one
    month -- "the last monday of 2026", "the first monday in 2027". Returns
    ``None`` when the year has no such occurrence (an out-of-range ordinal --
    a year only ever has 52 or 53 of any given weekday), the same refusal
    policy as :func:`_nth_weekday_of_month`, never fabricating a reading."""
    jan1 = date(year, 1, 1)
    first = jan1 + timedelta(days=(weekday - jan1.weekday()) % 7)
    count = ((date(year, 12, 31) - first).days // 7) + 1
    idx = n if n < 0 else n - 1
    if not -count <= idx < count:
        return None
    if idx < 0:
        idx += count
    return first + timedelta(days=7 * idx)


def _nth_weekend_of_month(year: int, month: int, weekend_start: int,
                          n: int) -> Optional[date]:
    """The Saturday (locale ``weekend_start``, Mon=0) that opens the ``n``-th
    weekend of ``month``/``year``; ``n < 0`` counts from the end (``-1`` =
    last). A weekend belongs to the month its OPENING day falls in -- a
    weekend straddling a month boundary (e.g. Sat Jan 31 / Sun Feb 1) counts
    for the month the Saturday is in, not the one the Sunday spills into, so
    "the first weekend of february" skips it and starts at the next Saturday
    actually inside February. Returns ``None`` when the month has no such
    occurrence (an out-of-range ordinal), same refusal policy as
    :func:`_nth_weekday_of_month`."""
    return _nth_weekday_of_month(year, month, weekend_start, n)


def _add_months(dt: datetime, months: int) -> datetime:
    total = dt.month - 1 + months
    year = dt.year + total // 12
    month = total % 12 + 1
    day = min(dt.day, calendar.monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)


#: week-start convention name -> Python weekday index (Monday=0)
_WEEK_START = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
               "friday": 4, "saturday": 5, "sunday": 6}


class ResolverInvariant(Exception):
    """A handler reached a state that a consistent grammar/locale should make
    unreachable (an exhaustive elif fell through on an unmapped unit/kind).

    This is a bug in the engine or locale data, NOT "this text is not a date".
    It deliberately does NOT derive from ``ValueError``/``KeyError`` so the
    dispatch's degrade-to-``None`` guard never swallows it -- a mis-mapped unit
    surfaces loudly in tests instead of silently dropping a date."""

#: the parts of an ISO-8601 week designator token ("2026-W01", "2026-W1-3")
_ISOWEEK_PARTS = re.compile(r"(?P<year>\d{4})-[wW](?P<week>\d{1,2})"
                            r"(?:-(?P<weekday>\d))?")


def _shift_units(dt: datetime, kind: str, n: int):
    """Shift ``dt`` by ``n`` whole units of ``kind`` (n may be negative).
    Day/week/fortnight shift by timedelta; month and the year-family shift
    through :func:`_add_months` so a Feb-29 (or month-end) anchor clamps to the
    target month's last valid day.  Returns ``None`` for a sub-day or
    uncontainered unit (which names no whole-day span)."""
    if kind == "day":
        return dt + timedelta(days=n)
    if kind == "week":
        return dt + timedelta(weeks=n)
    if kind == "fortnight":
        return dt + timedelta(weeks=2 * n)
    if kind == "month":
        return _add_months(dt, n)
    month_steps = {"year": 12, "decade": 120, "century": 1200,
                   "millennium": 12000}
    if kind in month_steps:
        return _add_months(dt, n * month_steps[kind])
    return None


def _midnight(dt: datetime) -> datetime:
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def _point_span(dt: datetime, unit: str) -> DateSpan:
    """Half-open span of one ``unit``'s width starting at ``dt``.

    Width is the offset unit's granularity: day/week are fixed timedeltas,
    month/year advance the calendar so the span tiles cleanly.
    """
    start = AstroDate.from_datetime(dt)
    if unit == "minute":
        end = AstroDate.from_datetime(dt + timedelta(minutes=1))
    elif unit == "quarter_hour":
        end = AstroDate.from_datetime(dt + timedelta(minutes=15))
    elif unit == "hour":
        end = AstroDate.from_datetime(dt + timedelta(hours=1))
    elif unit == "day":
        end = AstroDate.from_datetime(dt + timedelta(days=1))
    elif unit == "week":
        end = AstroDate.from_datetime(dt + timedelta(days=7))
    elif unit == "fortnight":
        end = AstroDate.from_datetime(dt + timedelta(days=14))
    elif unit == "second":
        end = AstroDate.from_datetime(dt + timedelta(seconds=1))
    elif unit == "month":
        end = AstroDate.from_datetime(_add_months(dt, 1))
    elif unit == "year":
        end = AstroDate.from_datetime(_add_months(dt, 12))
    elif unit == "decade":
        end = AstroDate.from_datetime(_add_months(dt, 120))
    elif unit == "century":
        end = AstroDate.from_datetime(_add_months(dt, 1200))
    elif unit == "millennium":
        end = AstroDate.from_datetime(_add_months(dt, 12000))
    else:
        raise ResolverInvariant(f"unsupported offset unit {unit!r}")
    return DateSpan(start, end)


def _day_span(dt: datetime) -> DateSpan:
    """Day-wide span ``[midnight(dt), next midnight)``."""
    start = AstroDate.from_datetime(_midnight(dt))
    return DateSpan(start, start + timedelta(days=1))


def _week_span(start_astro: AstroDate, week_start_name: str) -> DateSpan:
    """The locale-aligned seven-day week containing ``start_astro``.

    ``week_start_name`` is the locale ``week_start`` convention (Monday for
    the languages carrying the "week of" marker); the span begins on that
    weekday on-or-before the given date and is a fixed seven days wide, so
    its width reads WEEK.  Shared by ``timespan._apply_week_of`` ("the week
    of X") and ``anchored._try_offset`` ("the week after/before X"), which
    both widen a resolved date to its calendar week under the same
    convention.
    """
    idx = _WEEK_START.get(week_start_name, 0)
    d = datetime(start_astro.year, start_astro.month, start_astro.day)
    back = (d.weekday() - idx) % 7
    week_start = d - timedelta(days=back)
    s = AstroDate.from_datetime(week_start)
    return DateSpan(s, s + timedelta(days=7))


#: constructions that name a *date* (a day or a wider calendar period); a
#: clock_time in the same text composes onto the day these select.
DATE_CONSTRUCTIONS = frozenset({
    "calendar_date", "reckoned_date", "nongregorian_date", "iso_date",
    "numeric_date",
    "weekday_ref", "named_day", "season_ref", "solar_event", "scoped_ordinal",
    # the named-day offset idioms ("the day after tomorrow", "the day before
    # yesterday") resolve to a whole day, so a further stranded "the day
    # after/before" pre-amble composes onto them exactly as onto any other
    # date -- letting the double nest "the day after the day after tomorrow"
    # step one more day past the inner result instead of stranding the outer.
    "named_day_after", "named_day_before",
    "scoped_bc", "scoped_ad", "decade_bc",
    "regnal_date", "roman_date", "era_date",
    "era_bc", "era_ad", "era_bp", "era_auc", "era_buddhist",
    "era_buddhist_be", "era_hijri", "era_solar_hijri",
    "olympiad_ref", "archon_ref",
    "roman_classical", "deep_time", "named_period",
    # a day-of-month reference ("on the 15th", "by the 15th") resolves to a
    # whole day (its own prefer-future month choice); it composes with a lone
    # clock exactly as any other date does, so "5pm on the 15th" places the
    # clock on that day instead of dropping the day and timing the anchor's.
    "month_day_ref",
    "holiday_ref", "new_year_ref",
    # a bare calendar year ("2020", "in 1995") resolves to a year-wide span
    # exactly like era_bc/era_ad -- without this the anchored-offset pass
    # (chronologia/extract/anchored.py) silently skips it, stranding "100
    # years before" in the remainder instead of composing onto the year's
    # start ("100 years before 2020" -> 1920-01-01, day-wide, same convention
    # as "100 years before june 2020" and "100 years before 44 BC").
    "year_ref"})


def compose_date_clock(date_res: Resolution, clock_res: Resolution) -> Resolution:
    """Intersect a date span with a clock span: the minute-wide clock time
    placed on the day the date construction selected.

    The date span's ``start`` supplies the calendar day (its left edge is
    that day's midnight); the clock span's ``start`` supplies the
    time-of-day.  The result is the clock's minute-wide span on that day --
    "june 5 at half past ten" -> ``[2027-06-05 10:30, ...10:31)``.
    """
    d = date_res.value.start
    c = clock_res.value.start
    start = AstroDate(d.year, d.month, d.day,
                      c.hour, c.minute, c.second, c.microsecond,
                      tzinfo=c.tzinfo)
    consumed = tuple(sorted(set(date_res.consumed) | set(clock_res.consumed)))
    return Resolution(DateSpan(start, start + timedelta(minutes=1)), consumed)


def _daypart_band(day: AstroDate, name: str) -> DateSpan:
    """The conventional time-of-day band ``name`` on the civil ``day``.

    The boundaries come from :func:`chronologia.dayparts.daypart_span` (Unicode
    CLDR 47 day-period rules, locale ``en``): morning ``[06:00, 12:00)``,
    afternoon ``[12:00, 18:00)``, evening ``[18:00, 21:00)``, night
    ``[21:00, 06:00)`` (crossing midnight into the next civil day).  The result
    carries ``BASIS_RECONSTRUCTED``, never ``exact``: a day-part is a
    conventional cultural boundary, not a clock reading the speaker gave, so the
    span must not claim the exactness a spoken "at 6am" would.
    """
    band = daypart_span(AstroDate(day.year, day.month, day.day), name)
    return DateSpan(band.start, band.end, BASIS_RECONSTRUCTED)


def compose_date_daypart(date_res: Resolution, daypart_res: Resolution,
                         name: str) -> Resolution:
    """Narrow a resolved day to the ``name`` day-part band on that day.

    The date construction ("yesterday", "tomorrow") supplies the civil day (its
    span's left edge); ``name`` supplies the band.  "yesterday morning" is the
    morning band of yesterday, replacing the whole-day span the bare date would
    yield -- the fix for the silent daypart drop.  A midnight-crosser (night)
    reaches into the following civil day, so "tomorrow night" runs tomorrow
    21:00 -> the day after 06:00.
    """
    d = date_res.value.start
    band = _daypart_band(d, name)
    consumed = tuple(sorted(set(date_res.consumed) | set(daypart_res.consumed)))
    return Resolution(band, consumed)


def _daypart_pm_side(name: str) -> bool:
    """Whether the day-part ``name`` sits on the PM side of noon -- its
    band starts at/after 12:00, or it crosses midnight (a "night"-shaped
    band, whatever the locale's own name for it).  Read from the same
    CLDR-derived band :func:`_daypart_band` already uses, so the check is
    locale-agnostic: it works for a locale's own canonical daypart key
    (``"vecher_ru"``) exactly as for the English ``"evening"``.
    """
    band = _daypart_band(AstroDate(2000, 1, 1), name)
    return band.end.day != band.start.day or band.start.hour >= 12


def _daypart_wraps_midnight(name: str) -> bool:
    """Whether the day-part ``name``'s band crosses midnight into the next
    civil day (a "night"-shaped band) -- the only kind that legitimately
    covers the literal hour 0.
    """
    band = _daypart_band(AstroDate(2000, 1, 1), name)
    return band.end.day != band.start.day


def compose_daypart_clock(clock_res: Resolution, daypart_res: Resolution,
                          name: str, has_explicit_meridiem: bool,
                          force_today: bool = False
                          ) -> Optional[Resolution]:
    """Apply a day-part word adjacent to an explicit clock as a MERIDIEM
    hint on it, rather than a competing reading -- "evening at 9" is 21:00,
    not a dropped "evening" plus a wrong-by-luck 09:00.

    The clock stays the pinpoint minute; the day-part just supplies the
    AM/PM side of a bare 12-hour reading (a PM-side day-part -- see
    :func:`_daypart_pm_side` -- shifts a spoken 1..11 by +12; an AM-side one
    like ``morning`` leaves it alone).  Over an already-PINNED hour -- an
    explicit am/pm marker on the clock itself, a 24-hour hour ``>= 13``, or
    the literal midnight ``0`` -- the day-part must instead *agree* with
    which side of noon that hour falls on (midnight only agrees with a
    midnight-crossing "night"-shaped band); a genuine clash ("morning at
    9pm") declines rather than silently pick a winner, the same refusal
    convention a contradictory bare-hour-plus-meridiem clock already uses
    (R57).

    ``force_today`` is set for an EXPLICIT-today day-part ("this evening",
    "tonight", "vanavond") -- one that names today's band regardless of the
    wall clock.  The clock's own resolution already ran its "roll to
    tomorrow if already past" rule on the UNSHIFTED hour ("8" < the 10:00
    anchor), which fires wrongly for a day-part that has not been shifted
    into its PM band yet ("tonight at 8" == 20:00, not tomorrow).  Pinning
    the date back to the day-part's own resolved day undoes that premature
    roll; a bare, non-explicit day-part ("evening at 3") keeps the clock's
    roll untouched, per the documented R117 convention.

    Returns ``None`` on contradiction.
    """
    c = clock_res.value.start
    hour = c.hour
    is_pm_daypart = _daypart_pm_side(name)
    if has_explicit_meridiem or hour >= 13 or hour == 0:
        # already a definite 24-hour reading -- the day-part must agree.
        if hour == 0:
            if not _daypart_wraps_midnight(name):
                return None
        elif is_pm_daypart != (hour >= 12):
            return None
        new_hour = hour
    else:
        # bare 1..12 hour, no meridiem of its own: let the day-part supply
        # the AM/PM side.
        new_hour = (hour % 12) + 12 if is_pm_daypart and hour != 12 else hour
    new_start = c.replace(hour=new_hour)
    if force_today:
        d = daypart_res.value.start
        new_start = new_start.replace(year=d.year, month=d.month, day=d.day)
    consumed = tuple(sorted(set(clock_res.consumed) | set(daypart_res.consumed)))
    return Resolution(DateSpan(new_start, new_start + timedelta(minutes=1)),
                      consumed)


def _astro_add_years(start: AstroDate, years: int) -> AstroDate:
    """``start`` advanced by whole years (day/month preserved, Feb 29 clamped)."""
    day = 28 if (start.month == 2 and start.day == 29
                 and not _astro_is_leap(start.year + years)) else start.day
    return start.replace(year=start.year + years, day=day)


def _astro_is_leap(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def _unit_end(start: AstroDate, kind: str) -> AstroDate:
    """Half-open end of a one-``kind``-wide span starting at ``start``.

    The width IS the referential uncertainty; the derived resolution tiles
    with :class:`DateSpan`'s width thresholds (a week-wide span reads WEEK,
    a century-wide span reads CENTURY).
    """
    if kind == "day":
        return start + timedelta(days=1)
    if kind == "week":
        return start + timedelta(days=7)
    if kind == "month":
        nyear, nmonth = (start.year + 1, 1) if start.month == 12 \
            else (start.year, start.month + 1)
        return AstroDate(nyear, nmonth, 1)
    steps = {"year": 1, "decade": 10, "century": 100, "millennium": 1000}
    if kind in steps:
        return _astro_add_years(AstroDate(start.year, start.month, start.day),
                                steps[kind])
    raise ResolverInvariant(f"unsupported scoped unit {kind!r}")


def _gregorian_month_span(year: int, month: int) -> DateSpan:
    """Month-wide span ``[first of month, first of next month)``."""
    start = AstroDate(year, month, 1)
    nyear, nmonth = (year + 1, 1) if month == 12 else (year, month + 1)
    return DateSpan(start, AstroDate(nyear, nmonth, 1))


class Resolver:
    """Configured once from a :class:`LangSpec`."""

    def __init__(self, spec: LangSpec):
        self.spec = spec
        self.conventions: Conventions = spec.conventions

    def resolve(self, match: Match, anchor: datetime,
                scale_mode: str = "short") -> Optional[Resolution]:
        if match.construction in UNIMPLEMENTED:
            raise NotImplementedError(
                f"construction {match.construction!r} is declared but not "
                f"resolved in the engine-core phase; it lands with its own "
                f"migration wave")
        handler = getattr(self, f"_resolve_{match.construction}", None)
        if handler is None:
            raise NotImplementedError(
                f"no resolver for construction {match.construction!r}")
        try:
            # deep time is the only construction whose reading depends on the
            # dialect short/long scale (the billion-cognate is 10^9 short, 10^12
            # long); every other handler ignores the mode.
            if match.construction == "deep_time":
                return self._resolve_deep_time(match, anchor, scale_mode)
            return handler(match, anchor)
        except (ValueError, OverflowError, KeyError):
            # "This reading does not resolve to a real date" -- an out-of-range
            # or calendar-invalid value (day 31 of a 30-day month, a year beyond
            # datetime's reach: ValueError/OverflowError), or a slot whose
            # surface has no entry in the map a handler consults (KeyError is
            # load-bearing decline control flow in several handlers, e.g. a
            # cross-slot lookup that legitimately misses). All three DECLINE the
            # reading rather than raise to the caller.
            #
            # NOT caught: ResolverInvariant -- an exhaustive elif falling through
            # on an unmapped unit/kind is an engine/locale-data BUG, and must
            # fail loudly here instead of silently dropping a date.
            return None

    def _scale_factor(self, surface: str, scale_mode: str) -> int:
        """The multiplier of a SCALE surface under the active dialect scale.

        The dialect-ambiguous billion-cognate is registered in
        ``spec.scales_by_mode[mode]`` (10^9 short, 10^12 long); every
        unambiguous scale word (thousand/million/milliard-cognate) lives only in
        the base ``spec.scales`` map.  The mode table wins when it has the word.
        """
        by_mode = self.spec.scales_by_mode.get(scale_mode, {})
        if surface in by_mode:
            return by_mode[surface]
        return self.spec.scales[surface]

    def _consumed(self, match: Match):
        return tuple(range(*match.span))

    # -- constructions -----------------------------------------------------

    def _offset_quantity(self, match):
        """The count of a relative offset: an explicit NUM, else a quantifier
        ("a"=1, "couple"=2, "half"=0.5), else an implicit 1 ("a week ago")."""
        num_tok = match.slots.get("NUM")
        quant_tok = match.slots.get("QUANT")
        # A NUM and a QUANT together read as a product of the two ("three
        # quarters of an hour" = 3 x 0.25 hour); a lone slot is taken as-is,
        # and a bare unit ("in a week", "через неделю") is an implicit one.
        if num_tok is not None and quant_tok is not None:
            return float(num_tok.value) * self.spec.quantifiers[quant_tok.text]
        if num_tok is not None:
            return float(num_tok.value)
        if quant_tok is not None:
            return self.spec.quantifiers[quant_tok.text]
        return 1.0

    _CALENDAR_GRAIN_MONTHS = {
        "month": 1, "year": 12, "decade": 120, "century": 1200,
        "millennium": 12000,
    }

    def _calendar_grain_offset(self, anchor, unit, step):
        """A (possibly fractional) offset of a calendar-grain unit
        (month/year/decade/century/millennium) -> a concrete datetime, or
        ``None`` when the fraction has no defensible calendar reading.

        A whole count steps through :func:`_add_months` exactly as before --
        a year is 12 calendar months, a decade 120, a century 1200, a
        millennium 12000.  A FRACTIONAL count is accepted where it converts
        to a WHOLE number of months: "half a decade" is exactly 5 years (60
        months), "a quarter of a century" exactly 25 years (300 months), "a
        quarter of a decade" exactly 2.5 years (30 months) -- all of those
        compose through the same calendar-month arithmetic with no rounding,
        because decade/century/millennium are themselves whole multiples of
        12 months.

        ``month`` has no finer CALENDAR unit to exchange a fraction for (a
        "half month" isn't a whole number of months), so a fractional month
        count is read in plain-meaning DAYS instead: half a month is 15 days
        (the ordinary English reading, not an exact half of the variable
        28-31 day month), a quarter month is 7 days (floored from 7.5, so it
        composes: four quarters of a month total 28 days, one short of a
        full month, rather than overshooting it).  Any other fractional
        month (thirds, tenths, ...) has no defensible day count and is
        refused (``None``) rather than silently truncated to the anchor.
        """
        months_per_unit = self._CALENDAR_GRAIN_MONTHS[unit]
        if unit == "month":
            whole = math.trunc(step)
            frac = step - whole
            if frac == 0:
                return _add_months(anchor, whole)
            sign = 1 if frac > 0 else -1
            mag = abs(frac)
            if math.isclose(mag, 0.5, abs_tol=1e-9):
                extra_days = 15
            elif math.isclose(mag, 0.25, abs_tol=1e-9):
                extra_days = 7
            else:
                return None
            return _add_months(anchor, whole) + timedelta(days=sign * extra_days)
        total_months = step * months_per_unit
        rounded = round(total_months)
        if not math.isclose(total_months, rounded, abs_tol=1e-9):
            return None
        return _add_months(anchor, rounded)

    def _resolve_relative_offset(self, match, anchor):
        qty = self._offset_quantity(match)
        usg_tok = match.slots.get("USG")
        if usg_tok is not None:
            unit = self.spec.singular_units[usg_tok.text]
        else:
            unit = self.spec.units[match.slots["UNIT"].text]
        sign = self.spec.directions[match.slots["MARKER"].text]
        step = sign * qty
        if unit == "minute":
            value = anchor + timedelta(minutes=step)
        elif unit == "quarter_hour":
            value = anchor + timedelta(minutes=15 * step)
        elif unit == "hour":
            value = anchor + timedelta(hours=step)
        elif unit == "day":
            value = anchor + timedelta(days=step)
        elif unit == "week":
            value = anchor + timedelta(weeks=step)
        elif unit == "fortnight":
            value = anchor + timedelta(weeks=2 * step)
        elif unit == "second":
            value = anchor + timedelta(seconds=step)
        elif unit in ("month", "year", "decade", "century", "millennium"):
            value = self._calendar_grain_offset(anchor, unit, step)
            if value is None:
                return None
        else:
            raise ResolverInvariant(f"unsupported offset unit {unit!r}")
        return Resolution(_point_span(value, unit), self._consumed(match))

    def _resolve_named_day(self, match, anchor):
        offset = self.spec.named_days[match.slots["DAY_WORD"].text]
        value = _midnight(anchor) + timedelta(days=offset)
        return Resolution(_day_span(value), self._consumed(match))

    def _resolve_daypart_ref(self, match, anchor):
        """A time-of-day band ("morning", "night") on a deictically-selected day.

        A bare daypart ("in the morning", "tonight") and "this <daypart>" both
        name TODAY's band; "last <daypart>" the band a day earlier, "next
        <daypart>" a day later -- the ``this/last/next`` marker read as a **day**
        offset (0/-1/+1), not the week offset it means for a calendar period.
        This is what makes "last night" the night that just ended: the night
        band anchored to yesterday, ``[yesterday 21:00, today 06:00)``, reaching
        through midnight into today's small hours.  "tonight" is a lexical
        today+night surface (it carries no marker).

        When a same-text date construction is present ("yesterday morning"),
        the engine composes instead (:func:`compose_date_daypart`); this
        standalone reading is the deictic-only path.
        """
        name = self.spec.dayparts[match.slots["DAYPART"].text]
        dpx_tok = match.slots.get("DPDEIX")
        if dpx_tok is not None:
            # deictic daypart ("tadi pagi"/"nanti malam"): the marker names the
            # NEAREST past/future occurrence of the band, so the day it lands on
            # depends on whether today's band edge has passed the anchor.  This
            # is what makes Indonesian "tadi pagi" = this morning (today's
            # morning already began) but "tadi malam" = last night (tonight's
            # band has not begun, so the nearest past night is yesterday's).
            kind = self.spec.daypart_deictics[dpx_tok.text]
            now = AstroDate.from_datetime(anchor)
            band = _daypart_band(AstroDate.from_datetime(_midnight(anchor)), name)
            if kind == "past" and band.start > now:
                band = _daypart_band(
                    AstroDate.from_datetime(_midnight(anchor) - timedelta(days=1)),
                    name)
            elif kind == "future" and band.start < now:
                band = _daypart_band(
                    AstroDate.from_datetime(_midnight(anchor) + timedelta(days=1)),
                    name)
            return Resolution(band, self._consumed(match))
        rel_tok = match.slots.get("REL_MARKER")
        off = self.spec.rel_markers[rel_tok.text] if rel_tok is not None else 0
        day = AstroDate.from_datetime(_midnight(anchor) + timedelta(days=off))
        return Resolution(_daypart_band(day, name), self._consumed(match))

    def _named_day_offset(self, match, anchor, step):
        """"the day after/before <named day>": one day past/short of a named
        day ("the day after tomorrow" -> +2, "the day before yesterday" -> -2).
        Only the day unit shifts a named day by a whole day -- the grammar's
        ``DAYUNIT`` slot (see ``matcher._bind``) already restricts the bound
        token to "day", so this check is a defensive belt-and-braces guard,
        not the primary gate (that lives at bind time now)."""
        if self.spec.units[match.slots["DAYUNIT"].text] != "day":
            return None
        offset = self.spec.named_days[match.slots["DAY_WORD"].text] + step
        return Resolution(_day_span(_midnight(anchor) + timedelta(days=offset)),
                          self._consumed(match))

    def _resolve_named_day_after(self, match, anchor):
        return self._named_day_offset(match, anchor, +1)

    def _resolve_named_day_before(self, match, anchor):
        return self._named_day_offset(match, anchor, -1)

    def _resolve_weekday_offset(self, match, anchor):
        """"a week from tuesday", "two weeks from monday": N weeks after the
        next occurrence (strictly future) of the named weekday."""
        if self.spec.units[match.slots["UNIT"].text] != "week":
            return None
        weeks = int(self._offset_quantity(match))
        target = self.spec.weekdays[match.slots["WEEKDAY"].text]
        ahead = (target - anchor.weekday()) % 7 or 7          # strictly future
        value = _midnight(anchor) + timedelta(days=ahead, weeks=weeks)
        return Resolution(_day_span(value), self._consumed(match))

    #: whole-day offset units (a named-day idiom only shifts by whole days).
    _DAY_UNIT_DAYS = {"day": 1, "week": 7, "fortnight": 14}

    def _named_day_base(self, match, anchor):
        """Midnight of the day a DAY_WORD ("today"/"tomorrow"/...) names."""
        offset = self.spec.named_days[match.slots["DAY_WORD"].text]
        return _midnight(anchor) + timedelta(days=offset)

    def _resolve_named_day_span_idiom(self, match, anchor):
        """British/Irish idiom "a week today", "a fortnight tomorrow", "two
        weeks today": N whole-day units *after* the day a DAY_WORD names.
        "a week today" is one week from today, "a week tomorrow" one week from
        tomorrow (Cambridge/Collins)."""
        unit_kind = self.spec.units[match.slots["UNIT"].text]
        days = self._DAY_UNIT_DAYS.get(unit_kind)
        if days is None:                            # only day-granular units
            return None
        qty = self._offset_quantity(match)
        value = self._named_day_base(match, anchor) + timedelta(days=days * qty)
        return Resolution(_day_span(value), self._consumed(match))

    def _resolve_named_day_offset_from(self, match, anchor):
        """"a month from tomorrow", "two months from today", "a week from
        tomorrow": N units after the day a DAY_WORD names -- the named-day
        counterpart of "3 weeks from monday"."""
        unit_kind = self.spec.units[match.slots["UNIT"].text]
        qty = self._offset_quantity(match)
        base = self._named_day_base(match, anchor)
        if unit_kind == "month":
            value = _add_months(base, int(qty))
        elif unit_kind == "year":
            value = _add_months(base, int(qty) * 12)
        else:
            days = self._DAY_UNIT_DAYS.get(unit_kind)
            if days is None:
                return None
            value = base + timedelta(days=days * qty)
        return Resolution(_day_span(value), self._consumed(match))

    def _resolve_sametime_shift(self, match, anchor):
        """"this time last year", "this time next week", "this time tomorrow":
        the anchor's exact instant (its time-of-day preserved) shifted by the
        named period -- a minute-wide moment, like any other time-carrying
        reference."""
        dw_tok = match.slots.get("DAY_WORD")
        if dw_tok is not None:
            value = anchor + timedelta(days=self.spec.named_days[dw_tok.text])
            return Resolution(_point_span(value, "minute"),
                              self._consumed(match))
        rel = self.spec.rel_markers[match.slots["REL_MARKER"].text]
        wd_tok = match.slots.get("WEEKDAY")
        if wd_tok is not None:                       # "this time next monday"
            target = self.spec.weekdays[wd_tok.text]
            if rel > 0:
                shift = (target - anchor.weekday()) % 7 or 7
            elif rel < 0:
                shift = -((anchor.weekday() - target) % 7 or 7)
            else:
                shift = target - anchor.weekday()
            value = anchor + timedelta(days=shift)
            return Resolution(_point_span(value, "minute"),
                              self._consumed(match))
        kind = self.spec.units[match.slots["UNIT"].text]
        if kind == "day":
            value = anchor + timedelta(days=rel)
        elif kind == "week":
            value = anchor + timedelta(weeks=rel)
        elif kind == "fortnight":
            value = anchor + timedelta(weeks=2 * rel)
        elif kind == "month":
            value = _add_months(anchor, rel)
        elif kind == "year":
            value = _add_months(anchor, rel * 12)
        else:
            return None
        return Resolution(_point_span(value, "minute"), self._consumed(match))

    def _resolve_holiday_eve(self, match, anchor):
        """"the eve of christmas", "eve of the new year": the day before a
        named holiday.  Reuses the holiday's own occurrence selection, then
        steps one whole day back (Christmas Eve is the eve of Christmas)."""
        holiday = self._resolve_holiday_ref(match, anchor)
        if holiday is None:
            return None
        span = holiday.value
        return Resolution(
            DateSpan(span.start - timedelta(days=1), span.end - timedelta(days=1)),
            self._consumed(match))

    def _resolve_weekday_ref(self, match, anchor):
        wd_tok = match.slots.get("WEEKDAY") or match.slots["WEEKDAYFULL"]
        target = self.spec.weekdays[wd_tok.text]
        rel_tok = match.slots.get("REL_MARKER")
        # A bare weekday ("friday") names the NEXT occurrence, strictly future:
        # the same prefer-future reckoning as an explicit "next", so when the
        # anchor already IS that weekday the span is seven days out.
        rel = self.spec.rel_markers[rel_tok.text] if rel_tok is not None else 1
        base = _midnight(anchor)
        if rel > 0:      # next
            ahead = (target - anchor.weekday()) % 7 or 7
            value = base + timedelta(days=ahead)
        elif rel < 0:    # last
            back = (anchor.weekday() - target) % 7 or 7
            value = base - timedelta(days=back)
        else:            # this: within the current week (honouring week_start)
            start_idx = _WEEK_START.get(self.conventions.week_start, 0)
            week_start = base - timedelta(days=(anchor.weekday() - start_idx) % 7)
            value = week_start + timedelta(days=(target - start_idx) % 7)
        return Resolution(_day_span(value), self._consumed(match))

    def _resolve_before_last(self, match, anchor):
        """"the <X> before last" -- the X two occurrences into the past: the
        most recent past X, then one whole period earlier.  "the Tuesday
        before last" is the Tuesday before *last* Tuesday (last Tuesday minus a
        week); "the week before last" the week before *last* week; "the night
        before last" the night two nights ago.  The trailing marker must be the
        BACKWARD one ("last") -- "X before next" is not this idiom, so a
        non-``-1`` marker declines the reading and lets the sub-parts stand."""
        if self.spec.rel_markers[match.slots["REL_MARKER"].text] != -1:
            return None
        base = _midnight(anchor)
        wd_tok = match.slots.get("WEEKDAY")
        if wd_tok is not None:
            target = self.spec.weekdays[wd_tok.text]
            back = (anchor.weekday() - target) % 7 or 7          # last occurrence
            value = base - timedelta(days=back + 7)              # one more back
            return Resolution(_day_span(value), self._consumed(match))
        dp_tok = match.slots.get("DAYPART")
        if dp_tok is not None:
            name = self.spec.dayparts[dp_tok.text]
            day = AstroDate.from_datetime(base - timedelta(days=2))
            return Resolution(_daypart_band(day, name), self._consumed(match))
        kind = self.spec.units.get(match.slots["UNIT"].text)
        span = self._period_span(kind, -2, anchor)
        if span is None:
            return None
        return Resolution(span, self._consumed(match))

    def _resolve_after_next(self, match, anchor):
        """"the <X> after next" -- skip one occurrence ahead (next-next): "the
        day after next" is the anchor + 2 days, "the morning after next" the
        morning of that day, "the week after next" the week after *next* week.
        The trailing marker must be the FORWARD one ("next")."""
        if self.spec.rel_markers[match.slots["REL_MARKER"].text] != 1:
            return None
        base = _midnight(anchor)
        dp_tok = match.slots.get("DAYPART")
        if dp_tok is not None:
            name = self.spec.dayparts[dp_tok.text]
            day = AstroDate.from_datetime(base + timedelta(days=2))
            return Resolution(_daypart_band(day, name), self._consumed(match))
        kind = self.spec.units.get(match.slots["UNIT"].text)
        if kind == "day":
            return Resolution(_day_span(base + timedelta(days=2)),
                              self._consumed(match))
        # Coarser "the <unit> after next" (week/month) is a DEFERRED gap: the
        # repo deliberately returns None for "the week after next" (an offset
        # the grammar does not spell -- see test_nl_gap_residue), so declining
        # the reading here preserves that contract rather than fabricating a
        # span.  Only the day-granular "day after next" is resolved.
        return None

    def _resolve_weekday_ago(self, match, anchor):
        """"a <weekday> ago" -- the most recent PAST occurrence of the weekday,
        the same reckoning as "last <weekday>" ("a Monday ago" == "last
        Monday").  The "... ago" framing looks back exactly like "a week
        ago"."""
        target = self.spec.weekdays[match.slots["WEEKDAY"].text]
        back = (anchor.weekday() - target) % 7 or 7              # strictly past
        value = _midnight(anchor) - timedelta(days=back)
        return Resolution(_day_span(value), self._consumed(match))

    def _resolve_unit_ago_weekday(self, match, anchor):
        """"a week ago Tuesday", "a fortnight ago Monday" -- the named weekday
        of the week that was N units ago.  The week/fortnight offset picks the
        target week (a whole-day granular back-shift); the weekday then pins the
        exact day WITHIN that week's Monday-start seven days.  The weekday is
        consumed and actually consulted, so the result is that weekday, not the
        offset's landing day."""
        kind = self.spec.units.get(match.slots["UNIT"].text)
        weeks = {"week": 1, "fortnight": 2}.get(kind)
        if weeks is None:
            return None
        qty = int(self._offset_quantity(match))
        base = _midnight(anchor) - timedelta(weeks=weeks * qty)
        target = self.spec.weekdays[match.slots["WEEKDAY"].text]
        start_idx = _WEEK_START.get(self.conventions.week_start, 0)
        week_start = base - timedelta(days=(base.weekday() - start_idx) % 7)
        value = week_start + timedelta(days=(target - start_idx) % 7)
        return Resolution(_day_span(value), self._consumed(match))

    def _resolve_rel_period(self, match, anchor):
        """"next/last/this <period unit>": the whole calendar period that
        contains the anchor -- the week, month, year, decade, ... -- shifted
        by the relative marker.  Calendar-aligned and one-unit wide, so
        "next week" tiles the seven days of the following week, "this month"
        the anchor's own month, "last year" the preceding January-December.

        The width IS the referential uncertainty (a seven-day span reads
        WEEK, a year-wide span reads YEAR), matching the scoped-ordinal and
        offset families.  Sub-day units and the fortnight have no calendar
        container to align to, so they fall through to the offset family.
        """
        kind = self.spec.units.get(match.slots["UNIT"].text)
        rel = self.spec.rel_markers[match.slots["REL_MARKER"].text]
        span = self._period_span(kind, rel, anchor)
        if span is None:
            return None
        return Resolution(span, self._consumed(match))

    def _resolve_rel_span(self, match, anchor):
        """"the next/last <N> <units>": a rolling span of N whole units forward
        (next/coming) or backward (last/past) from the anchor DAY -- "the next 3
        weeks" is ``[today, today + 21 days)``, "the last 2 months" is
        ``[2 months ago, today)``.  Unlike :meth:`_resolve_rel_period`'s single
        calendar-aligned unit, the span is anchored on the current day, not the
        calendar grid.  A "this" marker (rel 0), a non-positive count, or a
        sub-day / uncontainered unit names no such span."""
        rel = self.spec.rel_markers[match.slots["REL_MARKER"].text]
        num = int(match.slots["NUM"].value)
        kind = self.spec.units.get(match.slots["UNIT"].text)
        if rel == 0 or num < 1:
            return None
        base = _midnight(anchor)
        far = _shift_units(base, kind, num if rel > 0 else -num)
        if far is None:
            return None
        lo, hi = (base, far) if rel > 0 else (far, base)
        return Resolution(DateSpan(AstroDate.from_datetime(lo),
                                   AstroDate.from_datetime(hi)),
                          self._consumed(match))

    def _resolve_rel_span_quarter(self, match, anchor):
        """"the next/last <N> quarters": calendar-aligned, unlike the
        day-anchored :meth:`_resolve_rel_span`. "the next 2 quarters" is the
        *next* two whole calendar quarters -- ``[start of next quarter, start
        of the quarter 2 further)`` -- matching the calendar grid the
        singular "the next quarter" (:meth:`_resolve_quarter_ref`) already
        uses. "the last 2 quarters" is the two whole quarters already ended --
        ``[start of the quarter 2 back, start of the current quarter)``. A
        "this" marker (rel 0) or a non-positive count names no such span."""
        rel = self.spec.rel_markers[match.slots["REL_MARKER"].text]
        num = int(match.slots["NUM"].value)
        if rel == 0 or num < 1:
            return None
        cur = (anchor.month - 1) // 3          # 0-based current quarter
        cur_abs = anchor.year * 4 + cur         # absolute quarter index

        def _quarter_start(abs_idx):
            year, q = divmod(abs_idx, 4)
            return datetime(year, 3 * q + 1, 1)

        if rel > 0:
            lo = _quarter_start(cur_abs + 1)
            hi = _quarter_start(cur_abs + 1 + num)
        else:
            lo = _quarter_start(cur_abs - num)
            hi = _quarter_start(cur_abs)
        return Resolution(DateSpan(AstroDate.from_datetime(lo),
                                   AstroDate.from_datetime(hi)),
                          self._consumed(match))

    def _resolve_rel_span_weekend(self, match, anchor):
        """"the next/last <N> weekends": the *covering* span from the start
        of the nearest upcoming weekend through the end of the Nth ("the next
        2 weekends" is Sat-start of the imminent weekend to Sun-end of the
        one after it), or from the start of the Nth-back weekend through the
        end of the most recently ended one ("the last 2 weekends").

        Deliberately asymmetric with the singular "next weekend"
        (:meth:`_resolve_weekend_ref`), which skips the imminent weekend --
        that skip reads right for naming ONE weekend deictically ("this
        weekend" already means the imminent one, so "next weekend" must mean
        the one after), but a COUNT of weekends is naturally inclusive of the
        nearest one: "the next 2 weekends" covers the two soonest weekends,
        starting with the one about to happen. A "this" marker (rel 0) or a
        non-positive count names no such span."""
        rel = self.spec.rel_markers[match.slots["REL_MARKER"].text]
        num = int(match.slots["NUM"].value)
        if rel == 0 or num < 1:
            return None
        base = _midnight(anchor)
        start_idx = _WEEK_START.get(self.conventions.week_start, 0)
        wknd_idx = self.conventions.weekend_start
        week_start = base - timedelta(days=(anchor.weekday() - start_idx) % 7)
        first = week_start + timedelta(days=(wknd_idx - start_idx) % 7)
        if rel > 0:
            if first < base:
                first += timedelta(weeks=1)
            lo = first
            hi = first + timedelta(weeks=num - 1) + timedelta(days=2)
        else:
            if first + timedelta(days=2) > base:
                first -= timedelta(weeks=1)
            hi = first + timedelta(days=2)
            lo = first - timedelta(weeks=num - 1)
        return Resolution(DateSpan(AstroDate.from_datetime(lo),
                                   AstroDate.from_datetime(hi)),
                          self._consumed(match))

    def _period_span(self, kind, rel, anchor):
        """The whole calendar period of ``kind`` containing the anchor, shifted
        by ``rel`` whole units.  Returns a :class:`DateSpan` for the civil
        containers (day/week/month/year/decade/century/millennium), or ``None``
        for a kind with no calendar container (sub-day units, the fortnight).

        Shared by ``rel_period`` and ``fuzzy_period`` so "next week" and the
        parent of "early next week" are the identical span."""
        if kind == "week":
            base = _midnight(anchor)
            start_idx = _WEEK_START.get(self.conventions.week_start, 0)
            back = (anchor.weekday() - start_idx) % 7
            week_start = base - timedelta(days=back) + timedelta(weeks=rel)
            s = AstroDate.from_datetime(week_start)
            return DateSpan(s, s + timedelta(days=7))
        if kind == "day":
            value = _midnight(anchor) + timedelta(days=rel)
            return _day_span(value)
        if kind == "month":
            base = _add_months(_midnight(anchor).replace(day=1), rel)
            return _gregorian_month_span(base.year, base.month)
        steps = {"year": 1, "decade": 10, "century": 100, "millennium": 1000}
        if kind in steps:
            step = steps[kind]
            start_year = (anchor.year // step) * step + rel * step
            s = AstroDate(start_year, 1, 1)
            return DateSpan(s, _unit_end(s, kind))
        return None

    def _resolve_fuzzy_period(self, match, anchor):
        """"early/mid/late" (or "beginning/end of") a calendar period naming a
        UNIT -- "the beginning of the month", "early next week", "late this
        year".  The parent is the calendar period the UNIT names (anchor's
        current one, or the one an optional REL_MARKER shifts to); the PART
        slices it into the conventional first/middle/last third (edges rounded
        by :func:`chronologia.subdivide`)."""
        from chronologia import subdivide
        kind = self.spec.units.get(match.slots["UNIT"].text)
        if kind not in ("week", "month", "year", "decade", "century",
                        "millennium"):
            return None
        rel_tok = match.slots.get("REL_MARKER")
        rel = self.spec.rel_markers[rel_tok.text] if rel_tok is not None else 0
        parent = self._period_span(kind, rel, anchor)
        if parent is None:
            return None
        part = self.spec.period_parts[match.slots["PART"].text]
        # Snap the interior thirds of an era-scale period (decade/century/
        # millennium) to whole years so a coarse-precision phrase yields no
        # fractional-day boundaries; week/month/year keep their finer native
        # cuts.
        snap = {"decade": "year", "century": "year",
                "millennium": "year"}.get(kind)
        span = subdivide(parent, part, snap=snap)
        return Resolution(DateSpan(span.start, span.end), self._consumed(match))

    #: month index a calendar quarter (1..4) begins on.
    def _resolve_quarter_ref(self, match, anchor):
        """A calendar quarter: "Q3 2026", "the third quarter of 2026", "the
        third quarter" (anchor year), "next/this/last quarter".  Quarter N
        (1..4) is the three-month span ``[month 3N-2, month 3N+1)``.  A
        REL_MARKER shifts by whole quarters from the anchor's current one.
        Anything outside 1..4 does not name a quarter and the construction does
        not fire.

        An optional ``PART`` ("end of Q3", "start of the quarter") narrows the
        whole quarter to its first/middle/last third via the same span-native
        :func:`chronologia.subdivide` the month/year fuzzy narrowings use; an
        ``ordlast`` day selector ("last day of the quarter", "last day of Q3")
        returns the single final civil day of the quarter."""
        rel_tok = match.slots.get("REL_MARKER")
        num_tok = match.slots.get("ORD") or match.slots.get("NUM")
        if rel_tok is not None:
            rel = self.spec.rel_markers[rel_tok.text]
            cur = (anchor.month - 1) // 3               # 0-based current quarter
            total = cur + rel
            year = anchor.year + total // 4
            q = total % 4 + 1
        elif num_tok is not None:
            q = int(num_tok.value)
            if not 1 <= q <= 4:
                return None
            year_tok = match.slots.get("YEAR")
            era_tok = match.slots.get("ERA")
            if era_tok is not None and year_tok is None:
                # a stray era marker with no YEAR bound alongside it -- see
                # the identical guard in ``_resolve_calendar_date`` for why
                # this refuses rather than silently falling back to the
                # anchor's year.
                return None
            if year_tok is not None and era_tok is not None:
                # an era-qualified year ("the first quarter of 500 BC")
                # composes through the same era registry the bare era_bc/
                # era_ad constructions use -- see the ``ERA`` slot's
                # docstring.  ``AstroDate`` below already supports arbitrary
                # (including negative/BC) years, so no further branching is
                # needed past computing the right astronomical year here.
                year = _year_with_era(year_tok, era_tok, self.spec)
            else:
                year = (_pivot_two_digit_year(year_tok, anchor.year)
                        if year_tok is not None else anchor.year)
        else:                                           # bare "the quarter"
            q = (anchor.month - 1) // 3 + 1              # anchor's own quarter
            year = anchor.year
        m = 3 * (q - 1) + 1
        end_year, end_month = (year + 1, 1) if m + 3 > 12 else (year, m + 3)
        span = DateSpan(AstroDate(year, m, 1), AstroDate(end_year, end_month, 1))
        part_tok = match.slots.get("PART")
        if part_tok is not None:
            from chronologia import subdivide
            span = subdivide(span, self.spec.period_parts[part_tok.text])
            return Resolution(DateSpan(span.start, span.end),
                              self._consumed(match))
        unit_tok = match.slots.get("UNIT")               # "last day of ..."
        if unit_tok is not None and self.spec.units.get(unit_tok.text) == "day":
            last = span.end + timedelta(days=-1)
            return Resolution(DateSpan(last, span.end), self._consumed(match))
        return Resolution(span, self._consumed(match))

    def _resolve_iso_week_ref(self, match, anchor):
        """An ISO-8601 week: "week 32", "week 32 of 2026".  ISO weeks are
        **Monday-based by the standard**, independent of the locale's civil
        ``week_start`` convention (which only governs "this/next week"); week 1
        is the week containing the year's first Thursday.  The span is the
        seven days ``[Monday, next Monday)``.  A number naming no ISO week in
        the year (0, or past the year's 52nd/53rd) does not fire.

        The week number arrives either as a cardinal (``NUM`` -- "week 10 of
        2024") or as an ordinal in the prose form (``ORD`` -- "the 10th week of
        2024"); the two surfaces name the same week and MUST resolve to the
        identical span.
        """
        num_tok = match.slots.get("NUM") or match.slots["ORD"]
        w = int(num_tok.value)
        year_tok = match.slots.get("YEAR")
        # a two-digit / apostrophe year ("week 5 of '24") pivots through the
        # anchor-relative window like every other year slot; reading it raw gave
        # ISO year 24 AD.
        year = (_pivot_two_digit_year(year_tok, anchor.year)
                if year_tok is not None else anchor.year)
        monday = date.fromisocalendar(year, w, 1)       # ValueError -> None
        s = AstroDate.from_date(monday)
        return Resolution(DateSpan(s, s + timedelta(days=7)),
                          self._consumed(match))

    def _resolve_iso_week_date(self, match, anchor):
        """The ISO-8601 **week designator** literal (ISO 8601 §4.4.4.2):
        ``YYYY-Www`` (a whole week) and ``YYYY-Www-D`` (one day of it).

        Per the standard, weeks begin on **Monday** and week 01 is the week
        containing the year's first Thursday -- equivalently, the week
        containing 4 January.  The year in the literal is the *ISO week-numbering
        year*, which is not the calendar year at the boundaries: a long year has
        53 weeks, and ``2020-W53`` legitimately starts 2020-12-28 and runs into
        January 2021.  All of that arithmetic is delegated to
        :meth:`datetime.date.fromisocalendar`, the standard-conforming
        implementation, so no ISO week rule is restated here.

        Spans: ``YYYY-Www`` -> the seven days ``[Monday, next Monday)``;
        ``YYYY-Www-D`` -> the single day for ISO weekday ``D`` (1 = Monday
        .. 7 = Sunday).

        **Refusal policy.** A literal that names no week or no weekday resolves
        to ``None`` -- the construction simply does not fire -- rather than
        degrading to some wider reading.  ``2024-W53`` (2024 has only 52 ISO
        weeks), ``2024-W00``, ``2024-W99``, ``2024-W10-0`` and ``2024-W10-8``
        are all ``None``.  Returning the enclosing year for these would be a
        confidently wrong answer, which is worse than no answer at all.
        """
        raw = match.slots["ISOWEEK"].text
        # the week number is one or two digits (the standard pads it, real
        # writing often does not), so the parts are read by shape rather than
        # by fixed offsets into the literal.
        parts = _ISOWEEK_PARTS.fullmatch(raw)
        year, week = int(parts["year"]), int(parts["week"])
        weekday = parts["weekday"]
        if weekday:
            d = int(weekday)
            if not 1 <= d <= 7:
                return None
            day = date.fromisocalendar(year, week, d)   # ValueError -> None
            s = AstroDate.from_date(day)
            return Resolution(DateSpan(s, s + timedelta(days=1)),
                              self._consumed(match))
        monday = date.fromisocalendar(year, week, 1)    # ValueError -> None
        s = AstroDate.from_date(monday)
        return Resolution(DateSpan(s, s + timedelta(days=7)),
                          self._consumed(match))

    def _resolve_weekend_ref(self, match, anchor):
        """"this/next/last weekend": the two-day weekend of the anchor's
        week, shifted a whole week per the relative marker.  A two-day span
        starting at the locale's first weekend day (``weekend_start``,
        default Saturday; Friday for Israel and much of the Arab world).
        The two-day width reads as the weekend it names, not the seven-day
        week.
        """
        rel_tok = match.slots.get("REL_MARKER")
        rel = self.spec.rel_markers[rel_tok.text] if rel_tok is not None else 0
        base = _midnight(anchor)
        start_idx = _WEEK_START.get(self.conventions.week_start, 0)
        week_start = base - timedelta(days=(anchor.weekday() - start_idx) % 7)
        wknd_idx = self.conventions.weekend_start
        first = week_start + timedelta(days=(wknd_idx - start_idx) % 7)
        first = first + timedelta(weeks=rel)
        s = AstroDate.from_datetime(first)
        return Resolution(DateSpan(s, s + timedelta(days=2)),
                          self._consumed(match))

    def _resolve_weekend_of_month(self, match, anchor):
        """"the first/second/.../last weekend of <month> [year]": the Nth
        (or, with ``ordlast``, the last) weekend WITHIN that month -- the
        Saturday/Sunday pair whose Saturday (the locale's ``weekend_start``
        day) falls in the named month, reusing the same weekend-opens-the-day
        machinery as :meth:`_resolve_weekend_ref` / :meth:`_resolve_rel_span_weekend`
        (:func:`_nth_weekend_of_month`).

        The month's year follows the same anchor-relative rule as a bare
        month reference (``month_fuzzy``): an explicit YEAR wins; otherwise
        it is always the ANCHOR's year, never rolled forward or back to make
        the month "upcoming" -- "the first weekend of june" in December still
        names June of the anchor's own year.
        """
        ord_tok = match.slots.get("ORD")
        n = int(ord_tok.value) if ord_tok is not None else -1
        month = self.spec.months[match.slots["MONTH"].text]
        year_tok = match.slots.get("YEAR")
        era_tok = match.slots.get("ERA")
        if era_tok is not None and year_tok is None:
            # a stray era marker with no YEAR bound alongside it means the
            # number that should have been the year instead got swallowed by
            # a DIFFERENT slot (the YEAR slot's own >=32-or-4-digit floor
            # refuses a small year like "5" in "5 BC" -- see the ``YEAR``
            # slot's docstring in matcher.py) -- e.g. "5th january 5 BC"
            # with DAY consuming the second "5" and ERA left dangling on its
            # own. Composing a date here would silently substitute the
            # ANCHOR's year for the (unreadable) named one, exactly the
            # silent-wrong failure mode this fix exists to close, so this
            # reading is refused rather than guessed.
            return None
        if year_tok and era_tok is not None:
            # an era-qualified year ("the last weekend of june 500 BC")
            # composes through the same era registry the bare era_bc/era_ad
            # constructions use -- see the ``ERA`` slot's docstring.  Routed
            # through the AstroDate-native weekend finder since stdlib
            # ``date`` cannot represent a BC astronomical year at all.
            year = _year_with_era(year_tok, era_tok, self.spec)
            start = _nth_weekday_of_month_astro(
                year, month, self.conventions.weekend_start, n)
            if start is None:                         # no such Nth weekend
                return None
            return Resolution(DateSpan(start, start + timedelta(days=2)),
                              self._consumed(match))
        year = (_pivot_two_digit_year(year_tok, anchor.year) if year_tok
                else anchor.year)
        value = _nth_weekend_of_month(year, month,
                                      self.conventions.weekend_start, n)
        if value is None:                            # no such Nth weekend
            return None
        start = AstroDate.from_date(value)
        return Resolution(DateSpan(start, start + timedelta(days=2)),
                          self._consumed(match))

    def _resolve_calendar_date(self, match, anchor):
        month = self.spec.months[match.slots["MONTH"].text]
        day_tok = match.slots.get("DAY")
        year_tok = match.slots.get("YEAR")
        era_tok = match.slots.get("ERA")
        day = int(day_tok.value) if day_tok else 1
        prefer_future = self.spec.construction_flags.get(
            "calendar_date", {}).get("prefer_future", False)
        if era_tok is not None and year_tok is None:
            # a stray era marker with no YEAR bound alongside it: the number
            # that should have been the year instead got swallowed by DAY
            # (the YEAR slot's own >=32-or-4-digit floor refuses a small
            # year like "5" in "5 BC" -- see the ``YEAR`` slot's docstring in
            # matcher.py) -- e.g. "5th january 5 BC" with DAY consuming the
            # second "5" and ERA left dangling on its own. Composing a date
            # here would silently substitute the ANCHOR's year for the
            # (unreadable) named one, exactly the silent-wrong failure mode
            # this fix exists to close, so this reading is refused rather
            # than guessed.
            return None
        if year_tok and era_tok is not None:
            # an era-qualified year ("1st january 500 BC") composes through
            # the same era registry the bare era_bc/era_ad constructions use,
            # rather than reading "500" as the Gregorian year AD 500 and
            # stranding "BC" as remainder -- see the ``ERA`` slot's docstring.
            year = _year_with_era(year_tok, era_tok, self.spec)
            astro = AstroDate(year, month, day)     # raises on impossible
            span = DateSpan(astro, astro + timedelta(days=1)) if day_tok \
                else _gregorian_month_span(year, month)
            return Resolution(span, self._consumed(match))
        if year_tok:
            year = _pivot_two_digit_year(year_tok, anchor.year)
        else:
            year = anchor.year
        value = datetime(year, month, day)          # raises on impossible
        if not year_tok and prefer_future and day_tok \
                and value < _midnight(anchor):
            # The date exists in the anchor's year but has already passed, so
            # roll to its next occurrence.  Feb 29 is the only day that skips
            # years, so a naive .replace(year=year + 1) lands on a non-leap Feb
            # 29 and raises, discarding this valid answer entirely; walk forward
            # to the next year the (month, day) actually occurs instead, bounded
            # to one leap cycle (a century-boundary gap like 2096 -> 2104 is 8
            # years).  (A date that does not exist in the anchor year at all --
            # Feb 29 in a non-leap year, "the 30th of February" -- already
            # raised above and correctly declined to None; it is not rolled.)
            for y in range(year + 1, year + 9):
                try:
                    value = datetime(y, month, day)
                except ValueError:
                    continue
                year = y
                break
            else:
                return None
        span = _day_span(value) if day_tok \
            else _gregorian_month_span(year, month)
        return Resolution(span, self._consumed(match))

    def _resolve_reckoned_date(self, match, anchor):
        """Reckoned date over a registered calendar ("5 Tishrei 5785",
        "15 Sha'ban"): the unified family the design folds ``era_date`` and
        ``nongregorian_date`` into.  Resolved through JDN to a DateSpan --
        day-wide when a day is named, month-wide otherwise.
        """
        cal_key = match.calendar
        surface = match.slots["CAL_MONTH"].text
        month = self.spec.calendar_months[cal_key][surface]
        calendar = CALENDARS[cal_key]
        day_tok = match.slots.get("DAY")
        year_tok = match.slots.get("YEAR")
        day = int(day_tok.value) if day_tok else 1
        prefer_future = self.spec.construction_flags.get(
            match.construction, {}).get("prefer_future", False)
        anchor_jdn = gregorian_to_jdn(anchor.year, anchor.month, anchor.day)
        if year_tok:
            year = _pivot_two_digit_year(year_tok, anchor.year)
        else:
            year = calendar.from_jdn(anchor_jdn)[0]     # anchor's calendar year
        jdn = calendar.to_jdn(year, month, day)
        if not year_tok and prefer_future and day_tok and jdn < anchor_jdn:
            year += 1                                   # bump in calendar space
            jdn = calendar.to_jdn(year, month, day)
        if calendar.from_jdn(jdn) != (year, month, day):
            return None                                 # impossible day-in-month
        start = AstroDate(*jdn_to_gregorian(jdn))       # ValueError -> None
        if day_tok:
            span = DateSpan(start, start + timedelta(days=1))
        else:
            # month-wide: convert this month's first day AND next month's
            # first day through the calendar's own JDN hub, so the span tiles
            month_count = calendar.month_count
            nyear, nmonth = (year, month + 1) if month < month_count \
                else (year + 1, 1)
            end = AstroDate(*jdn_to_gregorian(calendar.to_jdn(nyear, nmonth, 1)))
            span = DateSpan(start, end)
        return Resolution(span, self._consumed(match))

    # ``nongregorian_date`` is the legacy construction name kept as an alias
    # for the unified ``reckoned_date`` family (zz/ar/he lang.json still use it)
    _resolve_nongregorian_date = _resolve_reckoned_date

    def _resolve_iso_date(self, match, anchor):
        """An ISO-8601 year-first literal: full date or day-less year-month.

        Three literal shapes reach this one resolver (all year-first, so
        component order is always Y-M-D, locale-independent):

        * ``YYYY-MM-DD`` / ``YYYY/MM/DD`` / ``YYYY.MM.DD`` (the Hungarian
          civil form) -> a **day-wide** span, exactly as the strict ISO date
          always did;
        * ``YYYY-MM`` (the ISO year-month, dash only) -> the **month-wide**
          span the named month occupies, reusing the same
          :func:`_gregorian_month_span` width "June 2027" and ``calendar_date``
          use.  A month outside 1..12 names no month, so "2024-13" resolves to
          ``None`` (the construction does not fire) rather than silently
          collapsing to the bare year.

        An impossible day ("2024/02/31") raises ``ValueError`` from
        ``AstroDate`` and :meth:`resolve` turns it into ``None``.
        """
        parts = re.split(r"[/.-]", match.slots["ISO"].text)
        if len(parts) == 2:                              # year-month, no day
            y, m = int(parts[0]), int(parts[1])
            if not 1 <= m <= 12:
                return None
            return Resolution(_gregorian_month_span(y, m),
                              self._consumed(match))
        y, m, d = (int(p) for p in parts)
        start = AstroDate(y, m, d)                       # ValueError -> None
        return Resolution(DateSpan(start, start + timedelta(days=1)),
                          self._consumed(match))

    def _resolve_numeric_date(self, match, anchor):
        """A numeric date ("12/11/2024", "5-6-24", "15.06.2020"), day-wide.

        The separator carries no meaning here -- slash, dash and the dotted
        continental form all reach this one resolver, and which of them a
        language writes is settled in the tokenizer.

        The two leading components map to day/month by the locale's ``dmy``
        convention: dmy=true reads day-first ("15/06/2024" = 15 June),
        dmy=false reads month-first ("06/15/2024" = 15 June via the swap
        below).  The year component is 4-digit as written, 2-digit through the
        POSIX ``%y`` pivot.

        Ambiguity guard: when the component the locale flag would read as the
        *month* exceeds 12 while the other is a valid month (<= 12), the two
        are swapped -- "13/12/2024" is unambiguously 13 December even in a
        month-first locale (this mirrors dateutil's dayfirst heuristic).  When
        both components are <= 12 ("01/02/03") the locale flag decides, no
        swap.  Any component that still names no real calendar date (month > 12,
        day 0, day-in-month impossible like 31/02) resolves to None rather than
        being fabricated -- ``AstroDate`` raises ``ValueError`` for the bad day.
        """
        # the dotted civil date may be written with a space after each dot
        # ("15. 6. 2020"); strip the separator's surrounding whitespace so each
        # component is bare digits and the two-digit year pivot still measures
        # length correctly.
        a, b, y = re.split(r"\s*[/.-]\s*", match.slots["NUMDATE"].text.strip())
        year = _pivot_year_str(y, anchor.year)
        first, second = int(a), int(b)
        if self.spec.conventions.dmy:
            day, month = first, second
        else:
            month, day = first, second
        # unambiguous swap: the flagged month can't be a month but the other
        # component is a valid one -> the surface must be day-first here
        if month > 12 and day <= 12:
            day, month = month, day
        if not 1 <= month <= 12:
            return None
        try:
            start = AstroDate(year, month, day)          # bad day -> ValueError
        except ValueError:
            return None
        return Resolution(DateSpan(start, start + timedelta(days=1)),
                          self._consumed(match))

    def _resolve_hebrew_new_year(self, match, anchor):
        """"the hebrew new year N": Rosh Hashanah of Hebrew year N -- 1 Tishrei
        (month 7 in the Nisan-first month numbering this calendar uses),
        day-wide, converted through the Hebrew calendar's JDN hub."""
        year = _pivot_two_digit_year(match.slots["YEAR"], anchor.year)
        cal = CALENDARS["hebrew"]
        start = AstroDate(*jdn_to_gregorian(cal.to_jdn(year, 7, 1)))
        return Resolution(DateSpan(start, start + timedelta(days=1)),
                          self._consumed(match))

    def _resolve_year_ref(self, match, anchor):
        """A bare calendar year ("2027", "in 1995", "the year 2000"): a
        year-wide span ``[Jan 1 y, Jan 1 y+1)``.  The GYEAR slot only binds a
        bare digit run inside the GYEAR window, so plain small integers never
        read as years.  A spelled "year NUM SCALE" ("the year twelve
        thousand") multiplies the NUM by its scale word -- safe here because
        the scale word is reserved for deep time only in the "... years ago"
        framing.

        The product is held to the same window the digit form is: a scale
        word carries any magnitude ("the year two billion"), and a year no
        digit numeral could name is not a year, so it resolves to nothing
        instead of to a span of the year 2000000000."""
        gyear = match.slots.get("GYEAR")
        smallyear = match.slots.get("SMALLYEAR")
        if gyear is not None:
            # an apostrophe two-digit GYEAR ("'99", "in '05") pivots through the
            # anchor-relative window; a full digit year is taken as written.
            year = (_window_two_digit_year(int(gyear.value), anchor.year)
                    if gyear.apostrophe
                    and len(gyear.raw.rstrip(".")) == 2 else int(gyear.value))
        elif smallyear is not None:
            # "in year 5"/"the year 5": an explicit year_word licenses a
            # small (< GYEAR_MIN) bare year as the absolute year N -- the
            # only alternative reading in play ("in a year" + a stranded
            # count) is never acceptable, so a below-window numeral bound to
            # year_word is taken literally rather than refused.
            year = int(smallyear.value)
        else:
            year = int(match.slots["NUM"].value) * self.spec.scales[
                match.slots["SCALE"].text]
            if not GYEAR_MIN <= year <= GYEAR_MAX:
                return None
        # Dual-calendar locales (fa) read a bare full-digit year on their
        # PRIMARY civil calendar, not literal Gregorian: contemporary Persian
        # "1402" is Solar-Hijri 1402 (2023-03-21..2024-03-21), never medieval
        # Gregorian 1402 AD.  The reading is bounded to the civil Solar-Hijri
        # window so Gregorian-scale years (e.g. "2024") stay Gregorian, and the
        # explicit میلادی/AD marker escapes through the separate era_ad
        # construction and is unaffected.  Apostrophe two-digit years never
        # take this path.
        flags = self.spec.construction_flags.get("year_ref", {})
        cal_key = flags.get("calendar")
        lo, hi = flags.get("calendar_year_range", (0, -1))
        if (cal_key and gyear is not None and not gyear.apostrophe
                and lo <= year <= hi):
            calendar = CALENDARS[cal_key]
            start = AstroDate(*jdn_to_gregorian(calendar.to_jdn(year, 1, 1)))
            end = AstroDate(*jdn_to_gregorian(calendar.to_jdn(year + 1, 1, 1)))
            span = DateSpan(start, end)
        else:
            span = DateSpan(AstroDate(year, 1, 1), AstroDate(year + 1, 1, 1))
        # An optional early/mid/late PART narrows the year to that third
        # ("late 2017"), the same span-native narrowing decade/month fuzzy use.
        part_tok = match.slots.get("PART")
        if part_tok is not None:
            from chronologia import subdivide
            span = subdivide(span, self.spec.period_parts[part_tok.text])
        return Resolution(DateSpan(span.start, span.end), self._consumed(match))

    def _decade_start(self, decade_tok, num_tok, anchor):
        """The Gregorian year a decade phrase begins on.

        Digit forms carry their own century: "1990s"/"2020s" -> that decade
        outright.  A bare tens ("the nineties", "the 90s") uses the
        *nearest-past* century convention -- the most recent decade with that
        tens digit that has already begun on the anchor date -- so in 2017
        "the twenties" is 1920 (2020 is still future) and "the nineties" is
        1990.  Returns None when the phrase names no whole-ten decade.
        """
        if decade_tok is not None:
            tens = self.spec.decade_words[decade_tok.text]
        else:
            n = int(num_tok.value)
            if n >= 1000:                       # explicit 4-digit decade
                return n - n % 10
            if n % 10 or not 0 <= n <= 90:      # a bare tens must be a multiple
                return None
            tens = n
        base = (anchor.year // 100) * 100 + tens
        return base - 100 if base > anchor.year else base

    def _resolve_decade_ref(self, match, anchor):
        """A decade span ("the 1990s", "the nineties", "the 90s"): ten years
        wide.  An optional early/mid/late PART slices it into thirds via
        :func:`chronologia.subdivide`, whose interior cuts are snapped to whole
        years (a decade is only decade-precise -- no fractional-day
        boundaries): early = first ~3 years, mid = middle ~4, late = last ~3
        ("the mid-2000s" -> 2003..2007)."""
        base = self._decade_start(match.slots.get("DECADE"),
                                  match.slots.get("NUM")
                                  or match.slots.get("DNUM"), anchor)
        if base is None:
            return None
        span = DateSpan(AstroDate(base, 1, 1), AstroDate(base + 10, 1, 1))
        part_tok = match.slots.get("PART")
        if part_tok is not None:
            from chronologia import subdivide
            span = subdivide(span, self.spec.period_parts[part_tok.text],
                             snap="year")
        return Resolution(DateSpan(span.start, span.end), self._consumed(match))

    def _resolve_month_fuzzy(self, match, anchor):
        """"early/mid/late <month>": the early/mid/late third of that month,
        sliced by :func:`chronologia.subdivide`.  An explicit trailing year
        ("early March 2019") places the third in THAT year; without one the
        month is the anchor year's."""
        from chronologia import subdivide
        month = self.spec.months[match.slots["MONTH"].text]
        part = self.spec.period_parts[match.slots["PART"].text]
        year_tok = match.slots.get("YEAR")
        year = (_pivot_two_digit_year(year_tok, anchor.year)
                if year_tok is not None else anchor.year)
        span = subdivide(_gregorian_month_span(year, month), part)
        return Resolution(DateSpan(span.start, span.end), self._consumed(match))

    def _resolve_month_day_ref(self, match, anchor):
        """"the first of the month" / "on the 3rd": the Nth day of the current
        month, rolled to next month when that day has already passed
        (prefer_future).  The bare-preposition orders ("on the 3rd", "by the
        5th") bind a *digit* day-of-month ordinal via the NORD slot; the
        "of month_word" order binds a general ORD."""
        ord_tok = match.slots.get("ORD") or match.slots["NORD"]
        day = int(ord_tok.value)
        rel_tok = match.slots.get("REL_MARKER")
        rel = self.spec.rel_markers[rel_tok.text] if rel_tok else 0
        base = _add_months(datetime(anchor.year, anchor.month, 1), rel)
        prefer_future = self.spec.construction_flags.get(
            "month_day_ref", {}).get("prefer_future", False)
        try:
            value = datetime(base.year, base.month, day)
        except ValueError:
            value = None                            # day absent in this month
        # an explicit this/next/last marker names the month outright; only the
        # bare "the Nth of the month" rolls forward -- to the next month that
        # actually HAS this day-of-month -- when the day is absent this month or
        # has already passed.  A blind +1-month _add_months would day-clamp ("the
        # 30th" past a Jan-31 anchor clamps Feb 30 -> Feb 28, silently
        # relabelling the day); walk forward instead (a 31st skips the short
        # months to the next long one).
        roll = rel == 0 and prefer_future and (
            value is None or value < _midnight(anchor))
        if roll:
            for step in range(1, 13):
                nxt = _add_months(datetime(base.year, base.month, 1), step)
                try:
                    value = datetime(nxt.year, nxt.month, day)
                    break
                except ValueError:
                    continue
            else:
                return None
        if value is None:                           # no roll and day is absent
            return None
        return Resolution(_day_span(value), self._consumed(match))

    #: scope-word kind -> that period's length in whole years.
    _HALF_SCOPES = {"decade": 10, "century": 100, "millennium": 1000}

    def _resolve_half_period(self, match, anchor):
        """"the first/second half of <period>": the calendar half of a year,
        decade, century or millennium -- or, over a NAMED MONTH, the
        arithmetic half of that month's span.  Year/decade/century/millennium
        halves are calendar-clean -- the year splits at July 1 (not the
        arithmetic mid-instant), a decade/century at its midpoint year -- so
        consecutive halves tile with no gap.  A month is short enough that no
        such rounding is needed (the same reasoning ``month_fuzzy``'s
        early/mid/late thirds already use): the month order below slices via
        :func:`chronologia.subdivide`'s exact elapsed-microsecond convention,
        so "the first half of august" (31 days) is Aug 1 .. Aug 16 12:00, and
        "the first half of february" is Feb 1 .. Feb 15 (28-day February) or
        Feb 1 .. Feb 15 12:00 (leap February, 29 days).

        ``ordlast`` ("last half of august", "last half of 2027") is a literal
        connector, not a slot -- it carries no token in ``match.slots`` the
        way the spelled ``NUM`` ordinal does, so its order's absence of
        ``NUM`` is itself the signal (mirrors ``_resolve_scoped_ordinal``'s
        ``ORD``-absent-means-``ordlast`` read): "last" selects the FINAL
        half, n=2, the same value "second" already spells out."""
        num_tok = match.slots.get("NUM")
        n = int(num_tok.value) if num_tok is not None else 2
        if n not in (1, 2):
            return None
        month_tok = match.slots.get("MONTH")
        if month_tok is not None:
            from chronologia import subdivide
            month = self.spec.months[month_tok.text]
            year_tok = match.slots.get("YEAR")
            era_tok = match.slots.get("ERA")
            if era_tok is not None and year_tok is None:
                # a stray era marker with no YEAR bound alongside it -- see
                # ``_resolve_calendar_date``'s identical guard: composing here
                # would silently substitute the anchor's year for the
                # (unreadable) named one, so this reading is refused rather
                # than guessed.
                return None
            if year_tok is not None and era_tok is not None:
                # an era-qualified year ("first half of august 44 BC")
                # composes through the same era registry the bare
                # era_bc/era_ad constructions and calendar_date/
                # weekend_of_month use -- see the ``ERA`` slot's docstring.
                year = _year_with_era(year_tok, era_tok, self.spec)
            else:
                year = (_pivot_two_digit_year(year_tok, anchor.year)
                        if year_tok is not None else anchor.year)
            part = "first_half" if n == 1 else "second_half"
            span = subdivide(_gregorian_month_span(year, month), part)
            return Resolution(DateSpan(span.start, span.end),
                              self._consumed(match))
        year_tok = match.slots.get("GYEAR")
        if year_tok is not None:
            # pivot a two-digit / apostrophe year ("the first half of '99")
            # through the anchor-relative window like the rest of the year
            # layer; reading it raw resolved to year 99 AD.
            y = _pivot_two_digit_year(year_tok, anchor.year)
            if n == 1:
                span = DateSpan(AstroDate(y, 1, 1), AstroDate(y, 7, 1))
            else:
                span = DateSpan(AstroDate(y, 7, 1), AstroDate(y + 1, 1, 1))
            return Resolution(span, self._consumed(match))
        length = self._HALF_SCOPES[self._scope_kind(match.slots["SCOPE_UNIT"])]
        base = (anchor.year // length) * length
        # a "this/next/last" marker shifts the scope one whole unit ("the first
        # half of NEXT century" is the coming century's first half); a bare
        # scope ("... of THE century") stays on the anchor's own.
        rel_tok = match.slots.get("REL_MARKER")
        if rel_tok is not None:
            base += self.spec.rel_markers[rel_tok.text] * length
        h = length // 2
        if n == 1:
            span = DateSpan(AstroDate(base, 1, 1), AstroDate(base + h, 1, 1))
        else:
            span = DateSpan(AstroDate(base + h, 1, 1),
                            AstroDate(base + length, 1, 1))
        return Resolution(span, self._consumed(match))

    _QUARTER_PARTS = {1: "first_quarter", 2: "second_quarter",
                      3: "third_quarter", 4: "fourth_quarter"}

    def _resolve_quarter_of_month(self, match, anchor):
        """"the first/second/third/fourth quarter of <month>": a quarter of a
        NAMED MONTH's span, sliced by :func:`chronologia.subdivide`'s exact
        elapsed-microsecond convention (the same one ``half_period``'s
        month order and ``month_fuzzy``'s thirds use).  Distinct from
        ``quarter_ref``'s calendar quarter of a YEAR ("the first quarter of
        2027") -- that construction binds ``YEAR``, this one binds ``MONTH``,
        so the two never compete for the same span.

        ``ordlast`` ("last quarter of august") is a literal connector, not a
        slot, so a match with no bound ``NUM`` came through that order --
        "last" selects the FINAL quarter of the month, n=4, the same value
        "fourth" already spells out.  Deliberately MONTH-only (see
        ``base_grammar.py``'s ``quarter_of_month`` comment): a GYEAR order
        would collide with ``quarter_ref``'s pre-existing "last quarter"
        anchor-relative reading, so that YEAR case is left untouched."""
        num_tok = match.slots.get("NUM")
        n = int(num_tok.value) if num_tok is not None else 4
        part = self._QUARTER_PARTS.get(n)
        if part is None:
            return None
        from chronologia import subdivide
        month = self.spec.months[match.slots["MONTH"].text]
        year_tok = match.slots.get("YEAR")
        era_tok = match.slots.get("ERA")
        if era_tok is not None and year_tok is None:
            # a stray era marker with no YEAR bound alongside it -- see
            # ``_resolve_calendar_date``'s identical guard.
            return None
        if year_tok is not None and era_tok is not None:
            # an era-qualified year ("third quarter of february 44 BC")
            # composes through the same era registry ``half_period``'s MONTH
            # order and calendar_date/weekend_of_month use.
            year = _year_with_era(year_tok, era_tok, self.spec)
        else:
            year = (_pivot_two_digit_year(year_tok, anchor.year)
                    if year_tok is not None else anchor.year)
        span = subdivide(_gregorian_month_span(year, month), part)
        return Resolution(DateSpan(span.start, span.end), self._consumed(match))

    # -- scoped_ordinal ----------------------------------------------------

    def _scope_kind(self, tok):
        return self.spec.scope_units.get(tok.text) or self.spec.units[tok.text]

    def _resolve_scoped_ordinal(self, match, anchor):
        """"Nth UNIT of SCOPE" nesting, absolute periods, last-ordinal (-1).

        Ports :func:`scoped_scan.extract_scoped_date` into the engine: the
        selected-unit width IS the span, resolved through
        :func:`ranges.get_date_ordinal` (reused verbatim, its scope/unit
        resolution tables imported).  Shapes are told apart by which slots
        the matcher bound:

        * ``ORD SCOPE_UNIT`` (no UNIT)              -> absolute period
          ("the 21st century");
        * ``ORD UNIT of SORD SCOPE_UNIT``           -> one nesting level
          ("the first decade of the 21st century");
        * ``ORD UNIT of MONTH [YEAR]``              -> month-scoped
          ("the 3rd week of june");
        * ``ORD UNIT of <year-word> [YEAR]``        -> year-scoped
          ("the 100th day of the year").

        ``last`` in place of the ordinal selects the final unit (-1).
        """
        ord_tok = match.slots.get("ORD")
        ntolast_tok = match.slots.get("NTOLAST")
        penult_tok = match.slots.get("PENULT")
        if penult_tok is not None:
            # "penultimate" -- a fixed synonym for "second-to-last" (-2).
            n = -2
        elif ntolast_tok is not None:
            # an "<ordinal> to last" / "next to last" idiom: ``ORD`` present
            # means "Nth-to-last" (-N), absent means the "next to last" idiom
            # (-2).  Bounded at -4 -- "fifth-to-last" and beyond refuse rather
            # than invent a reading past what the idiom is ever actually used
            # for.
            if ord_tok is not None:
                v = int(ord_tok.value)
                if not 2 <= v <= 4:
                    return None
                n = -v
            else:
                n = -2
        else:
            n = int(ord_tok.value) if ord_tok is not None else -1

        # A scoped-ordinal selection ("the Nth <unit> of ...") names ONE unit
        # and is grammatically SINGULAR in every language, so a PLURAL selected
        # unit is a bare COUNT, never the ordinal day-of-month the ORD slot
        # read.  The number fold collapses the spelled ordinal "second" and the
        # cardinal "two" to one token, so unit plurality is the only surviving
        # signal that "the two days of June" is a count, not "the 2nd day".
        # Refuse the reading (honest None, exactly as an out-of-range ordinal
        # already resolves) instead of fabricating June 2.  ``plural_units`` is
        # every unit surface a locale does NOT list as singular (from its
        # ``unit1_`` vocab), falling back to ``-s`` morphology for locales that
        # ship no such vocab; either way the singular "the second day", "the
        # third week", "the 100th day of the year" are never in it.
        sel_tok = (match.slots.get("UNIT") or match.slots.get("SEL_UNIT"))
        if sel_tok is not None and sel_tok.text in self.spec.plural_units:
            return None
        # The same collapse applies to the OUTER scope noun: "the 2nd century"
        # is a true ordinal, but "two centuries" folds its cardinal "two" to
        # the identical ORD token and must not be read as era index 2. A
        # plural SCOPE_UNIT ("decades"/"centuries") is a bare COUNT, never a
        # scoped-ordinal's singular scope noun, so it refuses the same way the
        # SEL_UNIT check above does; genuine offsets ("two centuries ago",
        # "in two decades") are unaffected -- they bind through
        # ``relative_offset``'s UNIT slot, not this construction's SCOPE_UNIT.
        scope_tok = match.slots.get("SCOPE_UNIT")
        if scope_tok is not None and scope_tok.text in self.spec.plural_units:
            return None

        wd_tok = match.slots.get("WEEKDAY")
        if wd_tok is not None:                      # nth weekday of a month
            target = self.spec.weekdays[wd_tok.text]
            month_tok = match.slots.get("MONTH")
            gyear_tok = match.slots.get("GYEAR")
            if month_tok is not None:               # named month ("... of June")
                month = self.spec.months[month_tok.text]
                year_tok = match.slots.get("YEAR")
                year = (_pivot_two_digit_year(year_tok, anchor.year) if year_tok
                        else anchor.year)
                value = _nth_weekday_of_month(year, month, target, n)
            elif gyear_tok is not None:              # bare year, no month:
                # "the first/last <weekday> of <YEAR>" -- the Nth (or, with
                # ``ordlast``, final) occurrence of that weekday WITHIN the
                # calendar year, not the month-scoped reading above. Without
                # this branch a bare trailing GYEAR is never bound here at
                # all (only "of MONTH of? YEAR?" binds a YEAR, and only
                # alongside a MONTH), so "last monday of 2026" fell through
                # to the anchor-relative ``weekday_ref`` ("last monday")
                # instead, silently stranding "of 2026" and answering
                # relative to the anchor year rather than the named one.
                year = int(gyear_tok.value)
                value = _nth_weekday_of_year(year, target, n)
            else:
                scope_tok = match.slots.get("SCOPE_UNIT")
                scope_kind = (self.spec.units.get(scope_tok.text)
                              if scope_tok is not None else None)
                if scope_kind == "month":
                    # "... of (the|this|next|last) month": the scope word
                    # names the anchor's own calendar month, shifted by an
                    # optional this/next/last marker, NOT a named month.
                    rel_tok = match.slots.get("REL_MARKER")
                    rel = self.spec.rel_markers[rel_tok.text] if rel_tok else 0
                    base = _add_months(_midnight(anchor).replace(day=1), rel)
                    year, month = base.year, base.month
                    value = _nth_weekday_of_month(year, month, target, n)
                elif scope_kind == "year":
                    # "the last monday of the year" / "of this year":
                    # sibling of the plain UNIT branch's ``scope_kind ==
                    # "year"`` case a few lines below. Before this branch
                    # existed the WEEKDAY resolver only ever recognised
                    # SCOPE_UNIT == "month" here and refused (returned None)
                    # for "of the year"/"of this year" -- a clean refusal
                    # rather than a silent-wrong answer, but one that should
                    # now resolve given the bare-GYEAR reading is established
                    # (this resolves within the anchor's own year,
                    # optionally shifted by this/next/last, same as the
                    # bare-GYEAR case resolving within the NAMED year).
                    rel_tok = match.slots.get("REL_MARKER")
                    rel = self.spec.rel_markers[rel_tok.text] if rel_tok else 0
                    year = anchor.year + rel
                    value = _nth_weekday_of_year(year, target, n)
                elif scope_tok is None:
                    # "the first/last <weekday> of the year_word", bare (no
                    # GYEAR, no SCOPE_UNIT bound at all) -- ``year_word`` is
                    # a literal connector, not a slot, so its presence is
                    # never recorded in ``match.slots``; but the only
                    # ``scoped_ordinal`` orders that bind WEEKDAY with none
                    # of MONTH/GYEAR/SCOPE_UNIT are the year_word orders
                    # added ("ORD WEEKDAY of? article? year_word
                    # GYEAR?" / "ORD WEEKDAY GYEAR? year_word" with the
                    # optional GYEAR absent), so reaching here already means
                    # the match was one of those. Bare year_word ("pierwszy
                    # poniedziałek roku", "ostatni poniedziałek roku") names
                    # the anchor's OWN calendar year -- consistent with the
                    # plain ``UNIT`` "year-scoped (year_word)" branch below,
                    # which likewise falls back to ``anchor.year`` with no
                    # explicit YEAR token. Without this branch these bare
                    # forms had no order binding WEEKDAY+year_word at all, so
                    # they fell through to the anchor-relative
                    # ``weekday_ref`` reading ("first/last monday"),
                    # stranding "roku"/"года".
                    value = _nth_weekday_of_year(anchor.year, target, n)
                else:                                # week/decade/... -> no fit
                    return None
            if value is None:                       # no such Nth weekday
                return None
            start = AstroDate.from_date(value)
            return Resolution(DateSpan(start, start + timedelta(days=1)),
                              self._consumed(match))

        sord = match.slots.get("SORD")
        if sord is not None:                        # nested one level
            unit_kind = self._scope_kind(match.slots["SEL_UNIT"])
            scope_kind = self._scope_kind(match.slots["SCOPE_UNIT"])
            scope_ref = get_date_ordinal(int(sord.value),
                                         resolution=_ABSOLUTE[scope_kind])
            table = (_UNIT_OF_CENTURY if scope_kind == "century"
                     else _UNIT_OF_MILLENNIUM)
            res = table[unit_kind]
            value = get_date_ordinal(n, scope_ref, res)
            return self._ordinal_result(value, unit_kind, match)

        unit_tok = match.slots.get("UNIT") or match.slots.get("DMUNIT")
        if unit_tok is None:                        # absolute period
            # SCOPE_UNIT (preposed "the 21st century") or CMUNIT (postposed
            # Romance "século XII") -- same absolute-period resolution
            kind = self._scope_kind(
                match.slots.get("SCOPE_UNIT") or match.slots["CMUNIT"])
            value = get_date_ordinal(n, resolution=_ABSOLUTE[kind])
            part_tok = match.slots.get("PART")
            if part_tok is not None:
                # "the mid-20th century": narrow the whole period to its
                # early/mid/late third, interior cuts snapped to whole years
                # (a century is only century-precise -- no fractional-day
                # boundaries).
                from chronologia import subdivide
                start = value if isinstance(value, AstroDate) \
                    else AstroDate.from_date(value)
                whole = DateSpan(start, _unit_end(start, kind))
                span = subdivide(whole, self.spec.period_parts[part_tok.text],
                                 snap="year")
                return Resolution(DateSpan(span.start, span.end),
                                  self._consumed(match))
            return self._ordinal_result(value, kind, match)

        unit_kind = self.spec.units[unit_tok.text]
        year_tok = match.slots.get("YEAR") or match.slots.get("GYEAR")
        year = _pivot_two_digit_year(year_tok, anchor.year) if year_tok else anchor.year
        month_tok = match.slots.get("MONTH")
        scope_tok = match.slots.get("SCOPE_UNIT")
        if month_tok is not None:                   # month-scoped (named month)
            month = self.spec.months[month_tok.text]
            res = _UNIT_OF_MONTH[unit_kind]
            value = get_date_ordinal(n, date(year, month, 1), res)
        elif scope_tok is not None:                 # anchor-relative period
            # "the last day of (the|this|next|last) month/year": the scope word
            # names the anchor's own calendar period, shifted by an optional
            # this/next/last marker, NOT a named month.
            scope_kind = self.spec.units.get(scope_tok.text)
            rel_tok = match.slots.get("REL_MARKER")
            rel = self.spec.rel_markers[rel_tok.text] if rel_tok else 0
            if scope_kind == "month":
                base = _add_months(_midnight(anchor).replace(day=1), rel)
                value = get_date_ordinal(n, date(base.year, base.month, 1),
                                         _UNIT_OF_MONTH[unit_kind])
            elif scope_kind == "year":
                value = get_date_ordinal(n, date(anchor.year + rel, 1, 1),
                                         _UNIT_OF_YEAR[unit_kind])
            else:                                   # week/decade/... -> no fit
                return None
        else:                                       # year-scoped (year_word)
            res = _UNIT_OF_YEAR[unit_kind]
            value = get_date_ordinal(n, date(year, 1, 1), res)
        return self._ordinal_result(value, unit_kind, match)

    def _ordinal_result(self, value, kind, match):
        start = value if isinstance(value, AstroDate) \
            else AstroDate.from_date(value)
        return Resolution(DateSpan(start, _unit_end(start, kind)),
                          self._consumed(match))

    # -- scoped period on an era axis ("the 3rd century bc", "2nd century ad")

    #: scope-word kind -> that period's length in whole years.  A scoped
    #: period ("century") is this many years wide on either axis.
    _SCOPE_YEARS = {"decade": 10, "century": 100, "millennium": 1000}

    def _resolve_scoped_ad(self, match, anchor):
        """"Nth SCOPE ad/ce": an explicit-AD scoped period.  Identical
        semantics to the plain absolute scoped period ("the 3rd century")
        -- the era marker only makes the AD axis explicit and consumes the
        marker token so it never leaks into the remainder."""
        n = int(match.slots["ORD"].value)
        kind = self._scope_kind(match.slots["SCOPE_UNIT"])
        value = get_date_ordinal(n, resolution=_ABSOLUTE[kind])
        part_tok = match.slots.get("PART")
        if part_tok is not None:                    # "the mid 3rd century AD"
            return self._scoped_part(value, kind, part_tok, match)
        return self._ordinal_result(value, kind, match)

    def _scoped_part(self, value, kind, part_tok, match):
        """Narrow an absolute scoped period to its early/mid/late third,
        interior cuts snapped to whole years (shared by the AD and BC axes)."""
        from chronologia import subdivide
        start = value if isinstance(value, AstroDate) \
            else AstroDate.from_date(value)
        whole = DateSpan(start, _unit_end(start, kind))
        span = subdivide(whole, self.spec.period_parts[part_tok.text],
                         snap="year")
        return Resolution(DateSpan(span.start, span.end), self._consumed(match))

    def _resolve_scoped_bc(self, match, anchor):
        """"Nth SCOPE bc/bce": a scoped period on the *BC axis*.

        The nth century BC spans the BC years ``(n-1)*100+1 .. n*100`` -- e.g.
        the 3rd century BC is 300 BC..201 BC, astronomically ``[-299, -199)``.
        Both edges are derived through the era registry (``before_christ``,
        which counts years backwards from AD 1): the older edge is the
        ``n*length``-th BC year, the younger edge the ``(n-1)*length``-th (the
        first year already in the next, more-recent period), so consecutive
        periods tile with no gap.  The span is one whole ``length`` wide.
        """
        from chronologia import resolve_era
        n = int(match.slots["ORD"].value)
        kind = self._scope_kind(match.slots["SCOPE_UNIT"])
        length = self._SCOPE_YEARS[kind]
        start = self._as_astro(resolve_era("before_christ", length * n))
        end = self._as_astro(resolve_era("before_christ", length * (n - 1)))
        part_tok = match.slots.get("PART")
        if part_tok is not None:                    # "the early 5th century BC"
            from chronologia import subdivide
            # "early" is chronologically-first (the oldest years); subdivide by
            # wall-time gives that -- the earlier third sits at the span start.
            span = subdivide(DateSpan(start, end),
                             self.spec.period_parts[part_tok.text], snap="year")
            return Resolution(DateSpan(span.start, span.end),
                              self._consumed(match))
        return Resolution(DateSpan(start, end), self._consumed(match))

    def _resolve_decade_bc(self, match, anchor):
        """"the 300s bc" / "os anos 300 ac": a *base-number* decade on the BC
        axis.

        Unlike the ordinal ``scoped_bc`` decade ("the 2nd decade bc", counting
        1st/2nd/... decade back from AD 1), this names a decade by its base
        year the way an AD decade does ("the 1990s"): the BC-labelled years
        ``N .. N+9`` -- the "three-hundreds BC" are 309..300 BC.

        Convention (documented, tiled with ``scoped_bc``): both edges are
        derived through the same ``before_christ`` era registry ``scoped_bc``
        uses for its century boundaries, so the two families agree on where a
        BC year sits.  The older edge (span start) is the ``(N+9)``-th BC year;
        the younger edge (span end, exclusive) is the ``(N-1)``-th BC year --
        the first year already in the next, more-recent decade -- so
        consecutive decades tile with no gap.  In astronomical numbering
        (``X`` BC == year ``1 - X``): "the 300s bc" -> ``[-308, -298)``, "the
        290s bc" -> ``[-298, -288)``.  ``N`` must be a positive whole ten;
        anything else does not name a decade and the construction does not
        fire.
        """
        from chronologia import resolve_era
        n = int(match.slots["NUM"].value)
        if n < 10 or n % 10:
            return None
        start = self._as_astro(resolve_era("before_christ", n + 9))
        end = self._as_astro(resolve_era("before_christ", n - 1))
        return Resolution(DateSpan(start, end), self._consumed(match))

    @staticmethod
    def _as_astro(d) -> AstroDate:
        return d if isinstance(d, AstroDate) else AstroDate.from_date(d)

    # -- regnal_date -------------------------------------------------------

    def _resolve_regnal_date(self, match, anchor):
        """"<era-name> N" / "the Nth year of <era-name>" -> the Gregorian year
        span that regnal year occupies inside its reign segment.

        Delegates to :class:`~chronologia.regnal.RegnalSequence`, which
        clamps the year to the segment (Reiwa 1 begins at the 2019 accession,
        the last year of a closed era ends at the successor's accession).
        """
        seqkey, segname = self.spec.regnal_names[match.slots["ERANAME"].text]
        seq = REGNAL_SEQUENCES[seqkey]
        num_tok = match.slots.get("NUM") or match.slots.get("ORD")
        n = int(num_tok.value) if num_tok is not None else 1   # bare eponym
        span = seq.year_span(segname, n)
        if span is None:
            return None
        # an adjacent calendar month ("Reiwa 2 May") narrows the reign-year
        # span to that Gregorian month of the resolved year, the same
        # named-month binding "May 2020" uses.
        narrowed = self._narrow_to_month(DateSpan(*span), match)
        return Resolution(narrowed, self._consumed(match))

    # -- roman_date (Kalends / Nones / Ides) -------------------------------

    def _resolve_roman_date(self, match, anchor):
        """"a.d. III Kal. Apr." / "pridie Idus Martias" / "Idibus Martiis":
        inclusive backward counting from a monthly anchor, over the Julian
        calendar (see :mod:`chronologia.roman`).  Day-wide span; the
        ordinal-beyond-the-span case yields ``None``.
        """
        anchor_name = self.spec.roman_anchors[match.slots["ANCHOR_DAY"].text]
        month = self.spec.months[match.slots["MONTH"].text]
        if "ORD" in match.slots:
            count = int(match.slots["ORD"].value)
        elif "PRIDIE" in match.slots:
            count = 2
        else:
            count = 1                       # bare ablative: the anchor day
        ymd = roman_to_julian(anchor.year, month, anchor_name, count)
        if ymd is None:
            return None
        start = AstroDate(*ymd)             # Julian-calendar labels
        return Resolution(DateSpan(start, start + timedelta(days=1)),
                          self._consumed(match))

    def _resolve_archon_ref(self, match, anchor):
        """"in the archonship of Eucleides": the midsummer-to-midsummer span of
        that eponymous archon-year (403/402 BC), from the attested Attic archon
        table (:data:`chronologia.archons.ARCHONS`)."""
        from chronologia.archons import ARCHONS
        key = self.spec.archon_names[match.slots["ARCHON"].text]
        start, end = ARCHONS[key]
        return Resolution(DateSpan(start, end), self._consumed(match))

    def _resolve_roman_classical(self, match, anchor):
        """Raw-Latin date formula ("ante diem III kalends of april"): the same
        inclusive-backward reckoning as :meth:`_resolve_roman_date`, exposed as
        a separate construction so the ``classical`` group flag can gate it OFF
        by default (the a.d.-count Latin surface is opt-in)."""
        return self._resolve_roman_date(match, anchor)

    # -- cycle_ref (generalised weekday over any named day cycle) ----------

    def _resolve_cycle_ref(self, match, anchor):
        """"next/last/this <cycle-day>" over an arbitrary named day cycle.

        The generalisation of ``weekday_ref``: the seven-day week is just the
        ``week`` cycle, so a bare-week query here lands the identical day the
        legacy weekday path returns.  Also resolves the French Republican
        décade (month-anchored) and the Roman nundinal cycle (free-running).
        Day-wide span; midnight of the resolved day.
        """
        surface = match.slots["CYCLE_DAY"].text
        cycle = DAY_CYCLES[self.spec.day_cycles[surface]]
        position = self.spec.cycle_positions[surface]
        rel_tok = match.slots.get("REL_MARKER")
        rel = self.spec.rel_markers[rel_tok.text] if rel_tok is not None else 0
        anchor_jdn = gregorian_to_jdn(anchor.year, anchor.month, anchor.day)
        target = resolve_cycle_day(cycle, position, rel, anchor_jdn)
        if target is None:
            return None
        start = AstroDate(*jdn_to_gregorian(target))
        return Resolution(DateSpan(start, start + timedelta(days=1)),
                          self._consumed(match))

    # -- season_ref --------------------------------------------------------

    def _resolve_season_ref(self, match, anchor):
        """Hemisphere-aware meteorological season, next/last/this, "of YYYY".

        Ports the season handling of :func:`scoped_scan.extract_scoped_date`
        into the engine, reusing ``ranges``'s season tables.  The width is a
        fixed **three months** (the meteorological season length) from the
        season's first day; the hemisphere is the language's ``hemisphere``
        convention (a fact), so the same vocabulary resolves correctly north
        and south of the equator.

        The ``this``/``last``/``next`` markers are read against the season
        the anchor falls in, not against the calendar year: a speaker inside
        a season means that season by "this", the one already over by
        "last", and the one still to begin by "next".
        """
        season = Season[self.spec.seasons[match.slots["SEASON"].text].upper()]
        hemi = (Hemisphere.SOUTH if self.conventions.hemisphere == "south"
                else Hemisphere.NORTH)
        ref = anchor.date()
        year_tok = match.slots.get("YEAR")
        rel_tok = match.slots.get("REL_MARKER")
        if year_tok is not None:
            start = season_to_date(season,
                                   _pivot_two_digit_year(year_tok, anchor.year), hemi)
        elif rel_tok is not None and self.spec.rel_markers[rel_tok.text] > 0:
            start = next_season_date(season, ref, hemi)
        elif rel_tok is not None and self.spec.rel_markers[rel_tok.text] < 0:
            start = last_season_date(season, ref, hemi)
        else:                                       # this / bare
            start = current_season_date(season, ref, hemi)
        start_dt = datetime(start.year, start.month, start.day)
        span_start = AstroDate.from_datetime(start_dt)
        end = AstroDate.from_datetime(_add_months(start_dt, 3))
        return Resolution(DateSpan(span_start, end), self._consumed(match))

    def _resolve_season_fuzzy(self, match, anchor):
        """"early/mid/late <season> [year]": the early/mid/late third of
        that season's 3-month span, sliced by :func:`chronologia.subdivide`.

        Sibling of ``_resolve_month_fuzzy`` over a ``SEASON`` instead of a
        ``MONTH``: an explicit trailing ``YEAR`` ("early spring 2027") places
        the third in THAT year's season; without one the season is the one
        the anchor currently falls in (the same deictic "bare season" rule
        ``_resolve_season_ref`` uses for its own bare form -- there is no
        REL_MARKER slot on this construction, so "early"/"mid"/"late" is
        always read against the CURRENT season, never "next"/"last").
        """
        from chronologia import subdivide
        season = Season[self.spec.seasons[match.slots["SEASON"].text].upper()]
        part = self.spec.period_parts[match.slots["PART"].text]
        hemi = (Hemisphere.SOUTH if self.conventions.hemisphere == "south"
                else Hemisphere.NORTH)
        year_tok = match.slots.get("YEAR")
        if year_tok is not None:
            start = season_to_date(season,
                                   _pivot_two_digit_year(year_tok, anchor.year), hemi)
        else:
            start = current_season_date(season, anchor.date(), hemi)
        start_dt = datetime(start.year, start.month, start.day)
        season_span = DateSpan(AstroDate.from_datetime(start_dt),
                               AstroDate.from_datetime(_add_months(start_dt, 3)))
        span = subdivide(season_span, part)
        return Resolution(DateSpan(span.start, span.end), self._consumed(match))

    # -- solar_event (equinoxes / solstices) -------------------------------

    _MONTH_CARDINAL = {3: "march", 6: "june", 9: "september", 12: "december"}

    def _resolve_solar_event(self, match, anchor):
        """"the summer solstice", "vernal equinox 2017", "march equinox 2000".

        A season-qualified (or month-named) equinox/solstice resolves to the
        astronomical event's civil DAY, computed by the Meeus ch.27 machinery
        in :mod:`chronologia.equinoxes` -- a location-independent instant,
        unlike sunrise/sunset (which need coordinates and are unsupported).
        The whole-day span mirrors a single-day holiday; the minute-level
        instant precision is documented in ``chronologia.equinoxes``.

        The qualifier names which of the four cardinal events is meant.  A
        season word ("summer") is read hemisphere-aware, exactly as
        ``season_ref`` is: the event that OPENS that astronomical season (north
        summer -> June solstice, south summer -> December solstice).  The formal
        names "vernal"/"autumnal" (SOLARQUAL) map to spring/autumn; a month name
        ("June solstice", "March equinox") names its cardinal event directly.
        A pairing whose event word contradicts its qualifier ("summer equinox")
        does not resolve.

        Which year:

        * an explicit ``YEAR`` slot -> that year;
        * bare (no year) -> the next occurrence ON OR AFTER the anchor date,
          exactly as a bare holiday: from an anchor past the June solstice,
          "the summer solstice" is next year's.

        A BARE "the solstice"/"the equinox" with no qualifier does not match
        this construction at all (no order lacks the qualifier), so it stays
        unresolved -- the event is ambiguous between the two solstices/equinoxes.
        """
        from chronologia.equinoxes import (CARDINAL_KIND, equinox_instant,
                                           season_cardinal)
        kind = self.spec.solar_events[match.slots["EVENT"].text]
        hemi = ("south" if self.conventions.hemisphere == "south"
                else "north")
        month_tok = match.slots.get("MONTH")
        if month_tok is not None:
            which = self._MONTH_CARDINAL.get(self.spec.months[month_tok.text])
            if which is None:
                return None
        else:
            qual_tok = match.slots.get("SEASON")
            if qual_tok is not None:
                season = self.spec.seasons[qual_tok.text]
            else:
                season = self.spec.solar_quals[match.slots["SOLARQUAL"].text]
            which = season_cardinal(season, hemi)
        if CARDINAL_KIND[which] != kind:
            return None
        year_tok = match.slots.get("YEAR")
        if year_tok is not None:
            year = _pivot_two_digit_year(year_tok, anchor.year)
        else:
            ref = anchor.date()
            inst = equinox_instant(ref.year, which)
            year = (ref.year if date(inst.year, inst.month, inst.day) >= ref
                    else ref.year + 1)
        inst = equinox_instant(year, which)
        return Resolution(_day_span(datetime(inst.year, inst.month, inst.day)),
                          self._consumed(match))

    # -- era_date family (BC / AD / before-present), year-wide -------------

    def _era_span(self, era, n):
        from chronologia import resolve_era
        from chronologia.eras import ERAS, Era, resolve_era_year_span
        era_obj = era if isinstance(era, Era) else ERAS[era]
        if era_obj.calendar:
            # A CALENDAR-BACKED era (Anno Mundi numbers the Hebrew calendar's
            # own, variable-length years) does NOT start its next year on the
            # same Gregorian month/day one year later, so a naive +1 Gregorian
            # year gives a span that is days too long.  Advance the NATIVE
            # calendar year through the JDN hub instead (calendar-exact).
            start, end = resolve_era_year_span(era_obj, n)
            return DateSpan(start, end)
        # a plain offset era (BC/AD, BP, Saka, Holocene, Buddhist, AUC) steps
        # exactly one Gregorian year.
        d = resolve_era(era, n)
        start = d if isinstance(d, AstroDate) else AstroDate.from_date(d)
        end = AstroDate(start.year + 1, start.month, start.day)
        return DateSpan(start, end)

    def _resolve_era_bc(self, match, anchor):
        n = int(match.slots["NUM"].value)
        return Resolution(self._era_span("before_christ", n),
                          self._consumed(match))

    def _resolve_era_ad(self, match, anchor):
        n = int(match.slots["NUM"].value)
        return Resolution(self._era_span("common_era", n),
                          self._consumed(match))

    def _resolve_era_bp(self, match, anchor):
        n = int(match.slots["NUM"].value)
        return Resolution(self._era_span("before_present", n),
                          self._consumed(match))

    def _resolve_era_auc(self, match, anchor):
        """"753 ab urbe condita" / "AUC 753": the year-wide Gregorian span of
        that ab-urbe-condita year, Varronian epoch (AUC 1 == 753 BC)."""
        n = int((match.slots.get("NUM") or match.slots.get("ORD")).value)
        return Resolution(self._era_span("ab_urbe_condita", n),
                          self._consumed(match))

    def _resolve_era_saka(self, match, anchor):
        """"in Saka 1900": the Gregorian year-span of that Saka year, resolved
        through the era registry's epoch (Saka 1 == AD 78), so the epoch offset
        is applied instead of reading the literal number as a Gregorian year."""
        n = int(match.slots["NUM"].value)
        return Resolution(self._era_span("saka", n), self._consumed(match))

    def _resolve_era_byzantine(self, match, anchor):
        """"the year 6260 of the Byzantine era": the Byzantine (Creation) Anno
        Mundi year, resolved through its epoch (AM 1 == 5509 BC), not the
        literal number."""
        n = int(match.slots["NUM"].value)
        return Resolution(self._era_span("byzantine_am", n),
                          self._consumed(match))

    def _resolve_era_holocene(self, match, anchor):
        """"the Holocene year 12026": the Human/Holocene Era year (HE == CE +
        10000), resolved through the registry to its CE year."""
        n = int(match.slots["NUM"].value)
        return Resolution(self._era_span("holocene", n), self._consumed(match))

    def _resolve_era_anno_mundi(self, match, anchor):
        """"anno mundi 5786": the (Hebrew) Anno Mundi / year-of-Creation year,
        resolved through its epoch (AM 1 == 3761 BC, the Hebrew calendar's
        Tishrei-based year), not the literal number."""
        n = int(match.slots["NUM"].value)
        return Resolution(self._era_span("anno_mundi", n),
                          self._consumed(match))

    def _resolve_era_buddhist(self, match, anchor):
        """"Buddhist Era 2560" / "2560 BE": the Gregorian year-span of that
        Buddhist-Era year, resolved through the registry's epoch (BE == CE +
        543, so BE 2560 == AD 2017), not the literal number.  An adjacent
        calendar month ("Buddhist Era 2560 May") narrows the span to that
        month of the resolved Gregorian year (see :meth:`_narrow_to_month`)."""
        n = int(match.slots["NUM"].value)
        span = self._era_span("buddhist", n)
        return Resolution(self._narrow_to_month(span, match),
                          self._consumed(match))

    def _resolve_era_buddhist_be(self, match, anchor):
        """"2540 BE": the bare "BE" Buddhist-Era abbreviation, wired SUFFIX-ONLY
        (``NUM be``, never ``be NUM``).  "be" is a common English verb, so a
        prefix order would misfire on "there will be 3 dogs"; requiring the year
        to PRECEDE the marker keeps the surface adjacent-to-year, exactly as the
        spelled ``buddhist`` form does.  Resolves through the same BE epoch
        (BE == CE + 543, so BE 2540 == 1997 CE)."""
        n = int(match.slots["NUM"].value)
        span = self._era_span("buddhist", n)
        return Resolution(self._narrow_to_month(span, match),
                          self._consumed(match))

    def _resolve_era_hijri(self, match, anchor):
        """"1447 AH" / "AH 1447" / "Anno Hegirae 1447": the Gregorian year-span
        of that Islamic (lunar) Hijri year, resolved through the registry's
        epoch (AH 1 == 622-07-19, the tabular civil-Hijri calendar), never the
        literal number read as a Gregorian year.  Calendar-backed, so the span
        advances the native Hijri year (not a naive +1 Gregorian year)."""
        n = int(match.slots["NUM"].value)
        span = self._era_span("hijri", n)
        return Resolution(self._narrow_to_month(span, match),
                          self._consumed(match))

    def _resolve_era_solar_hijri(self, match, anchor):
        """"1404 Solar Hijri" / "S.H. 1404": the Gregorian year-span of that
        Iranian Solar Hijri (Jalali) year, resolved through the registry's
        epoch (SH 1 == 622-03-21, vernal-equinox Nowruz), not the literal
        number.  Calendar-backed, so the span advances the native solar year."""
        n = int(match.slots["NUM"].value)
        span = self._era_span("solar_hijri", n)
        return Resolution(self._narrow_to_month(span, match),
                          self._consumed(match))

    def _narrow_to_month(self, span, match):
        """Narrow a whole-year era span to a single month when the match
        carries a MONTH slot; otherwise return the year span unchanged.  The
        month is the same named-month binding a plain "May 2020" uses -- the
        Gregorian month of the era-resolved year."""
        month_tok = match.slots.get("MONTH")
        if month_tok is None:
            return span
        month = self.spec.months[month_tok.text]
        return _gregorian_month_span(span.start.year, month)

    def _resolve_roman_eve(self, match, anchor):
        """"the eve of the Ides of March": the day before a Roman-anchor date.
        Reuses the Roman-anchor resolution, then steps one whole day back --
        the same -1-day offset the holiday eve applies."""
        roman = self._resolve_roman_date(match, anchor)
        if roman is None:
            return None
        span = roman.value
        return Resolution(
            DateSpan(span.start - timedelta(days=1),
                     span.end - timedelta(days=1)),
            self._consumed(match))

    def _resolve_olympiad_ref(self, match, anchor):
        """"the third olympiad" / "olympiad 87": the 4-year span of Olympiad N
        from the 776 BC epoch.  An optional inner ORD ("the 2nd year of the
        87th olympiad") narrows the span to that single year of the tetrad.
        """
        from chronologia.eras import resolve_era_year_span
        onum = match.slots.get("ORD") or match.slots.get("NUM")
        n = int(onum.value)
        start, end = resolve_era_year_span("olympiad", n)
        year_tok = match.slots.get("SORD")   # inner "Nth year of" ordinal
        if year_tok is not None:
            # year k of the 4-year Olympiad (1..4): the single year span
            k = int(year_tok.value)
            if not 1 <= k <= 4:
                return None
            start = AstroDate(start.year + k - 1, start.month, start.day)
            end = AstroDate(start.year + 1, start.month, start.day)
        return Resolution(DateSpan(start, end), self._consumed(match))

    # -- deep_time ("66 million years ago", "4.5 billion years ago") ------

    #: scale multiplier -> chronologia SI-prefixed Before-Present unit.  The
    #: sig-fig precision rule lives *at the spoken unit*: "66 million" is
    #: 1-Ma-wide (one place of the "66"), not year-precise, so the value
    #: string and its scale unit -- not the pre-multiplied year count -- are
    #: what :func:`chronologia.resolve_bp` must see.
    _BP_SCALE_UNITS = {1_000: "ka", 1_000_000: "Ma", 1_000_000_000: "Ga"}

    def _resolve_deep_time(self, match, anchor, scale_mode="short"):
        """Numeric deep time via the radiocarbon before-present convention.

        The value is ``NUM x SCALE`` years before present (1950).  The span's
        width is the *referential precision* read off the spoken value's last
        significant digit at its scale unit: "66 million" -> 1 Ma wide, "66.5
        million" -> 100 ka, "4.5 billion" -> 100 Ma.  We route the untouched
        value **string** and the SI unit through :func:`chronologia.resolve_bp`
        so the sig-fig rule applies before value x scale collapses to years.
        """
        from chronologia import resolve_bp
        num = match.slots["NUM"]
        factor = self._scale_factor(match.slots["SCALE"].text, scale_mode)
        if num.article:
            # the indefinite-article form ("a million years ago") is a
            # colloquial count-from-now offset, not a geological measurement:
            # a single-year point at ``anchor.year - count*scale``, never the
            # numeral form's sig-fig span.
            year = anchor.year - int(num.value) * factor
            start = AstroDate(year, anchor.month, anchor.day,
                              anchor.hour, anchor.minute)
            end = AstroDate(year + 1, anchor.month, anchor.day,
                            anchor.hour, anchor.minute)
            return Resolution(DateSpan(start, end), self._consumed(match))
        unit = self._BP_SCALE_UNITS.get(factor)
        if unit is not None:
            span = resolve_bp(num.text, unit)
        else:  # scale word with no SI unit (e.g. "hundred"): fall back to years
            span = resolve_bp(num.value * factor, "a")
        return Resolution(DateSpan(span.start, span.end), self._consumed(match))

    # -- named_period ("during the jurassic", "the late cretaceous") ------

    def _resolve_named_period(self, match, anchor):
        from chronologia import PERIODS, subdivide
        key = self.spec.periods[match.slots["PERIOD"].text]
        period = PERIODS[key]
        part_tok = match.slots.get("PART")
        if part_tok is not None:
            span = subdivide(period, self.spec.period_parts[part_tok.text])
        else:
            span = period.span
        return Resolution(DateSpan(span.start, span.end), self._consumed(match))

    # -- holiday_ref -------------------------------------------------------

    def _resolve_holiday_ref(self, match, anchor):
        """"christmas" / "when is easter" / "next christmas" / "last easter" /
        "natal 2020" -> the holiday's own :class:`DateSpan`.

        The surface names a globally well-known holiday (``spec.holidays`` maps
        it to a stable key); the date is produced by that holiday's canonical
        rule in :data:`chronologia.civil_holidays.WELL_KNOWN` — a movable
        holiday (easter and its cycle) still resolves through the computus
        engine, never re-derived here.  Which *year*'s occurrence is chosen:

        * an explicit ``YEAR`` slot -> that year;
        * a ``next`` marker -> the strictly-future next occurrence;
        * a ``last`` marker -> the most recent strictly-past occurrence;
        * a ``this`` marker -> this anchor year's occurrence;
        * bare (no marker) -> the next occurrence **on or after** the anchor
          date (so on Christmas Day itself, "christmas" is that very day; the
          day after, it is next year's).

        The result carries the holiday's own span shape (whole-day, or half-day
        where the rule is a half-day).
        """
        from chronologia.civil_holidays import (JURISDICTION_KNOWN_BY_KEY_LANG,
                                                 WELL_KNOWN_BY_KEY)
        key = self.spec.holidays.get(match.slots["HOLIDAY"].text)
        wk = WELL_KNOWN_BY_KEY.get(key) if key is not None else None
        if wk is None and key is not None:
            # Second tier: the rule is chosen by the locale's jurisdiction
            # default (mother's/father's day differ by country).
            wk = JURISDICTION_KNOWN_BY_KEY_LANG.get((key, self.spec.lang))
        if wk is None:
            return None
        year_tok = match.slots.get("YEAR")
        rel_tok = match.slots.get("REL_MARKER")
        if year_tok is not None:
            year = _pivot_two_digit_year(year_tok, anchor.year)
        else:
            rel = (self.spec.rel_markers[rel_tok.text]
                   if rel_tok is not None else None)
            year = self._holiday_year(wk, anchor.date(), rel)
            if year is None:
                return None
        got = wk.span_for(year)
        if got is None:
            return None
        span, _basis = got
        return Resolution(DateSpan(span.start, span.end), self._consumed(match))

    def _resolve_new_year_ref(self, match, anchor):
        """Bare "new year" / "new years" -> New Year's Day (Jan 1), the
        occurrence on or after the anchor date -- the same choice a bare
        holiday reference makes.

        Kept a construction of its own (order ``new year_word``) rather than a
        multiword holiday surface: folding "new year" into a single token would
        shadow :meth:`_resolve_hebrew_new_year` ("the hebrew new year 5786"),
        whose grammar needs "new" and "year" as SEPARATE slots.  Wiring it here
        makes ``extract_candidates``, ``extract_timespan`` and phrase
        composition ("new year party") all agree on the same reading, instead
        of only the whole-utterance fast path resolving it.

        The DEFINITE-ARTICLE form ("the new year") is deliberately NOT this
        holiday -- it is the ambiguous "coming year" period.  The order carries
        no ``article`` slot, so "the" is never folded in; a leading "the" is
        vetoed by :func:`_new_year_definite_article_veto` in both public APIs.
        """
        from chronologia.extract.timespan import _new_year_span
        # an explicit year ("new year 2030", "new year in 2027") names THAT
        # year's Jan 1, not the prefer-future occurrence -- bind and pivot it
        # like hebrew_new_year does, instead of dropping it to the remainder.
        year_tok = match.slots.get("YEARANY")
        if year_tok is not None:
            y = _pivot_two_digit_year(year_tok, anchor.year)
            start = AstroDate(y, 1, 1)          # New Year's DAY of that year,
            return Resolution(DateSpan(start, start + timedelta(days=1)),  # day-wide
                              self._consumed(match))
        return Resolution(_new_year_span(anchor), self._consumed(match))

    @staticmethod
    def _holiday_year(wk, anchor_date, rel):
        """The Gregorian year of the occurrence selected by ``rel`` (or bare).

        ``rel`` is None (bare, on-or-after), +1 (next, strictly future), -1
        (last, strictly past) or 0 (this year).
        """
        def occ(y):
            got = wk.date_for(y)
            if got is None:
                return None
            d = got[0]
            return date(d.year, d.month, d.day)

        y = anchor_date.year
        this_year = occ(y)
        if this_year is None:
            return None
        if rel is None:                       # bare: next on-or-after anchor
            return y if this_year >= anchor_date else y + 1
        if rel > 0:                           # next: strictly future
            return y if this_year > anchor_date else y + 1
        if rel < 0:                           # last: most recent strictly past
            return y if this_year < anchor_date else y - 1
        return y                              # this: this anchor year

    # -- clock_time --------------------------------------------------------

    def _resolve_clock_time(self, match, anchor):
        """Resolve a clock reference to a **minute-wide** span anchored on the
        resolved-or-anchor date.

        Three shapes, distinguished by which slots the matcher bound:

        * ``CLOCK`` -- a ``HH:MM[:SS]`` digit literal, taken verbatim;
        * ``FRACTION CLOCKDIR HOUR`` -- "half past ten", "quarter to five":
          the fraction's minutes are added on the *past* side and subtracted
          (rolling the hour back one) on the *to* side;
        * bare ``HOUR`` (from "at ten", "ten o'clock") -- minute 0.

        An optional ``MERIDIEM`` slot applies the language's am/pm policy
        (12h -> 24h).  ``prefer_future`` (a construction fact) rolls a time
        already past on the anchor day to the next day.
        """
        hms = self._clock_hms(match)
        if hms is None:
            return None
        hour, minute, second = hms
        if not (0 <= minute <= 59 and 0 <= second <= 59):
            return None
        if hour == 24 and minute == 0 and second == 0:
            hour = 0
        if not 0 <= hour <= 23:
            return None
        base = _midnight(anchor)
        dt = base.replace(hour=hour, minute=minute, second=second)
        prefer_future = self.spec.construction_flags.get(
            match.construction, {}).get("prefer_future", False)
        if prefer_future and dt < anchor:
            dt = dt + timedelta(days=1)
        start = AstroDate.from_datetime(dt)
        tz = self._zone_tzinfo(match.slots.get("ZONE"))
        if tz is not None:
            start = start.replace(tzinfo=tz)
        return Resolution(DateSpan(start, start + timedelta(minutes=1)),
                          self._consumed(match))

    def _zone_tzinfo(self, zone_tok):
        """Parse a bound ZONE token into a fixed-offset
        :class:`datetime.timezone`, or ``None`` when no zone is present.

        Three shapes resolve, all to a *fixed* offset:

        * ``"utc"`` / ``"gmt"`` optionally with a signed offset ("utc+2",
          "gmt-5:30") -- the acronym's base offset (0 for UTC/GMT) plus the tail.
        * a curated set of common, **unambiguous** zone abbreviations
          ("est", "cet", "jst", ...) whose fixed offset lives in the
          ``clock_zone_<minutes>.voc`` tables.  These are deliberately a
          simplification: FIXED offsets, NOT DST-aware IANA zones, and the
          curated set excludes genuinely ambiguous abbreviations (IST, ACST,
          CST-as-China, ...), which stay in the remainder rather than guess.
        * a bare RFC/ISO signed numeric offset ("-0500", "+05:30", "-08:00"):
          hours = the leading digits, minutes = the trailing two.

        Named-city / region words ("Berlin", "Eastern time") are out of scope --
        they never bind here and leave the wall time naive."""
        if zone_tok is None:
            return None
        from datetime import timezone
        text = zone_tok.text
        # bare signed numeric offset: no acronym, sign + digits only.
        num = re.fullmatch(r"([+-])(\d{1,2}):?(\d{2})", text)
        if num is not None:
            sign = 1 if num.group(1) == "+" else -1
            off = sign * (int(num.group(2)) * 60 + int(num.group(3)))
            return timezone(timedelta(minutes=off))
        m = re.match(r"([a-z]+)([+-])?(\d{1,2})?:?(\d{2})?$", text)
        base_min = self.spec.clock_zones.get(m.group(1), 0)
        off = base_min
        if m.group(2) is not None:
            hh = int(m.group(3) or 0)
            mm = int(m.group(4) or 0)
            sign = 1 if m.group(2) == "+" else -1
            off = base_min + sign * (hh * 60 + mm)
        return timezone(timedelta(minutes=off))

    #: military "HHMM hours" / bare "0600" reuse the clock resolver verbatim.
    _resolve_military_time = _resolve_clock_time

    #: "<hour[:min]> this <daypart>" ("2:30 this afternoon", "3 this morning"):
    #: the daypart word binds the MERIDIEM slot (afternoon/evening -> pm,
    #: morning -> am), so the reading resolves through the shared clock path.
    #: It carries no ``prefer_future`` flag, so the wall time stays on TODAY --
    #: "this afternoon" is this calendar day's afternoon even when already past.
    _resolve_clock_this_daypart = _resolve_clock_time

    def _resolve_subdivision_time(self, match, anchor):
        """A clock reading in an alternative day subdivision, rescaled to civil
        time by exact day-fraction arithmetic.

        French decimal time ("5 decimal hours" == exactly noon): the reading
        is converted through the subdivision's unit->day-fraction table to
        civil microseconds since midnight.  The span width is the smallest
        named subdivision unit's civil duration -- honest referential width,
        so "5 decimal hours" is a 2.4-civil-hour-wide span, not a false point.
        """
        sub = DAY_SUBDIVISIONS[self.spec.day_subdivision]
        subh = int(match.slots["SUBH"].value)
        subm_tok = match.slots.get("SUBM")
        subs_tok = match.slots.get("SUBS")
        subm = int(subm_tok.value) if subm_tok else 0
        subs = int(subs_tok.value) if subs_tok else 0
        start_us = sub.units_to_us(subh, subm, subs)
        if not 0 <= start_us < US_PER_DAY:
            return None
        smallest = "second" if subs_tok else "minute" if subm_tok else "hour"
        width_us = sub.unit_width_us(smallest)
        base = _midnight(anchor)
        start_dt = base + timedelta(microseconds=start_us)
        start = AstroDate.from_datetime(start_dt)
        end = start + timedelta(microseconds=width_us)
        return Resolution(DateSpan(start, end), self._consumed(match))

    def _clock_hms(self, match):
        # the hour AS SPOKEN, captured before any subtractive "to"/bare-half
        # rollback in the spelled-clock paths below; None here means the branch
        # never rolls the hour back (digit/military clocks), so the meridiem can
        # safely read it as the final hour (defaulted just before that block).
        spoken_hour = None
        clock = match.slots.get("CLOCK")
        miltime = (match.slots.get("MILTIME") or match.slots.get("MILTIMEZ")
                   or match.slots.get("MILTIMENZ"))
        landmark = match.slots.get("LANDMARK")
        dotclock = match.slots.get("DOTCLOCK") or match.slots.get("PADCLOCK")
        if clock is not None:
            parts = [int(p) for p in clock.text.split(":")]
            hour, minute = parts[0], parts[1]
            second = parts[2] if len(parts) > 2 else 0
            # A trailing spoken fraction after a folded CLOCK hour: Arabic tells
            # the hour first ("الساعة الثالثة" -> CLOCK 3:00) and hangs the
            # fraction off it in HOUR-CLOCKDIR-FRACTION order -- "الثالثة والنصف"
            # (three and-a-half == 03:30), "العاشرة والربع" (ten and-a-quarter ==
            # 10:15), "الواحدة إلا ربع" (one less-a-quarter == 00:45).  This is
            # the mirror of English's "half past three"; the CLOCK branch reads
            # the bare hour, so the fraction offset is applied here, reusing the
            # shared clock_fractions/clock_dirs spec maps.  The meridiem below
            # reads the hour AS SPOKEN, so a subtractive "to" rollback lands on
            # the right side of noon/midnight.
            frac_tok = match.slots.get("FRACTION")
            dir_tok = match.slots.get("CLOCKDIR")
            if frac_tok is not None and dir_tok is not None:
                spoken_hour = hour
                offset = self.spec.clock_fractions[frac_tok.text]
                if self.spec.clock_dirs[dir_tok.text] > 0:      # past ("و")
                    minute += offset
                else:                                           # to ("إلا")
                    hour -= 1
                    minute = 60 - offset
                    # 12-hour reckoning spells the pre-one hour as twelve
                    # ("الواحدة إلا ربع" == 12:45); the default 24-hour reckoning
                    # keeps 00:45.  A landmark base never reaches 0 here.
                    if hour == 0 and self.spec.conventions.toward_hour_12h:
                        hour = 12
                    elif hour < 0:
                        hour += 24
        elif dotclock is not None:
            # the timetable "HH.MM" -- read the wall clock from the dotted raw
            # the tokenizer preserved (the number reading truncated it to HH)
            hh, mm = dotclock.raw.split(".")
            hour, minute, second = int(hh), int(mm), 0
        elif miltime is not None:
            raw = miltime.raw.rstrip(".")
            hour, minute, second = int(raw[:2]), int(raw[2:]), 0
        elif match.slots.get("QUARTS") is not None:
            # Catalan *sistema de campanar* -- the traditional bell-tower
            # reckoning, which counts quarters already struck **toward** the
            # named hour, and is numerically incompatible with the additive
            # *sistema de rellotge* the same language also uses:
            #
            #     un quart de deu    == 09:15   (rellotge: les nou i quart)
            #     dos quarts de deu  == 09:30   (rellotge: les nou i mitja)
            #     tres quarts de deu == 09:45   (rellotge: les deu menys quart)
            #
            # The named hour is the one being *approached*, so the value is
            # (hour - 1) + N*15 minutes -- "un quart de deu" is 9:15, never
            # 10:15.  Worked example: "un quart d'una" names one o'clock with
            # one quarter struck -> 12:15, the twelve-hour name of the
            # preceding hour (campanar is inherently a 12-hour reckoning).
            #
            # Source: Optimot / Nova gramatica (IEC), "Les hores en catala:
            # sistema de campanar i sistema de rellotge",
            # https://aplicacions.llengua.gencat.cat/llc/AppJava/index.html?action=Principal&method=detall&input_cercar=hores&numPagina=1&database=FITXES_PUB&idFont=12802&idHit=12802&tipusFont=Fitxes+de+l%27Optimot
            # and Diputacio de Barcelona, "Sistema tradicional o de campanar",
            # https://llengua.diba.cat/sistema-tradicional-o-de-campanar
            second = 0
            quarters = int(match.slots["QUARTS"].value or 0)
            hour = int(match.slots["HOUR"].value)
            # There is no fourth quarter -- four quarters is simply the hour
            # itself ("una hora"), and no zeroth quarter exists either.  Both
            # are refused rather than guessed.
            if not 1 <= quarters <= 3 or not 1 <= hour <= 12:
                return None
            spoken_hour = hour
            hour -= 1
            if hour == 0:
                hour = 12
            minute = quarters * 15
        else:
            second = 0
            # base hour/minute: a landmark ("midnight" 0, "noon" 720) or a
            # bare hour ("at ten") -- the fraction/minute offset applies on top
            if landmark is not None:
                hour, minute = divmod(self.spec.clock_landmarks[landmark.text], 60)
            else:
                hour, minute = int(match.slots["HOUR"].value), 0
            # the meridiem attaches to the spoken hour, before any subtractive
            # "to"/bare-half rollback decrements it ("a quarter to twelve pm" is
            # a quarter to NOON = 11:45, not 23:45).
            spoken_hour = hour
            frac_tok = match.slots.get("FRACTION")
            min_tok = match.slots.get("MINUTE")
            clockmin_tok = match.slots.get("CLOCKMIN")
            dir_tok = match.slots.get("CLOCKDIR")
            if dir_tok is not None and (frac_tok is not None or min_tok is not None
                                         or clockmin_tok is not None):
                offset = (self.spec.clock_fractions[frac_tok.text] if frac_tok is not None
                          else self.spec.clock_dir_minutes[clockmin_tok.text]
                          if clockmin_tok is not None else int(min_tok.value))
                if self.spec.clock_dirs[dir_tok.text] > 0:      # past
                    minute += offset
                else:                                           # to (before)
                    hour -= 1
                    minute = 60 - offset
                    # 12-hour reckoning: minutes/quarter *to* one o'clock are
                    # spoken as twelve-something ("une heure moins le quart" =
                    # 12:45), so the hour that rolls back from 1 to 0 surfaces
                    # as 12, not 00 -- but only where the locale reckons the
                    # clock in 12 hours (French), not the Germanic 24-hour
                    # "kvart i ett" == 00:45.  A landmark base (noon 12 -> 11,
                    # midnight 0 -> -1 -> 23) never lands on 0 here, so this
                    # only ever fires for the spelled hour 1.
                    if hour == 0 and self.spec.conventions.toward_hour_12h:
                        hour = 12
            elif (frac_tok is not None and dir_tok is None
                    and self.spec.conventions.bare_half_past):
                # British-colloquial additive bare half: "half nine" == 09:30,
                # i.e. half *past* the stated hour (the opposite of the
                # Continental-Germanic "halb neun" == 08:30).  Only the half is
                # colloquial; "quarter nine" is not English, so a bare quarter
                # is rejected rather than guessed.
                offset = self.spec.clock_fractions[frac_tok.text]
                if offset != 30:
                    return None
                minute = offset
            elif (frac_tok is not None and dir_tok is None
                    and self.spec.conventions.bare_half_to):
                # Continental-Germanic "halb neun"/"halv nio" == the half
                # *before* nine (08:30).  Only the half-fraction takes this
                # bare form; a bare quarter ("viertel neun") is regionally
                # ambiguous, so it is rejected rather than guessed -- UNLESS
                # the locale runs the Finno-Ugric counting-toward-the-hour
                # system (bare_quarter_to), where every fraction names that
                # much of the way toward the coming hour and so the quarters
                # are unambiguous: Hungarian "negyed kilenc" == 08:15,
                # "haromnegyed kilenc" == 08:45; Estonian "veerand uheksa" /
                # "kolmveerand uheksa" likewise.  In both readings the stated
                # hour is the *coming* one, so minute == the fraction offset
                # applied to the previous hour.
                offset = self.spec.clock_fractions[frac_tok.text]
                if offset != 30 and not self.spec.conventions.bare_quarter_to:
                    return None
                hour -= 1
                minute = offset
                # Slavic/12h reckoning: half toward the first hour is 12:30,
                # not 00:30 ("pol enih", "polovina pervogo") -- the previous
                # hour is spoken as twelve.
                if hour == 0 and self.spec.conventions.toward_hour_12h:
                    hour = 12
            if hour < 0:            # "quarter to midnight" underflows -> 23:45
                hour += 24
        meridiem = match.slots.get("MERIDIEM")
        if meridiem is not None:
            # digit/military clocks never roll the hour back, so their spoken
            # hour IS the final hour.  They also reach here with spoken_hour
            # still None (only the bare/spelled hour paths set it), so its
            # None-ness marks an explicit 24-hour clock whose hour is final.
            bare_12h = spoken_hour is not None
            if spoken_hour is None:
                spoken_hour = hour
            if meridiem.text in self.spec.night_meridiems:
                # NIGHT is a daypart BAND that crosses midnight, not a uniform
                # +12 PM shift.  "the one at night" is 01:00 (not 13:00) and
                # "twelve at night" is midnight 00:00 (not noon).  The band
                # splits the named 12-hour clock into: small hours 1..5 stay
                # AM (01..05), evening hours 6..11 are PM (18..23), and twelve
                # is midnight.  The AM/PM cut at 5|6 follows Arabic usage,
                # where ليل covers the small hours as AM and the late evening
                # as PM (cf. CLDR day-period bands for ar: night starts at
                # 00:00 and morning at ~06:00).
                if hour == 12:
                    hour = 0
                elif 6 <= hour <= 11:
                    hour += 12
                # hours 1..5 keep their AM value unchanged
            else:
                # a 12-hour am/pm marker only qualifies a valid 12-hour SPOKEN
                # hour, 1..12.  A bare spoken hour of 0 or >=13 combined with a
                # meridiem is contradictory ("13 pm", "0 am") and names no time
                # -- decline, exactly as the numeric literal overflow guards do
                # ("13:60" -> None), rather than silently drop the meridiem and
                # return a confident wrong hour.  This does NOT apply to a
                # daypart marker over an explicit 24-hour clock ("15:30
                # odpoledne", "öğleden sonra 15:30"), whose hour is already final.
                if bare_12h and not 1 <= spoken_hour <= 12:
                    return None
                off = self.spec.meridiems[meridiem.text]
                # decide the +/-12 shift from the SPOKEN hour's 12h meaning, then
                # apply it to the (possibly rolled-back) hour, so a subtractive
                # "to twelve pm/am" lands the right side of noon/midnight.  "pm"
                # promotes a spoken 1..11 into the afternoon (12 pm is already
                # noon); "am" demotes a spoken 12 (midnight) by 12 hours.
                if off == 12 and spoken_hour < 12:
                    hour = (hour + 12) % 24
                elif off == 0 and spoken_hour == 12:
                    hour = (hour - 12) % 24
        return hour, minute, second
