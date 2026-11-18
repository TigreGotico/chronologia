# -*- coding: utf-8 -*-
"""R146 (Swedish) -- see ``test_nl_r146_before_after_holiday.py`` (en) for the
full root-cause writeup. A bare "före jul"/"efter jul" (no magnitude) used to
strand "före"/"efter" and return Christmas Day unchanged; "före jul" now
binds ``[now, christmas end)`` (mirroring "tills jul"), "efter jul" is the open span
from the end of X onward. Magnitude forms ("en vecka
före jul") are untouched.

Expected values are independently hand-computed against the anchor.
"""
from datetime import datetime

from chronologia.extract import extract_timespan

LANG = "sv"
_A = datetime(2026, 8, 13, 10, 0)  # Thursday


def _span(text, anchor=_A):
    return extract_timespan(text, LANG, anchor)


def test_bare_before_binds_span():
    r = _span("före jul")
    assert r is not None
    assert r[0].start == _A
    # ruling 29: "before X" ends when X begins, 25 December 00:00
    assert r[0].end == datetime(2026, 12, 25)
    assert r.remainder == ""


def test_bare_before_ends_where_until_ends_on_the_day_before():
    # ruling 29: "before X" stops when X begins; "until X" takes X in
    before = _span("före jul")
    until = _span("tills jul")
    assert before[0].start == until[0].start
    assert (before[0].end, until[0].end) == (datetime(2026, 12, 25),
                                             datetime(2026, 12, 26))


def test_bare_after_is_open_from_the_end_of_the_holiday():
    # Christmas 2026 is 25 December and Easter 2027 is 28 March; the span
    # starts when that day ends and has no end
    r = _span("efter jul")
    assert (r[0].start, r[0].open_end, r[1]) == (datetime(2026, 12, 26), True, "")


def test_bare_before_past_endpoint_refused():
    assert _span("före i går") is None  # "before yesterday"


def test_magnitude_offset_before_unaffected():
    r = _span("en vecka före jul")
    assert r is not None
    assert r[0].start == datetime(2026, 12, 18)
    assert r[0].end == datetime(2026, 12, 19)
    assert r.remainder == ""


def test_magnitude_offset_after_unaffected():
    r = _span("en vecka efter jul")
    assert r is not None
    assert r[0].start == datetime(2027, 1, 1)
    assert r[0].end == datetime(2027, 1, 2)
    assert r.remainder == ""
