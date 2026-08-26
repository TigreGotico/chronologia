"""Relative time: the counted offsets, the deictic days and the periods."""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, day, nomatch, parse, span, start_end  # noqa: F401


@pytest.mark.parametrize("text,delta", [
    ("3일 전", timedelta(days=-3)),
    ("2주 전", timedelta(weeks=-2)),
    ("10분 전", timedelta(minutes=-10)),
    ("30초 전", timedelta(seconds=-30)),
    ("5시간 전", timedelta(hours=-5)),
    ("일주일 전", timedelta(weeks=-1)),
])
def test_a_counted_offset_backward(text, delta):
    assert span(text).start == _ad(ANCHOR + delta)


@pytest.mark.parametrize("text,delta", [
    ("3일 후", timedelta(days=3)),
    ("2주 후", timedelta(weeks=2)),
    ("45분 후", timedelta(minutes=45)),
    ("2시간 후", timedelta(hours=2)),
])
def test_a_counted_offset_forward(text, delta):
    assert span(text).start == _ad(ANCHOR + delta)


def _ad(dt):
    from chronologia.astrodate import AstroDate
    return AstroDate(dt.year, dt.month, dt.day, dt.hour, dt.minute,
                     dt.second, dt.microsecond)


@pytest.mark.parametrize("text,years", [("2년 전", -2), ("11년 전", -11)])
def test_a_counted_year_offset(text, years):
    assert span(text).start.year == ANCHOR.year + years


@pytest.mark.parametrize("text,months", [("3개월 전", -3), ("6개월 후", 6)])
def test_the_counted_month_is_gaewol_not_wol(text, months):
    """개월 counts months; 월 labels them.  Both are grammatical in the same
    slot and one produces a duration where the other produces a date, so
    3개월 전 is three months back and 3월 is March."""
    got = span(text).start
    total = (ANCHOR.year * 12 + ANCHOR.month - 1) + months
    assert (got.year, got.month) == (total // 12, total % 12 + 1)


def test_a_month_count_and_a_month_label_are_not_the_same_reading():
    assert start_end("3개월 전") != start_end("3월")


@pytest.mark.parametrize("text,offset", [
    ("오늘", 0), ("내일", 1), ("어제", -1), ("모레", 2), ("그저께", -2),
    ("글피", 3), ("그끄저께", -3),
])
def test_the_deictic_days(text, offset):
    d = ANCHOR + timedelta(days=offset)
    assert start_end(text) == day(d.year, d.month, d.day)


@pytest.mark.parametrize("text,expected", [
    ("작년", (2026, 1, 1)), ("올해", (2027, 1, 1)), ("내년", (2028, 1, 1)),
])
def test_the_lexical_year_periods(text, expected):
    """CLDR spells last/this/next year as three suppletive single words, not
    as a determiner plus a unit."""
    s, _ = start_end(text)
    assert (s.year, s.month, s.day) == expected


@pytest.mark.parametrize("text,month", [
    ("지난달", 4), ("이번 달", 5), ("다음 달", 6),
])
def test_the_month_periods(text, month):
    """지난달 is written as one word and 이번 달 / 다음 달 as two -- the
    spelling CLDR carries, and both have to read."""
    s, _ = start_end(text)
    assert (s.year, s.month, s.day) == (2027, month, 1)


@pytest.mark.parametrize("text,monday", [
    ("지난주", datetime(2027, 5, 3)),
    ("이번 주", datetime(2027, 5, 10)),
    ("다음 주", datetime(2027, 5, 17)),
])
def test_the_week_periods(text, monday):
    s, e = start_end(text)
    assert (s.year, s.month, s.day) == (monday.year, monday.month, monday.day)
    assert (e - s).days == 7


@pytest.mark.parametrize("text", ["다음주", "이번주"])
def test_the_week_periods_written_as_one_word(text):
    """Standard orthography spaces these two and fuses 지난주, but the fused
    spelling is ordinary in running text, so both are read."""
    assert parse(text) is not None


@pytest.mark.parametrize("text", ["전", "후", "지난", "다음", "이번"])
def test_a_lone_marker_is_not_a_date(text):
    nomatch(text)
