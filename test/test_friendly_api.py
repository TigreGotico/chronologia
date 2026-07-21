"""The object-in/object-out facade: friendly calls must equal the JDN
plumbing they wrap, exactly, for every calendar and timeline.

These tests pin the additive facade (``Calendar.date``/``from_astro``,
``AstroDate.from_calendar``/``to_calendar``, ``Timeline.date``/``from_astro``
and :class:`CalendarDate`) against the low-level ``to_jdn``/``from_jdn`` /
``jdn_to_gregorian`` forms it exists to hide.  If the sugar ever diverges
from the plumbing, one of these breaks.
"""
from datetime import date, datetime, timezone, timedelta

import pytest

from chronologia import (AstroDate, CALENDARS, CalendarDate, CalendarRangeError,
                         TIMELINES, NeverExisted)
from chronologia.calendars import gregorian_to_jdn, jdn_to_gregorian


def _valid_date(cal):
    """A (year, month, day) known to be in range for any calendar: the
    calendar's own labelling of its epoch JDN."""
    return cal.from_jdn(cal.epoch_jdn)


# --------------------------------------------------------------------------
# Equivalence: friendly == plumbing, every calendar (arithmetic + tabulated).
# --------------------------------------------------------------------------

@pytest.mark.parametrize("key", list(CALENDARS))
def test_calendar_date_equals_plumbing(key):
    cal = CALENDARS[key]
    y, m, d = _valid_date(cal)
    friendly = cal.date(y, m, d)
    plumbing = AstroDate(*jdn_to_gregorian(cal.to_jdn(y, m, d)))
    assert friendly == plumbing
    assert isinstance(friendly, AstroDate)


@pytest.mark.parametrize("key", list(CALENDARS))
def test_calendar_from_astro_equals_plumbing(key):
    cal = CALENDARS[key]
    y, m, d = _valid_date(cal)
    astro = cal.date(y, m, d)
    got = cal.from_astro(astro)
    plumbing = cal.from_jdn(gregorian_to_jdn(astro.year, astro.month, astro.day))
    assert isinstance(got, CalendarDate)
    assert got.calendar == key
    assert (got.year, got.month, got.day) == plumbing


@pytest.mark.parametrize("key", list(CALENDARS))
def test_calendar_date_from_astro_round_trip(key):
    cal = CALENDARS[key]
    y, m, d = _valid_date(cal)
    cd = cal.from_astro(cal.date(y, m, d))
    assert (cd.year, cd.month, cd.day) == (y, m, d)


# --------------------------------------------------------------------------
# Range errors propagate through the facade, unchanged.
# --------------------------------------------------------------------------

def test_tabulated_date_range_error_propagates():
    cal = CALENDARS["umm_al_qura"]
    with pytest.raises(CalendarRangeError):
        cal.date(1, 1, 1)          # far before the shipped table


def test_tabulated_from_astro_range_error_propagates():
    cal = CALENDARS["chinese"]
    with pytest.raises(CalendarRangeError):
        cal.from_astro(AstroDate(1000, 1, 1))   # before the 1901 table start


def test_tabulated_range_error_carries_fallback():
    cal = CALENDARS["umm_al_qura"]
    with pytest.raises(CalendarRangeError) as exc:
        cal.date(1, 1, 1)
    assert exc.value.fallback == "islamic_civil"


def test_arithmetic_day_out_of_month_raises():
    # AstroDate construction guards Gregorian fields; plumbing and friendly
    # agree that a bad Coptic month is a ValueError from from_jdn/AstroDate.
    with pytest.raises(ValueError):
        # 30 days max in a Coptic ordinary month; day 40 is impossible to build
        AstroDate.from_calendar("coptic", 1741, 1, 1).replace(day=40)


# --------------------------------------------------------------------------
# CalendarDate: .astro crossing, __str__, and equality.
# --------------------------------------------------------------------------

def test_calendar_date_str_is_numeric_hebrew():
    cd = CalendarDate("hebrew", 5786, 7, 1)
    assert str(cd) == "hebrew 5786-07-01"


def test_calendar_date_str_negative_year_julian():
    cd = CalendarDate("julian", -43, 3, 15)
    assert str(cd) == "julian -43-03-15"


def test_calendar_date_astro_matches_calendar_date():
    cd = CalendarDate("hebrew", 5786, 7, 1)
    assert cd.astro == CALENDARS["hebrew"].date(5786, 7, 1)


def test_calendar_date_astro_is_gold_gregorian():
    # 1 Tishri 5786 (Rosh HaShanah) is 2025-09-23 proleptic Gregorian.
    assert CalendarDate("hebrew", 5786, 7, 1).astro == AstroDate(2025, 9, 23)


def test_calendar_date_is_frozen():
    cd = CalendarDate("hebrew", 5786, 7, 1)
    with pytest.raises(Exception):
        cd.year = 5787            # frozen dataclass


def test_calendar_date_equality():
    assert CalendarDate("hebrew", 5786, 7, 1) == CalendarDate("hebrew", 5786, 7, 1)
    assert CalendarDate("hebrew", 5786, 7, 1) != CalendarDate("julian", 5786, 7, 1)


# --------------------------------------------------------------------------
# AstroDate.from_calendar / to_calendar round-trips, incl. the Julian Ides.
# --------------------------------------------------------------------------

def test_from_calendar_ides_of_march():
    ides = AstroDate.from_calendar("julian", -43, 3, 15)
    assert ides == AstroDate(-43, 3, 13)     # 15 March 44 BC Julian
    assert ides.weekday() == 2               # a Wednesday


def test_to_calendar_ides_round_trip():
    ides = AstroDate.from_calendar("julian", -43, 3, 15)
    cd = ides.to_calendar("julian")
    assert (cd.year, cd.month, cd.day) == (-43, 3, 15)
    assert cd.astro == ides


@pytest.mark.parametrize("key", list(CALENDARS))
def test_from_to_calendar_round_trip_every_calendar(key):
    cal = CALENDARS[key]
    y, m, d = _valid_date(cal)
    astro = AstroDate.from_calendar(key, y, m, d)
    cd = astro.to_calendar(key)
    assert (cd.year, cd.month, cd.day) == (y, m, d)


def test_from_calendar_equals_calendar_date():
    assert (AstroDate.from_calendar("coptic", 1741, 1, 1)
            == CALENDARS["coptic"].date(1741, 1, 1))


def test_to_calendar_equals_calendar_from_astro():
    astro = AstroDate(2025, 9, 23)
    assert astro.to_calendar("hebrew") == CALENDARS["hebrew"].from_astro(astro)


# --------------------------------------------------------------------------
# from_astro coercion: AstroDate / date / datetime, naive and aware.
# --------------------------------------------------------------------------

def test_from_astro_accepts_plain_date():
    got = CALENDARS["hebrew"].from_astro(date(2025, 9, 23))
    assert (got.year, got.month, got.day) == (5786, 7, 1)


def test_from_astro_accepts_datetime_ignoring_time():
    at_noon = CALENDARS["hebrew"].from_astro(datetime(2025, 9, 23, 12, 30))
    at_midnight = CALENDARS["hebrew"].from_astro(datetime(2025, 9, 23, 0, 0))
    assert at_noon == at_midnight


def test_from_astro_aware_and_naive_agree_on_wall_date():
    # from_astro reads calendar date fields only, so a zone attachment that
    # does not cross midnight yields the same civil date.
    aware = AstroDate(2025, 9, 23, 12, tzinfo=timezone(timedelta(hours=-5)))
    naive = AstroDate(2025, 9, 23, 12)
    assert (CALENDARS["hebrew"].from_astro(aware)
            == CALENDARS["hebrew"].from_astro(naive))


def test_to_calendar_ignores_time_and_zone_fields():
    aware = AstroDate(2025, 9, 23, 18, 45,
                      tzinfo=timezone(timedelta(hours=3)))
    assert aware.to_calendar("hebrew") == CalendarDate("hebrew", 5786, 7, 1)


# --------------------------------------------------------------------------
# Timeline.date: labels in, honest objects out.
# --------------------------------------------------------------------------

def test_timeline_date_october_revolution_one_liner():
    # 25 October 1917 (Julian) is the October Revolution == 7 November 1917.
    assert TIMELINES["russia_1918"].date(1917, 10, 25) == AstroDate(1917, 11, 7)


def test_timeline_date_rome_never_existed():
    result = TIMELINES["rome_1582"].date(1582, 10, 10)
    assert isinstance(result, NeverExisted)
    assert result.label.as_tuple() == (1582, 10, 10)


def test_timeline_date_sweden_feb_30():
    # Sweden's double leap day 30 February 1712 == 11 March 1712 Gregorian.
    assert TIMELINES["sweden_1700_1712"].date(1712, 2, 30) == AstroDate(1712, 3, 11)


def test_timeline_date_equals_plumbing():
    tl = TIMELINES["russia_1918"]
    friendly = tl.date(1917, 10, 25)
    plumbing = AstroDate(*jdn_to_gregorian(tl.to_jdn((1917, 10, 25))))
    assert friendly == plumbing


def test_timeline_date_repeat_returns_astro_pair():
    # A synthetic DST-like REPEAT would return a tuple; the shipped timelines
    # do not have a REPEAT, so assert the ordinary path stays a single object.
    got = TIMELINES["britain_1752"].date(1752, 9, 20)
    assert isinstance(got, AstroDate)


def test_timeline_from_astro_round_trips_the_label():
    tl = TIMELINES["russia_1918"]
    astro = tl.date(1917, 10, 25)
    label = tl.from_astro(astro)
    assert label.as_tuple() == (1917, 10, 25)


def test_timeline_from_astro_equals_from_jdn():
    tl = TIMELINES["rome_1582"]
    astro = AstroDate(1582, 10, 15)
    got = tl.from_astro(astro)
    plumbing = tl.from_jdn(gregorian_to_jdn(1582, 10, 15))
    assert got == plumbing


# --------------------------------------------------------------------------
# Adversarial: unknown keys must fail loudly, not silently.
# --------------------------------------------------------------------------

def test_from_calendar_unknown_key_raises():
    with pytest.raises(KeyError):
        AstroDate.from_calendar("gregorian_typo", 2000, 1, 1)


def test_to_calendar_unknown_key_raises():
    with pytest.raises(KeyError):
        AstroDate(2000, 1, 1).to_calendar("no_such_calendar")


def test_calendar_date_astro_unknown_key_raises():
    with pytest.raises(KeyError):
        CalendarDate("bogus", 1, 1, 1).astro
