"""Czech prepositions that belong to the date or clock they introduce.

"v 15:00" (at 15:00), "na zítra" (for tomorrow), "na pátek" (for Friday) and
"v pátek příští týden" (on Friday next week) name the same instant as the bare
phrase; the preposition is part of the match and never left in the remainder.
"dneska" is the colloquial "dnes", so "co je dneska za den v týdnu" asks about
today and "za den" is the question word "co ... za", not "in a day".

Anchor: Tuesday 2017-06-27 13:04.  Every gold value is read off a calendar.
"""
from datetime import date, datetime, timedelta

import pytest

from ._corpus import parse, span


def _day(y, m, d):
    return datetime(y, m, d)


def test_dneska_is_today():
    s = span("dneska")
    assert (s.start, s.end) == (_day(2017, 6, 27), _day(2017, 6, 28))


def test_dneska_za_den_asks_about_today_not_in_a_day():
    r = parse("co je dneska za den v týdnu")
    assert r[0].start == _day(2017, 6, 27)
    assert r[0].end == _day(2017, 6, 28)
    assert r[1] == "co je za den v týdnu"


@pytest.mark.parametrize("text,remainder", [
    ("v 15:00", ""),
    ("ve 15:00", ""),
    ("sejdeme se v 15:00", "sejdeme se"),
    ("v 15:30", ""),
])
def test_clock_consumes_its_at_preposition(text, remainder):
    r = parse(text)
    assert r[1] == remainder
    hh, mm = (15, 30) if text.endswith("15:30") else (15, 0)
    assert r[0].start == datetime(2017, 6, 27, hh, mm)


def test_v_pul_devate_consumes_the_preposition():
    r = parse("v půl deváté")
    assert r[1] == ""
    # 08:30 has passed at 13:04, so the next one is tomorrow's
    assert r[0].start == datetime(2017, 6, 28, 8, 30)


@pytest.mark.parametrize("text,day", [
    ("na zítra", date(2017, 6, 28)),
    ("na pátek", date(2017, 6, 30)),
    ("v pátek", date(2017, 6, 30)),
])
def test_for_and_on_prepositions_before_a_day_are_consumed(text, day):
    r = parse(text)
    assert r[1] == ""
    assert r[0].start == datetime(day.year, day.month, day.day)


@pytest.mark.parametrize("text,remainder", [
    ("v pátek příští týden", ""),
    ("na pátek příští týden", ""),
    ("sejdeme se v pátek příští týden", "sejdeme se"),
])
def test_weekday_of_next_week_consumes_its_preposition(text, remainder):
    r = parse(text)
    assert r[1] == remainder
    # week of Tue 2017-06-27 starts Mon 06-26; next week starts Mon 07-03
    assert r[0].start == datetime(2017, 7, 7)


def test_weekday_of_next_week_from_a_sunday():
    sunday = datetime(2017, 7, 2, 10, 0)
    assert sunday.weekday() == 6
    r = parse("v pátek příští týden", sunday)
    # Sunday ends the week that began Mon 06-26; next week begins Mon 07-03
    assert r[0].start == datetime(2017, 7, 3) + timedelta(days=4)
    assert r[1] == ""
