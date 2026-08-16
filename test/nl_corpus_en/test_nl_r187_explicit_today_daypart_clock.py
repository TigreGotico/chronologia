"""R187: an EXPLICIT-today day-part ("tonight", "this evening") composed
with an ambiguous bare-hour clock must anchor TODAY -- it must never roll to
tomorrow just because the unshifted hour sits before the anchor's wall time.

Before this fix, "tonight at 8" (anchor 10:00) read 2026-08-15 20:00
(tomorrow): the clock's own resolution rolled the UNSHIFTED hour 8 forward
because 8 < 10, and only afterwards did the day-part's PM shift turn 8 into
20 -- the roll decision ran on the wrong (pre-shift) number.  "tonight at
11" happened to read correctly by luck (11 > 10, so no roll fired), and
"tonight at 8pm" was unaffected because an explicit meridiem pins the hour
straight to 24-hour form, bypassing the ambiguous-hour roll rule entirely.

The fix pins the day-part+clock composition to the day-part's own resolved
day (today) whenever the day-part is explicitly "this <daypart>" or a bare
word lexically fused with today ("tonight"); a genuinely bare, non-explicit
day-part ("evening at 3", no "this"/"tonight") keeps the clock's own
roll-to-tomorrow rule untouched (see test_nl_r117_daypart_clock_meridiem.py).

Anchor: Friday 2026-08-14 10:00 -- every hour 1..12 is tested so the fixed
composition is exercised across the whole PM shift (hours < 10 used to
roll, hours >= 10 already didn't).

Gold is derived by hand: today's date at the PM-shifted hour for PM-side
day-parts (evening/afternoon/night), the literal hour for the AM-side
morning day-part.
"""
import pytest

from ._corpus import parse

ANCHOR_R187 = __import__("datetime").datetime(2026, 8, 14, 10, 0)
TODAY = 14


def _p(text):
    return parse(text, ANCHOR_R187)


def _pm(h):
    return h + 12 if h != 12 else 12


def _am(h):
    return h if h != 12 else 12


# (label, pm_side)
_PM_DAYPARTS = ["tonight", "this evening", "this afternoon"]


@pytest.mark.parametrize("daypart", _PM_DAYPARTS)
@pytest.mark.parametrize("h", range(1, 13))
def test_pm_explicit_today_daypart_stays_on_anchor_day(daypart, h):
    text = f"{daypart} at {h}"
    r = _p(text)
    assert r is not None, f"{text!r} did not parse"
    s = r.span.start
    assert (s.year, s.month, s.day) == (2026, 8, TODAY), text
    assert s.hour == _pm(h), text
    assert r.remainder == "", text


@pytest.mark.parametrize("h", range(1, 13))
def test_am_explicit_today_daypart_stays_on_anchor_day(h):
    text = f"this morning at {h}"
    r = _p(text)
    assert r is not None, f"{text!r} did not parse"
    s = r.span.start
    assert (s.year, s.month, s.day) == (2026, 8, TODAY), text
    assert s.hour == _am(h), text
    assert r.remainder == "", text


@pytest.mark.parametrize("text,hour", [
    ("tonight at 8pm", 20),      # explicit meridiem, already pinned
    ("tonight at 20:00", 20),    # 24-hour clock, already pinned
])
def test_unambiguous_forms_unaffected(text, hour):
    r = _p(text)
    assert r is not None
    s = r.span.start
    assert (s.year, s.month, s.day, s.hour) == (2026, 8, TODAY, hour)
    assert r.remainder == ""


def test_bare_non_explicit_daypart_still_rolls_forward():
    """"evening at 3" (no "this"/"tonight") keeps the clock's own
    roll-to-tomorrow rule -- the documented R117 convention, untouched by
    this fix."""
    r = _p("evening at 3")
    assert r is not None
    s = r.span.start
    assert (s.year, s.month, s.day, s.hour) == (2026, 8, 15, 15)


def test_bare_tonight_band_still_todays_night():
    """A bare "tonight" with no clock stays the whole-band reading,
    unaffected by the clock-composition fix."""
    r = _p("tonight")
    s = r.span.start
    assert (s.year, s.month, s.day, s.hour) == (2026, 8, TODAY, 21)


# ---------------------------------------------------------------------------
# Defect 2: fraction-carrying clock forms must compose with "this <daypart>"
# the same way a bare hour already does.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("text,hour,minute", [
    ("quarter past 3 this afternoon", 15, 15),
    ("half past 3 this afternoon", 15, 30),
    ("20 past 3 this afternoon", 15, 20),
    ("quarter to 4 this afternoon", 15, 45),
    ("half past 9 this morning", 9, 30),
])
def test_fraction_clock_composes_with_this_daypart(text, hour, minute):
    r = _p(text)
    assert r is not None, f"{text!r} did not parse"
    s = r.span.start
    assert (s.year, s.month, s.day, s.hour, s.minute) == (
        2026, 8, TODAY, hour, minute), text
    assert r.remainder == "", text


def test_bare_hour_this_daypart_control_unaffected():
    """"3 this afternoon" (the pre-existing bare-hour composition) must not
    regress alongside the new fraction-carrying orders."""
    r = _p("3 this afternoon")
    assert r is not None
    s = r.span.start
    assert (s.year, s.month, s.day, s.hour, s.minute) == (2026, 8, TODAY, 15, 0)
    assert r.remainder == ""
