"""Coarse relative periods in the oblique forms speakers actually use.

Bulgarian has no cases; the determiner agrees in gender and carries the
postposed definite article, and the phrase may be introduced by "prez"
(Institute for Bulgarian Language, BAS).

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
    ('миналата седмица', -1, 'week'),
    ('през миналата седмица', -1, 'week'),
    ('тази седмица', 0, 'week'),
    ('следващата седмица', 1, 'week'),
    ('миналия месец', -1, 'month'),
    ('следващия месец', 1, 'month'),
    ('миналата година', -1, 'year'),
    ('тази година', 0, 'year'),
    ('следващата година', 1, 'year'),
])
def test_oblique_rel_period(text, rel, unit):
    s = span(text)
    exp_s, exp_e = _expected(rel, unit)
    assert (s.start, s.end) == (exp_s, exp_e)
