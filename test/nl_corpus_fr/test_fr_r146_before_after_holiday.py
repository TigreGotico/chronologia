# -*- coding: utf-8 -*-
"""R146 (French) -- see ``test_nl_r146_before_after_holiday.py`` (en) for the
full root-cause writeup. A bare "avant noël"/"après noël" (no magnitude)
used to strand "avant"/"après" and return Christmas Day unchanged; "avant X"
now binds ``[now, X end)`` (mirroring "jusqu'à X"), "après X" is refused (no
open-ended-future representation). Magnitude forms ("une semaine avant
noël") are untouched, as is the unrelated "avant-hier" idiom (its own
fully-consuming construction, never reaching this pass).

Expected values are independently hand-computed against the anchor.
"""
from datetime import datetime

from chronologia.extract import extract_timespan

LANG = "fr"
_A = datetime(2026, 8, 13, 10, 0)  # Thursday


def _span(text, anchor=_A):
    return extract_timespan(text, LANG, anchor)


def test_bare_before_binds_span():
    r = _span("avant noël")
    assert r is not None
    assert r[0].start == _A
    assert r[0].end == datetime(2026, 12, 26)
    assert r.remainder == ""


def test_bare_before_mirrors_until():
    before = _span("avant noël")
    until = _span("jusqu'à noël")
    assert before is not None and until is not None
    assert before[0] == until[0]


def test_bare_after_refused_not_stranded():
    assert _span("après noël") is None


def test_magnitude_offset_before_unaffected():
    r = _span("une semaine avant noël")
    assert r is not None
    assert r[0].start == datetime(2026, 12, 18)
    assert r[0].end == datetime(2026, 12, 19)
    assert r.remainder == ""


def test_magnitude_offset_after_unaffected():
    r = _span("une semaine après noël")
    assert r is not None
    assert r[0].start == datetime(2027, 1, 1)
    assert r[0].end == datetime(2027, 1, 2)
    assert r.remainder == ""


def test_avant_hier_idiom_unaffected():
    # "avant-hier" ("the day before yesterday") is its own idiom, fully
    # consuming both tokens -- never reaches the bare-directional pass, so
    # it must keep resolving to a real day, not be refused as a bare
    # "avant <past date>".
    r = _span("avant hier")
    assert r is not None
    assert r[0].start == datetime(2026, 8, 11)
    assert r[0].end == datetime(2026, 8, 12)
