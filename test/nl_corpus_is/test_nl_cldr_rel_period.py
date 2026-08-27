"""The CLDR relative periods, both sides of the anchor.

The oblique period puts a preposition in front and the weak superlative
inside: "á síðasta ári" against "á næsta ári", "í síðustu viku" against
"í næstu viku".  The future and present halves are the control -- they must
keep resolving exactly as they did.
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
    ('á síðasta ári', -1, 'year'),
    ('á þessu ári', 0, 'year'),
    ('á næsta ári', 1, 'year'),
    ('í síðasta mánuði', -1, 'month'),
    ('í þessum mánuði', 0, 'month'),
    ('í næsta mánuði', 1, 'month'),
    ('í síðustu viku', -1, 'week'),
    ('í þessari viku', 0, 'week'),
    ('í næstu viku', 1, 'week'),
])
def test_relative_period(text, rel, unit):
    s = span(text)
    assert (s.start, s.end) == _expected(rel, unit)
    assert parse(text)[1] == ""
