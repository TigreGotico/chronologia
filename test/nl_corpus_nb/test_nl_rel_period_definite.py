"""Wave 2 -- coarse relative periods in the definite (Scandinavian).

The Nordic languages routinely mark the noun for definiteness -- "förra
veckan", "dette året", "neste uka" -- rather than the bare citation
form.  Same calendar arithmetic as the plain rel_period wave.
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
    else:
        s = ANCHOR.replace(month=1, day=1, **_MIDNIGHT) + relativedelta(years=rel)
        e = s + relativedelta(years=1)
    return AstroDate(s.year, s.month, s.day), AstroDate(e.year, e.month, e.day)


CASES = [
    ('dette året', 0, 'year'),
    ('neste uka', 1, 'week'),
]


@pytest.mark.parametrize("text,rel,unit", CASES)
def test_rel_period_definite(text, rel, unit):
    sp = span(text)
    assert (sp.start, sp.end) == _expected(rel, unit)
