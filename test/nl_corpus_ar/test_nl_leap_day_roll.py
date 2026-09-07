"""The Hijri days a common year does not hold.

Dhu al-Hijjah has 30 days only in a leap year of the tabular Islamic cycle.
A bare day-and-month with no year names the next time that day comes round,
so at the corpus anchor (2017-06-27, Hijri 1438) ``30 ذو الحجة`` is 30
Dhu al-Hijjah 1439 -- 2018-09-11 by the calendar's own JDN arithmetic, the
first year on or after the anchor whose last month has a 30th.
"""
from datetime import datetime, timedelta

from ._corpus import ad, parse


def test_bare_thirtieth_of_dhu_al_hijjah_rolls_to_a_year_that_has_it():
    r = parse("30 ذو الحجة")
    assert r is not None
    assert r.span.start == ad(datetime(2018, 9, 11))
    assert r.span.end - r.span.start == timedelta(days=1)
    assert r.remainder == ""
