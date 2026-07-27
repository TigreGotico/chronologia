# -*- coding: utf-8 -*-
"""Anchored arithmetic (hr): a signed unit offset or a strict weekday roll on a
resolved reference date. Anchor 2017-06-27; the reference "1 April" resolves to
Sun 2018-04-01 (prefer-future). Every expected date hand-derived."""
from datetime import date, timedelta
import pytest
from ._corpus import AstroDate, span, start, nomatch

REF = date(2018, 4, 1)   # Sunday


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


@pytest.mark.parametrize("text,expected", [
    ("2 tjedna nakon 1. travnja", REF + timedelta(days=14)),
    ("2 tjedna prije 1. travnja", REF - timedelta(days=14)),
])
def test_unit_offset(text, expected):
    assert start(text) == _ad(expected)


@pytest.mark.parametrize("text,expected", [
    ("ponedjeljak nakon 1. travnja", date(2018, 4, 2)),
    ("ponedjeljak prije 1. travnja", date(2018, 3, 26)),
    ("utorak nakon 1. travnja", date(2018, 4, 3)),
    ("utorak prije 1. travnja", date(2018, 3, 27)),
])
def test_weekday_roll(text, expected):
    assert start(text) == _ad(expected)


# an offset resolves to the single shifted day, not a period-wide span:
# the offset amount is the SHIFT, never the result width (was days=7,
# a silent-wrong -- see en test_nl_anchored_offset_point).
def test_week_offset_is_day_wide():
    assert span("2 tjedna nakon 1. travnja").width == timedelta(days=1)


def test_weekday_roll_is_day_wide():
    assert span("ponedjeljak nakon 1. travnja").width == timedelta(days=1)


@pytest.mark.parametrize("text", ["poslovni sastanak"])
def test_no_reference_no_offset(text):
    nomatch(text)
