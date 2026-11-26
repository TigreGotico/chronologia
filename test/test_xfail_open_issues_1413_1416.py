"""Strict xfails for open issues 1413, 1415 and 1416.

Each row asserts the value the issue expects. Strict mode turns the run red
when a fix lands, so the fix removes the mark from its rows. Issue 1414 is a
speed defect and has no row here.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2026, 11, 25, 10, 0)
URL = "https://github.com/TigreGotico/chronologia/issues/"


def xfail(issue):
    return pytest.mark.xfail(strict=True, reason=URL + str(issue))


def start(text):
    return extract_timespan(text, "en", ANCHOR).span.start.datetime()


@pytest.mark.parametrize("text,day", [
    ("the last business day of december 9999", datetime(9999, 12, 31)),
    ("the first business day of january 0001", datetime(1, 1, 1)),
])
def test_a_business_day_at_the_calendar_edge(text, day):
    assert start(text) == day


@xfail(1415)
def test_business_days_ago_count_back():
    result = extract_timespan("5 business days ago", "en", ANCHOR)
    assert result.span.start.datetime() == datetime(2026, 11, 18)
    assert result.remainder == ""


@xfail(1416)
@pytest.mark.parametrize("text,year", [
    ("noon to 10000 BC", -9999),
    ("noon to the 1990s", 1990),
])
def test_a_clock_start_to_a_past_point_reads_the_reversed_interval(text, year):
    result = extract_timespan(text, "en", ANCHOR)
    assert (result.span.start.year, result.span.start.month, result.span.start.day) == (year, 1, 1)
    assert (result.span.end.year, result.span.end.month, result.span.end.day) == (2026, 11, 25)


def test_control_the_business_day_before_the_edge_reads():
    assert start("the last business day of november 9999") == datetime(9999, 11, 30)
