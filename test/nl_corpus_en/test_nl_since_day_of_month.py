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
