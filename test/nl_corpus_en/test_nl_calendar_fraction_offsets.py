"""Fractional-quantity offsets over CALENDAR-GRAIN units (month, decade,
century, millennium) -- R110.

Before the fix, ``_resolve_relative_offset`` (chronologia/extract/resolver.py)
built the calendar-grain branch on ``int(step)``: a fractional quantifier
("half"=0.5, "quarter"=0.25) truncated straight to zero, so "in half a
month" silently resolved to a span starting AT THE ANCHOR (offset zero)
instead of ~+15 days -- a wrong answer with no signal anything was refused.

The fix converts the fraction to the finest calendar unit that composes it
EXACTLY where one exists:

* decade/century/millennium are themselves whole multiples of 12 months, so
  half/quarter fractions land on a whole month count and compose through the
  ordinary calendar-month arithmetic with no rounding ("half a decade" = 60
  months = exactly 5 years; "a quarter of a decade" = 30 months = 2.5 years).
* ``month`` has no finer CALENDAR unit to exchange a fraction for, so its
  fraction is read in plain-meaning DAYS instead: half a month = 15 days,
  a quarter month = 7 days (floored from 7.5).  Any other month fraction
  (e.g. three quarters) has no defensible day count and is refused (``None``)
  rather than silently truncated.
* ``year`` fractions never reach the resolver as floats in English -- the
  numfold pass (chronologia/extract/numfold.py) pre-folds a fractional year
  onto a whole month count ("half a year" -> "6 months") upstream of this
  code -- so "in half a year" is included below purely as a CONTROL that the
  fix left that existing path untouched.

Every expected value is independently hand-derived with ``timedelta`` /
``dateutil.relativedelta`` -- never read back from the parser.
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, nomatch, start_end

LANG = "en"


# -- previously-truncated-to-zero calendar-grain fractions -----------------

def test_half_a_month_is_fifteen_days_forward():
    start, end = start_end("in half a month")
    exp_start = ANCHOR + timedelta(days=15)
    assert start == exp_start
    assert end == exp_start + relativedelta(months=1), \
        "month-wide span from the resolved start, not the anchor"


def test_half_a_month_ago_is_fifteen_days_backward():
    start, end = start_end("half a month ago")
    exp_start = ANCHOR - timedelta(days=15)
    assert start == exp_start
    assert end == exp_start + relativedelta(months=1)


def test_quarter_of_a_month_is_seven_days_floored():
    start, end = start_end("in a quarter of a month")
    exp_start = ANCHOR + timedelta(days=7)
    assert start == exp_start
    assert end == exp_start + relativedelta(months=1)


def test_half_a_decade_is_exactly_five_years():
    start, end = start_end("in half a decade")
    exp_start = ANCHOR + relativedelta(years=5)
    assert start == exp_start
    assert end == exp_start + relativedelta(months=120), \
        "decade-wide span from the resolved start"


def test_half_a_century_is_exactly_fifty_years():
    start, end = start_end("in half a century")
    exp_start = ANCHOR + relativedelta(years=50)
    assert start == exp_start
    assert end == exp_start + relativedelta(months=1200)


def test_half_a_millennium_is_exactly_five_hundred_years():
    start, end = start_end("in half a millennium")
    exp_start = ANCHOR + relativedelta(years=500)
    assert start == exp_start
    assert end == exp_start + relativedelta(months=12000)


def test_quarter_of_a_decade_is_exactly_two_and_a_half_years():
    start, end = start_end("in a quarter of a decade")
    exp_start = ANCHOR + relativedelta(months=30)          # 0.25 * 120
    assert start == exp_start
    assert end == exp_start + relativedelta(months=120)


def test_quarter_of_a_century_is_exactly_twenty_five_years():
    start, end = start_end("in a quarter of a century")
    exp_start = ANCHOR + relativedelta(months=300)         # 0.25 * 1200
    assert start == exp_start
    assert end == exp_start + relativedelta(months=1200)


# -- refusal: month fractions with no defensible day count -----------------

def test_three_quarters_of_a_month_refuses_rather_than_guess():
    # 0.75 lands on neither the "half"=15d nor "quarter"=7d reading, and has
    # no other defensible day count -- refused (None), never silently
    # truncated to the anchor the way the pre-fix code did for ALL
    # fractions.
    nomatch("in three quarters of a month")


# -- controls: paths the fix must leave byte-identical ----------------------

def test_half_a_year_control_still_six_months():
    # pre-folded upstream by numfold ("half a year" -> "6 months") --
    # exercises the resolver's ordinary whole-month path, untouched by this
    # fix.  The folded UNIT is "months", so the span is month-wide (the same
    # width convention "in 2 months" already uses), not year-wide.
    start, end = start_end("in half a year")
    exp_start = ANCHOR + relativedelta(months=6)
    assert start == exp_start
    assert end == exp_start + relativedelta(months=1)


def test_whole_number_months_control_unchanged():
    start, end = start_end("in 2 months")
    exp_start = ANCHOR + relativedelta(months=2)
    assert start == exp_start
    assert end == exp_start + relativedelta(months=1)


def test_half_an_hour_control_unaffected_fixed_grain():
    # a FIXED-grain unit (hour) -- always went through plain float
    # arithmetic (timedelta), never the int()-truncating calendar-grain
    # branch this fix touches.
    start, end = start_end("in half an hour")
    exp_start = ANCHOR + timedelta(minutes=30)
    assert start == exp_start
    assert end == exp_start + timedelta(hours=1)
