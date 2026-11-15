# -*- coding: utf-8 -*-
"""A digit clock with "сутринта" agrees with the spoken hour, bg.

The morning band that "сутринта" names reaches into 13:00, so the spoken
"в 13 сутринта" is 13:00 and "в 15 сутринта" names no time.  The digit clock
past noon reads the same way.  Anchor: Tuesday 2017-06-27 13:04.
"""
from ._corpus import AstroDate, nomatch, start


def test_a_digit_clock_inside_the_morning_band():
    assert start("в 13 сутринта") == AstroDate(2017, 6, 28, 13, 0)
    assert start("13:30 сутринта") == AstroDate(2017, 6, 27, 13, 30)


def test_a_digit_clock_past_the_morning_band_is_no_time():
    nomatch("в 15 сутринта")
    nomatch("15:30 сутринта")
