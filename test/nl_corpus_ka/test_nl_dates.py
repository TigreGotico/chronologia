"""Absolute dates, weekdays, named days and the day-part bands.

Dates run day-month-year (CLDR ka's long pattern is "d MMMM, y") and the
month name does not inflect.  The weekday names are transparently
compositional -- ორშაბათი is "two-Sabbath", the second day of the week -- and
the day-naming series reaches THREE days out on each side of today, one step
further than most languages: გუშინწინ, გუშინ, დღეს, ხვალ, ზეგ, მაზეგ.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, remainder, start, start_end


@pytest.mark.parametrize("text,y,m,d", [
    ("5 ივნისი 2020", 2020, 6, 5),
    ("12 იანვარი 1999", 1999, 1, 12),
    ("31 დეკემბერი 2000", 2000, 12, 31),
    ("1 მარტი 2018", 2018, 3, 1),
    ("20 ოქტომბერი 2021", 2021, 10, 20),
    ("8 აგვისტო 2019", 2019, 8, 8),
])
def test_day_month_year(text, y, m, d):
    s, e = start_end(text)
    assert (s.year, s.month, s.day) == (y, m, d)
    assert e - s == timedelta(days=1)


@pytest.mark.parametrize("text,y,m,d", [
    ("5 ივნ 2020", 2020, 6, 5),
    ("12 იან 1999", 1999, 1, 12),
    ("3 სექ 2005", 2005, 9, 3),
])
def test_abbreviated_months(text, y, m, d):
    s = start(text)
    assert (s.year, s.month, s.day) == (y, m, d)


@pytest.mark.parametrize("text,m,d", [
    ("ხუთი ივნისი", 6, 5),
    ("ოცდაათი აპრილი", 4, 30),
    ("თხუთმეტი ნოემბერი", 11, 15),
])
def test_spelled_day_of_month(text, m, d):
    """The day may be spelled, vigesimal compounds included."""
    s = start(text)
    assert (s.month, s.day) == (m, d)


@pytest.mark.parametrize("text,weekday", [
    ("ორშაბათი", 0), ("სამშაბათი", 1), ("ოთხშაბათი", 2), ("ხუთშაბათი", 3),
    ("პარასკევი", 4), ("შაბათი", 5), ("კვირა", 6),
])
def test_weekday_names_its_next_occurrence(text, weekday):
    s = start(text)
    assert s.weekday() == weekday
    assert ad(ANCHOR) <= s <= ad(ANCHOR + timedelta(days=7))


@pytest.mark.parametrize("text,offset", [
    ("გუშინწინისწინ", -3),
    ("გუშინწინ", -2),
    ("გუშინ", -1),
    ("დღეს", 0),
    ("ხვალ", 1),
    ("ზეგ", 2),
    ("მაზეგ", 3),
])
def test_named_days_reach_three_out(text, offset):
    day = (ANCHOR + timedelta(days=offset)).replace(hour=0, minute=0)
    s, e = start_end(text)
    assert s == ad(day)
    assert e - s == timedelta(days=1)


@pytest.mark.parametrize("text,h0,h1", [
    ("დილა", 5, 12),
    ("დილით", 5, 12),
    ("ნაშუადღევი", 12, 18),
    ("ნაშუადღევს", 12, 18),
    ("საღამო", 18, 21),
    ("საღამოს", 18, 21),
])
def test_daypart_bands(text, h0, h1):
    """CLDR ka opens the morning at 05:00 and closes the evening at 21:00 --
    both boundaries differ from the library's English default, so a band read
    off the wrong locale row would land an hour or three out."""
    s, e = start_end(text)
    assert (s.hour, e.hour) == (h0, h1)
    assert s.date() == ANCHOR.date()


@pytest.mark.parametrize("text", ["ღამე", "ღამით"])
def test_night_wraps_past_midnight(text):
    s, e = start_end(text)
    assert s.hour == 21
    assert e.hour == 5
    assert e.day != s.day


@pytest.mark.parametrize("text,year", [
    ("2020", 2020), ("1999", 1999), ("2031", 2031),
])
def test_bare_year(text, year):
    s, e = start_end(text)
    assert (s.year, s.month, s.day) == (year, 1, 1)
    assert e.year == year + 1


@pytest.mark.parametrize("text", ["", "   ", "გამარჯობა", "qwerty zxcvb"])
def test_junk_is_not_a_date(text):
    from ._corpus import nomatch
    nomatch(text)


def test_month_name_is_read_whole():
    assert remainder("5 ივნისი 2020") == ""
