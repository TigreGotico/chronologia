# -*- coding: utf-8 -*-
"""The "Nth week of <month>" construction for nn (Nynorsk).

Norwegian names an ordinal week inside a month with the preposition "i"
("tredje veka i mars" = the third week in March), the same "i" that means "in".
Before the connector was taught, the ordinal-week qualifier was silently
dropped and the bare month returned; now the phrase reads the week itself.

Changed with ruling 1 on 26 November 2026: a part of a month takes its month's
year.  The anchor is 2017-06-27, March has ended, so it is March 2018 (first
Monday 5 March).
"""
import pytest

from ._corpus import AstroDate, start_end


@pytest.mark.parametrize("text", [
    'tredje veka i mars',
    'tredje veke i mars',
])
def test_third_week_of_march(text):
    s, e = start_end(text)
    assert (s, e) == (AstroDate(2018, 3, 19), AstroDate(2018, 3, 26))  # ruling 1: March 2018


@pytest.mark.parametrize("text,ymd", [
    ('fyrste veka i mars', (2018, 3, 5, 2018, 3, 12)),
    ('andre veka i mars', (2018, 3, 12, 2018, 3, 19)),
])
def test_other_weeks_of_march(text, ymd):
    s, e = start_end(text)
    assert (s, e) == (AstroDate(*ymd[:3]), AstroDate(*ymd[3:]))
