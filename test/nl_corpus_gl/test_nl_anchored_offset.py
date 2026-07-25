"""Anchored arithmetic (feature 1), Galician.

"N días antes/despois de <unha data resolta>" -- a signed unit offset on an
already-resolved calendar date, tolerating the article/"de" gap.  Anchor
2017-06-27; 5 de abril resolves forward to 2018-04-05.
"""
from datetime import date

import pytest

from ._corpus import AstroDate, parse, start


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


@pytest.mark.parametrize("text,expected", [
    ("3 días antes do 5 de abril", date(2018, 4, 2)),
    ("3 días despois do 5 de abril", date(2018, 4, 8)),
    ("unha semana antes do 5 de abril", date(2018, 3, 29)),
    ("2 semanas despois do 5 de abril", date(2018, 4, 19)),
])
def test_unit_offset(text, expected):
    assert start(text) == _ad(expected)
    assert parse(text).remainder == ""
