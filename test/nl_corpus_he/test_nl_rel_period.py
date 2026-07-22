# -*- coding: utf-8 -*-
"""Coarse relative periods: הבא/שעבר/הזה over week/month/year.  The week tiles
from its **Sunday** start (week_start=sunday), verified by independent
arithmetic against the anchor."""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from chronologia.astrodate import AstroDate

from ._corpus import ANCHOR, span

_MIDNIGHT = dict(hour=0, minute=0, second=0, microsecond=0)
_SUN = 6  # week_start=sunday -> python weekday index 6


def _expected(rel, unit):
    if unit == "week":
        base = ANCHOR.replace(**_MIDNIGHT)
        back = (base.weekday() - _SUN) % 7
        s = base - timedelta(days=back) + timedelta(weeks=rel)
        e = s + timedelta(days=7)
    elif unit == "month":
        s = ANCHOR.replace(day=1, **_MIDNIGHT) + relativedelta(months=rel)
        e = s + relativedelta(months=1)
    elif unit == "year":
        s = ANCHOR.replace(month=1, day=1, **_MIDNIGHT) + relativedelta(years=rel)
        e = s + relativedelta(years=1)
    else:
        raise AssertionError(unit)
    return AstroDate(s.year, s.month, s.day), AstroDate(e.year, e.month, e.day)


CASES = [
    ('השבוע הבא', 1, 'week'),
    ('השבוע הזה', 0, 'week'),
    ('השבוע שעבר', -1, 'week'),
    ('החודש הבא', 1, 'month'),
    ('החודש הזה', 0, 'month'),
    ('החודש שעבר', -1, 'month'),
    ('השנה הבאה', 1, 'year'),
    ('השנה הזאת', 0, 'year'),
    ('השנה שעברה', -1, 'year'),
]


@pytest.mark.parametrize("text,rel,unit", CASES)
def test_rel_period(text, rel, unit):
    sp = span(text)
    assert (sp.start, sp.end) == _expected(rel, unit)
