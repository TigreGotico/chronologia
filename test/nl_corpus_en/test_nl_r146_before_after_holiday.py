# -*- coding: utf-8 -*-
"""R146 -- a bare "before X" / "after X" (no magnitude: contrast "a week
before X", which already worked) strands the direction word and returns X
unchanged, UNIVERSALLY across every locale carrying "before"/"after"
connectors -- "before christmas" silently answered with plain Christmas Day
and a leftover "before" in the remainder; "after christmas" the same with
"after".

ROOT CAUSE: the only machinery that composes a "before"/"after" marker onto a
resolved date reference is ``anchored._try_offset``/``_try_offset_postfix``,
which -- via ``anchored._parse_preamble`` -- REQUIRES a magnitude pre-amble
("a week", "3 days", a bare weekday) immediately before the marker. A bare
marker with nothing in front of it (``c0 - 1 < 0``) makes ``_parse_preamble``
return ``None`` unconditionally, so the whole anchored-offset pass declines
and the marker is left as plain unconsumed text beside the otherwise-correct
holiday/date match.

FIX: ``timespan._extract_directional_bare`` recognises a LEADING bare
"before"/"after" + resolvable-endpoint shape (mirroring the existing
``_extract_open_range`` "until"/"since" scan) and either:

* "before X" -- mirrors "until X" EXACTLY (reuses its own span): ``[now, X's
  end)`` when X resolves to a FUTURE endpoint;
* "after X" -- the open span from X's end onward, a ``DateSpan`` with
  ``open_end``;
* refuses the WHOLE parse (returns ``None`` from ``extract_timespan``,
  never a bare-X fallback) when "before X" but X is not in the future (an
  explicit past date).

A magnitude offset ("a week before christmas") is UNCHANGED: it never
reaches this new pass (the marker there does not lead the whole utterance),
so it still goes through the pre-existing, already-correct anchored-offset
composition. A recurrence's own "before"-as-UNTIL binding ("every monday
before christmas") is likewise unaffected -- that construction already
consumed "before" via its own machinery before this pass ever runs.

Expected values are independently hand-computed against the anchor (exact
calendar arithmetic), never read back from the parser.
"""
from datetime import datetime

import pytest

from chronologia.extract import extract_timespan

LANG = "en"
_A = datetime(2026, 8, 13, 10, 0)  # Thursday


def _span(text, anchor=_A):
    return extract_timespan(text, LANG, anchor)


# -- bare "before X" binds a span, direction word never stranded -----------

@pytest.mark.parametrize("text,start,end", [
    # ruling 29: "before X" ends when X begins
    ("before christmas", _A, datetime(2026, 12, 25)),
    ("before march 3", _A, datetime(2027, 3, 3)),
])
def test_bare_before_binds_span(text, start, end):
    r = _span(text)
    assert r is not None, f"{text!r} did not parse (expected a span)"
    assert r[0].start == start
    assert r[0].end == end
    assert r.remainder == "", f"direction word stranded in {r.remainder!r}"


def test_bare_before_ends_where_until_ends_on_the_day_before():
    # ruling 29: "before X" stops when X begins; "until X" takes X in
    before = _span("before christmas")
    until = _span("until christmas")
    assert before[0].start == until[0].start
    assert (before[0].end, until[0].end) == (datetime(2026, 12, 25),
                                             datetime(2026, 12, 26))


# -- bare "after X" is the open span from the end of X, never X itself ------

@pytest.mark.parametrize("text, start", [
    # Christmas 2026 is 25 December; Easter 2027 is 28 March
    ("after christmas", datetime(2026, 12, 26)),
    ("after easter", datetime(2027, 3, 29)),
])
def test_bare_after_is_open_from_the_end(text, start):
    r = _span(text)
    assert (r[0].start, r[0].open_end, r[1]) == (start, True, "")


# -- "before X" where X is in the past: refused too, never re-pointed ------

@pytest.mark.parametrize("text", [
    "before yesterday",
    "before easter 2020",
])
def test_bare_before_past_endpoint_refused(text):
    assert _span(text) is None


def test_bare_after_past_endpoint_is_open_from_its_end():
    # Easter 2020 is 12 April; the open span starts when that day ends
    r = _span("after easter 2020")
    assert (r[0].start, r[0].open_end) == (datetime(2020, 4, 13), True)


# -- magnitude forms are untouched: still compose exactly as before --------

def test_magnitude_offset_before_unaffected():
    r = _span("a week before christmas")
    assert r is not None
    assert r[0].start == datetime(2026, 12, 18)
    assert r[0].end == datetime(2026, 12, 19)
    assert r.remainder == ""


def test_magnitude_offset_after_unaffected():
    r = _span("a week after christmas")
    assert r is not None
    assert r[0].start == datetime(2027, 1, 1)
    assert r[0].end == datetime(2027, 1, 2)
    assert r.remainder == ""


# -- recurrence's own UNTIL binding is unaffected ---------------------------

def test_recurrence_before_holiday_unaffected():
    # "every monday before christmas" resolves to the last Monday strictly
    # before Christmas Day -- a pre-existing, DIFFERENT recurrence-binding
    # semantic from the bare "before"/"until" open-range this defect fixes.
    # It must keep working exactly as it already did (both strand the
    # out-of-scope, pre-existing "every" recurrence marker identically), and
    # NOT be swallowed by the new bare-directional pass.
    r = _span("every monday before christmas")
    assert r is not None
    assert r.remainder == "every"
    assert r[0].start == datetime(2026, 12, 21)
    assert r[0].end == datetime(2026, 12, 22)
