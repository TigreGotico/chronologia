"""Wave 1 -- ranges: "from A to B" / "between A and B".

The span runs from the start of the left sub-parse to the end of the right
one; the two endpoints are independent parses.  A bare "A to B" is honoured
too, but must never hijack a clock ("quarter to five" stays a time).
"""
from datetime import timedelta

import pytest

from ._corpus import AstroDate, start_end, span, start, nomatch


def _d(s):
    y, m, dd = (int(x) for x in s.split("-"))
    return AstroDate(y, m, dd)


# -- month and date ranges -------------------------------------------------

@pytest.mark.parametrize("text,s,e", [
    ("from june to august", "2017-6-1", "2017-9-1"),
    ("from january to march", "2017-1-1", "2017-4-1"),
    ("between june and september", "2017-6-1", "2017-10-1"),
    ("from october to december", "2017-10-1", "2018-1-1"),
    ("from june 2020 to august 2021", "2020-6-1", "2021-9-1"),
    ("from january 2000 to december 2009", "2000-1-1", "2010-1-1"),
    ("from march to may", "2017-3-1", "2017-6-1"),
    ("between april and june", "2017-4-1", "2017-7-1"),
    ("from september to november", "2017-9-1", "2017-12-1"),
    ("from june to june", "2017-6-1", "2017-7-1"),
    ("from january to december", "2017-1-1", "2018-1-1"),
    ("between february and april", "2017-2-1", "2017-5-1"),
])
def test_month_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == _d(s) and ee == _d(e)


@pytest.mark.parametrize("text,s,e", [
    ("from june 5th to june 12th", "2018-6-5", "2018-6-13"),
    ("june 5th to june 12th", "2018-6-5", "2018-6-13"),
    ("from december 24 2020 to december 26 2020", "2020-12-24", "2020-12-27"),
    ("from july 1 1969 to july 31 1969", "1969-7-1", "1969-8-1"),
    ("from 2020-01-01 to 2020-01-31", "2020-1-1", "2020-2-1"),
    ("from june 10 2020 to june 20 2020", "2020-6-10", "2020-6-21"),
    ("from march 1 2000 to march 31 2000", "2000-3-1", "2000-4-1"),
    ("from 2019-12-25 to 2019-12-31", "2019-12-25", "2020-1-1"),
])
def test_date_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == _d(s) and ee == _d(e)


# -- era ranges -----------------------------------------------------------

def test_bc_to_ad_range():
    ss, ee = start_end("from 44 bc to 14 ad")
    assert ss == AstroDate(-43, 1, 1) and ee == AstroDate(15, 1, 1)


def test_ad_to_ad_range():
    ss, ee = start_end("from 800 ad to 1200 ad")
    assert ss == AstroDate(800, 1, 1) and ee == AstroDate(1201, 1, 1)


# -- clock ranges ----------------------------------------------------------

@pytest.mark.parametrize("text,sh,eh", [
    ("between 3 pm and 5 pm", 15, 17),
    ("from 2 pm to 6 pm", 14, 18),
    ("between 10 am and 11 am", 10, 11),
])
def test_clock_range(text, sh, eh):
    ss, ee = start_end(text)
    assert ss.hour == sh
    assert ee.hour == eh
    assert (ee - ss).total_seconds() > 0


# -- the range must not fabricate: right-before-left falls through --------

def test_quarter_to_five_is_a_clock_not_a_range():
    # "quarter to five" must stay a clock time, never a "quarter"->"five" range
    assert start("quarter to five") == AstroDate(2017, 6, 28, 4, 45)


# -- deferred phrasings ---------------------------------------------------

# bare weekday endpoints; the end rolls a week when it lands before the start
@pytest.mark.parametrize("text,days", [
    ("from monday to friday", 5), ("from tuesday to thursday", 3),
    ("from friday to monday", 4),        # monday wraps to the next week
])
def test_weekday_range(text, days):
    ss, ee = start_end(text)
    assert (ee - ss).days == days


@pytest.mark.parametrize("text,s,e", [
    ("from 2020 to 2023", AstroDate(2020, 1, 1), AstroDate(2024, 1, 1)),
    ("between 1990 and 2000", AstroDate(1990, 1, 1), AstroDate(2001, 1, 1)),
    ("from 1776 to 1789", AstroDate(1776, 1, 1), AstroDate(1790, 1, 1)),
])
def test_year_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == s and ee == e


# a bare left endpoint borrows the right endpoint's trailing meridiem
@pytest.mark.parametrize("text,sh,eh", [
    ("between 3 and 5 pm", 15, 17), ("from 9 to 11 am", 9, 11),
    ("between 2 and 4 pm", 14, 16),
])
def test_shared_meridiem_range(text, sh, eh):
    ss, ee = start_end(text)
    assert ss.hour == sh and ee.hour == eh


# an AM->PM / cross-midnight clock range: the end rolls forward a day when it
# lands before the start (both endpoints then read on the same clock day).
@pytest.mark.parametrize("text,sh,eh", [
    ("from 9 am to 5 pm", 9, 17), ("from 10 pm to 2 am", 22, 2),
    ("from 8 am to 6 pm", 8, 18),
])
def test_am_to_pm_range(text, sh, eh):
    ss, ee = start_end(text)
    assert ss.hour == sh and ee.hour == eh
