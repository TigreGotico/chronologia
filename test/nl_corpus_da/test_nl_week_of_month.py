# -*- coding: utf-8 -*-
"""The "Nth week of <month>" construction for da (Danish).

Danish names an ordinal week inside a month with the preposition "i"
("den 3. uge i marts" = the third week in March); "af" is accepted too.  The
connector was already present, so once an ordinal is supplied the week reads
correctly.  Spelled ordinals ("tredje") are being taught to fold on a separate
branch, so these cases assert the numeric ordinal that folds today.

Changed with ruling 1 on 26 November 2026: a part of a month takes its month's
year.  The anchor is 2017-06-27, March has ended, so it is March 2018.
"""
import pytest

from ._corpus import AstroDate, start_end


@pytest.mark.parametrize("text", [
    'den 3. uge i marts',
    '3. uge i marts',
    'den 3. uge af marts',
])
def test_third_week_of_march(text):
    s, e = start_end(text)
    assert (s, e) == (AstroDate(2018, 3, 19), AstroDate(2018, 3, 26))  # ruling 1: March 2018


@pytest.mark.parametrize("text,ymd", [
    # ruling 1: March has ended at the anchor, so it is March 2018
    ('den 1. uge i marts', (2018, 3, 5, 2018, 3, 12)),
    ('den 2. uge i marts', (2018, 3, 12, 2018, 3, 19)),
])
def test_other_weeks_of_march(text, ymd):
    s, e = start_end(text)
    assert (s, e) == (AstroDate(*ymd[:3]), AstroDate(*ymd[3:]))
