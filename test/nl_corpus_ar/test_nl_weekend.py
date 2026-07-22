# -*- coding: utf-8 -*-
"""The weekend as a named two-day span.  The Arab civil weekend is
Friday-Saturday (weekend_start=4), so نهاية الأسبوع / عطلة resolves to the
upcoming Friday-Saturday, NOT the Western Saturday-Sunday.  Verified against
independent weekday arithmetic from the Tuesday anchor."""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, span, start_end

_MIDNIGHT = dict(hour=0, minute=0, second=0, microsecond=0)
_FRI = 4  # weekend_start -> Friday


def _weekend(rel):
    base = ANCHOR.replace(**_MIDNIGHT)
    # week starts Saturday (idx 5); first weekend day is Friday (idx 4)
    week_start = base - timedelta(days=(base.weekday() - 5) % 7)
    fri = week_start + timedelta(days=(_FRI - 5) % 7) + timedelta(weeks=rel)
    return AstroDate(fri.year, fri.month, fri.day), \
        AstroDate((fri + timedelta(days=2)).year,
                  (fri + timedelta(days=2)).month,
                  (fri + timedelta(days=2)).day)


@pytest.mark.parametrize("text,rel", [
    ("نهاية الأسبوع", 0),
    ("عطلة نهاية الأسبوع", 0),
    ("نهاية الأسبوع القادمة", 1),
    ("نهاية الأسبوع الماضية", -1),
])
def test_weekend(text, rel):
    sp = span(text)
    assert (sp.start, sp.end) == _weekend(rel)


def test_weekend_is_friday_saturday():
    # concretely: the upcoming weekend from Tue 2017-06-27 is Fri 30 - Sat 1
    s, e = start_end("نهاية الأسبوع")
    assert s == AstroDate(2017, 6, 30)      # Friday
    assert e == AstroDate(2017, 7, 2)       # exclusive end (Fri+Sat)
