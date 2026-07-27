"""Anchored arithmetic (feature 1), German.

A signed unit offset or a strict weekday roll composed onto a resolved
reference ("2 wochen nach ostern", "der montag nach weihnachten").  Anchor
2017-06-27 (Dienstag).  Reference dates from the independent computus /
civil table: ostern 2018 = So 2018-04-01, weihnachten = Mo 2017-12-25.
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, span, start, nomatch

OSTERN = date(2018, 4, 1)
WEIHNACHTEN = date(2017, 12, 25)


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


@pytest.mark.parametrize("text,expected", [
    ("2 wochen nach ostern", OSTERN + timedelta(days=14)),
    ("1 woche vor ostern", OSTERN - timedelta(days=7)),
    ("2 wochen vor weihnachten", WEIHNACHTEN - timedelta(days=14)),
    ("3 tage vor weihnachten", WEIHNACHTEN - timedelta(days=3)),
    ("10 tage nach weihnachten", WEIHNACHTEN + timedelta(days=10)),
    ("ein tag nach weihnachten", WEIHNACHTEN + timedelta(days=1)),
    ("der tag nach weihnachten", WEIHNACHTEN + timedelta(days=1)),
    ("1 monat nach ostern", date(2018, 5, 1)),
])
def test_unit_offset(text, expected):
    assert start(text) == _ad(expected)


@pytest.mark.parametrize("text,expected", [
    ("der montag nach weihnachten", date(2018, 1, 1)),
    ("der freitag nach weihnachten", date(2017, 12, 29)),
    ("der dienstag vor weihnachten", date(2017, 12, 19)),
    ("der sonntag nach ostern", date(2018, 4, 8)),
    ("der samstag vor ostern", date(2018, 3, 31)),
    ("der freitag vor ostern", date(2018, 3, 30)),
])
def test_weekday_roll(text, expected):
    assert start(text) == _ad(expected)


# an offset resolves to the single shifted day, not a period-wide span:
# the offset amount is the SHIFT, never the result width (was days=7,
# a silent-wrong -- see en test_nl_anchored_offset_point).
def test_week_offset_is_day_wide():
    assert span("2 wochen nach ostern").width == timedelta(days=1)


def test_weekday_roll_is_day_wide():
    assert span("der montag nach weihnachten").width == timedelta(days=1)


def test_bare_after_holiday_unchanged():
    assert start("nach ostern") == _ad(OSTERN)


@pytest.mark.parametrize("text", ["vor dem termin", "der tag nach dem meeting"])
def test_no_reference_no_offset(text):
    nomatch(text)
