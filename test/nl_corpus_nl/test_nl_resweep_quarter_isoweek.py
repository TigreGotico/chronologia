# -*- coding: utf-8 -*-
"""Second-pass resweep: quarters and ISO weeks (nl), fresh years.

Quarters: "Qn <jaar>" and "het <ord> kwartaal <jaar>", both surfaces already
proven in :mod:`test_nl_quarter` but only for a handful of hand-picked years;
this sweeps every quarter over years 2029-2048. Quarter N spans months
[3N-2 .. 3N], edges hand-derived.

ISO weeks: "week <n> van <jaar>", extending :mod:`test_nl_iso_week` (which
only hand-picks ten (year, week) pairs) with a systematic sweep over years
2029-2038 and mid-range week numbers, Mondays computed with stdlib
``date.fromisocalendar`` -- independent of the parser.

Anchor 2017-06-27.
"""
from datetime import date, timedelta

import pytest

from ._corpus import AstroDate, parse, start_end

_QORD = {1: "eerste", 2: "tweede", 3: "derde", 4: "vierde"}


def _build_quarters():
    cases = []
    for y in range(2029, 2049):
        for qn in range(1, 5):
            sm = 3 * qn - 2
            em = sm + 3
            gold_s = (y, sm, 1)
            gold_e = (y + 1, em - 12, 1) if em > 12 else (y, em, 1)
            cases.append((f"Q{qn} {y}", gold_s, gold_e))
            cases.append((f"het {_QORD[qn]} kwartaal {y}", gold_s, gold_e))
    return cases


def _build_iso_weeks():
    cases = []
    for y in range(2029, 2039):
        for w in (3, 11, 20, 29, 37, 45):
            try:
                mon = date.fromisocalendar(y, w, 1)
            except ValueError:
                continue
            cases.append((f"week {w} van {y}", y, w))
    return cases


_Q_CASES = _build_quarters()
_ISO_CASES = _build_iso_weeks()


@pytest.mark.parametrize("phrase,gs,ge", _Q_CASES, ids=[c[0] for c in _Q_CASES])
def test_quarter_resweep(phrase, gs, ge):
    s, e = start_end(phrase)
    assert s == AstroDate(*gs), phrase
    assert e == AstroDate(*ge), phrase


@pytest.mark.parametrize("phrase,iy,iw", _ISO_CASES, ids=[c[0] for c in _ISO_CASES])
def test_iso_week_resweep(phrase, iy, iw):
    mon = date.fromisocalendar(iy, iw, 1)
    s, e = start_end(phrase)
    assert s == AstroDate(mon.year, mon.month, mon.day), phrase
    nxt = mon + timedelta(days=7)
    assert e == AstroDate(nxt.year, nxt.month, nxt.day), phrase
