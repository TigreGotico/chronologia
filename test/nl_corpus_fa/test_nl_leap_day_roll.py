"""The Solar Hijri day a common year does not hold.

Esfand has 30 days only in a leap year of the arithmetic Solar Hijri cycle.
A bare day-and-month with no year names the next time that day comes round,
so at the corpus anchor (2017-06-27, Solar Hijri 1396) ``30 اسفند`` is
30 Esfand 1399 -- 2021-03-20 by the calendar's own JDN arithmetic, the first
year on or after the anchor whose last month has a 30th.
"""
from datetime import datetime, timedelta

from ._corpus import ad, parse


def test_bare_thirtieth_of_esfand_rolls_to_a_year_that_has_it():
    r = parse("30 اسفند")
    assert r is not None
    assert r.span.start == ad(datetime(2021, 3, 20))
    assert r.span.end - r.span.start == timedelta(days=1)
    assert r.remainder == ""
