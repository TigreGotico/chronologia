# -*- coding: utf-8 -*-
"""Turkish fuzzy month thirds (ay başı / ortası / sonu) across all months.

"MONTH başı/ortası/sonu" names the first/middle/last third of that calendar
month.  The oracle is pure timedelta arithmetic: split [month_start,
next_month_start) into three equal parts.  A 30-day month gives clean 10-day
thirds; a 31-day month gives 10 days 8 hours.  Bare month resolves in the
anchor's calendar year (2017).  Anchor: 2017-06-27.
"""
from datetime import datetime

import pytest

from chronologia.astrodate import AstroDate
from ._corpus import start_end

A = datetime(2017, 6, 27, 13, 4)

_MONTHS = {
    1: "ocak", 2: "şubat", 3: "mart", 4: "nisan", 5: "mayıs", 6: "haziran",
    7: "temmuz", 8: "ağustos", 9: "eylül", 10: "ekim", 11: "kasım",
    12: "aralık",
}

_PART = {"başı": "early", "ortası": "mid", "sonu": "late"}


def _dt(a):
    return datetime(a.year, a.month, a.day, a.hour, a.minute, a.second,
                    a.microsecond)


def _third(s, e, part):
    s, e = _dt(s), _dt(e)
    w = (e - s) / 3
    edges = {"early": (s, s + w), "mid": (s + w, s + 2 * w),
             "late": (s + 2 * w, e)}[part]
    return AstroDate.from_datetime(edges[0]), AstroDate.from_datetime(edges[1])


def _cases():
    out = []
    for m in range(1, 13):
        m_start = AstroDate(2017, m, 1)
        m_end = AstroDate(2018, 1, 1) if m == 12 else AstroDate(2017, m + 1, 1)
        for word, part in _PART.items():
            out.append((f"{_MONTHS[m]} {word}", m_start, m_end, part))
    return out


@pytest.mark.parametrize("text,m_start,m_end,part", _cases())
def test_month_third(text, m_start, m_end, part):
    want = _third(m_start, m_end, part)
    assert start_end(text, A) == want
