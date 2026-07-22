# -*- coding: utf-8 -*-
"""Anchored arithmetic (sl): a signed unit offset or a strict weekday roll on a
resolved reference date. Anchor 2017-06-27; the reference "1 April" resolves to
Sun 2018-04-01 (prefer-future). Every expected date hand-derived."""
from datetime import date, timedelta
import pytest
from ._corpus import AstroDate, span, start, nomatch

REF = date(2018, 4, 1)   # Sunday


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


@pytest.mark.parametrize("text,expected", [
    ("2 tedna po 1. aprila", REF + timedelta(days=14)),
    ("2 tedna pred 1. aprila", REF - timedelta(days=14)),
])
def test_unit_offset(text, expected):
    assert start(text) == _ad(expected)


@pytest.mark.parametrize("text,expected", [
    ("ponedeljek po 1. aprila", date(2018, 4, 2)),
    ("ponedeljek pred 1. aprila", date(2018, 3, 26)),
    ("torek po 1. aprila", date(2018, 4, 3)),
    ("torek pred 1. aprila", date(2018, 3, 27)),
])
def test_weekday_roll(text, expected):
    assert start(text) == _ad(expected)


def test_week_offset_is_week_wide():
    assert span("2 tedna po 1. aprila").width == timedelta(days=7)


def test_weekday_roll_is_day_wide():
    assert span("ponedeljek po 1. aprila").width == timedelta(days=1)


@pytest.mark.parametrize("text", ["poslovni sestanek"])
def test_no_reference_no_offset(text):
    nomatch(text)
