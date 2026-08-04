""""the next/last <N> <units>" -- a rolling span of N whole units.

Distinct from rel_period's single calendar-aligned unit ("next week" is the
seven days of the following calendar week): "the next 3 weeks" is the 21 days
starting today, "the last 2 months" the two months ending today.  The span is
anchored on the current DAY, not the calendar grid, mirroring how "in N weeks"
offsets from now.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

A = datetime(2024, 6, 15, 12, 0)


def _span(text):
    r = extract_timespan(text, "en", A)
    return None if r is None else (r.span.start, r.span.end)


@pytest.mark.parametrize("text,s,e", [
    # forward: [today, today + N units)
    ("the next 3 weeks", AstroDate(2024, 6, 15), AstroDate(2024, 7, 6)),
    ("next 3 weeks", AstroDate(2024, 6, 15), AstroDate(2024, 7, 6)),
    ("the next three weeks", AstroDate(2024, 6, 15), AstroDate(2024, 7, 6)),
    ("the next 2 days", AstroDate(2024, 6, 15), AstroDate(2024, 6, 17)),
    ("the next 3 months", AstroDate(2024, 6, 15), AstroDate(2024, 9, 15)),
    ("the next 2 years", AstroDate(2024, 6, 15), AstroDate(2026, 6, 15)),
    ("over the next 3 weeks", AstroDate(2024, 6, 15), AstroDate(2024, 7, 6)),
    # backward: [today - N units, today)
    ("the last 3 weeks", AstroDate(2024, 5, 25), AstroDate(2024, 6, 15)),
    ("the last 2 days", AstroDate(2024, 6, 13), AstroDate(2024, 6, 15)),
])
def test_next_last_n_units_span(text, s, e):
    got = _span(text)
    assert got == (s, e), text


@pytest.mark.parametrize("text,s,e", [
    # the single-unit rel_period reading is UNCHANGED: a calendar-aligned unit,
    # not a rolling span anchored on today.
    ("the next week", AstroDate(2024, 6, 17), AstroDate(2024, 6, 24)),
    ("the next month", AstroDate(2024, 7, 1), AstroDate(2024, 8, 1)),
    ("next year", AstroDate(2025, 1, 1), AstroDate(2026, 1, 1)),
    ("this week", AstroDate(2024, 6, 10), AstroDate(2024, 6, 17)),
])
def test_single_unit_rel_period_unchanged(text, s, e):
    assert _span(text) == (s, e), text


@pytest.mark.parametrize("text,s,e", [
    # synonym relative markers: coming/upcoming == next (+1), previous/prior/
    # past == last (-1), in both the single-unit and the N-unit-span readings.
    ("the coming week", AstroDate(2024, 6, 17), AstroDate(2024, 6, 24)),
    ("the upcoming month", AstroDate(2024, 7, 1), AstroDate(2024, 8, 1)),
    ("the past month", AstroDate(2024, 5, 1), AstroDate(2024, 6, 1)),
    ("the coming 3 weeks", AstroDate(2024, 6, 15), AstroDate(2024, 7, 6)),
    ("the past 2 months", AstroDate(2024, 4, 15), AstroDate(2024, 6, 15)),
    ("the previous 2 weeks", AstroDate(2024, 6, 1), AstroDate(2024, 6, 15)),
])
def test_relative_marker_synonyms(text, s, e):
    assert _span(text) == (s, e), text


def test_past_synonym_does_not_break_clock_past():
    # "past" is a relative marker (-1) AND the clock "quarter past" direction;
    # the clock uses a separate slot, so both readings coexist.
    r = extract_timespan("quarter past nine", "en", A)
    assert r is not None and (r.span.start.hour, r.span.start.minute) == (9, 15)


def test_offset_point_readings_unchanged():
    # "in N weeks" is still a POINT N weeks out (a week-wide span at the offset
    # instant, keeping the anchor's time-of-day), NOT a rolling span from now --
    # compare dates, since the offset reading preserves the 12:00 anchor time.
    s, e = _span("in 3 weeks")
    assert (s.date(), e.date()) == (AstroDate(2024, 7, 6).date(),
                                    AstroDate(2024, 7, 13).date())
    s, e = _span("3 weeks ago")
    assert (s.date(), e.date()) == (AstroDate(2024, 5, 25).date(),
                                    AstroDate(2024, 6, 1).date())
