"""Welsh relative time: offsets in both directions, periods and weekdays.

The two offset markers sit on opposite sides of their quantity.  "ymhen"
(within, after a period) LEADS it -- "ymhen tair blynedd" is in three years --
while "yn ôl" (ago) TRAILS it -- "tri diwrnod yn ôl" is three days back.  The
relative markers "nesaf" (next), "diwethaf" (last) and the demonstratives
"hwn"/"hon" (this) all trail their noun too, so a Welsh period phrase reads
article-noun-marker throughout.

Every expected value is computed here from the anchor with plain date
arithmetic, never read back from the parser.
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, nomatch, remainder, span, start


@pytest.mark.parametrize("text,days", [
    ("ymhen diwrnod", 1),
    ("ymhen dau ddiwrnod", 2),
    ("ymhen tri diwrnod", 3),
    ("ymhen pedwar diwrnod", 4),
    ("ymhen deg diwrnod", 10),
    ("ymhen deunaw diwrnod", 18),
    ("ymhen un deg wyth diwrnod", 18),
    ("ymhen ugain diwrnod", 20),
])
def test_offset_forward_in_days(text, days):
    assert start(text) == ad(ANCHOR + timedelta(days=days))


@pytest.mark.parametrize("text,days", [
    ("diwrnod yn ôl", 1),
    ("dau ddiwrnod yn ôl", 2),
    ("tri diwrnod yn ôl", 3),
    ("saith diwrnod yn ôl", 7),
    ("deg diwrnod yn ôl", 10),
    ("pymtheg diwrnod yn ôl", 15),
])
def test_offset_back_in_days(text, days):
    assert start(text) == ad(ANCHOR - timedelta(days=days))


@pytest.mark.parametrize("text,minutes", [
    ("ymhen pum munud", 5), ("ymhen deg munud", 10),
    ("ymhen ugain munud", 20), ("ymhen deugain munud", 40),
])
def test_offset_forward_in_minutes(text, minutes):
    assert start(text) == ad(ANCHOR + timedelta(minutes=minutes))


@pytest.mark.parametrize("text,hours", [
    ("ymhen awr", 1), ("ymhen dwy awr", 2), ("ymhen tair awr", 3),
    ("ymhen chwe awr", 6),
])
def test_offset_forward_in_hours(text, hours):
    assert start(text) == ad(ANCHOR + timedelta(hours=hours))


@pytest.mark.parametrize("text,weeks", [
    ("ymhen wythnos", 1), ("ymhen dwy wythnos", 2), ("ymhen tair wythnos", 3),
])
def test_offset_forward_in_weeks(text, weeks):
    assert start(text) == ad(ANCHOR + timedelta(weeks=weeks))


@pytest.mark.parametrize("text,months", [
    ("ymhen mis", 1), ("ymhen dau fis", 2), ("ymhen tri mis", 3),
    ("ymhen chwe mis", 6),
])
def test_offset_forward_in_months(text, months):
    assert start(text) == ad(ANCHOR + relativedelta(months=months))


@pytest.mark.parametrize("text,years", [
    ("ymhen blwyddyn", 1),
    ("ymhen dwy flynedd", 2),
    ("ymhen tair blynedd", 3),
    ("ymhen pum mlynedd", 5),
    ("ymhen deng mlynedd", 10),
])
def test_offset_forward_in_years(text, years):
    assert start(text) == ad(ANCHOR + relativedelta(years=years))


@pytest.mark.parametrize("text,years", [
    ("blwyddyn yn ôl", 1),
    ("dwy flynedd yn ôl", 2),
    ("tair blynedd yn ôl", 3),
    ("pum mlynedd yn ôl", 5),
    ("deng mlynedd yn ôl", 10),
    ("ugain mlynedd yn ôl", 20),
])
def test_offset_back_in_years(text, years):
    assert start(text) == ad(ANCHOR - relativedelta(years=years))


def test_the_two_offset_markers_point_opposite_ways():
    assert start("tair blynedd yn ôl") < ad(ANCHOR) < start("ymhen tair blynedd")


@pytest.mark.parametrize("text", [
    "ymhen tair blynedd", "tri diwrnod yn ôl", "dwy flynedd yn ôl",
])
def test_offset_consumes_everything(text):
    assert remainder(text) == ""


#: the anchor Tuesday's own calendar week, Monday to Monday.
_THIS_WEEK = ANCHOR.date() - timedelta(days=ANCHOR.weekday())


@pytest.mark.parametrize("text,weeks", [
    ("yr wythnos hon", 0), ("yr wythnos nesaf", 1),
    ("yr wythnos diwethaf", -1), ("wythnos nesaf", 1),
])
def test_relative_week(text, weeks):
    s = span(text)
    expected = _THIS_WEEK + timedelta(weeks=weeks)
    assert (s.start.year, s.start.month, s.start.day) == (
        expected.year, expected.month, expected.day)


@pytest.mark.parametrize("text,y,m", [
    ("y mis hwn", 2017, 6), ("y mis nesaf", 2017, 7),
    ("y mis diwethaf", 2017, 5),
])
def test_relative_month(text, y, m):
    s = span(text)
    assert (s.start.year, s.start.month, s.start.day) == (y, m, 1)


@pytest.mark.parametrize("text,y", [
    ("y flwyddyn hon", 2017), ("y flwyddyn nesaf", 2018),
    ("y flwyddyn diwethaf", 2016),
])
def test_relative_year(text, y):
    s = span(text)
    assert (s.start.year, s.start.month, s.start.day) == (y, 1, 1)


#: the anchor is a Tuesday; weekday 0 is Monday.
@pytest.mark.parametrize("text,weekday", [
    ("dydd Llun", 0), ("dydd Mawrth", 1), ("dydd Mercher", 2),
    ("dydd Iau", 3), ("dydd Gwener", 4), ("dydd Sadwrn", 5), ("dydd Sul", 6),
])
def test_bare_weekday_resolves_forward(text, weekday):
    s = start(text)
    ahead = (weekday - ANCHOR.weekday()) % 7 or 7
    expected = ANCHOR.date() + timedelta(days=ahead)
    assert (s.year, s.month, s.day) == (expected.year, expected.month,
                                        expected.day)


@pytest.mark.parametrize("text,weekday", [
    ("ddydd Llun", 0), ("ddydd Gwener", 4), ("ddydd Sul", 6),
])
def test_mutated_weekday_head_resolves_the_same(text, weekday):
    """"ar ddydd Llun" is how a Welsh sentence says "on Monday"; the head noun
    carries the mutation and the day is unchanged."""
    ahead = (weekday - ANCHOR.weekday()) % 7 or 7
    expected = ANCHOR.date() + timedelta(days=ahead)
    s = start(text)
    assert (s.year, s.month, s.day) == (expected.year, expected.month,
                                        expected.day)


@pytest.mark.parametrize("text,days", [
    ("heddiw", 0), ("yfory", 1), ("ddoe", -1), ("echdoe", -2), ("fory", 1),
])
def test_named_days(text, days):
    expected = ANCHOR.date() + timedelta(days=days)
    s = start(text)
    assert (s.year, s.month, s.day) == (expected.year, expected.month,
                                        expected.day)


@pytest.mark.parametrize("text", ["nesaf", "diwethaf", "hwn", "ymhen ymhen"])
def test_a_bare_marker_is_not_a_time(text):
    nomatch(text)
