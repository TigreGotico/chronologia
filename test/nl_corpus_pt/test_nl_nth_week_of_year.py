# -*- coding: utf-8 -*-
"""The nth and the last week of a year are ISO 8601 weeks, pt.

"The ISO 8601 definition for calendar week 01 is the week with the first
Thursday of the Gregorian year"; equivalently "It has 4 January in it"
(Wikipedia, "ISO week date").  The last week of a year is the ISO week
for which the same page gives "It has 28 December in it".

1 January 2026 is a Thursday, so week 01 of 2026 runs from Monday
29 December 2025 to Sunday 4 January 2026, and week 02 starts on Monday
5 January.  1 January 2027 and 1 January 2021 are Fridays, so week 01 of
each starts on Monday 4 January; week 03 of 2027 starts on Monday 18
January.  28 December 2026 is a Monday, so the last week of 2026 runs
from 28 December 2026 to 3 January 2027.  28 December 2027 is a Tuesday
(Monday 27 December), and 28 December 2029 a Friday (Monday 24 December).
28 December 2025 is a Sunday, so the last week of 2025 starts on Monday
22 December.  "do ano" names the anchor's year, 2026.  Counted on the
calendar by hand.
"""
from datetime import datetime

import pytest

from ._corpus import ad, parse

SATURDAY = datetime(2026, 10, 17, 12, 0)


@pytest.mark.parametrize("text,begin,end", [
    ("a primeira semana de 2026", (2025, 12, 29), (2026, 1, 5)),
    ("a segunda semana de 2026", (2026, 1, 5), (2026, 1, 12)),
    ("a terceira semana de 2027", (2027, 1, 18), (2027, 1, 25)),
    ("a primeira semana de 2021", (2021, 1, 4), (2021, 1, 11)),
    ("primeira semana de 2026", (2025, 12, 29), (2026, 1, 5)),
    ("na primeira semana de 2026", (2025, 12, 29), (2026, 1, 5)),
    ("a última semana de 2026", (2026, 12, 28), (2027, 1, 4)),
    ("a última semana de 2027", (2027, 12, 27), (2028, 1, 3)),
    ("a última semana de 2029", (2029, 12, 24), (2029, 12, 31)),
    ("a primeira semana do ano", (2025, 12, 29), (2026, 1, 5)),
    ("a segunda semana do ano", (2026, 1, 5), (2026, 1, 12)),
    ("a última semana do ano passado", (2025, 12, 22), (2025, 12, 29)),
])
def test_nth_week_of_year(text, begin, end):
    r = parse(text, SATURDAY)
    assert r is not None, f"{text!r} did not parse"
    assert (r.span.start, r.span.end) == (ad(datetime(*begin)),
                                          ad(datetime(*end)))
    assert r.remainder == ""
