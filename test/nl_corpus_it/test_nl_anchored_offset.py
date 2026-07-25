"""Anchored arithmetic (feature 1), Italian.

"N giorni prima/dopo <una data risolta>" -- a signed unit offset applied to
an already-resolved calendar date, tolerating the article/"di" gap.  The
directional marker "prima" is also the feminine ordinal "first"; the number
fold must not swallow it here.  Anchor 2017-06-27; 5 aprile resolves forward
to 2018-04-05.
"""
from datetime import date

import pytest

from ._corpus import AstroDate, parse, start


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


@pytest.mark.parametrize("text,expected", [
    ("3 giorni prima del 5 aprile", date(2018, 4, 2)),
    ("3 giorni dopo il 5 aprile", date(2018, 4, 8)),
    ("una settimana prima del 5 aprile", date(2018, 3, 29)),
    ("2 settimane dopo il 5 aprile", date(2018, 4, 19)),
])
def test_unit_offset(text, expected):
    assert start(text) == _ad(expected)
    assert parse(text).remainder == ""
