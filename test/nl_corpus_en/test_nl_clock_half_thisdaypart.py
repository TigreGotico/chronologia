"""Two clock-composition idioms that used to drop their qualifier.

Both build on the PR #281 machinery that lets "<hour> in the <daypart>"
compose a 24-hour clock reading ("3 in the afternoon" -> 15:00).

(A) The British colloquial "half <hour>" (half *past* the stated hour) kept
    its half-past offset only bare ("half ten" -> 10:30); combined with an
    "in the <daypart>" phrase the "half" was stranded in the remainder and the
    time lost its 30 minutes ("half five in the evening" -> 17:00, not 17:30).

(B) "<hour[:min]> this <daypart>" must read the daypart as an am/pm meridiem
    AND anchor to TODAY -- "this afternoon" is this calendar day's afternoon
    even when the wall time has already elapsed, so no prefer-future roll to
    tomorrow: "2:30 this afternoon" -> today 14:30, "9:15 this morning" ->
    today 09:15.

Anchor: Tuesday 2017-06-27 13:04.
"""
import pytest

from ._corpus import span, start, parse, ANCHOR


# ---------------------------------------------------------------------------
# (A) "half <hour> in the <daypart>" keeps the half-past offset AND takes the
#     daypart meridiem.  "half" is British additive: half *past* the hour.
# ---------------------------------------------------------------------------
# (text, y, mo, d, hh, mm)
_HALF_DAYPART = [
    ("half five in the evening",   2017, 6, 27, 17, 30),
    ("half three in the afternoon", 2017, 6, 27, 15, 30),
    ("half six in the evening",    2017, 6, 27, 18, 30),
    # morning is before the anchor -> prefer_future rolls to tomorrow, exactly
    # as the bare "3 in the morning" already does; the point is the :30 survives
    ("half eight in the morning",  2017, 6, 28, 8, 30),
]


@pytest.mark.parametrize("text,y,mo,d,hh,mm", _HALF_DAYPART)
def test_half_hour_in_the_daypart_keeps_half_and_meridiem(text, y, mo, d, hh, mm):
    s = span(text).start
    assert (s.year, s.month, s.day, s.hour, s.minute) == (y, mo, d, hh, mm)


# ---------------------------------------------------------------------------
# (B) "<hour[:min]> this <daypart>": meridiem from the daypart, anchored TODAY
#     (no prefer-future roll even when the wall time is already past).
# ---------------------------------------------------------------------------
_THIS_DAYPART = [
    ("2:30 this afternoon",    2017, 6, 27, 14, 30),
    ("at 2:30 this afternoon", 2017, 6, 27, 14, 30),
    ("4:45 this afternoon",    2017, 6, 27, 16, 45),
    ("9:15 this morning",      2017, 6, 27, 9, 15),   # < anchor, but stays TODAY
    ("3 this afternoon",       2017, 6, 27, 15, 0),
    ("9 this morning",         2017, 6, 27, 9, 0),
]


@pytest.mark.parametrize("text,y,mo,d,hh,mm", _THIS_DAYPART)
def test_hour_this_daypart_composes_meridiem_today(text, y, mo, d, hh, mm):
    s = span(text).start
    assert (s.year, s.month, s.day, s.hour, s.minute) == (y, mo, d, hh, mm)


@pytest.mark.parametrize("text", [t[0] for t in _THIS_DAYPART])
def test_hour_this_daypart_consumes_the_daypart(text):
    # the daypart word must not strand in the remainder
    _, rem = parse(text)
    assert "afternoon" not in rem and "morning" not in rem


# ---------------------------------------------------------------------------
# Regression pins: the #281 "in the" forms, bare "half", and bare dayparts all
# stay byte-identical.
# ---------------------------------------------------------------------------
_UNCHANGED = [
    # (text, y, mo, d, hh, mm)  -- clock (minute-wide)
    ("3 in the afternoon", 2017, 6, 27, 15, 0),
    ("3 in the morning",   2017, 6, 28, 3, 0),
    ("half ten",           2017, 6, 28, 10, 30),
    ("half past three",    2017, 6, 28, 3, 30),
    ("at 3pm",             2017, 6, 27, 15, 0),
    ("2:30pm",             2017, 6, 27, 14, 30),
]


@pytest.mark.parametrize("text,y,mo,d,hh,mm", _UNCHANGED)
def test_neighbouring_clock_forms_unchanged(text, y, mo, d, hh, mm):
    s = span(text).start
    assert (s.year, s.month, s.day, s.hour, s.minute) == (y, mo, d, hh, mm)


def test_half_nine_at_night_unchanged():
    # only "at night" strands; the half-past 09:30 survives, on tomorrow
    s = span("half nine at night").start
    assert (s.year, s.month, s.day, s.hour, s.minute) == (2017, 6, 28, 9, 30)


# bare dayparts remain whole-band spans, not clock points
_BARE_BANDS = [
    ("this morning",   6, 6, 12),   # (name, start_h, ... ) start/end hours
    ("this afternoon", 12, 12, 18),
]


def test_bare_this_morning_band_unchanged():
    s = span("this morning")
    assert (s.start.hour, s.end.hour) == (6, 12)
    assert s.start.day == 27


def test_bare_this_afternoon_band_unchanged():
    s = span("this afternoon")
    assert (s.start.hour, s.end.hour) == (12, 18)
    assert s.start.day == 27


def test_tonight_band_unchanged():
    s = span("tonight")
    assert (s.start.hour, s.start.day) == (21, 27)
