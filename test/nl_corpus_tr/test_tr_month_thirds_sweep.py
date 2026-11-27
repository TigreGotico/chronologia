# -*- coding: utf-8 -*-
"""Turkish fuzzy month thirds (ay başı / ortası / sonu) across all months.

"MONTH başı/ortası/sonu" names the first/middle/last third of that calendar
month.  The oracle is pure timedelta arithmetic: split [month_start,
next_month_start) into three equal parts.  A 30-day month gives clean 10-day
thirds; a 31-day month gives 10 days 8 hours.  A bare month takes the year the month
alone takes (ruling 1, changed 26 November 2026): this year if it holds the
anchor or is still to come, next year if it has ended (2018 for January to
May).  Anchor: 2017-06-27.
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
        # ruling 1 (changed 26 November 2026): a part of a month takes its month's year; a month that has ended at the anchor is next year's
        y = A.year + (m < A.month)
        for word, part in _PART.items():
            # ruling 1 (26 November 2026): a part of a month is read as a
            # span; a part of the anchor's own month that has ended at the
            # anchor (başı, ortası of June 2017) is June 2018, the part that
            # holds it (sonu) stays 2017
            py = y
            if m == A.month:
                s0 = datetime(y, m, 1)
                w0 = (datetime(y, m + 1, 1) - s0) / 3
                end0 = {"early": s0 + w0, "mid": s0 + 2 * w0,
                        "late": datetime(y, m + 1, 1)}[part]
                if end0 <= A:
                    py = y + 1
            m_start = AstroDate(py, m, 1)
            m_end = (AstroDate(py + 1, 1, 1) if m == 12
                     else AstroDate(py, m + 1, 1))
            out.append((f"{_MONTHS[m]} {word}", m_start, m_end, part))
    return out


@pytest.mark.parametrize("text,m_start,m_end,part", _cases())
def test_month_third(text, m_start, m_end, part):
    want = _third(m_start, m_end, part)
    assert start_end(text, A) == want
