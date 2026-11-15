# -*- coding: utf-8 -*-
"""A 24-hour clock with the pm marker بعدازظهر, fa.

بعدازظهر is the pm marker of fa (Unicode CLDR 47, fa ca-gregorian.json,
dayPeriods.format.wide pm), so a later 24-hour clock keeps its hour:
"20:30 بعدازظهر" is 20:30.  An afternoon or evening marker never
holds midnight, so "00:30 بعدازظهر" names no time.
Anchor: Tuesday 2017-06-27 13:04.
"""
from datetime import datetime

from ._corpus import ad, nomatch, start


def test_the_pm_marker_keeps_a_later_clock():
    assert start("20:30 بعدازظهر") == ad(datetime(2017, 6, 27, 20, 30))


def test_the_pm_marker_holds_no_midnight():
    nomatch("00:30 بعدازظهر")
