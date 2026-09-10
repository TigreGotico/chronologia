"""The December abbreviation is the homograph of the cardinal ten.

CLDR abbreviates dezembro as "dez", which is also Portuguese for ten, so the
number fold won and "3 de dez" resolved to nothing while every other
abbreviated month resolved.  The month reading is available in one position
only -- the month slot of the "N de MONTH" date frame -- and the numeral
keeps every other.

Anchor 2017-06-27 13:04.
"""
from datetime import date

import pytest

from ._corpus import AstroDate, parse, start


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


@pytest.mark.parametrize("text,expected", [
    ("3 de dez", date(2017, 12, 3)),
    ("1 de dez", date(2017, 12, 1)),
    ("3 de dez de 2018", date(2018, 12, 3)),
])
def test_dez_in_the_month_slot(text, expected):
    assert start(text) == _ad(expected)
    assert parse(text).remainder == ""


def test_dez_with_an_hour():
    assert start("3 de dez às 9 horas") == AstroDate(2017, 12, 3, 9, 0)
    assert parse("3 de dez às 9 horas").remainder == ""


@pytest.mark.parametrize("text,expected", [
    # "dez" is the numeral everywhere else and must stay one
    ("dez de dezembro", date(2017, 12, 10)),
    ("em dez dias", date(2017, 7, 7)),
    ("daqui a dez dias", date(2017, 7, 7)),
])
def test_dez_is_still_the_cardinal(text, expected):
    got = start(text)
    assert (got.year, got.month, got.day) == (expected.year, expected.month,
                                              expected.day)


@pytest.mark.parametrize("text,expected", [
    # the spelled month and the other abbreviations are untouched
    ("3 de dezembro", date(2017, 12, 3)),
    ("3 de jan", date(2018, 1, 3)),
])
def test_the_other_month_surfaces(text, expected):
    assert start(text) == _ad(expected)
