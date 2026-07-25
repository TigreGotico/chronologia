"""Anchored arithmetic (feature 1), Romanian.

"(cu) N zile înainte de/după <o dată rezolvată>" -- a signed unit offset on
an already-resolved calendar date.  The optional lead-in preposition "cu"
("with") heading the offset phrase is consumed, not stranded.  Anchor
2017-06-27; 5 aprilie resolves forward to 2018-04-05.
"""
from datetime import date

import pytest

from ._corpus import AstroDate, parse, start


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


@pytest.mark.parametrize("text,expected", [
    ("3 zile înainte de 5 aprilie", date(2018, 4, 2)),
    ("3 zile după 5 aprilie", date(2018, 4, 8)),
    ("cu 3 zile înainte de 5 aprilie", date(2018, 4, 2)),
    ("cu 3 zile după 5 aprilie", date(2018, 4, 8)),
])
def test_unit_offset(text, expected):
    assert start(text) == _ad(expected)
    assert parse(text).remainder == ""
