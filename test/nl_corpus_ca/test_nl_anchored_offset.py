"""Anchored arithmetic (feature 1), Catalan.

"N dies abans/després de <una data resolta>" -- a signed unit offset on an
already-resolved calendar date, tolerating the article/"de" gap.  Anchor
2017-06-27; 5 d'abril resolves forward to 2018-04-05.
"""
from datetime import date

import pytest

from ._corpus import AstroDate, parse, start


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


@pytest.mark.parametrize("text,expected", [
    ("3 dies abans del 5 d'abril", date(2018, 4, 2)),
    ("3 dies després del 5 d'abril", date(2018, 4, 8)),
    ("una setmana abans del 5 d'abril", date(2018, 3, 29)),
    ("2 setmanes després del 5 d'abril", date(2018, 4, 19)),
])
def test_unit_offset(text, expected):
    assert start(text) == _ad(expected)
    assert parse(text).remainder == ""
