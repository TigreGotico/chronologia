# -*- coding: utf-8 -*-
"""``marker_during.voc`` used to hold "pola"/"polo" -- the part-of-day frame,
not a during-word -- so Galician never inherited the base grammar's
"during MONTH DAY? YEAR?" order and "en xaneiro" stranded "en" in the
remainder. The part-of-day surfaces now live in their own
``marker_dayframe.voc``, bound by ``daypart_ref``'s "dayframe DAYPART" order,
and ``marker_during.voc`` holds the genuine preposition "en", so ``calendar_date``
opts in to the base grammar's marker-prefixed month order.

"mañá" is a homograph: DRAG gives it both the morning day-part and "tomorrow".
The split must not let the genuine during-word "en" drag the tomorrow reading
into the morning band -- "en mañá" is adversarially pinned to keep meaning
tomorrow, unlike "pola mañá", which is the morning.

Expected spans are hand-computed against the anchor.

Anchor 2026-08-14 10:00 (Friday).
"""
from datetime import datetime

import pytest

from chronologia.astrodate import AstroDate
from chronologia.extract import extract_timespan

LANG = "gl"
_A = datetime(2026, 8, 14, 10, 0)


def _span(text, anchor=_A):
    return extract_timespan(text, LANG, anchor)


@pytest.mark.parametrize("marker", ["en"])
@pytest.mark.parametrize("month,num", [
    ("xaneiro", 1), ("febreiro", 2), ("marzo", 3), ("abril", 4),
    ("maio", 5), ("xuño", 6), ("xullo", 7), ("agosto", 8),
    ("setembro", 9), ("outubro", 10), ("novembro", 11), ("decembro", 12),
])
def test_en_month_fully_consumes(marker, month, num):
    r = _span(f"{marker} {month}")
    assert r is not None, f"{marker} {month!r} did not parse"
    assert r.remainder == ""
    assert r[0].start == AstroDate(2026, num, 1)


@pytest.mark.parametrize("phrase,start_h,end_h", [
    ("pola madrugada", 0, 6),
    ("pola mañá", 6, 12),
    ("pola tarde", 13, 21),
    ("pola noite", 21, 24),
])
def test_pola_dayframe_control_unchanged(phrase, start_h, end_h):
    # "pola"/"polo" moved from marker_during.voc to marker_dayframe.voc; the
    # part-of-day reading must resolve to the identical band as before.
    r = _span(phrase)
    assert r is not None
    assert r.remainder == ""
    assert r[0].start == datetime(2026, 8, 14, start_h)
    end = datetime(2026, 8, 15) if end_h == 24 else datetime(2026, 8, 14, end_h)
    assert r[0].end == end


def test_en_mana_still_means_tomorrow():
    # Adversarial pin: "en" is the during-word, not the dayframe connector, so
    # "en mañá" must NOT resolve to the morning band -- it keeps the bare
    # named_day "mañá" = tomorrow reading, with "en" left stranded.
    r = _span("en mañá")
    assert r is not None
    assert r[0].start == AstroDate(2026, 8, 15)
    assert r[0].end == AstroDate(2026, 8, 16)
    assert r.remainder == "en"


def test_en_dayframe_is_not_accepted():
    # "en" is the month preposition, not the part-of-day frame -- it must NOT
    # newly widen daypart_ref to accept "en tarde" as "in the afternoon".
    assert _span("en tarde") is None
