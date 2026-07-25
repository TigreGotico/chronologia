"""Vernacular Roman-calendar anchors (pt) -- Kalends, Nones, Ides.

The three monthly anchors read as pt's own words and compose for free
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
    ('os idos de março', '2017-3-15'),
    ('as calendas de abril', '2017-4-1'),
    ('as nonas de julho', '2017-7-7'),
    ('as nonas de janeiro', '2017-1-5'),
    ('os idos de janeiro', '2017-1-13'),
    ('as calendas de janeiro', '2017-1-1'),
])
def test_roman_anchor_vernacular(text, iso):
    assert start(text) == _d(iso)
    assert span(text).width == timedelta(days=1)
    assert parse(text)[1] == ""


# -- composed with the N-days offset --------------------------------------

@pytest.mark.parametrize("text,iso", [
    ('3 dias antes das calendas de abril', '2017-3-29'),
    ('uma semana antes dos idos de março', '2017-3-8'),
    ('2 dias depois das calendas de abril', '2017-4-3'),
])
def test_roman_anchor_offset(text, iso):
    assert start(text) == _d(iso)
    assert parse(text)[1] == ""


# -- Nones/ninth homograph is licensed by position only -------------------
# "nonas" is at once the Nones and the feminine-plural ordinal "ninth".  In
# the anchor frame ("as nonas DE julho") it is the Nones; without the "of"
# preposition it is NOT read as the anchor -- the positional licence, both
# directions.

def test_nonas_is_nones_only_in_anchor_frame():
    assert start("as nonas de julho") == _d("2017-7-7")
    # "nonas" before a noun (not an "of" preposition) is never the Nones
    assert parse("as nonas semanas de março") is None
