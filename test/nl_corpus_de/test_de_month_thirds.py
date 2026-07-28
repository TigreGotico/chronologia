# -*- coding: utf-8 -*-
"""German month-thirds: "Anfang / Mitte / Ende <Monat>".

A German speaker splits the month into three equal *time* slabs, not three
whole-day blocks: "Anfang Juni" is the first third of June, "Ende Februar" the
last third of February. The engine cuts the month at exact fractional
boundaries, so a 31-day month lands its cut at 10 d 8 h (31/3 d) rather than a
rounded day. The oracle here is independent arithmetic: for a month of ``L``
days the interior cuts fall at ``L*28800`` and ``2*L*28800`` seconds after the
first (28800 = 86400/3, so every 28/29/30/31-day month lands on a whole hour).

All bare (year-less) references resolve in the anchor year 2017 (anchor
2017-06-27). Both endpoints are asserted exactly -- a third that silently
rounded to whole days would still look like a working month-part.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import AstroDate, span

_MONTHS = [
    ("januar", 1), ("februar", 2), ("märz", 3), ("april", 4),
    ("mai", 5), ("juni", 6), ("juli", 7), ("august", 8),
    ("september", 9), ("oktober", 10), ("november", 11), ("dezember", 12),
]


def _month_len(y, m):
    nxt = datetime(y + 1, 1, 1) if m == 12 else datetime(y, m + 1, 1)
    return (nxt - datetime(y, m, 1)).days


def _to_ad(dt):
    return AstroDate(dt.year, dt.month, dt.day, dt.hour, dt.minute)


def _thirds(y, m):
    """(anfang, mitte, ende) as (start, end) datetime pairs -- equal splits."""
    start = datetime(y, m, 1)
    end = datetime(y + 1, 1, 1) if m == 12 else datetime(y, m + 1, 1)
    L = _month_len(y, m)
    c1 = start + timedelta(seconds=L * 28800)      # L/3 days
    c2 = start + timedelta(seconds=2 * L * 28800)  # 2L/3 days
    return (start, c1), (c1, c2), (c2, end)


_CASES = []
for _name, _m in _MONTHS:
    _a, _mi, _e = _thirds(2017, _m)
    _CASES.append((f"anfang {_name}", _a[0], _a[1]))
    _CASES.append((f"mitte {_name}", _mi[0], _mi[1]))
    _CASES.append((f"ende {_name}", _e[0], _e[1]))


@pytest.mark.parametrize("text,s,e", _CASES)
def test_month_third(text, s, e):
    sp = span(text)
    assert (sp.start, sp.end) == (_to_ad(s), _to_ad(e)), f"{text!r} -> {sp}"


def test_thirds_tile_the_whole_month():
    """The three parts of a month abut exactly and cover it with no gap."""
    a = span("anfang oktober")
    m = span("mitte oktober")
    e = span("ende oktober")
    assert a.end == m.start
    assert m.end == e.start
    assert a.start == AstroDate(2017, 10, 1)
    assert e.end == AstroDate(2017, 11, 1)
