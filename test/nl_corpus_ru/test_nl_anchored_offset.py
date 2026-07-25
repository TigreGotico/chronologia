# -*- coding: utf-8 -*-
"""Anchored arithmetic (ru): a signed unit offset or a strict weekday roll on a
resolved reference date. Anchor 2017-06-27; the reference "1 April" resolves to
Sun 2018-04-01 (prefer-future). Every expected date hand-derived."""
from datetime import date, timedelta
import pytest
from ._corpus import AstroDate, span, start, nomatch

REF = date(2018, 4, 1)   # Sunday


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


@pytest.mark.parametrize("text,expected", [
    ("2 недели после 1 апреля", REF + timedelta(days=14)),
    ("2 недели перед 1 апреля", REF - timedelta(days=14)),
])
def test_unit_offset(text, expected):
    assert start(text) == _ad(expected)


@pytest.mark.parametrize("text,expected", [
    ("понедельник после 1 апреля", date(2018, 4, 2)),
    ("понедельник перед 1 апреля", date(2018, 3, 26)),
    ("вторник после 1 апреля", date(2018, 4, 3)),
    ("вторник перед 1 апреля", date(2018, 3, 27)),
])
def test_weekday_roll(text, expected):
    assert start(text) == _ad(expected)


def test_week_offset_is_week_wide():
    assert span("2 недели после 1 апреля").width == timedelta(days=7)


def test_weekday_roll_is_day_wide():
    assert span("понедельник после 1 апреля").width == timedelta(days=1)


@pytest.mark.parametrize("text", ["рабочая встреча"])
def test_no_reference_no_offset(text):
    nomatch(text)


# -- circumfix frame "за N дней до <date>" / "через N дней после <date>" ----
# the offset phrase is led by "за"/"через" and the direction is marked by
# "до" (before) / "после" (after); the lead-in must not be stranded.
@pytest.mark.parametrize("text,expected", [
    ("за 3 дня до 5 апреля", date(2018, 4, 2)),
    ("через 3 дня после 5 апреля", date(2018, 4, 8)),
])
def test_circumfix_offset(text, expected):
    from ._corpus import parse
    assert start(text) == _ad(expected)
    assert parse(text).remainder == ""
