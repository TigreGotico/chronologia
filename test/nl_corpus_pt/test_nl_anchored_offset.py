"""Anchored arithmetic (feature 1), Portuguese.

"2 semanas depois da páscoa", "a segunda depois do natal" -- a signed unit
offset or strict weekday roll on a resolved reference, tolerating the
"de"-contraction gap ("da", "do").  Anchor 2017-06-27 (terça); páscoa 2018 =
dom 2018-04-01, natal = seg 2017-12-25.
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, span, start, nomatch

PASCOA = date(2018, 4, 1)
NATAL = date(2017, 12, 25)


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


@pytest.mark.parametrize("text,expected", [
    ("2 semanas depois da páscoa", PASCOA + timedelta(days=14)),
    ("uma semana depois da páscoa", PASCOA + timedelta(days=7)),
    ("1 semana antes da páscoa", PASCOA - timedelta(days=7)),
    ("2 semanas antes do natal", NATAL - timedelta(days=14)),
    ("3 dias antes do natal", NATAL - timedelta(days=3)),
    ("10 dias depois do natal", NATAL + timedelta(days=10)),
    ("o dia depois do natal", NATAL + timedelta(days=1)),
    ("1 mês depois da páscoa", date(2018, 5, 1)),
])
def test_unit_offset(text, expected):
    assert start(text) == _ad(expected)


@pytest.mark.parametrize("text,expected", [
    ("a segunda depois do natal", date(2018, 1, 1)),
    ("a sexta depois do natal", date(2017, 12, 29)),
    ("a terça antes do natal", date(2017, 12, 19)),
    ("o domingo depois da páscoa", date(2018, 4, 8)),
    ("o sábado antes da páscoa", date(2018, 3, 31)),
    ("a sexta antes da páscoa", date(2018, 3, 30)),
])
def test_weekday_roll(text, expected):
    assert start(text) == _ad(expected)


# an offset resolves to the single shifted day, not a period-wide span:
# the offset amount is the SHIFT, never the result width (was days=7,
# a silent-wrong -- see en test_nl_anchored_offset_point).
def test_week_offset_is_day_wide():
    assert span("2 semanas depois da páscoa").width == timedelta(days=1)


def test_weekday_roll_is_day_wide():
    assert span("a segunda depois do natal").width == timedelta(days=1)


def test_bare_after_holiday_refused():
    # R146: was a silent "depois da" strand over the plain holiday; refused
    # now -- see test_nl_r146_before_after_holiday.py (en) for the writeup.
    nomatch("depois da páscoa")


@pytest.mark.parametrize("text", ["antes da reunião", "o dia depois do casamento"])
def test_no_reference_no_offset(text):
    nomatch(text)
