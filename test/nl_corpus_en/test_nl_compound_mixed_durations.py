"""Mixed-grain duration/offset compounds -- a calendar-grain unit
(month/year/decade/...) chained by "and"/"," to a fixed-grain unit
(second..fortnight), in EITHER order.

Two public edges are covered:

* :func:`extract_timespan` -- "in 3 months and 2 days" must COMPOSE both
  components into one AstroDate-space point (calendar-grain first, then
  fixed-grain, regardless of the TEXTUAL order the units were said in), not
  return the span of the first unit alone with the rest stranded in the
  remainder.  The composed span is a POINT of the FINEST unit named anywhere
  in the compound -- the same width convention a bare single-unit offset
  ("in 2 days" -> a day-wide span) already follows.

* :func:`extract_duration` -- a calendar-grain unit is not a fixed-width
  length (a bare "3 months" already refuses with ``None`` rather than guess
  a 30-day month; see ``test_nl_duration.py::test_not_a_duration``).  A MIXED
  compound must follow the identical convention and refuse WHOLE, never
  answer with only its fixed-width part and strand the calendar part in the
  remainder -- a partial value with the rest dropped is a wrong answer, not
  a partial one.

Every expected span is hand-derived with ``dateutil.relativedelta`` (which
itself applies the month/day components in the same calendar-then-fixed
order), never by reading the parser's own output back as gold.
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from chronologia.extract import extract_duration
from chronologia.extract.timespan import extract_timespan
from chronologia.astrodate import AstroDate

from ._corpus import ANCHOR, nomatch, start_end

LANG = "en"


def _point(anchor=ANCHOR, **delta):
    """anchor + relativedelta(**delta) -> AstroDate, dropping nothing."""
    dt = anchor + relativedelta(**delta)
    return AstroDate(dt.year, dt.month, dt.day, dt.hour, dt.minute,
                     dt.second, dt.microsecond)


# -- extract_timespan: calendar + fixed compose into ONE point -------------

@pytest.mark.parametrize("text", [
    "in 3 months and 2 days",
    "in 2 days and 3 months",          # reversed textual order: same instant
])
def test_month_day_compound_composes_both(text):
    start, end = start_end(text)
    exp_start = _point(months=3, days=2)
    assert start == exp_start, f"{text!r}: {start} != {exp_start}"
    assert end == exp_start + timedelta(days=1), \
        "finest unit here is 'day' -> a day-wide span"


def test_year_month_day_three_part_compound():
    start, end = start_end("in 1 year, 2 months and 3 days")
    exp_start = _point(years=1, months=2, days=3)
    assert start == exp_start
    assert end == exp_start + timedelta(days=1)


def test_year_and_day_compound():
    # probed convention: "in a year and a day" composes to year+1, then +1
    # day -- a day-wide span, not the bare year-wide span "in a year" alone
    # gives.
    start, end = start_end("in a year and a day")
    exp_start = _point(years=1, days=1)
    assert start == exp_start
    assert end == exp_start + timedelta(days=1)


def test_month_hour_compound_finest_is_hour():
    start, end = start_end("in 1 month and 3 hours")
    exp_start = _point(months=1, hours=3)
    assert start == exp_start
    assert end == exp_start + timedelta(hours=1)


# -- controls: pure fixed-grain compounds already worked, must stay exact --

def test_pure_fixed_grain_compound_composes():
    start, end = start_end("in 3 days and 2 hours")
    exp_start = ANCHOR + timedelta(days=3, hours=2)
    exp_start = AstroDate(exp_start.year, exp_start.month, exp_start.day,
                          exp_start.hour, exp_start.minute, exp_start.second,
                          exp_start.microsecond)
    assert start == exp_start
    assert end == exp_start + timedelta(hours=1)


def test_bare_single_unit_controls_unchanged():
    start, end = start_end("in 3 months")
    exp_start = _point(months=3)
    assert start == exp_start
    assert end == _point(months=4)

    start, end = start_end("in 2 days")
    exp_start = ANCHOR + timedelta(days=2)
    exp_start = AstroDate(exp_start.year, exp_start.month, exp_start.day,
                          exp_start.hour, exp_start.minute, exp_start.second,
                          exp_start.microsecond)
    assert start == exp_start
    assert end == exp_start + timedelta(days=1)


def test_recurrence_every_n_weeks_untouched():
    # "every 2 weeks" is a recurrence, not an offset compound -- must stay
    # unmatched by extract_timespan exactly as before this change.
    nomatch("every 2 weeks")


# -- extract_duration: mixed compounds refuse WHOLE, never strand a part ---

@pytest.mark.parametrize("text", [
    "3 months and 2 days",
    "2 days and 3 months",
    "3 years and 2 months",
    "1 year, 2 months and 3 days",
    "in a year and a day",
])
def test_mixed_calendar_fixed_duration_refuses(text):
    assert extract_duration(text, LANG) is None


def test_bare_calendar_duration_still_refuses():
    # unchanged control (test_nl_duration.py already pins this; repeated here
    # as the reference point the mixed-compound refusal must match).
    assert extract_duration("3 months", LANG) is None


def test_pure_fixed_grain_duration_compound_unaffected():
    got = extract_duration("3 days and 2 hours", LANG)
    assert got == (timedelta(days=3, hours=2), "")

    got = extract_duration("1 year, 2 months and 3 days".replace(
        "1 year, 2 months and ", ""), LANG)
    assert got == (timedelta(days=3), "")
