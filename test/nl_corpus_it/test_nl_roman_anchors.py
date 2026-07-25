"""Vernacular Roman-calendar anchors (it) -- Kalends, Nones, Ides.

The three monthly anchors read as it's own words and compose for free
with the general "N days before/after <date>" offset.  Dates are the
Julian-calendar Roman reckoning: the Ides of March is the 15th, the Nones
of July the 7th, the Nones of January the 5th.  Expected values are
independent of the parser (hand-derived).
"""
from datetime import timedelta

import pytest

from ._corpus import AstroDate, parse, span, start


def _d(s):
    y, m, dd = (int(x) for x in s.split("-"))
    return AstroDate(y, m, dd)


# -- bare vernacular anchor: "<anchor> of <month>" ------------------------

@pytest.mark.parametrize("text,iso", [
    ('le idi di marzo', '2017-3-15'),
    ('le calende di aprile', '2017-4-1'),
    ('le none di luglio', '2017-7-7'),
    ('le none di gennaio', '2017-1-5'),
    ('le idi di gennaio', '2017-1-13'),
    ('le calende di gennaio', '2017-1-1'),
])
def test_roman_anchor_vernacular(text, iso):
    assert start(text) == _d(iso)
    assert span(text).width == timedelta(days=1)
    assert parse(text)[1] == ""


# -- composed with the N-days offset --------------------------------------

@pytest.mark.parametrize("text,iso", [
    ('3 giorni prima delle calende di aprile', '2017-3-29'),
    ('una settimana prima delle idi di marzo', '2017-3-8'),
    ('2 giorni dopo le calende di aprile', '2017-4-3'),
])
def test_roman_anchor_offset(text, iso):
    assert start(text) == _d(iso)
    assert parse(text)[1] == ""
