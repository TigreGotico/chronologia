"""The CLDR relative periods, and "yesterday" in both spellings.

Ukrainian alternates initial у- and в-, so "учора" and "вчора" are the same
word; both are pinned, with the coarse periods as the control.
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from chronologia.astrodate import AstroDate

from ._corpus import ANCHOR, parse, span

_MIDNIGHT = dict(hour=0, minute=0, second=0, microsecond=0)


def _expected(rel, unit):
    """The period ``rel`` steps from the anchor, by calendar arithmetic that
    never touches the extractor."""
    if unit == "week":
        base = ANCHOR.replace(**_MIDNIGHT)
        s = base - timedelta(days=base.weekday()) + timedelta(weeks=rel)
        e = s + timedelta(days=7)
    elif unit == "day":
        s = ANCHOR.replace(**_MIDNIGHT) + timedelta(days=rel)
        e = s + timedelta(days=1)
    elif unit == "month":
        s = ANCHOR.replace(day=1, **_MIDNIGHT) + relativedelta(months=rel)
        e = s + relativedelta(months=1)
    else:
        s = ANCHOR.replace(month=1, day=1, **_MIDNIGHT) + relativedelta(years=rel)
        e = s + relativedelta(years=1)
    return AstroDate(s.year, s.month, s.day), AstroDate(e.year, e.month, e.day)


@pytest.mark.parametrize("text,rel,unit", [
    ('учора', -1, 'day'),
    ('вчора', -1, 'day'),
    ('минулого тижня', -1, 'week'),
    ('наступного тижня', 1, 'week'),
    ('минулого місяця', -1, 'month'),
    ('минулого року', -1, 'year'),
])
def test_relative_period(text, rel, unit):
    s = span(text)
    assert (s.start, s.end) == _expected(rel, unit)
    assert parse(text)[1] == ""
