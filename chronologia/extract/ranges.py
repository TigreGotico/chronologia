"""Calendar range and season arithmetic for the extraction resolver.

Seasons are meteorological (month-aligned) and hemisphere-aware: northern
spring starts March 1st, southern spring starts September 1st.
"""
import calendar as _calendar
from datetime import date, timedelta
from enum import Enum
from typing import Optional, Tuple

from chronologia.resolution import DateTimeResolution


class relativedelta:
    """Stdlib stand-in for the week and month offsets of ``dateutil``.

    Weeks are exact seven-day steps; months roll the year over and clamp the
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


BEFORE_PRESENT_EPOCH = date(year=1950, day=1, month=1)

DateRange = Tuple[date, date]


def get_week_range(ref_date: date) -> DateRange:
    """Monday..Sunday range of the week containing ``ref_date``."""
    start = ref_date - timedelta(days=ref_date.weekday())
    end = start + timedelta(days=6)
    return start, end


def get_month_range(ref_date: date) -> DateRange:
    """First..last day of the month containing ``ref_date``."""
    start = ref_date.replace(day=1)
    if ref_date.month == 12:
        end = ref_date.replace(day=31)
    else:
        end = ref_date.replace(day=1, month=ref_date.month + 1) - \
            timedelta(days=1)
    return start, end


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


_SEASON_START_MONTH = {
    Hemisphere.NORTH: {Season.SPRING: 3, Season.SUMMER: 6, Season.FALL: 9,
                       Season.WINTER: 12},
    Hemisphere.SOUTH: {Season.FALL: 3, Season.WINTER: 6, Season.SPRING: 9,
                       Season.SUMMER: 12},
}


def season_to_date(season: Season, year: int,
                   hemisphere: Hemisphere = Hemisphere.NORTH) -> date:
    """Start date of ``season`` in ``year``."""
    return date(day=1, month=_SEASON_START_MONTH[hemisphere][season], year=year)


def _season_occurrence(season: Season, year: int,
                       hemisphere: Hemisphere) -> DateRange:
    """Half-open ``[start, end)`` of the ``year`` occurrence of ``season``.

    The December-starting season ends on March 1st of the following year.
    """
    start = season_to_date(season, year, hemisphere)
    return start, start + relativedelta(months=3)


def next_season_date(season: Season, ref_date: date,
                     hemisphere: Hemisphere = Hemisphere.NORTH) -> date:
    """Start of the first occurrence of ``season`` that begins after ``ref_date``."""
    for year in range(ref_date.year - 1, ref_date.year + 3):
        start, _ = _season_occurrence(season, year, hemisphere)
        if start > ref_date:
            return start
    raise ValueError(f"no future occurrence of {season}")


def last_season_date(season: Season, ref_date: date,
                     hemisphere: Hemisphere = Hemisphere.NORTH) -> date:
    """Start of the latest occurrence of ``season`` that ended by ``ref_date``.

    "Last winter" in January is two Decembers back: the December just gone is
    still running.
    """
    for year in range(ref_date.year + 1, ref_date.year - 3, -1):
        start, end = _season_occurrence(season, year, hemisphere)
        if end <= ref_date:
            return start
    raise ValueError(f"no completed occurrence of {season}")


def current_season_date(season: Season, ref_date: date,
                        hemisphere: Hemisphere = Hemisphere.NORTH) -> date:
    """Start of the occurrence of ``season`` that "this" means at ``ref_date``.

    Inside an occurrence that occurrence is meant, so in January "this
    winter" began in December; outside it the calendar year decides.
    """
    for year in (ref_date.year - 1, ref_date.year):
        start, end = _season_occurrence(season, year, hemisphere)
        if start <= ref_date < end:
            return start
    return season_to_date(season, ref_date.year, hemisphere)


def get_date_ordinal(ordinal: int, ref_date: Optional[date] = None,
                     resolution: DateTimeResolution =
                     DateTimeResolution.DAY_OF_MONTH) -> date:
    """Resolve "the Nth {unit} of {scope}" into a date.

    ``ordinal`` is 1-based and -1 selects the last unit of the scope, which
    ``ref_date`` (default: today) fixes.  Weeks resolve to their Monday and
    longer units to their first day.  A BEFORE_PRESENT_* resolution before
    year 1 returns an :class:`~chronologia.eras.AstroDate`.
    """
    ordinal = int(ordinal)
    ref_date = ref_date or date.today()

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
        value = date(year=ref_date.year, day=1, month=1) + \
            timedelta(days=ordinal - 1)
        if value.year != ref_date.year:             # e.g. 366th day of 2017
            raise ValueError(f"year {ref_date.year} has no day {ordinal}")
        return value
    if resolution == DateTimeResolution.DAY_OF_DECADE:
        if ordinal == -1:
            return date(year=_decade + 9, day=31, month=12)
        value = date(year=_decade, day=1, month=1) + \
            timedelta(days=ordinal - 1)
        if not _decade <= value.year <= _decade + 9:
            raise ValueError(f"decade {_decade}s has no day {ordinal}")
        return value
    if resolution == DateTimeResolution.DAY_OF_CENTURY:
        if ordinal == -1:
            return date(year=_century + 99, day=31, month=12)
        value = date(year=_century, day=1, month=1) + \
            timedelta(days=ordinal - 1)
        if not _century <= value.year <= _century + 99:
            raise ValueError(f"century {_century} has no day {ordinal}")
        return value
    if resolution == DateTimeResolution.DAY_OF_MILLENNIUM:
        if ordinal == -1:
            return date(year=_mil + 999, day=31, month=12)
        value = date(year=_mil, day=1, month=1) + timedelta(days=ordinal - 1)
        if not _mil <= value.year <= _mil + 999:
            raise ValueError(f"millennium {_mil} has no day {ordinal}")
        return value

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
            if ordinal <= 0:
                raise ValueError(f"a month has no week {ordinal}")
            _day = ref_date.replace(day=1) + relativedelta(weeks=ordinal) - \
                timedelta(days=1)
            # a month spans 4 to 6 Mon-Sun weeks; the ordinal is valid while
            # its week still intersects the month
            if get_week_range(_day)[0] > get_month_range(ref_date)[1]:
                raise ValueError(f"month {ref_date:%Y-%m} has no week {ordinal}")
        return get_week_range(_day)[0]
    if resolution == DateTimeResolution.WEEK_OF_YEAR:
        if ordinal == -1:
            _day = ref_date.replace(day=31, month=12)
        else:
            # Dec 28 is always in the year's last ISO week
            max_week = ref_date.replace(month=12, day=28).isocalendar()[1]
            if not 1 <= ordinal <= max_week:
                raise ValueError(
                    f"a {ref_date.year}-week year has no week {ordinal}")
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
        if not 1 <= ordinal <= 12:
            raise ValueError(f"a year has 12 months, not {ordinal}")
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
        if ordinal == 0:                            # no year 0
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


#: Julian day number of BEFORE_PRESENT_EPOCH (1950-01-01)
_JD_BP_EPOCH = 2433283


def _before_present(ordinal, resolution):
    """Resolve "N {unit}s before present" (present = 1950, as in radiocarbon
    dating).  A result before year 1 is an ``AstroDate``, otherwise a ``date``.

    Day and week counts use Julian-day arithmetic, exact at any depth; month
    and year counts are integer arithmetic from the epoch.
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


#: unit name -> the {unit}_OF_{scope} resolution a scoped ordinal ("the 3rd
#: week of june", "the first decade of the 21st century") passes to
#: :func:`get_date_ordinal`.
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
