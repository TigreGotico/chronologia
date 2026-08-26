"""The CLDR relative periods, in both "previous" determiners.

Bulgarian offers "минал" and "предходен" for the same sense, and the
calendar phrases use both.  Each is pinned beside the other so neither
reading drifts.
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
    elif unit == "month":
        s = ANCHOR.replace(day=1, **_MIDNIGHT) + relativedelta(months=rel)
        e = s + relativedelta(months=1)
    else:
        s = ANCHOR.replace(month=1, day=1, **_MIDNIGHT) + relativedelta(years=rel)
        e = s + relativedelta(years=1)
    return AstroDate(s.year, s.month, s.day), AstroDate(e.year, e.month, e.day)


@pytest.mark.parametrize("text,rel,unit", [
    ('предходния месец', -1, 'month'),
    ('миналия месец', -1, 'month'),
    ('следващия месец', 1, 'month'),
    ('предходната седмица', -1, 'week'),
    ('миналата седмица', -1, 'week'),
    ('тази седмица', 0, 'week'),
    ('предходната година', -1, 'year'),
    ('миналата година', -1, 'year'),
    ('следващата година', 1, 'year'),
])
def test_relative_period(text, rel, unit):
    s = span(text)
    assert (s.start, s.end) == _expected(rel, unit)
    assert parse(text)[1] == ""
