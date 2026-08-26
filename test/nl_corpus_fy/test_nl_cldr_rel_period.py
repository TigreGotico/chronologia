"""The CLDR relative periods, in both determiner forms.

A West Frisian attributive adjective inflects before most nouns but stays
bare before an indefinite neuter singular, so "jier" takes "foarich" and
"folgjend" where "moanne" and "wike" take "foarige" and "folgjende".  Both
forms are pinned side by side.
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
    ('foarich jier', -1, 'year'),
    ('foarige jier', -1, 'year'),
    ('dit jier', 0, 'year'),
    ('folgjend jier', 1, 'year'),
    ('folgjende jier', 1, 'year'),
    ('foarige moanne', -1, 'month'),
    ('folgjende moanne', 1, 'month'),
    ('foarige wike', -1, 'week'),
    ('folgjende wike', 1, 'week'),
])
def test_relative_period(text, rel, unit):
    s = span(text)
    assert (s.start, s.end) == _expected(rel, unit)
    assert parse(text)[1] == ""
