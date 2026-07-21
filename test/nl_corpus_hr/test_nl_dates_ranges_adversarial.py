"""Croatian dates, ranges, seasons, clock, adversarial + English parity."""
from datetime import timedelta

import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR, AstroDate, ad, span, start, start_end, parse, nomatch


def _d(s):
    y, m, dd = (int(x) for x in s.split("-"))
    return AstroDate(y, m, dd)


@pytest.mark.parametrize("text,y,m,d", [
    ("3. siječnja 2020", 2020, 1, 3),
    ("15. kolovoza 2020", 2020, 8, 15),
    ("25. lipnja 1991", 1991, 6, 25),
    ("29. veljače 2020", 2020, 2, 29),
    ("1. svibnja 1945", 1945, 5, 1),
])
def test_full_date(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)


def test_full_date_is_day_wide():
    assert span("15. kolovoza 2020").width == timedelta(days=1)


@pytest.mark.parametrize("text,y,m,d", [("15. kolovoza", 2017, 8, 15),
                                        ("10. travnja", 2018, 4, 10)])
def test_day_month_prefer_future(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)


def test_iso_and_year():
    assert start("2017-06-30") == AstroDate(2017, 6, 30)
    assert start("2019") == AstroDate(2019, 1, 1)


@pytest.mark.parametrize("text,s,e", [
    ("od lipnja do rujna", "2017-6-1", "2017-10-1"),
    ("od siječnja do ožujka", "2017-1-1", "2017-4-1"),
    ("od listopada do prosinca", "2017-10-1", "2018-1-1"),
])
def test_from_to_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == _d(s) and ee == _d(e)


@pytest.mark.parametrize("text,s,e", [
    ("između travnja i lipnja", "2017-4-1", "2017-7-1"),
    ("između lipnja i rujna", "2017-6-1", "2017-10-1"),
])
def test_between_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == _d(s) and ee == _d(e)


@pytest.mark.parametrize("text,s,e", [
    ("sljedeća zima", "2017-12-1", "2018-3-1"),
    ("ljeto 2020", "2020-6-1", "2020-9-1"),
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
                                       ("09:30", 9, 30), ("podne", 12, 0),
                                       ("ponoć", 0, 0)])
def test_clock(text, h, mi):
    assert start(text) == clk(h, mi)


# -- adversarial ---------------------------------------------------------

@pytest.mark.parametrize("text", ["", "   ", "bok kako si", "qwerty",
                                  "nema datuma ovdje"])
def test_junk(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["pet dana", "dva tjedna", "deset godina"])
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
    nomatch("za 45 sekundi")


def test_halfto_idiom_gap():
    # "pola deset" = 9:30 (half-TO ten); no direction word -> not 10:30
    r = parse("pola deset")
    if r is not None:
        assert (r[0].start.hour, r[0].start.minute) != (10, 30)


# -- English semantic parity ---------------------------------------------

PAIRS = [
    ('15. kolovoza 2020', 'august 15 2020'),
    ('1. svibnja 1945', 'may 1 1945'),
    ('10. travnja', 'april 10'),
    ('2017-06-30', '2017-06-30'),
    ('15:30', '15:30'),
    ('09:30', '09:30'),
    ('15. kolovoza', 'august 15'),

    ("danas", "today"), ("sutra", "tomorrow"), ("jučer", "yesterday"),
    ("za 3 dana", "in 3 days"), ("za 2 tjedna", "in 2 weeks"),
    ("za 5 godina", "in 5 years"), ("sljedeći petak", "next friday"),
    ("prošli utorak", "last tuesday"), ("15:30", "15:30"), ("00:00", "00:00"),
    ("podne", "noon"), ("ponoć", "midnight"), ("2019", "2019"),
    ("2017-06-30", "2017-06-30"),
    ("od lipnja do rujna", "from june to september"),
    ("između travnja i lipnja", "between april and june"),
    ("ljeto 2020", "summer 2020"), ("sljedeća zima", "next winter"),
]


@pytest.mark.parametrize("hr_text,en_text", PAIRS)
def test_span_parity(hr_text, en_text):
    hr = extract_timespan(hr_text, "hr", ANCHOR)
    en = extract_timespan(en_text, "en", ANCHOR)
    assert hr is not None and en is not None, (hr_text, en_text)
    assert hr[0].start == en[0].start and hr[0].end == en[0].end, (hr_text, en_text)
