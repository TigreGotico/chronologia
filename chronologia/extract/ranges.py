"""Language-agnostic calendar range and season utilities.

Ranges are inclusive ``(start, end)`` tuples of the same type as the
reference date passed in. Decades, centuries and millennia follow the
calendar convention (the 1990s are 1990-1999, the 1900s are 1900-1999).

Seasons are meteorological (month-aligned) and hemisphere-aware: northern
spring starts March 1st, southern spring starts September 1st.
"""
import calendar as _calendar
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Optional, Tuple, Union


# ``DateTimeResolution`` lives in the reckoning core; the same enum identity
# is shared across the extraction engine and the eras arithmetic (the
# chronologia enum is a superset, adding deep-time tiers).
from chronologia.resolution import DateTimeResolution


class relativedelta:
    """Stdlib-only stand-in for the ``month``/``week`` offsets this module
    needs (chronologia carries no ``python-dateutil`` runtime dependency).

    Only ``weeks`` and ``months`` are supported -- the sole forms the range
    arithmetic uses -- with the same right-add semantics: weeks are exact
    seven-day steps, months roll the year over and clamp an overshooting
    day to the last day of the target month.
    """

    __slots__ = ("months", "weeks")

    def __init__(self, months: int = 0, weeks: int = 0):
        self.months = months
        self.weeks = weeks

    def __radd__(self, base):
        if self.weeks:
            base = base + timedelta(weeks=self.weeks)
        if self.months:
            total = base.month - 1 + self.months
            year = base.year + total // 12
            month = total % 12 + 1
            day = min(base.day, _calendar.monthrange(year, month)[1])
            base = base.replace(year=year, month=month, day=day)
        return base


class Hemisphere(Enum):
    NORTH = 0
    SOUTH = 1


class Season(Enum):
    SPRING = 0
    SUMMER = 1
    FALL = 2
    WINTER = 3
    AUTUMN = 2


# before-present reference epoch (as in radiocarbon dating)
BEFORE_PRESENT_EPOCH = date(year=1950, day=1, month=1)

DateRange = Tuple[date, date]


def get_week_range(ref_date: date) -> DateRange:
    """Monday..Sunday range of the week containing ``ref_date``."""
    start = ref_date - timedelta(days=ref_date.weekday())
    end = start + timedelta(days=6)
    return start, end


def get_weekend_range(ref_date: date) -> DateRange:
    """Saturday..Sunday of the weekend containing or following ``ref_date``.

    During the week this is the upcoming weekend; on a weekend day it is
    the current weekend.
    """
    if ref_date.weekday() == 5:
        start = ref_date
    elif ref_date.weekday() == 6:
        start = ref_date - timedelta(days=1)
    else:
        start = get_week_range(ref_date)[0] + timedelta(days=5)
    return start, start + timedelta(days=1)


def get_month_range(ref_date: date) -> DateRange:
    """First..last day of the month containing ``ref_date``."""
    start = ref_date.replace(day=1)
    if ref_date.month == 12:
        end = ref_date.replace(day=31)
    else:
        end = ref_date.replace(day=1, month=ref_date.month + 1) - \
            timedelta(days=1)
    return start, end


def get_year_range(ref_date: date) -> DateRange:
    """January 1st..December 31st of the year containing ``ref_date``."""
    return (ref_date.replace(day=1, month=1),
            ref_date.replace(day=31, month=12))


def get_decade_range(ref_date: date) -> DateRange:
    """Calendar decade containing ``ref_date`` (1990s = 1990-1999)."""
    start = date(day=1, month=1, year=(ref_date.year // 10) * 10)
    end = date(day=31, month=12, year=start.year + 9)
    return start, end


def get_century_range(ref_date: date) -> DateRange:
    """Calendar century containing ``ref_date`` (1900s = 1900-1999)."""
    start = date(day=1, month=1, year=(ref_date.year // 100) * 100)
    end = date(day=31, month=12, year=start.year + 99)
    return start, end


def get_millennium_range(ref_date: date) -> DateRange:
    """Calendar millennium containing ``ref_date`` (1000-1999)."""
    start = date(day=1, month=1, year=(ref_date.year // 1000) * 1000)
    end = date(day=31, month=12, year=start.year + 999)
    return start, end


def get_week_number(ref_date: Optional[date] = None) -> int:
    """ISO-8601 week number of ``ref_date`` (default: today)."""
    ref_date = ref_date or datetime.now()
    return ref_date.isocalendar()[1]


def _as_date(ref_date: Union[date, datetime]) -> date:
    if isinstance(ref_date, datetime):
        return ref_date.date()
    return ref_date


# meteorological season boundaries: {season: (start_month, end_month)}
# northern hemisphere; the southern hemisphere is shifted by two seasons
_NORTH_SEASONS = {
    Season.SPRING: (3, 5),
    Season.SUMMER: (6, 8),
    Season.FALL: (9, 11),
}
_SOUTH_SEASONS = {
    Season.FALL: (3, 5),
    Season.WINTER: (6, 8),
    Season.SPRING: (9, 11),
}
# season starting in December, wrapping over the new year
_NORTH_WRAP = Season.WINTER
_SOUTH_WRAP = Season.SUMMER


def date_to_season(ref_date: Optional[date] = None,
                   hemisphere: Hemisphere = Hemisphere.NORTH) -> Season:
    """Meteorological season containing ``ref_date`` (default: today)."""
    ref_date = _as_date(ref_date or datetime.now().date())
    seasons = _NORTH_SEASONS if hemisphere == Hemisphere.NORTH \
        else _SOUTH_SEASONS
    for season, (first, last) in seasons.items():
        if first <= ref_date.month <= last:
            return season
    return _NORTH_WRAP if hemisphere == Hemisphere.NORTH else _SOUTH_WRAP


def season_to_date(season: Season, year: Optional[Union[int, date]] = None,
                   hemisphere: Hemisphere = Hemisphere.NORTH) -> date:
    """Start date of ``season`` in ``year`` (default: current year)."""
    if year is None:
        year = datetime.now().year
    elif not isinstance(year, int):
        year = year.year
    seasons = _NORTH_SEASONS if hemisphere == Hemisphere.NORTH \
        else _SOUTH_SEASONS
    wrap = _NORTH_WRAP if hemisphere == Hemisphere.NORTH else _SOUTH_WRAP
    season = Season(season.value) if isinstance(season, Season) \
        else Season(season)
    if season == wrap:
        return date(day=1, month=12, year=year)
    if season not in seasons:
        raise ValueError(f"Unknown Season: {season}")
    return date(day=1, month=seasons[season][0], year=year)


def _season_occurrence(season: Season, year: int,
                       hemisphere: Hemisphere) -> DateRange:
    """Half-open ``[start, end)`` of the ``year`` occurrence of ``season``.

    A meteorological season is three months wide, so the December-starting
    season ends on March 1st of the following year; every deictic reading
    below is expressed in terms of this span rather than the start date
    alone, which is what makes the year-wrapping season behave like the
    other three.
    """
    start = season_to_date(season, year, hemisphere)
    return start, start + relativedelta(months=3)


def next_season_date(season: Season, ref_date: Optional[date] = None,
                     hemisphere: Hemisphere = Hemisphere.NORTH) -> date:
    """Start date of the first occurrence of ``season`` still to begin.

    A speaker standing inside a season never means it by "next": the
    occurrence has to start strictly after the reference date, so on the
    first day of summer "next summer" is already the summer of the
    following year.
    """
    ref_date = _as_date(ref_date or datetime.now().date())
    for year in range(ref_date.year - 1, ref_date.year + 3):
        start, _ = _season_occurrence(season, year, hemisphere)
        if start > ref_date:
            return start
    raise ValueError(f"no future occurrence of {season}")


def last_season_date(season: Season, ref_date: Optional[date] = None,
                     hemisphere: Hemisphere = Hemisphere.NORTH) -> date:
    """Start date of the most recent occurrence of ``season`` that is over.

    "Last summer" said in July means the summer that has finished, never
    the one the speaker is living through, so the occurrence must have
    ended on or before the reference date.  The same reading places "last
    winter" in January two Decembers back, because the December just gone
    is still running.
    """
    ref_date = _as_date(ref_date or datetime.now().date())
    for year in range(ref_date.year + 1, ref_date.year - 3, -1):
        start, end = _season_occurrence(season, year, hemisphere)
        if end <= ref_date:
            return start
    raise ValueError(f"no completed occurrence of {season}")


def current_season_date(season: Season, ref_date: Optional[date] = None,
                        hemisphere: Hemisphere = Hemisphere.NORTH) -> date:
    """Start date of the occurrence of ``season`` a speaker means by "this".

    While the reference date falls inside an occurrence, that occurrence is
    the one meant -- in January "this winter" is the winter that began in
    December, not the one that begins eleven months later.  Outside the
    season the calendar year decides, so in July "this winter" is the
    winter that December brings.
    """
    ref_date = _as_date(ref_date or datetime.now().date())
    for year in (ref_date.year - 1, ref_date.year):
        start, end = _season_occurrence(season, year, hemisphere)
        if start <= ref_date < end:
            return start
    return season_to_date(season, ref_date, hemisphere)


def get_season_range(ref_date: Optional[date] = None,
                     hemisphere: Hemisphere = Hemisphere.NORTH) -> DateRange:
    """First..last day of the season containing ``ref_date``.

    The December-starting season wraps the new year: its range runs from
    December 1st to the last day of the following February (the 29th on
    leap years).
    """
    ref_date = _as_date(ref_date or datetime.now().date())
    seasons = _NORTH_SEASONS if hemisphere == Hemisphere.NORTH \
        else _SOUTH_SEASONS
    for first, last in seasons.values():
        if first <= ref_date.month <= last:
            start = date(day=1, month=first, year=ref_date.year)
            end = date(day=1, month=last + 1, year=ref_date.year) - \
                timedelta(days=1)
            return start, end
    # December..February wrap-around season
    if ref_date.month == 12:
        start = date(day=1, month=12, year=ref_date.year)
    else:
        start = date(day=1, month=12, year=ref_date.year - 1)
    end = date(day=1, month=3, year=start.year + 1) - timedelta(days=1)
    return start, end


def get_date_ordinal(ordinal: int, ref_date: Optional[date] = None,
                     resolution: DateTimeResolution =
                     DateTimeResolution.DAY_OF_MONTH) -> date:
    """Resolve "the Nth {unit} of {scope}" into a date.

    BEFORE_PRESENT_* resolutions may land before year 1, which
    ``datetime.date`` cannot hold; those return an
    :class:`~chronologia.eras.AstroDate` instead (never raise).

    Args:
        ordinal: 1-based ordinal; -1 selects the last unit in the scope.
        ref_date: reference date the containing scope is derived from
            (default: today).
        resolution: which unit/scope pair the ordinal refers to.

    Returns:
        The date of the requested unit (weeks resolve to their Monday,
        months/years/decades/centuries/millennia to their first day).
    """
    ordinal = int(ordinal)
    ref_date = _as_date(ref_date or datetime.now())

    _decade = (ref_date.year // 10) * 10 or 1
    _century = (ref_date.year // 100) * 100 or 1
    _mil = (ref_date.year // 1000) * 1000 or 1

    if resolution == DateTimeResolution.DAY:
        if ordinal < 0:
            raise OverflowError("The last day of existence can not be "
                                "represented")
        return date(year=1, day=1, month=1) + timedelta(days=ordinal - 1)
    if resolution == DateTimeResolution.DAY_OF_MONTH:
        if ordinal == -1:
            return get_month_range(ref_date)[1]
        return ref_date.replace(day=ordinal)
    if resolution == DateTimeResolution.DAY_OF_YEAR:
        if ordinal == -1:
            return date(year=ref_date.year, day=31, month=12)
        return date(year=ref_date.year, day=1, month=1) + \
            timedelta(days=ordinal - 1)
    if resolution == DateTimeResolution.DAY_OF_DECADE:
        if ordinal == -1:
            return date(year=_decade + 9, day=31, month=12)
        return date(year=_decade, day=1, month=1) + \
            timedelta(days=ordinal - 1)
    if resolution == DateTimeResolution.DAY_OF_CENTURY:
        if ordinal == -1:
            return date(year=_century + 99, day=31, month=12)
        return date(year=_century, day=1, month=1) + \
            timedelta(days=ordinal - 1)
    if resolution == DateTimeResolution.DAY_OF_MILLENNIUM:
        if ordinal == -1:
            return date(year=_mil + 999, day=31, month=12)
        return date(year=_mil, day=1, month=1) + timedelta(days=ordinal - 1)

    if resolution == DateTimeResolution.WEEK:
        if ordinal < 0:
            raise OverflowError("The last week of existence can not be "
                                "represented")
        _day = date(1, 1, 1) + relativedelta(weeks=ordinal) - \
            timedelta(days=1)
        return get_week_range(_day)[0]
    if resolution == DateTimeResolution.WEEK_OF_MONTH:
        if ordinal == -1:
            _day = get_month_range(ref_date)[1]
        else:
            if not 0 < ordinal <= 4:
                raise ValueError("months only have 4 weeks")
            _day = ref_date.replace(day=1) + relativedelta(weeks=ordinal) - \
                timedelta(days=1)
        return get_week_range(_day)[0]
    if resolution == DateTimeResolution.WEEK_OF_YEAR:
        if ordinal == -1:
            _day = ref_date.replace(day=31, month=12)
        else:
            _day = ref_date.replace(day=1, month=1) + \
                relativedelta(weeks=ordinal) - timedelta(days=1)
        return get_week_range(_day)[0]
    if resolution == DateTimeResolution.WEEK_OF_DECADE:
        if ordinal == -1:
            _day = date(day=31, month=12, year=_decade + 9)
        else:
            _day = date(day=1, month=1, year=_decade) + \
                relativedelta(weeks=ordinal) - timedelta(days=1)
        return get_week_range(_day)[0]
    if resolution == DateTimeResolution.WEEK_OF_CENTURY:
        if ordinal == -1:
            _day = date(day=31, month=12, year=_century + 99)
        else:
            _day = date(day=1, month=1, year=_century) + \
                relativedelta(weeks=ordinal) - timedelta(days=1)
        return get_week_range(_day)[0]
    if resolution == DateTimeResolution.WEEK_OF_MILLENNIUM:
        if ordinal == -1:
            _day = date(day=31, month=12, year=_mil + 999)
        else:
            _day = date(day=1, month=1, year=_mil) + \
                relativedelta(weeks=ordinal) - timedelta(days=1)
        return get_week_range(_day)[0]

    if resolution == DateTimeResolution.MONTH:
        if ordinal < 0:
            raise OverflowError("The last month of existence can not be "
                                "represented")
        return date(year=1, day=1, month=1) + \
            relativedelta(months=ordinal - 1)
    if resolution == DateTimeResolution.MONTH_OF_YEAR:
        if ordinal == -1:
            return ref_date.replace(month=12, day=1)
        return ref_date.replace(day=1, month=1) + \
            relativedelta(months=ordinal - 1)
    if resolution == DateTimeResolution.MONTH_OF_DECADE:
        if ordinal == -1:
            return date(year=_decade + 9, day=1, month=12)
        return date(year=_decade, month=1, day=1) + \
            relativedelta(months=ordinal - 1)
    if resolution == DateTimeResolution.MONTH_OF_CENTURY:
        if ordinal == -1:
            return date(year=_century + 99, day=1, month=12)
        return date(year=_century, month=1, day=1) + \
            relativedelta(months=ordinal - 1)
    if resolution == DateTimeResolution.MONTH_OF_MILLENNIUM:
        if ordinal == -1:
            return date(year=_mil + 999, day=1, month=12)
        return date(year=_mil, month=1, day=1) + \
            relativedelta(months=ordinal - 1)

    if resolution == DateTimeResolution.YEAR:
        if ordinal == -1:
            raise OverflowError("The last year of existence can not be "
                                "represented")
        if ordinal == 0:
            # NOTE: no year 0
            return date(year=1, day=1, month=1)
        return date(year=ordinal, day=1, month=1)
    if resolution == DateTimeResolution.YEAR_OF_DECADE:
        if ordinal == -1:
            return date(year=_decade + 9, day=1, month=1)
        if not 0 < ordinal <= 10:
            raise ValueError("decades only have 10 years")
        return date(year=_decade + ordinal - 1, day=1, month=1)
    if resolution == DateTimeResolution.YEAR_OF_CENTURY:
        if ordinal == -1:
            return date(year=_century + 99, day=1, month=1)
        if not 0 < ordinal <= 100:
            raise ValueError("centuries only have 100 years")
        return date(year=_century + ordinal - 1, day=1, month=1)
    if resolution == DateTimeResolution.YEAR_OF_MILLENNIUM:
        if ordinal == -1:
            return date(year=_mil + 999, day=1, month=1)
        if not 0 < ordinal <= 1000:
            raise ValueError("millennia only have 1000 years")
        return date(year=_mil + ordinal - 1, day=1, month=1)

    if resolution == DateTimeResolution.DECADE:
        if ordinal == -1:
            raise OverflowError("The last decade of existence can not be "
                                "represented")
        if ordinal == 1:
            return date(day=1, month=1, year=1)
        return date(year=(ordinal - 1) * 10, day=1, month=1)
    if resolution == DateTimeResolution.DECADE_OF_CENTURY:
        if ordinal == -1:
            return date(year=_century + 90, day=1, month=1)
        if not 0 < ordinal <= 10:
            raise ValueError("centuries only have 10 decades")
        if ordinal == 1:
            return date(day=1, month=1, year=_century)
        return date(year=_century + (ordinal - 1) * 10, day=1, month=1)
    if resolution == DateTimeResolution.DECADE_OF_MILLENNIUM:
        if ordinal == -1:
            return date(year=_mil + 990, day=1, month=1)
        if not 0 < ordinal <= 100:
            raise ValueError("millennia only have 100 decades")
        if ordinal == 1:
            return date(day=1, month=1, year=_mil)
        return date(year=_mil + (ordinal - 1) * 10, day=1, month=1)

    if resolution == DateTimeResolution.CENTURY:
        if ordinal == -1:
            raise OverflowError("The last century of existence can not be "
                                "represented")
        if ordinal == 1:
            # NOTE: no century 0 / year 0
            return date(day=1, month=1, year=1)
        return date(year=(ordinal - 1) * 100, day=1, month=1)
    if resolution == DateTimeResolution.CENTURY_OF_MILLENNIUM:
        if ordinal == -1:
            return date(year=_mil + 900, day=1, month=1)
        if not 0 < ordinal <= 10:
            raise ValueError("millennia only have 10 centuries")
        if ordinal == 1:
            return date(day=1, month=1, year=_mil)
        return date(year=_mil + (ordinal - 1) * 100, day=1, month=1)

    if resolution == DateTimeResolution.MILLENNIUM:
        if ordinal < 0:
            raise OverflowError("The last millennium of existence can not "
                                "be represented")
        if ordinal == 1:
            return date(day=1, month=1, year=1)
        return date(year=(ordinal - 1) * 1000, day=1, month=1)

    if resolution.name.startswith("BEFORE_PRESENT_"):
        if ordinal < 0:
            raise OverflowError("negative Before Present counts are not a "
                                "date before present")
        return _before_present(ordinal, resolution)

    raise ValueError(f"Invalid DateTimeResolution: {resolution}")


#: Julian day number on which BEFORE_PRESENT_EPOCH (1950-01-01) begins;
#: fixed origin for exact day arithmetic at any depth
_JD_BP_EPOCH = 2433283


def _before_present(ordinal, resolution):
    """Resolve "N {unit}s before present" (present = 1950, the radiocarbon
    convention).  Results the datetime range can hold are plain ``date``
    (unchanged behaviour); anything before year 1 is an ``AstroDate``
    instead of the previous ``OverflowError``.

    Day/week counts use Julian-day arithmetic so they stay exact at any
    depth; month/year counts are integer month/year arithmetic anchored at
    the epoch, matching what ``relativedelta`` produced in range.
    """
    # imported here: eras depends on this module for DateTimeResolution
    from chronologia.eras import AstroDate, julian_day_to_date

    if resolution == DateTimeResolution.BEFORE_PRESENT_DAY:
        return julian_day_to_date(_JD_BP_EPOCH - ordinal)
    if resolution == DateTimeResolution.BEFORE_PRESENT_WEEK:
        _day = julian_day_to_date(_JD_BP_EPOCH - 7 * ordinal)
        if isinstance(_day, AstroDate):
            return _day
        return get_week_range(_day)[1]
    if resolution == DateTimeResolution.BEFORE_PRESENT_MONTH:
        _months = (BEFORE_PRESENT_EPOCH.year * 12) - ordinal
        _year, _month = _months // 12, _months % 12 + 1
        if _year < 1:
            return AstroDate(_year, _month, 1)
        return date(year=_year, month=_month, day=1)

    _span = {DateTimeResolution.BEFORE_PRESENT_YEAR: 1,
             DateTimeResolution.BEFORE_PRESENT_DECADE: 10,
             DateTimeResolution.BEFORE_PRESENT_CENTURY: 100,
             DateTimeResolution.BEFORE_PRESENT_MILLENNIUM: 1000}[resolution]
    _year = BEFORE_PRESENT_EPOCH.year - _span * ordinal
    if _year < 1:
        return AstroDate(_year, 1, 1)
    return date(year=_year, month=1, day=1)


#: unit name -> the {unit}_OF_{scope} resolutions it participates in.
#: The scoped-ordinal construction ("the 3rd week of june", "the first
#: decade of the 21st century") maps a spelled unit + scope onto these
#: ``DateTimeResolution`` members before calling :func:`get_date_ordinal`.
_UNIT_OF_MONTH = {"day": DateTimeResolution.DAY_OF_MONTH,
                  "week": DateTimeResolution.WEEK_OF_MONTH}
_UNIT_OF_YEAR = {"day": DateTimeResolution.DAY_OF_YEAR,
                 "week": DateTimeResolution.WEEK_OF_YEAR,
                 "month": DateTimeResolution.MONTH_OF_YEAR}
_UNIT_OF_CENTURY = {"year": DateTimeResolution.YEAR_OF_CENTURY,
                    "decade": DateTimeResolution.DECADE_OF_CENTURY}
_UNIT_OF_MILLENNIUM = {"year": DateTimeResolution.YEAR_OF_MILLENNIUM,
                       "decade": DateTimeResolution.DECADE_OF_MILLENNIUM,
                       "century": DateTimeResolution.CENTURY_OF_MILLENNIUM}
_ABSOLUTE = {"decade": DateTimeResolution.DECADE,
             "century": DateTimeResolution.CENTURY,
             "millennium": DateTimeResolution.MILLENNIUM}
