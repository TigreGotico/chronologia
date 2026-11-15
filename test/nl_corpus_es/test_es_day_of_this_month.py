"""A named period is the calendar unit: "el día 5 de este mes" is the 5th of
the anchor's month even when that day has passed; "del mes que viene" is the
next one.

Anchor: Tuesday 2017-06-27 13:04.  Gold values are read off a calendar.
"""
from datetime import datetime

from ._corpus import parse


def test_este_mes_keeps_the_anchors_month_after_the_day():
    r = parse("el día 5 de este mes")
    assert r[0].start == datetime(2017, 6, 5)
    assert r[1] == ""


def test_este_mes_before_the_day():
    assert parse("el día 30 de este mes")[0].start == datetime(2017, 6, 30)


def test_mes_que_viene_is_next_month():
    assert parse("el día 5 del mes que viene")[0].start == datetime(2017, 7, 5)
