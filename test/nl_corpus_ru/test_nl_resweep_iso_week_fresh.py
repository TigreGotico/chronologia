# -*- coding: utf-8 -*-
"""Second-pass sweep: "week of <date>" (ru), fresh year x every month.

``test_week_of.py`` pinned six spot dates in 2026.  This file widens the
sweep to a fresh year (2029) across all twelve months, at four day-of-month
anchors each, so no (text) id collides with the round-1 file.
"""
from datetime import date, datetime, timedelta

import pytest

from ._corpus import AstroDate, span, start_end

_MONTHS_GEN = [None, "января", "февраля", "марта", "апреля", "мая", "июня",
               "июля", "августа", "сентября", "октября", "ноября", "декабря"]

_YEAR = 2029  # fresh year, disjoint from test_week_of.py's 2026
_DAYS = (1, 8, 15, 22)


def _week(y, m, d):
    day = date(y, m, d)
    ws = day - timedelta(days=day.weekday())
    start_ad = AstroDate(ws.year, ws.month, ws.day)
    end_dt = datetime(ws.year, ws.month, ws.day) + timedelta(days=7)
    return start_ad, AstroDate(end_dt.year, end_dt.month, end_dt.day)


def _cases():
    out = []
    for m in range(1, 13):
        for d in _DAYS:
            text = f"неделя от {d} {_MONTHS_GEN[m]} {_YEAR}"
            out.append((text, (_YEAR, m, d)))
    return out


_CASES = _cases()


@pytest.mark.parametrize("text,ymd", _CASES, ids=[c[0] for c in _CASES])
def test_week_of_fresh(text, ymd):
    s, e = start_end(text)
    assert (s, e) == _week(*ymd), text
    assert span(text).width.days == 7
