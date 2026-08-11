# -*- coding: utf-8 -*-
"""R117: a preceding day-part word composes onto an adjacent explicit clock
as a meridiem hint -- the shared-layer fix in
:mod:`chronologia.extract.resolver` (:func:`compose_daypart_clock`), proven
here in Russian.

Before the fix, "вечером в 9 часов" ("in the evening at 9 o'clock") read
18:00-00:00 -- a WEEK-scale/bare fallback that stranded the entire "в 9
часов" clock clause -- instead of composing to the intended 21:00.  Adding
an explicit date ("встретимся в следующий вторник вечером в 9 часов") made
it silently worse: a confident-looking 09:00 (a 12-hour error) with
"вечером" stranded in the remainder.

The postposed genitive form ("в 9 часов вечера") already worked before this
fix -- the day-part word there fuses into the clock construction's own
MERIDIEM slot at match time, never reaching the composer as a separate
``daypart_ref`` match.  It is pinned here as a regression control.

Gold is derived by hand from the mission anchor
``datetime(2026, 8, 11, 12, 0)`` (a Tuesday).  For the bare (dateless) forms,
the clock's own "roll to tomorrow if already past the anchor" rule (a
pre-existing, untouched pass) runs on the bare pre-shift hour BEFORE the
day-part's meridiem shift -- see the English R117 file's docstring for the
worked trace; the same rule applies here, so "вечером в 9 часов" and "утром
в 9 часов" both roll their bare hour (9, before the 12:00 anchor) to
2026-08-12 first, and the day-part shift (+12 for the PM-side "вечером",
+0 for "утром") lands on that rolled day.
"""
from datetime import datetime

from chronologia.astrodate import AstroDate
from ._corpus import parse, start_end, nomatch

ANCHOR_R117 = datetime(2026, 8, 11, 12, 0)


def _p(text):
    return parse(text, ANCHOR_R117)


def test_preceding_vecherom_composes_as_pm_meridiem_bare_no_date():
    r = _p("вечером в 9 часов")
    assert r is not None
    assert start_end("вечером в 9 часов", ANCHOR_R117) == (
        AstroDate(2026, 8, 12, 21, 0), AstroDate(2026, 8, 12, 21, 1))
    assert r.remainder == ""


def test_preceding_utrom_needs_no_shift_bare_no_date():
    r = _p("утром в 9 часов")
    assert r is not None
    assert start_end("утром в 9 часов", ANCHOR_R117) == (
        AstroDate(2026, 8, 12, 9, 0), AstroDate(2026, 8, 12, 9, 1))
    assert r.remainder == ""


def test_preceding_vecherom_with_explicit_weekday_date_and_clean_remainder():
    """The date, the day-part and the clock all compose into one reading;
    the leading verb phrase is all that is left in the remainder -- not
    "вечером" or any piece of the clock clause."""
    r = _p("встретимся в следующий вторник вечером в 9 часов")
    assert r is not None
    assert r.span.start == AstroDate(2026, 8, 18, 21, 0)
    assert r.remainder == "встретимся в"


def test_postposed_genitive_control_is_unaffected():
    """"в 9 часов вечера" already fused the genitive day-part into the
    clock's own MERIDIEM slot before this fix -- pinned as a regression
    control."""
    r = _p("в 9 часов вечера")
    assert r is not None
    assert r.span.start == AstroDate(2026, 8, 11, 21, 0)
    assert r.remainder == ""


def test_daypart_contradicting_an_explicit_24h_hour_declines():
    """"утром" (morning) cannot agree with the already-PM-pinned 21:00 --
    the composer refuses the whole reading rather than pick a winner."""
    nomatch("утром в 21:00", ANCHOR_R117)
