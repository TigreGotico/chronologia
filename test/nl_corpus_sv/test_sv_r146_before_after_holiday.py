# -*- coding: utf-8 -*-
"""R146 (Swedish) -- see ``test_nl_r146_before_after_holiday.py`` (en) for the
full root-cause writeup. A bare "före jul"/"efter jul" (no magnitude) used to
strand "före"/"efter" and return Christmas Day unchanged; "före jul" now
binds ``[now, christmas end)`` (mirroring "tills jul"), "efter jul" is
refused (no open-ended-future representation). Magnitude forms ("en vecka
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
    assert r[0].end == datetime(2026, 12, 26)
    assert r.remainder == ""


def test_bare_before_mirrors_until():
    before = _span("före jul")
    until = _span("tills jul")
    assert before is not None and until is not None
    assert before[0] == until[0]


def test_bare_after_refused_not_stranded():
    assert _span("efter jul") is None


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
