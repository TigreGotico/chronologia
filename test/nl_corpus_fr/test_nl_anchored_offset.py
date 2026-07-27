"""Anchored arithmetic (feature 1), French.

"2 semaines après pâques", "le lundi après noël" -- a signed unit offset or
strict weekday roll on a resolved reference.  Anchor 2017-06-27 (mardi);
pâques 2018 = dim 2018-04-01, noël = lun 2017-12-25.
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, span, start, nomatch

PAQUES = date(2018, 4, 1)
NOEL = date(2017, 12, 25)


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


@pytest.mark.parametrize("text,expected", [
    ("2 semaines après pâques", PAQUES + timedelta(days=14)),
    ("une semaine après pâques", PAQUES + timedelta(days=7)),
    ("1 semaine avant pâques", PAQUES - timedelta(days=7)),
    ("2 semaines avant noël", NOEL - timedelta(days=14)),
    ("3 jours avant noël", NOEL - timedelta(days=3)),
    ("10 jours après noël", NOEL + timedelta(days=10)),
    ("le jour après noël", NOEL + timedelta(days=1)),
    ("1 mois après pâques", date(2018, 5, 1)),
])
def test_unit_offset(text, expected):
    assert start(text) == _ad(expected)


@pytest.mark.parametrize("text,expected", [
    ("le lundi après noël", date(2018, 1, 1)),
    ("le jeudi après noël", date(2017, 12, 28)),
    ("le mardi avant noël", date(2017, 12, 19)),
    ("le dimanche après pâques", date(2018, 4, 8)),
    ("le samedi avant pâques", date(2018, 3, 31)),
    ("le vendredi avant pâques", date(2018, 3, 30)),
])
def test_weekday_roll(text, expected):
    assert start(text) == _ad(expected)


# an offset resolves to the single shifted day, not a period-wide span:
# the offset amount is the SHIFT, never the result width (was days=7,
# a silent-wrong -- see en test_nl_anchored_offset_point).
def test_week_offset_is_day_wide():
    assert span("2 semaines après pâques").width == timedelta(days=1)


def test_weekday_roll_is_day_wide():
    assert span("le lundi après noël").width == timedelta(days=1)


def test_bare_after_holiday_unchanged():
    assert start("après pâques") == _ad(PAQUES)


@pytest.mark.parametrize("text", ["avant la réunion", "le jour après le mariage"])
def test_no_reference_no_offset(text):
    nomatch(text)
