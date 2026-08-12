# -*- coding: utf-8 -*-
"""R134 -- a sub-day duration offset ("half an hour", "45 minutes", "2 hours")
before/after a reference that RESOLVES WITH a time-of-day silently dropped
the offset's own magnitude.

Before the fix, ``anchored._try_offset`` always rebuilt the reference as a
bare ``AstroDate(year, month, day)`` (dropping any hour/minute the reference
carried) and, for a "unit" pre-amble, always widened the shifted result to a
whole civil day via ``_astro_day_span`` -- even for minute/hour units.  Any
clock ("at 9am") in the same sentence is a SEPARATE match at this point in
the pipeline (date+clock composition runs later, in
``timespan._compose``/``compose_date_clock``); it then landed unchanged on
whatever day the offset pass produced.  The result: "half an hour before
March 3 at 9am" and "45 minutes before March 3 at 9am" -- two different
magnitudes -- produced the IDENTICAL wrong answer (2027-03-02 09:00): the day
decremented (any negative sub-day shift from a bare midnight crosses into the
previous day) while the actual minutes/hours requested were thrown away by
the day-wide floor, then the ORIGINAL 9am got re-stamped onto that shifted
day by the later composition, undoing even the accidental day shift's
intent.  A same-day positive shift ("2 hours after ... at 9am") never
crossed midnight, so the offset vanished with no trace at all.

The fix: when a sub-day unit (minute/hour) offsets a reference that either
IS a clock (a bare "before/after 9am") or has an ADJACENT, not-yet-composed
clock_time match right after it ("... at 9am"), do exact instant arithmetic
on the full date+time value and produce a minute-wide span at that exact
instant -- never the whole-day floor.

Expected values below are independently hand-computed (exact clock
subtraction/addition against the stated anchor), never read back from the
parser.
"""
from datetime import datetime

import pytest

from chronologia.extract import extract_timespan

LANG = "en"
_A = datetime(2026, 8, 12, 10, 0)


def _start_end(text, anchor=_A):
    r = extract_timespan(text, LANG, anchor)
    assert r is not None, f"{text!r} did not parse (expected a span)"
    return r[0].start, r[0].end


@pytest.mark.parametrize("text,start,end", [
    # the repro sentences, hand-derived against 2027-03-03 09:00.
    ("half an hour before March 3 at 9am",
     datetime(2027, 3, 3, 8, 30), datetime(2027, 3, 3, 8, 31)),
    ("45 minutes before March 3 at 9am",
     datetime(2027, 3, 3, 8, 15), datetime(2027, 3, 3, 8, 16)),
    ("2 hours after March 3 at 9am",
     datetime(2027, 3, 3, 11, 0), datetime(2027, 3, 3, 11, 1)),
    # a bare clock reference (no date at all) composes the same way.
    ("half an hour before 9am",
     datetime(2026, 8, 13, 8, 30), datetime(2026, 8, 13, 8, 31)),
    ("45 minutes after 9am",
     datetime(2026, 8, 13, 9, 45), datetime(2026, 8, 13, 9, 46)),
    # midnight-crossing: the exact-instant subtraction must cross the civil
    # day boundary, landing the PREVIOUS day at 23:00 -- not just "some
    # previous day, still 1am" (the old day-floor bug's shape).
    ("2 hours before March 3 at 1am",
     datetime(2027, 3, 2, 23, 0), datetime(2027, 3, 2, 23, 1)),
    # a sub-day offset that pushes the clock past midnight forward.
    ("2 hours after March 3 at 11pm",
     datetime(2027, 3, 4, 1, 0), datetime(2027, 3, 4, 1, 1)),
])
def test_subday_offset_clock_anchored_exact(text, start, end):
    got_start, got_end = _start_end(text)
    assert got_start == start
    assert got_end == end


def test_different_magnitudes_give_different_answers():
    # the literal shape of the defect: two different durations must NOT
    # collapse to the same wrong output.
    half_hour = _start_end("half an hour before March 3 at 9am")
    fortyfive = _start_end("45 minutes before March 3 at 9am")
    assert half_hour != fortyfive


def test_offset_direction_is_not_silently_dropped():
    # "2 hours after ... at 9am" must not read as an un-offset 9am.
    offset = _start_end("2 hours after March 3 at 9am")
    bare = _start_end("March 3 at 9am")
    assert offset != bare


# -- controls: pinned behaviour this fix must NOT disturb -------------------

@pytest.mark.parametrize("text,start,end", [
    # day-grain arithmetic on a bare date -- unaffected.
    ("2 days before March 3",
     datetime(2027, 3, 1, 0, 0), datetime(2027, 3, 2, 0, 0)),
])
def test_day_grain_offset_unaffected(text, start, end):
    got_start, got_end = _start_end(text)
    assert got_start == start
    assert got_end == end


def test_no_clock_subday_offset_still_floors_to_day():
    # a sub-day offset on a DATE with NO time-of-day in the sentence has no
    # clock to do exact arithmetic against: it still floors to the whole
    # shifted civil day (pinned pre-existing behaviour, not this defect).
    got_start, got_end = _start_end("half an hour before March 3")
    assert got_start == datetime(2027, 3, 2, 0, 0)
    assert got_end == datetime(2027, 3, 3, 0, 0)


@pytest.mark.parametrize("text,start,end", [
    ("the day after easter",
     datetime(2027, 3, 29, 0, 0), datetime(2027, 3, 30, 0, 0)),
    ("two weeks after easter",
     datetime(2027, 4, 11, 0, 0), datetime(2027, 4, 12, 0, 0)),
])
def test_anchored_holiday_offsets_unaffected(text, start, end):
    got_start, got_end = _start_end(text)
    assert got_start == start
    assert got_end == end
