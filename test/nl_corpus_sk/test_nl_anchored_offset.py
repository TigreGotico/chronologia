# -*- coding: utf-8 -*-
"""Anchored arithmetic (sk): a signed unit offset or a strict weekday roll on a
resolved reference date. Anchor 2017-06-27; the reference "1 April" resolves to
Sun 2018-04-01 (prefer-future). Every expected date hand-derived."""
from datetime import date, timedelta
import pytest
from ._corpus import AstroDate, span, start, nomatch

REF = date(2018, 4, 1)   # Sunday


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


@pytest.mark.parametrize("text,expected", [
    ("2 týždne po 1. apríla", REF + timedelta(days=14)),
    ("2 týždne pred 1. apríla", REF - timedelta(days=14)),
])
def test_unit_offset(text, expected):
    assert start(text) == _ad(expected)


@pytest.mark.parametrize("text,expected", [
    ("pondelok po 1. apríla", date(2018, 4, 2)),
    ("pondelok pred 1. apríla", date(2018, 3, 26)),
    ("utorok po 1. apríla", date(2018, 4, 3)),
    ("utorok pred 1. apríla", date(2018, 3, 27)),
])
def test_weekday_roll(text, expected):
    assert start(text) == _ad(expected)


# an offset resolves to the single shifted day, not a period-wide span:
# the offset amount is the SHIFT, never the result width (was days=7,
# a silent-wrong -- see en test_nl_anchored_offset_point).
def test_week_offset_is_day_wide():
    assert span("2 týždne po 1. apríla").width == timedelta(days=1)


def test_weekday_roll_is_day_wide():
    assert span("pondelok po 1. apríla").width == timedelta(days=1)


@pytest.mark.parametrize("text", ["pracovná schôdzka"])
def test_no_reference_no_offset(text):
    nomatch(text)
