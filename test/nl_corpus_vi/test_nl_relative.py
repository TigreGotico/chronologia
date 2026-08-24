"""Offsets, whose marker sits on either side of the duration it counts.

trước ("before, ago") and sau ("after, later") TRAIL the counted duration --
ba ngày trước is three days ago -- while cách đây, the dedicated ago-adverb,
LEADS it: cách đây ba ngày.  Both orders name the same span, and the marker's
side is a property of the word, so a locale-wide "markers go last" rule would
lose one of them.

Nothing agrees with the count: ngày is ngày whether one day or ninety pass,
which is what an isolating language gives instead of the declension tables the
Icelandic and Baltic corpora exercise.

Expected dates are computed here with ``timedelta``/``relativedelta``, never
read back from the extractor.
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, start


@pytest.mark.parametrize("text,days", [
    ("một ngày trước", 1),
    ("hai ngày trước", 2),
    ("ba ngày trước", 3),
    ("bốn ngày trước", 4),
    ("năm ngày trước", 5),
    ("sáu ngày trước", 6),
    ("bảy ngày trước", 7),
    ("tám ngày trước", 8),
    ("chín ngày trước", 9),
    ("mười ngày trước", 10),
    ("mười lăm ngày trước", 15),
    ("hai mươi ngày trước", 20),
    ("hai mươi mốt ngày trước", 21),
    ("hai mươi tư ngày trước", 24),
    ("hai mươi lăm ngày trước", 25),
    ("ba mươi ngày trước", 30),
    ("7 ngày trước", 7),
])
def test_days_ago_trailing_marker(text, days):
    assert start(text) == ad(ANCHOR - timedelta(days=days))


@pytest.mark.parametrize("text,days", [
    ("cách đây một ngày", 1),
    ("cách đây ba ngày", 3),
    ("cách đây năm ngày", 5),
    ("cách đây mười ngày", 10),
    ("cách đây hai mươi ngày", 20),
    ("cách đây 12 ngày", 12),
])
def test_days_ago_leading_marker(text, days):
    assert start(text) == ad(ANCHOR - timedelta(days=days))


@pytest.mark.parametrize("text,days", [
    ("hai ngày sau", 2),
    ("ba ngày sau", 3),
    ("chín ngày sau", 9),
    ("hai mươi mốt ngày sau", 21),
    ("4 ngày sau", 4),
])
def test_days_ahead(text, days):
    assert start(text) == ad(ANCHOR + timedelta(days=days))


@pytest.mark.parametrize("text,months", [
    ("một tháng trước", 1),
    ("ba tháng trước", 3),
    ("sáu tháng trước", 6),
    ("mười hai tháng trước", 12),
])
def test_months_ago(text, months):
    assert start(text) == ad(ANCHOR - relativedelta(months=months))


@pytest.mark.parametrize("text,months", [
    ("hai tháng sau", 2),
    ("năm tháng sau", 5),
])
def test_months_ahead(text, months):
    assert start(text) == ad(ANCHOR + relativedelta(months=months))


@pytest.mark.parametrize("text,years", [
    ("hai năm trước", 2),
    ("năm năm trước", 5),
    ("mười năm trước", 10),
    ("một trăm năm trước", 100),
])
def test_years_ago(text, years):
    assert start(text) == ad(ANCHOR - relativedelta(years=years))


@pytest.mark.parametrize("text,weeks", [
    ("một tuần trước", 1),
    ("hai tuần trước", 2),
    ("năm tuần trước", 5),
])
def test_weeks_ago(text, weeks):
    assert start(text) == ad(ANCHOR - timedelta(weeks=weeks))


@pytest.mark.parametrize("text,minutes", [
    ("năm phút trước", 5),
    ("mười lăm phút trước", 15),
    ("hai mươi lăm phút trước", 25),
    ("bốn mươi phút trước", 40),
])
def test_minutes_ago(text, minutes):
    assert start(text) == ad(ANCHOR - timedelta(minutes=minutes))


@pytest.mark.parametrize("text,y,m", [
    ("tháng trước", 2017, 5),
    ("tháng sau", 2017, 7),
])
def test_relative_month(text, y, m):
    s = start(text)
    assert (s.year, s.month, s.day) == (y, m, 1)


@pytest.mark.parametrize("text,year", [
    ("năm trước", 2016),
    ("năm sau", 2018),
])
def test_relative_year(text, year):
    s = start(text)
    assert (s.year, s.month, s.day) == (year, 1, 1)


@pytest.mark.parametrize("text,monday", [
    ("tuần trước", ANCHOR.date() - timedelta(days=8)),
    ("tuần sau", ANCHOR.date() + timedelta(days=6)),
])
def test_relative_week_starts_on_monday(text, monday):
    s = start(text)
    assert (s.year, s.month, s.day) == (monday.year, monday.month, monday.day)
