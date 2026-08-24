"""Absolute dates, numbered months, numbered weekdays and the named days.

Both calendar series are numbered rather than named.  A month is tháng plus
its number, written either spelled (tháng ba) or, exactly as CLDR gives it,
with a digit (tháng 3) -- one construction in two spellings, not a name and an
abbreviation of it.  A weekday is thứ plus its number, counted from the one
day that is named instead, chủ nhật, so Monday is thứ hai.

Dates run day-month-year and may carry the bare nouns ngày and năm in front of
the day and the year.
"""
from datetime import timedelta

import pytest

from ._corpus import remainder, start, start_end


@pytest.mark.parametrize("text,y,m,d", [
    ("5 tháng 3 năm 2020", 2020, 3, 5),
    ("12 tháng 1 năm 1999", 1999, 1, 12),
    ("31 tháng 12 năm 2000", 2000, 12, 31),
    ("1 tháng 3 năm 2018", 2018, 3, 1),
    ("20 tháng 10 năm 2021", 2021, 10, 20),
    ("8 tháng 8 năm 2019", 2019, 8, 8),
])
def test_day_month_year(text, y, m, d):
    s, e = start_end(text)
    assert (s.year, s.month, s.day) == (y, m, d)
    assert e - s == timedelta(days=1)


@pytest.mark.parametrize("text,y,m,d", [
    ("ngày 5 tháng 6 năm 2020", 2020, 6, 5),
    ("ngày 25 tháng 12 năm 1999", 1999, 12, 25),
    ("ngày 1 tháng 1 năm 2000", 2000, 1, 1),
])
def test_day_noun_leads_the_date(text, y, m, d):
    s = start(text)
    assert (s.year, s.month, s.day) == (y, m, d)


@pytest.mark.parametrize("text,y,m,d", [
    ("5 thg 3 năm 2020", 2020, 3, 5),
    ("18 thg 9 năm 2011", 2011, 9, 18),
])
def test_abbreviated_month(text, y, m, d):
    s = start(text)
    assert (s.year, s.month, s.day) == (y, m, d)


@pytest.mark.parametrize("text,month", [
    ("tháng một", 1), ("tháng hai", 2), ("tháng ba", 3), ("tháng tư", 4),
    ("tháng năm", 5), ("tháng sáu", 6), ("tháng bảy", 7), ("tháng tám", 8),
    ("tháng chín", 9), ("tháng mười", 10), ("tháng mười một", 11),
    ("tháng mười hai", 12),
])
def test_spelled_months(text, month):
    s = start(text)
    assert (s.month, s.day) == (month, 1)


@pytest.mark.parametrize("text,month", [
    ("tháng 1", 1), ("tháng 4", 4), ("tháng 9", 9), ("tháng 12", 12),
])
def test_digit_months(text, month):
    s = start(text)
    assert (s.month, s.day) == (month, 1)


@pytest.mark.parametrize("text,month", [
    ("tháng giêng", 1),
    ("tháng chạp", 12),
])
def test_lunar_flavoured_month_alternates(text, month):
    s = start(text)
    assert (s.month, s.day) == (month, 1)


@pytest.mark.parametrize("text,y,m,d", [
    ("thứ hai", 2017, 7, 3),
    ("thứ ba", 2017, 7, 4),
    ("thứ tư", 2017, 6, 28),
    ("thứ năm", 2017, 6, 29),
    ("thứ sáu", 2017, 6, 30),
    ("thứ bảy", 2017, 7, 1),
    ("chủ nhật", 2017, 7, 2),
])
def test_spelled_weekdays_from_a_tuesday_anchor(text, y, m, d):
    s = start(text)
    assert (s.year, s.month, s.day) == (y, m, d)


@pytest.mark.parametrize("text,y,m,d", [
    ("thứ 2", 2017, 7, 3),
    ("thứ 4", 2017, 6, 28),
    ("thứ 7", 2017, 7, 1),
])
def test_digit_weekdays_name_the_same_days(text, y, m, d):
    s = start(text)
    assert (s.year, s.month, s.day) == (y, m, d)


@pytest.mark.parametrize("text,y,m,d", [
    ("hôm nay", 2017, 6, 27),
    ("hôm qua", 2017, 6, 26),
    ("ngày mai", 2017, 6, 28),
    ("mai", 2017, 6, 28),
])
def test_named_days(text, y, m, d):
    s, e = start_end(text)
    assert (s.year, s.month, s.day) == (y, m, d)
    assert e - s == timedelta(days=1)


@pytest.mark.parametrize("text,year", [
    ("năm 2020", 2020),
    ("năm 1999", 1999),
    ("2020", 2020),
])
def test_year_reference(text, year):
    s, e = start_end(text)
    assert (s.year, s.month, s.day) == (year, 1, 1)
    assert e.year == year + 1


@pytest.mark.parametrize("text", [
    "5 tháng 3 năm 2020", "ngày 5 tháng 6 năm 2020", "thứ hai", "tháng tư",
    "hôm kia", "ngày kia", "hai giờ rưỡi", "ba giờ kém mười lăm",
])
def test_whole_phrase_is_consumed(text):
    assert remainder(text) == ""
