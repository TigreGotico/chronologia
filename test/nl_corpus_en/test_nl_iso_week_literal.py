"""The ISO-8601 week designator literal: "2024-W10" and "2024-W10-1".

ISO 8601 §4.4.4.2 writes a week as ``YYYY-Www`` and one day of it as
``YYYY-Www-D``.  Weeks begin on **Monday** and week 01 is the week containing
the year's first Thursday (equivalently, containing 4 January), so the year in
the literal is the ISO *week-numbering* year, not the calendar year: a long
year has 53 weeks and its last week runs on into January.

These literals used to be read as a bare year -- "2024-W10" resolved to the
whole of 2024, a confidently wrong answer.  The expected dates below are
computed with the stdlib ``date.fromisocalendar``, independent of the parser
under test.
"""
from datetime import date, timedelta

import pytest

from chronologia.astrodate import AstroDate
from ._corpus import start_end, nomatch, span


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


# (text, iso-year, iso-week) -- the week-wide literal
_WEEKS = [
    ("2024-W10", 2024, 10),
    ("2024-w10", 2024, 10),          # lowercase 'w' accepted as permissive input
    ("2024-W01", 2024, 1),
    ("2024-W52", 2024, 52),          # 2024's LAST ISO week -- it has only 52
    ("2026-W32", 2026, 32),
    ("1999-W10", 1999, 10),
    # 2020 is a 53-week ISO year and W53 spans the new year: 2020-12-28..2021-01-04
    ("2020-W53", 2020, 53),
]


@pytest.mark.parametrize("text,iy,iw", _WEEKS)
def test_iso_week_literal(text, iy, iw):
    monday = date.fromisocalendar(iy, iw, 1)
    s, e = start_end(text)
    assert s == _ad(monday)
    assert e == _ad(monday + timedelta(days=7))


def test_2020_w53_crosses_the_year_boundary():
    """The 53rd ISO week of 2020 starts 2020-12-28 and runs into 2021."""
    s, e = start_end("2020-W53")
    assert s == AstroDate(2020, 12, 28)
    assert e == AstroDate(2021, 1, 4)


# (text, iso-year, iso-week, iso-weekday) -- the day-wide literal
_DAYS = [
    ("2024-W10-1", 2024, 10, 1),     # 1 = Monday
    ("2024-W10-4", 2024, 10, 4),
    ("2024-W10-7", 2024, 10, 7),     # 7 = Sunday
    ("2024-w10-1", 2024, 10, 1),
    ("2020-W53-1", 2020, 53, 1),
    ("2020-W53-7", 2020, 53, 7),     # falls in January 2021
]


@pytest.mark.parametrize("text,iy,iw,iwd", _DAYS)
def test_iso_week_date_literal(text, iy, iw, iwd):
    day = date.fromisocalendar(iy, iw, iwd)
    s, e = start_end(text)
    assert s == _ad(day)
    assert e == _ad(day + timedelta(days=1))


def test_iso_weekday_1_is_monday():
    s, e = start_end("2024-W10-1")
    assert (s, e) == (AstroDate(2024, 3, 4), AstroDate(2024, 3, 5))
    assert date(2024, 3, 4).weekday() == 0          # Monday, independently


def test_iso_weekday_7_is_sunday():
    s, e = start_end("2024-W10-7")
    assert (s, e) == (AstroDate(2024, 3, 10), AstroDate(2024, 3, 11))
    assert date(2024, 3, 10).weekday() == 6         # Sunday, independently


def test_literal_and_prose_agree():
    """"2024-W10" and "week 10 of 2024" name the same week, exactly."""
    assert span("2024-W10") == span("week 10 of 2024")
    assert start_end("2024-W10") == (AstroDate(2024, 3, 4),
                                     AstroDate(2024, 3, 11))


def test_prose_ordinal_and_cardinal_agree():
    """"the 10th week of 2024" == "week 10 of 2024" -- the ordinal surface
    used to be dropped, leaving a bare-year reading of the whole of 2024."""
    assert span("the 10th week of 2024") == span("week 10 of 2024")
    assert start_end("the 10th week of 2024") == (AstroDate(2024, 3, 4),
                                                  AstroDate(2024, 3, 11))
    assert span("the tenth week of 2024") == span("week 10 of 2024")


# out of range: a literal naming no ISO week (or no ISO weekday) resolves to
# None -- never to the enclosing year, never to a fabricated span.  2024 has
# 52 ISO weeks and 2021 has 52; 2020 has 53.
@pytest.mark.parametrize("text", [
    "2024-W53",      # 2024 has only 52 ISO weeks
    "2021-W53",      # 2021 has only 52 ISO weeks
    "2024-W00",
    "2024-W99",
    "2024-w53",
    "2024-W10-8",
    "2024-W10-0",
    "2020-W54",
])
def test_out_of_range_refuses(text):
    nomatch(text)


def test_week_counts_are_what_the_standard_says():
    """Guard for the boundary cases above: 28 December always falls in the
    last ISO week of its year, so it names the week count directly."""
    assert date(2024, 12, 28).isocalendar()[1] == 52
    assert date(2021, 12, 28).isocalendar()[1] == 52
    assert date(2020, 12, 28).isocalendar()[1] == 53


# the neighbouring literal shapes must be untouched by the new one
@pytest.mark.parametrize("text,s,e", [
    ("2024-03", AstroDate(2024, 3, 1), AstroDate(2024, 4, 1)),
    ("2024-03-06", AstroDate(2024, 3, 6), AstroDate(2024, 3, 7)),
    ("12/11/2024", AstroDate(2024, 12, 11), AstroDate(2024, 12, 12)),
    ("2024", AstroDate(2024, 1, 1), AstroDate(2025, 1, 1)),
])
def test_neighbouring_literals_unchanged(text, s, e):
    assert start_end(text) == (s, e)
