# -*- coding: utf-8 -*-
"""The "Nth week of <month>" construction for nn (Nynorsk).

Norwegian names an ordinal week inside a month with the preposition "i"
("tredje veka i mars" = the third week in March), the same "i" that means "in".
Before the connector was taught, the ordinal-week qualifier was silently
dropped and the bare month returned; now the phrase reads the week itself.
"""
import pytest

from ._corpus import AstroDate, start_end


@pytest.mark.parametrize("text", [
    'tredje veka i mars',
    'tredje veke i mars',
])
def test_third_week_of_march(text):
    s, e = start_end(text)
    assert (s, e) == (AstroDate(2017, 3, 20), AstroDate(2017, 3, 27))


@pytest.mark.parametrize("text,ymd", [
    ('fyrste veka i mars', (2017, 3, 6, 2017, 3, 13)),
    ('andre veka i mars', (2017, 3, 13, 2017, 3, 20)),
])
def test_other_weeks_of_march(text, ymd):
    s, e = start_end(text)
    assert (s, e) == (AstroDate(*ymd[:3]), AstroDate(*ymd[3:]))
