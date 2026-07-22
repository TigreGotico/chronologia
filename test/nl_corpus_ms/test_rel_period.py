# -*- coding: utf-8 -*-
"""Coarse relative periods -- next/this/last week, month, year.

The whole calendar period containing the anchor, shifted by the relative
marker (next=+1, this=0, last=-1).  Expected spans come from independent
calendar arithmetic against this corpus's anchor -- never pinned from the
engine.  This locale's week starts on Monday (start index 0)."""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from chronologia.astrodate import AstroDate

from ._corpus import ANCHOR, span

_MID = dict(hour=0, minute=0, second=0, microsecond=0)
_SIDX = 0


def _expected(rel, unit):
    if unit == "week":
        base = ANCHOR.replace(**_MID)
        s = base - timedelta(days=(base.weekday() - _SIDX) % 7) + timedelta(weeks=rel)
        e = s + timedelta(days=7)
    elif unit == "month":
        s = ANCHOR.replace(day=1, **_MID) + relativedelta(months=rel)
        e = s + relativedelta(months=1)
    elif unit == "year":
        s = ANCHOR.replace(month=1, day=1, **_MID) + relativedelta(years=rel)
        e = s + relativedelta(years=1)
    else:
        raise AssertionError(unit)
    return AstroDate(s.year, s.month, s.day), AstroDate(e.year, e.month, e.day)


CASES = [
    ('minggu depan', 1, 'week'),
    ('minggu lepas', -1, 'week'),
    ('minggu ini', 0, 'week'),
    ('bulan depan', 1, 'month'),
    ('bulan lepas', -1, 'month'),
    ('tahun depan', 1, 'year'),
    ('tahun lepas', -1, 'year'),
]


@pytest.mark.parametrize("text,rel,unit", CASES)
def test_rel_period(text, rel, unit):
    sp = span(text)
    assert (sp.start, sp.end) == _expected(rel, unit)
