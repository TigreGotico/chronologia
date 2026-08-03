"""Wave 1 -- ranges: "from A to B" / "between A and B".

The span runs from the start of the left sub-parse to the end of the right
one; the two endpoints are independent parses.  A bare "A to B" is honoured
too, but must never hijack a clock ("quarter to five" stays a time).
"""
from datetime import timedelta

import pytest

from ._corpus import AstroDate, start_end, span, start, nomatch, ANCHOR, ad


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


# -- prefer-future consistency: a range straddling "now" (anchor 2017-06-27)
# keeps both endpoints in the same cycle instead of the left leaping a year --

@pytest.mark.parametrize("text,s,e", [
    # left endpoint just behind the anchor, right just ahead: stays in 2017
    ("from june 20 to june 30", "2017-6-20", "2017-7-1"),
    ("from june 25 to july 5", "2017-6-25", "2017-7-6"),        # cross-month
    ("june 20 - june 30", "2017-6-20", "2017-7-1"),             # dash form
    # both endpoints ahead of the anchor: plainly this year
    ("from june 28 to june 30", "2017-6-28", "2017-7-1"),
    ("from august 10 to september 20", "2017-8-10", "2017-9-21"),
    # both endpoints behind the anchor: the whole range prefers next year
    ("from june 1 to june 10", "2018-6-1", "2018-6-11"),
    # cross-year spans must not invert (the end rolls into the next year)
    ("from december 28 to january 3", "2017-12-28", "2018-1-4"),
    ("from november 30 to february 2", "2017-11-30", "2018-2-3"),
    # explicit years on both endpoints resolve verbatim
    ("from march 3 2001 to march 9 2001", "2001-3-3", "2001-3-10"),
    ("july 4 2020 - july 10 2020", "2020-7-4", "2020-7-11"),
])
def test_straddling_and_cross_year_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == _d(s) and ee == _d(e)


# -- holiday endpoints compose into a range like any other date -------------

@pytest.mark.parametrize("text,s,e", [
    ("from christmas to new year's day", "2017-12-25", "2018-1-2"),
    ("from christmas eve to christmas", "2017-12-24", "2017-12-26"),
])
def test_holiday_to_holiday_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == _d(s) and ee == _d(e)


# -- open-ended ranges: one edge is the anchor instant ("now") --------------
# convention: the known endpoint keeps the closed-range edge (an "until"
# endpoint contributes its .end, a "since" endpoint its .start); the open side
# is pinned to the anchor.

def test_until_open_start():
    # "until friday": from now through the whole of the next Friday
    s, e = start_end("until friday")
    assert s == ad(ANCHOR)                 # the anchor instant
    assert e == AstroDate(2017, 7, 1)      # end of Friday 2017-06-30

def test_through_open_start():
    s, e = start_end("through july 4")
    assert s == ad(ANCHOR)
    assert e == AstroDate(2017, 7, 5)

def test_since_open_end():
    # "since 2010": from the start of 2010 up to now
    s, e = start_end("since 2010")
    assert s == AstroDate(2010, 1, 1)
    assert e == ad(ANCHOR)


# -- clock ranges are untouched by the date-range fixes ---------------------

@pytest.mark.parametrize("text,sh,eh", [
    ("from 2 pm to 6 pm", 14, 18),
    ("between 10 am and 11 am", 10, 11),
    ("from 9 am to 5 pm", 9, 17),
])
def test_clock_range_unchanged(text, sh, eh):
    ss, ee = start_end(text)
    assert ss.hour == sh and ee.hour == eh
    assert (ee - ss).total_seconds() > 0


# -- negatives: non-temporal endpoints never fabricate a range --------------

@pytest.mark.parametrize("text", [
    "from here to there", "from apple to orange", "from soup to nuts",
])
def test_non_temporal_range_is_none(text):
    nomatch(text)


# -- the shared-month range: the month named ONCE for the pair ---------------
# The marginal English form ("June 5 to 12") of what is the default written
# form across Romance.  It used to lose the range entirely: the bare "12" made
# no endpoint, and the sentence fell through to the subtractive clock reading
# ("five to twelve"), returning a minute-wide span in the small hours.  The
# bare number is now read through its partner's own words.
@pytest.mark.parametrize("text", [
    "June 5 to 12",
    "June 5 to June 12",
    "5 June to 12 June",
    "from June 5 to 12",
])
def test_shared_month_range_reads_both_days(text):
    ss, ee = start_end(text)
    assert ss == AstroDate(2018, 6, 5) and ee == AstroDate(2018, 6, 13)


def test_shared_month_range_crosses_the_year():
    ss, ee = start_end("December 28 to 31")
    assert ss == AstroDate(2017, 12, 28) and ee == AstroDate(2018, 1, 1)


# -- adversarial: two bare numbers lend each other nothing, so every existing
# clock reading of "A to B" survives untouched.
def test_subtractive_clock_still_wins_with_no_month_in_sight():
    ss, ee = start_end("quarter to five")
    assert ss == AstroDate(2017, 6, 28, 4, 45)
    assert ee == AstroDate(2017, 6, 28, 4, 46)


def test_bare_hour_range_is_still_a_working_day():
    ss, ee = start_end("from 9 to 5")
    assert ss == AstroDate(2017, 6, 28, 9, 0)
    assert ee == AstroDate(2017, 6, 28, 17, 1)


def test_borrowed_meridiem_still_wins():
    ss, ee = start_end("between 3 and 5 pm")
    assert ss == AstroDate(2017, 6, 27, 15, 0)
    assert ee == AstroDate(2017, 6, 27, 17, 1)


def test_reversed_pinned_dates_still_refuse_to_compose():
    # the right endpoint is pinned and earlier: no roll, no borrow, no span
    r = span("june 12 2020 to june 5 2020")
    assert r.start == AstroDate(2020, 6, 12) and r.end == AstroDate(2020, 6, 13)


@pytest.mark.parametrize("text", ["June to", "to 12", "June 5 to", "5 to 12"])
def test_shared_month_garbage_never_raises(text):
    from ._corpus import parse
    parse(text)


def test_since_until_new_year_and_now_stay_backward():
    # "since christmas until new year": the "since" left endpoint is past-anchored
    # (last christmas), and the "until new year" right endpoint must resolve --
    # the "now"/"new year" special surfaces resolve in the directional-range
    # path too now, so the range stays the backward Dec 25 -> Jan 2 span instead
    # of silently downgrading to a forward range with "since" dropped.
    s, e = start_end("since christmas until new year")
    assert (s.year, s.month, s.day) == (2016, 12, 25)
    assert (e.year, e.month, e.day) == (2017, 1, 2)
    # "since X until now" ends at the anchor instant
    s2, e2 = start_end("since christmas until now")
    assert (s2.year, s2.month, s2.day) == (2016, 12, 25)
    assert e2 == ad(ANCHOR)
