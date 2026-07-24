"""Coarse relative periods in the oblique forms speakers actually use.

Polish names the containing period with "w" and the locative --
"w zeszlym tygodniu", "w tym miesiacu", "w przyszlym roku" -- which is the
only ordinary way to say it (PWN).

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
    ('w zeszłym tygodniu', -1, 'week'),
    ('w tym tygodniu', 0, 'week'),
    ('w przyszłym tygodniu', 1, 'week'),
    ('w zeszłym miesiącu', -1, 'month'),
    ('w tym miesiącu', 0, 'month'),
    ('w przyszłym miesiącu', 1, 'month'),
    ('w zeszłym roku', -1, 'year'),
    ('w tym roku', 0, 'year'),
    ('w przyszłym roku', 1, 'year'),
    ('w ubiegłym tygodniu', -1, 'week'),
    ('w poprzednim miesiącu', -1, 'month'),
])
def test_oblique_rel_period(text, rel, unit):
    s = span(text)
    exp_s, exp_e = _expected(rel, unit)
    assert (s.start, s.end) == (exp_s, exp_e)
