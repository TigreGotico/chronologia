"""The CLDR relative periods, across the mutation boundary.

A Welsh adjective after a feminine singular noun takes the soft mutation,
so the feminine "wythnos" is followed by "ddiwethaf" where the masculine
"mis" keeps the radical "diwethaf".  Both environments are pinned, and
"nesaf" is the control: n has no soft-mutation cell, so it is spelled the
same after either gender.
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
    else:
        s = ANCHOR.replace(day=1, **_MIDNIGHT) + relativedelta(months=rel)
        e = s + relativedelta(months=1)
    return AstroDate(s.year, s.month, s.day), AstroDate(e.year, e.month, e.day)


@pytest.mark.parametrize("text,rel,unit", [
    ('mis diwethaf', -1, 'month'),
    ('mis nesaf', 1, 'month'),
    ('wythnos ddiwethaf', -1, 'week'),
    ('wythnos nesaf', 1, 'week'),
])
def test_relative_period(text, rel, unit):
    s = span(text)
    assert (s.start, s.end) == _expected(rel, unit)
    assert parse(text)[1] == ""
