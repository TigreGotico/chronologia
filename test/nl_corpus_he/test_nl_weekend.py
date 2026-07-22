# -*- coding: utf-8 -*-
"""The weekend as a named two-day span.  The Israeli weekend is
Friday-Saturday (weekend_start=4), so סוף שבוע resolves to the upcoming
Friday-Saturday.  The abbreviation סופ״ש splits on its gershayim (סופ + ש)
and is folded back to the same weekend token by the pipeline multiword
merge."""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, span, start_end

_MIDNIGHT = dict(hour=0, minute=0, second=0, microsecond=0)


def _weekend(rel):
    base = ANCHOR.replace(**_MIDNIGHT)
    # week starts Sunday (idx 6); first weekend day is Friday (idx 4)
    week_start = base - timedelta(days=(base.weekday() - 6) % 7)
    fri = week_start + timedelta(days=(4 - 6) % 7) + timedelta(weeks=rel)
    end = fri + timedelta(days=2)
    return AstroDate(fri.year, fri.month, fri.day), \
        AstroDate(end.year, end.month, end.day)


@pytest.mark.parametrize("text,rel", [
    ("סוף שבוע", 0),
    ("סופ״ש", 0),
    ("סוף השבוע הבא", 1),
])
def test_weekend(text, rel):
    sp = span(text)
    assert (sp.start, sp.end) == _weekend(rel)


def test_weekend_is_friday_saturday():
    # the upcoming weekend from Tue 2017-06-27 is Fri 30 - Sat 1
    s, e = start_end("סוף שבוע")
    assert s == AstroDate(2017, 6, 30)      # Friday
    assert e == AstroDate(2017, 7, 2)       # exclusive (Fri+Sat)
