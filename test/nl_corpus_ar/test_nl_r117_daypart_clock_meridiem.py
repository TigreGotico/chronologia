# -*- coding: utf-8 -*-
"""R117: a preceding day-part word composes onto an adjacent explicit clock
as a meridiem hint, proven here in Arabic as a third locale for the shared
:func:`chronologia.extract.resolver.compose_daypart_clock` fix.

"مساءً الساعة التاسعة" ("in the evening, at the hour of nine") is the
preposed form; before the fix the day-part and the clock competed instead
of composing, and this shape lost the day-part meridiem hint entirely.  The
postposed control "الساعة التاسعة مساءً" already worked before the fix (the
day-part fuses into the clock construction's own MERIDIEM slot at match
time) and is pinned here as a regression control.

Gold is derived by hand from the mission anchor
``datetime(2026, 8, 11, 12, 0)`` (a Tuesday).  The hour takes the half the
day-part names and the next such time is meant: "مساءً الساعة التاسعة" is
21:00 on the anchor day, still ahead of 12:00, as the postposed control
below already gives.
"""
from datetime import datetime

from chronologia.astrodate import AstroDate
from ._corpus import parse, start_end

ANCHOR_R117 = datetime(2026, 8, 11, 12, 0)


def _p(text):
    return parse(text, ANCHOR_R117)


def test_preceding_masaan_composes_as_pm_meridiem_bare_no_date():
    r = _p("مساءً الساعة التاسعة")
    assert r is not None
    assert start_end("مساءً الساعة التاسعة", ANCHOR_R117) == (
        AstroDate(2026, 8, 11, 21, 0), AstroDate(2026, 8, 11, 21, 1))
    assert r.remainder == ""


def test_postposed_control_is_unaffected():
    """"الساعة التاسعة مساءً" already fused the day-part into the clock's
    own MERIDIEM slot before this fix -- pinned as a regression control."""
    r = _p("الساعة التاسعة مساءً")
    assert r is not None
    assert r.span.start == AstroDate(2026, 8, 11, 21, 0)
    assert r.remainder == ""
