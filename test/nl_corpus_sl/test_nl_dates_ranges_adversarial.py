"""Slovenian dates, ranges, seasons, clock, adversarial + English parity."""
from datetime import timedelta

import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR, AstroDate, ad, span, start, start_end, parse, nomatch


def _d(s):
    y, m, dd = (int(x) for x in s.split("-"))
    return AstroDate(y, m, dd)


@pytest.mark.parametrize("text,y,m,d", [
    ("3. januarja 2020", 2020, 1, 3),
    ("15. avgusta 2020", 2020, 8, 15),
    ("25. junija 1991", 1991, 6, 25),
    ("29. februarja 2020", 2020, 2, 29),
    ("1. maja 1945", 1945, 5, 1),
])
def test_full_date(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)


def test_full_date_is_day_wide():
    assert span("15. avgusta 2020").width == timedelta(days=1)


@pytest.mark.parametrize("text,y,m,d", [("15. avgusta", 2017, 8, 15),
                                        ("10. aprila", 2018, 4, 10)])
def test_day_month_prefer_future(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)


def test_iso_and_year():
    assert start("2017-06-30") == AstroDate(2017, 6, 30)
    assert start("2019") == AstroDate(2019, 1, 1)


@pytest.mark.parametrize("text,s,e", [
    ("od junija do avgusta", "2017-6-1", "2017-9-1"),
    ("od januarja do marca", "2017-1-1", "2017-4-1"),
    ("od oktobra do decembra", "2017-10-1", "2018-1-1"),
])
def test_from_to_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == _d(s) and ee == _d(e)


@pytest.mark.parametrize("text,s,e", [
    ("med aprilom in junijem", "2017-4-1", "2017-7-1"),
    ("med junijem in septembrom", "2017-6-1", "2017-10-1"),
])
def test_between_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == _d(s) and ee == _d(e)


@pytest.mark.parametrize("text,s,e", [
    ("naslednja zima", "2017-12-1", "2018-3-1"),
    ("poletje 2020", "2020-6-1", "2020-9-1"),
    ("zima 2019", "2019-12-1", "2020-3-1"),
])
def test_season(text, s, e):
    ss, ee = start_end(text)
    assert ss == _d(s) and ee == _d(e)


def clk(h, mi):
    dt = ANCHOR.replace(hour=h, minute=mi, second=0, microsecond=0)
    if dt < ANCHOR:
        dt += timedelta(days=1)
    return ad(dt)


@pytest.mark.parametrize("text,h,mi", [("15:30", 15, 30), ("00:00", 0, 0),
                                       ("09:30", 9, 30), ("poldne", 12, 0),
                                       ("polnoč", 0, 0)])
def test_clock(text, h, mi):
    assert start(text) == clk(h, mi)


@pytest.mark.parametrize("text", ["", "   ", "živjo kako si", "qwerty",
                                  "ni datuma tukaj"])
def test_junk(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["pet dni", "dva tedna", "deset let"])
def test_offset_without_marker(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["25:00", "15:99", "99:99"])
def test_impossible_clock(text):
    r = parse(text)
    if r is not None:
        assert 0 <= r[0].start.hour <= 23


@pytest.mark.parametrize("text", ["před 2 lety", "через 3 дня", "za 5 lat"])
def test_foreign_not_matched(text):
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


def test_seconds_offset_gap():
    nomatch("čez 45 sekund")


PAIRS = [
    ("danes", "today"), ("jutri", "tomorrow"), ("včeraj", "yesterday"),
    ("čez 3 dni", "in 3 days"), ("čez 2 tedna", "in 2 weeks"),
    ("čez 5 let", "in 5 years"), ("naslednji petek", "next friday"),
    ("prejšnji torek", "last tuesday"), ("15:30", "15:30"), ("00:00", "00:00"),
    ("poldne", "noon"), ("polnoč", "midnight"), ("2019", "2019"),
    ("2017-06-30", "2017-06-30"),
    ("od junija do avgusta", "from june to august"),
    ("med aprilom in junijem", "between april and june"),
    ("poletje 2020", "summer 2020"), ("naslednja zima", "next winter"),
]


@pytest.mark.parametrize("sl_text,en_text", PAIRS)
def test_span_parity(sl_text, en_text):
    sl = extract_timespan(sl_text, "sl", ANCHOR)
    en = extract_timespan(en_text, "en", ANCHOR)
    assert sl is not None and en is not None, (sl_text, en_text)
    assert sl[0].start == en[0].start and sl[0].end == en[0].end, (sl_text, en_text)
