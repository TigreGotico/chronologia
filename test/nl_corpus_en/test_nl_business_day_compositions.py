"""Business-day *compositions*: the last/Nth business day **of a month**, and
"N business days after/before <day-of-month>".

These are the two shapes the bare "in N business days" counter did not reach:

* **(A) day-of-month within a scoped month** -- "the last working day of this
  month", "the third business day of July".  The count is scoped to a calendar
  month (named, or this/next/last/the month) rather than the anchor; "last" is
  the last business day of that month, "Nth" the Nth counting from the 1st.
* **(B) offset from a resolved day-of-month** -- "5 business days after the
  1st".  The reference is a bare day-of-month ("the 1st"/"the 15th"), resolved
  prefer-future exactly as "the 1st" does elsewhere, then the business-day
  count runs forward/back from it.

Anchor is **Tuesday 2017-06-27 13:04**.  Weekday grid used for every gold::

    June 2017:  30 = Friday (last business day of June)
                 1 = Thursday (first business day of June)
    July 2017:   1 Sat  2 Sun  3 Mon  4 Tue  5 Wed  6 Thu  7 Fri
                15 Sat 17 Mon 18 Tue 19 Wed 20 Thu 21 Fri
                31 = Monday (last business day of July)

Holiday-blind (no jurisdiction): weekend-only, Sat/Sun skipped.
"""
from datetime import date, datetime

import pytest

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

ANCHOR = datetime(2017, 6, 27, 13, 4)   # Tuesday


def start(text):
    r = extract_timespan(text, "en", ANCHOR)
    assert r is not None, f"{text!r} did not parse"
    return r[0].start


def rem(text):
    r = extract_timespan(text, "en", ANCHOR)
    assert r is not None, f"{text!r} did not parse"
    return r[1]


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


# -- (A) last / Nth business day of a scoped month -------------------------

@pytest.mark.parametrize("text,expected", [
    ("the last working day of this month", date(2017, 6, 30)),   # Fri
    ("the last business day of next month", date(2017, 7, 31)),  # Mon
    ("the third business day of July", date(2017, 7, 5)),        # Wed
    ("the first working day of the month", date(2017, 6, 1)),    # Thu
])
def test_business_day_of_month(text, expected):
    assert start(text) == _ad(expected)


# -- (B) N business days after/before a day-of-month reference -------------

@pytest.mark.parametrize("text,expected", [
    ("5 business days after the 1st", date(2017, 7, 7)),    # from Sat Jul 1
    ("5 business days after the 15th", date(2017, 7, 21)),  # from Sat Jul 15
    ("2 business days after the 1st", date(2017, 7, 4)),
    ("1 business day before the 15th", date(2017, 7, 14)),  # Fri before Sat 15
])
def test_business_days_from_dom(text, expected):
    assert start(text) == _ad(expected)


# -- qualifiers are consumed, not stranded ---------------------------------

@pytest.mark.parametrize("text", [
    "the last working day of this month",
    "the last business day of next month",
    "the third business day of July",
    "5 business days after the 1st",
])
def test_no_stranded_qualifier(text):
    # the month scope / reference must be swallowed -- no "of July", "after the
    # 1", "the working day of" left behind.
    leftover = rem(text)
    for bad in ("of", "after", "working day", "business day"):
        assert bad not in leftover, f"{text!r} stranded {leftover!r}"


# -- regression pins: the bare counter stays byte-identical -----------------

@pytest.mark.parametrize("text,expected,expected_rem", [
    ("3 business days from now", date(2017, 6, 30), "from now"),
    ("in 3 business days", date(2017, 6, 30), ""),
    ("the next business day", date(2017, 6, 28), "the"),
])
def test_bare_counter_unchanged(text, expected, expected_rem):
    r = extract_timespan(text, "en", ANCHOR)
    assert r is not None
    assert r[0].start == _ad(expected)
    assert r[1] == expected_rem
