"""Coarse relative periods in the oblique forms speakers actually use.

Slovene agrees the determiner with the unit's gender, and the three units
span two of them -- masculine "teden" and "mesec", neuter "leto" -- so the
neuter "prejsnje leto" needs its own form (Fran, ZRC SAZU).

Expected spans come from independent calendar arithmetic against the corpus
anchor -- the week from its ISO-Monday start, the month and year from their
first day -- never from the parser's own output.
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from chronologia.astrodate import AstroDate

from ._corpus import ANCHOR, span

_MIDNIGHT = dict(hour=0, minute=0, second=0, microsecond=0)


def _expected(rel, unit):
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
    ('prejšnji teden', -1, 'week'),
    ('prejšnjega tedna', -1, 'week'),
    ('ta teden', 0, 'week'),
    ('naslednji teden', 1, 'week'),
    ('prejšnji mesec', -1, 'month'),
    ('naslednji mesec', 1, 'month'),
    ('prejšnje leto', -1, 'year'),
    ('naslednje leto', 1, 'year'),
])
def test_oblique_rel_period(text, rel, unit):
    s = span(text)
    exp_s, exp_e = _expected(rel, unit)
    assert (s.start, s.end) == (exp_s, exp_e)
