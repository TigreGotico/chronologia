# -*- coding: utf-8 -*-
"""A numbered day of the month without a month name, pt.

"dia N" names a numbered day of the month (Priberam s.v. "dia", "dia de
Reis": "Dia 6 de Janeiro ...").  Without a month name the next day with that
number is meant, and the anchor's own day when it has that number.  A month
that lacks the day is skipped.  "o próximo dia N" is "Seguinte ao actual"
(Priberam s.v. "próximo", 4): the next such day strictly after today.

Anchor Tuesday 2017-06-27 13:04.  The 5th and the 3rd have passed in June,
so they are 5 and 3 July; the 30th and the 28th are still ahead in June.
Anchor Saturday 2026-01-31: February 2026 has no 29th or 30th, so those are
29 and 30 March; the 28th is 28 February.  Counted on the calendar by hand.
"""
from datetime import datetime

import pytest

from ._corpus import ANCHOR, ad, nomatch, parse

JAN31 = datetime(2026, 1, 31, 12, 0)


@pytest.mark.parametrize("text,expected,rest", [
    ("o dia 5 do mês", datetime(2017, 7, 5), ""),
    ("o dia 30 do mês", datetime(2017, 6, 30), ""),
    ("no dia 3", datetime(2017, 7, 3), ""),
    ("dia 28", datetime(2017, 6, 28), ""),
    ("no dia 27", datetime(2017, 6, 27), ""),
    ("no dia 3 às 10h", datetime(2017, 7, 3, 10), ""),
    ("o próximo dia 5", datetime(2017, 7, 5), ""),
    ("o próximo dia 27", datetime(2017, 7, 27), ""),
    ("o dia 25 de dezembro", datetime(2017, 12, 25), ""),
    ("no dia 3 de julho", datetime(2017, 7, 3), ""),
    ("a reunião é no dia 3", datetime(2017, 7, 3), "a reunião é"),
])
def test_day_of_month(text, expected, rest):
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    assert r.span.start == ad(expected)
    assert r.remainder == rest


@pytest.mark.parametrize("text,expected", [
    ("o dia 30 do mês", datetime(2026, 3, 30)),
    ("o dia 29 do mês", datetime(2026, 3, 29)),
    ("o dia 28 do mês", datetime(2026, 2, 28)),
])
def test_day_of_month_skips_a_month_without_the_day(text, expected):
    r = parse(text, JAN31)
    assert r is not None, f"{text!r} did not parse"
    assert r.span.start == ad(expected)


@pytest.mark.parametrize("text", [
    "o dia foi longo",
    "o dia 40",
    "o último dia 5",
])
def test_not_a_day_of_month(text):
    nomatch(text)


# "desde o dia N" opens a span at the most recent day N at or before now.  A
# numbered day recurs each month, so the start steps back one month at a
# time, and a month that lacks the day is skipped.  A clock stays with its
# day.  Anchor Tuesday 2017-06-27 13:04: the 3rd, 1st, 20th, 5th and 15th
# have passed in June; the 30th has not, and May has 31 days, so the 30th is
# 30 May; the 27th is today; today's 15:00 is still ahead, so "o dia 27 às
# 15h" is 27 May.  Saturday 2017-07-01: June has no 31st, so the 31st is
# 31 May.  Wednesday 2017-03-01: February 2017 has no 29th, so the 29th is
# 29 January.  Counted on the calendar by hand.
JUL01 = datetime(2017, 7, 1, 12, 0)
MAR01 = datetime(2017, 3, 1, 12, 0)


@pytest.mark.parametrize("text,anchor,expected", [
    ("desde o dia 3", ANCHOR, datetime(2017, 6, 3)),
    ("desde o dia 1", ANCHOR, datetime(2017, 6, 1)),
    ("desde o dia 30", ANCHOR, datetime(2017, 5, 30)),
    ("desde dia 20", ANCHOR, datetime(2017, 6, 20)),
    ("desde o dia 27", ANCHOR, datetime(2017, 6, 27)),
    ("desde o dia 5 do mês", ANCHOR, datetime(2017, 6, 5)),
    ("desde o dia 15 às 10h", ANCHOR, datetime(2017, 6, 15, 10)),
    ("desde o dia 27 às 15h", ANCHOR, datetime(2017, 5, 27, 15)),
    ("desde o dia 31", JUL01, datetime(2017, 5, 31)),
    ("desde o dia 29", MAR01, datetime(2017, 1, 29)),
])
def test_since_day_of_month_steps_back_by_months(text, anchor, expected):
    r = parse(text, anchor)
    assert r is not None, f"{text!r} did not parse"
    assert (r.span.start, r.span.end) == (ad(expected), ad(anchor))
    assert r.remainder == ""


# The yearly and daily cycles stay: a named date rolls back by years, a bare
# clock by days.
@pytest.mark.parametrize("text,expected", [
    ("desde 5 de março", datetime(2017, 3, 5)),
    ("desde 30 de dezembro", datetime(2016, 12, 30)),
    ("desde o dia 30 de dezembro", datetime(2016, 12, 30)),
    ("desde as 15h", datetime(2017, 6, 26, 15)),
])
def test_since_other_cycles_unchanged(text, expected):
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    assert r.span.start == ad(expected)
