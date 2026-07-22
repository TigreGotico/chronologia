# -*- coding: utf-8 -*-
"""Anchored arithmetic (pl): a signed unit offset or a strict weekday roll on a
resolved reference date. Anchor 2017-06-27; the reference "1 April" resolves to
Sun 2018-04-01 (prefer-future). Every expected date hand-derived."""
from datetime import date, timedelta
import pytest
from ._corpus import AstroDate, span, start, nomatch

REF = date(2018, 4, 1)   # Sunday


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


@pytest.mark.parametrize("text,expected", [
    ("2 tygodnie po 1 kwietnia", REF + timedelta(days=14)),
    ("2 tygodnie przed 1 kwietnia", REF - timedelta(days=14)),
])
def test_unit_offset(text, expected):
    assert start(text) == _ad(expected)


@pytest.mark.parametrize("text,expected", [
    ("poniedziałek po 1 kwietnia", date(2018, 4, 2)),
    ("poniedziałek przed 1 kwietnia", date(2018, 3, 26)),
    ("wtorek po 1 kwietnia", date(2018, 4, 3)),
    ("wtorek przed 1 kwietnia", date(2018, 3, 27)),
])
def test_weekday_roll(text, expected):
    assert start(text) == _ad(expected)


def test_week_offset_is_week_wide():
    assert span("2 tygodnie po 1 kwietnia").width == timedelta(days=7)


def test_weekday_roll_is_day_wide():
    assert span("poniedziałek po 1 kwietnia").width == timedelta(days=1)


@pytest.mark.parametrize("text", ["spotkanie służbowe"])
def test_no_reference_no_offset(text):
    nomatch(text)
