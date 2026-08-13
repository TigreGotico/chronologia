# -*- coding: utf-8 -*-
"""R146 (Croatian) -- see ``test_nl_r146_before_after_holiday.py`` (en) for
the full root-cause writeup. A bare "prije božića"/"poslije božića" (no
magnitude) used to strand "prije"/"poslije" and return Christmas Day
unchanged (see the updated ``test_timespan_prije_bozica_genitive`` in
``test_nl_r137_genitive_until.py``, which pinned the pre-fix defect);
"prije X" now binds ``[now, X end)`` (mirroring "do X"), "poslije X" is
refused (no open-ended-future representation). A magnitude form ("tjedan
dana prije božića") is unaffected by this fix -- it already left "tjedan"
(a PRE-EXISTING, unrelated quirk) stranded before this defect was touched,
so that stranding is asserted here as a known baseline, not re-litigated.

Expected values are independently hand-computed against the anchor.
"""
from datetime import datetime

from chronologia.extract import extract_timespan

LANG = "hr"
_A = datetime(2026, 8, 13, 10, 0)  # Thursday


def _span(text, anchor=_A):
    return extract_timespan(text, LANG, anchor)


def test_bare_before_binds_span():
    r = _span("prije božića")
    assert r is not None
    assert r[0].start == _A
    assert r[0].end == datetime(2026, 12, 26)
    assert r.remainder == ""


def test_bare_before_mirrors_until():
    before = _span("prije božića")
    until = _span("do božića")
    assert before is not None and until is not None
    assert before[0] == until[0]


def test_bare_after_refused_not_stranded():
    assert _span("poslije božića") is None


def test_bare_before_past_endpoint_refused():
    assert _span("prije jučer") is None  # "before yesterday"


def test_magnitude_offset_before_unaffected():
    # pre-existing, unrelated "tjedan" stranding baseline -- unchanged by
    # this fix; the important assertion is the SPAN, which is correct.
    r = _span("tjedan dana prije božića")
    assert r is not None
    assert r[0].start == datetime(2026, 12, 24)
    assert r[0].end == datetime(2026, 12, 25)


def test_magnitude_offset_after_unaffected():
    r = _span("tjedan dana poslije božića")
    assert r is not None
    assert r[0].start == datetime(2026, 12, 26)
    assert r[0].end == datetime(2026, 12, 27)
