# -*- coding: utf-8 -*-
"""A 24-hour clock with the night word "ночы", be.

The word reads on the am half of the 12-hour clock, so "02:00 ночы" is
02:00.  Over a 24-hour clock it keeps the late evening as written ("23:30
ночы" is 23:30).  An hour from 13 to 17 is the afternoon, so "15:30 ночы"
names no time, as "15:30 раніцы" names none.  Anchor: Tuesday 2017-06-27 13:04.
"""
import pytest

from ._corpus import AstroDate, nomatch, start


@pytest.mark.parametrize("text,expected", [
    ("23:30 ночы", AstroDate(2017, 6, 27, 23, 30)),
    ("22:00 ночы", AstroDate(2017, 6, 27, 22, 0)),
    ("02:00 ночы", AstroDate(2017, 6, 28, 2, 0)),
])
def test_the_night_word_keeps_the_clock(text, expected):
    assert start(text) == expected


@pytest.mark.parametrize("text", ["15:30 ночы", "13:00 ночы", "17:30 ночы",
                                  "15:30 раніцы"])
def test_an_afternoon_clock_is_no_time(text):
    nomatch(text)
