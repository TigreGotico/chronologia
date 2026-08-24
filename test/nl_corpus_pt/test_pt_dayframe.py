# -*- coding: utf-8 -*-
"""``marker_during.voc`` used to hold "pela"/"pelo" -- the part-of-day frame,
not a during-word -- so Portuguese never inherited the base grammar's
"during MONTH DAY? YEAR?" order and "em janeiro" stranded "em" in the
remainder. The part-of-day surfaces now live in their own
``marker_dayframe.voc``, bound by ``daypart_ref``'s "dayframe DAYPART" order,
and ``marker_during.voc`` holds the genuine preposition "em", so ``calendar_date``
opts in to the base grammar's marker-prefixed month order.

Expected spans are hand-computed against the anchor; the daypart controls pin
that the rename moved no span.

Anchor 2026-08-14 10:00 (Friday).
"""
from datetime import datetime

import pytest

from chronologia.astrodate import AstroDate
from chronologia.extract import extract_timespan

LANG = "pt"
_A = datetime(2026, 8, 14, 10, 0)


def _span(text, anchor=_A):
    return extract_timespan(text, LANG, anchor)


@pytest.mark.parametrize("marker", ["em"])
@pytest.mark.parametrize("month,num", [
    ("janeiro", 1), ("fevereiro", 2), ("março", 3), ("abril", 4),
    ("maio", 5), ("junho", 6), ("julho", 7), ("agosto", 8),
    ("setembro", 9), ("outubro", 10), ("novembro", 11), ("dezembro", 12),
])
def test_em_month_fully_consumes(marker, month, num):
    r = _span(f"{marker} {month}")
    assert r is not None, f"{marker} {month!r} did not parse"
    assert r.remainder == ""
    assert r[0].start == AstroDate(2026, num, 1)


@pytest.mark.parametrize("phrase,start_h,end_h", [
    ("pela madrugada", 0, 6),
    ("pela manhã", 6, 12),
    ("pela tarde", 12, 19),
    ("pela noite", 19, 24),
])
def test_pela_dayframe_control_unchanged(phrase, start_h, end_h):
    # "pela"/"pelo" moved from marker_during.voc to marker_dayframe.voc; the
    # part-of-day reading must resolve to the identical band as before.
    r = _span(phrase)
    assert r is not None
    assert r.remainder == ""
    assert r[0].start == datetime(2026, 8, 14, start_h)
    end = datetime(2026, 8, 15) if end_h == 24 else datetime(2026, 8, 14, end_h)
    assert r[0].end == end


def test_em_dayframe_is_not_accepted():
    # "em" is the month preposition, not the part-of-day frame -- it must NOT
    # newly widen daypart_ref to accept "em manhã" as "in the morning".
    assert _span("em manhã") is None
