"""Bulgarian dates, ranges, seasons, clock, adversarial + English parity.

Bulgarian day-month-year uses a bare nominative month ("15 август 2020");
having no case system, between-ranges take that same nominative form.
"""
from datetime import timedelta

import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR, AstroDate, ad, span, start, start_end, parse, nomatch


def _d(s):
    y, m, dd = (int(x) for x in s.split("-"))
    return AstroDate(y, m, dd)


@pytest.mark.parametrize("text,y,m,d", [
    ("15 август 2020", 2020, 8, 15),
    ("3 март 1878", 1878, 3, 3),
    ("6 септември 1885", 1885, 9, 6),
    ("29 февруари 2020", 2020, 2, 29),
    ("1 януари 2000", 2000, 1, 1),
])
def test_full_date(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)


def test_full_date_is_day_wide():
    assert span("15 август 2020").width == timedelta(days=1)


@pytest.mark.parametrize("text,y,m,d", [("15 август", 2017, 8, 15),
                                        ("10 април", 2018, 4, 10)])
def test_day_month_prefer_future(text, y, m, d):
    assert start(text) == AstroDate(y, m, d)


def test_iso_and_year():
    assert start("2017-06-30") == AstroDate(2017, 6, 30)
    assert start("2019") == AstroDate(2019, 1, 1)


@pytest.mark.parametrize("text,s,e", [
    ("от юни до август", "2017-6-1", "2017-9-1"),
    ("от януари до март", "2017-1-1", "2017-4-1"),
    ("от октомври до декември", "2017-10-1", "2018-1-1"),
])
def test_from_to_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == _d(s) and ee == _d(e)


@pytest.mark.parametrize("text,s,e", [
    ("между април и юни", "2017-4-1", "2017-7-1"),
    ("между юни и септември", "2017-6-1", "2017-10-1"),
])
def test_between_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == _d(s) and ee == _d(e)


@pytest.mark.parametrize("text,s,e", [
    ("следващата зима", "2017-12-1", "2018-3-1"),
    ("лято 2020", "2020-6-1", "2020-9-1"),
    ("зима 2019", "2019-12-1", "2020-3-1"),
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
                                       ("09:30", 9, 30), ("обед", 12, 0),
                                       ("полунощ", 0, 0)])
def test_clock(text, h, mi):
    assert start(text) == clk(h, mi)


@pytest.mark.parametrize("text", ["", "   ", "здравей как си", "qwerty",
                                  "няма дата тук"])
def test_junk(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["пет дни", "две седмици", "десет години"])
def test_offset_without_marker(text):
    nomatch(text)


@pytest.mark.parametrize("text", ["25:00", "15:99", "99:99"])
def test_impossible_clock(text):
    r = parse(text)
    if r is not None:
        assert 0 <= r[0].start.hour <= 23


# Russian / Serbian-Croatian phrases must not parse as Bulgarian
@pytest.mark.parametrize("text", ["через 3 дня", "za 5 lat", "před 2 lety"])
def test_foreign_not_matched(text):
    r = parse(text)
    assert r is None or r[0].start.date() == ANCHOR.date()


def test_seconds_offset_gap():
    nomatch("след 45 секунди")


PAIRS = [
    ('15 август 2020', 'august 15 2020'),
    ('1 януари 2000', 'january 1 2000'),
    ('29 февруари 2020', 'february 29 2020'),
    ('10 април', 'april 10'),
    ('2017-06-30', '2017-06-30'),
    ('15:30', '15:30'),
    ('09:30', '09:30'),

    ("днес", "today"), ("утре", "tomorrow"), ("вчера", "yesterday"),
    ("след 3 дни", "in 3 days"), ("след 2 седмици", "in 2 weeks"),
    ("след 5 години", "in 5 years"), ("следващия петък", "next friday"),
    ("миналия вторник", "last tuesday"), ("15:30", "15:30"), ("00:00", "00:00"),
    ("обед", "noon"), ("полунощ", "midnight"), ("2019", "2019"),
    ("2017-06-30", "2017-06-30"),
    ("от юни до август", "from june to august"),
    ("между април и юни", "between april and june"),
    ("лято 2020", "summer 2020"), ("следващата зима", "next winter"),
]


@pytest.mark.parametrize("bg_text,en_text", PAIRS)
def test_span_parity(bg_text, en_text):
    bg = extract_timespan(bg_text, "bg", ANCHOR)
    en = extract_timespan(en_text, "en", ANCHOR)
    assert bg is not None and en is not None, (bg_text, en_text)
    assert bg[0].start == en[0].start and bg[0].end == en[0].end, (bg_text, en_text)
