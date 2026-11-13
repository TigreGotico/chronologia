""""since the Nth of the month" opens at the most recent such day.

A numbered day of the month recurs each month, so the start of a "since"
span steps back one month at a time until it is at or before now, and a
month that lacks the day is skipped.  A clock stays with its day.

Anchor Tuesday 2017-06-27 13:04: the 3rd has passed in June; the 30th has
not, and May has 31 days, so the 30th is 30 May.  Saturday 2017-07-01: June
has no 31st, so the 31st is 31 May.  Counted on the calendar by hand.
"""
from datetime import datetime

import pytest

from ._corpus import ANCHOR, ad, parse

JUL01 = datetime(2017, 7, 1, 12, 0)


@pytest.mark.parametrize("text,anchor,expected", [
    ("since the 3rd of the month", ANCHOR, datetime(2017, 6, 3)),
    ("since the 30th of the month", ANCHOR, datetime(2017, 5, 30)),
    ("since the 27th of the month", ANCHOR, datetime(2017, 6, 27)),
    ("since the 3rd of the month at 10am", ANCHOR, datetime(2017, 6, 3, 10)),
    ("since the 31st of the month", JUL01, datetime(2017, 5, 31)),
])
def test_since_day_of_month_steps_back_by_months(text, anchor, expected):
    r = parse(text, anchor)
    assert r is not None, f"{text!r} did not parse"
    assert (r.span.start, r.span.end) == (ad(expected), ad(anchor))
    assert r.remainder == ""


@pytest.mark.parametrize("text,expected", [
    ("since christmas", datetime(2016, 12, 25)),
    ("since march 5", datetime(2017, 3, 5)),
    ("since 3pm", datetime(2017, 6, 26, 15)),
])
def test_since_other_cycles_unchanged(text, expected):
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    assert r.span.start == ad(expected)


# "since the last friday of the month" and "from the last friday of the month
# to today" name the same start.  On Saturday 2026-10-17 the last Friday of
# October (the 30th) is ahead; September 2026 starts on a Tuesday, so its
# last Friday is the 25th.  On Saturday 2026-10-31 the 30th has passed.
SAT17 = datetime(2026, 10, 17, 12, 0)
SAT31 = datetime(2026, 10, 31, 12, 0)


@pytest.mark.parametrize("text,anchor,begin,end", [
    ("since the last friday of the month", SAT17, datetime(2026, 9, 25),
     SAT17),
    ("from the last friday of the month to today", SAT17,
     datetime(2026, 9, 25), datetime(2026, 10, 18)),
    ("since the last friday of the month", SAT31, datetime(2026, 10, 30),
     SAT31),
    ("from the last friday of the month to today", SAT31,
     datetime(2026, 10, 30), datetime(2026, 11, 1)),
])
def test_since_and_range_agree_on_the_last_weekday(text, anchor, begin, end):
    r = parse(text, anchor)
    assert r is not None, f"{text!r} did not parse"
    assert (r.span.start, r.span.end) == (ad(begin), ad(end))
    assert r.remainder == ""


# A right end that recurs each month is not rolled by weeks: on 17 October
# 2026 the third Tuesday is the 20th and the last Friday the 30th.
@pytest.mark.parametrize("text,begin,end", [
    ("from the 3rd of the month to the third tuesday of the month",
     datetime(2026, 10, 3), datetime(2026, 10, 21)),
    ("from the 3rd of the month to the last friday of the month",
     datetime(2026, 10, 3), datetime(2026, 10, 31)),
])
def test_range_to_a_monthly_weekday_is_not_rolled_by_weeks(text, begin, end):
    r = parse(text, SAT17)
    assert r is not None, f"{text!r} did not parse"
    assert (r.span.start, r.span.end) == (ad(begin), ad(end))
    assert r.remainder == ""


# "from sunday to the 31st of the month" said on Monday 2026-12-28: the
# Sunday is 3 January 2027 and the 31st is 31 December, so no range holds
# both; the left end is not pulled back a year.
def test_range_to_a_day_of_month_before_the_left_end_names_no_range():
    r = parse("from sunday to the 31st of the month",
              datetime(2026, 12, 28, 12, 0))
    assert r is None or r.remainder != "", f"read {r!r}"


# "since X until today" ends today: a day word counts from now, not from the
# start.  On Saturday 2026-10-17 the last Friday of September is the 25th.
@pytest.mark.parametrize("text,begin,end", [
    ("since the last friday of the month until tomorrow",
     datetime(2026, 9, 25), datetime(2026, 10, 19)),
    ("since the last friday of the month until today",
     datetime(2026, 9, 25), datetime(2026, 10, 18)),
    ("since the 3rd of the month until today", datetime(2026, 10, 3),
     datetime(2026, 10, 18)),
])
def test_since_until_a_day_word_counts_from_now(text, begin, end):
    r = parse(text, SAT17)
    assert r is not None, f"{text!r} did not parse"
    assert (r.span.start, r.span.end) == (ad(begin), ad(end))
    assert r.remainder == ""
