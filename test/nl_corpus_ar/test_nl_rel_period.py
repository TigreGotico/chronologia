# -*- coding: utf-8 -*-
"""Coarse relative periods: القادم/الماضي/هذا over week/month/year.  Expected
spans come from independent calendar arithmetic against this corpus's anchor;
the week tiles from its Saturday start (week_start=saturday)."""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from chronologia.astrodate import AstroDate

from ._corpus import ANCHOR, span

_MIDNIGHT = dict(hour=0, minute=0, second=0, microsecond=0)
_SAT = 5  # week_start=saturday -> python weekday index 5


def _expected(rel, unit):
    if unit == "week":
        base = ANCHOR.replace(**_MIDNIGHT)
        back = (base.weekday() - _SAT) % 7
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
    ('الأسبوع القادم', 1, 'week'),
    ('هذا الأسبوع', 0, 'week'),
    ('الأسبوع الماضي', -1, 'week'),
    ('الشهر القادم', 1, 'month'),
    ('هذا الشهر', 0, 'month'),
    ('الشهر الماضي', -1, 'month'),
    ('السنة القادمة', 1, 'year'),
    ('هذه السنة', 0, 'year'),
    ('السنة الماضية', -1, 'year'),
    ('العام القادم', 1, 'year'),
    ('العام الماضي', -1, 'year'),
]


@pytest.mark.parametrize("text,rel,unit", CASES)
def test_rel_period(text, rel, unit):
    sp = span(text)
    assert (sp.start, sp.end) == _expected(rel, unit)
