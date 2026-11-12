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

from ._corpus import ad, nomatch, parse

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
