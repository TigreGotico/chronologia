"""Coarse relative periods in the oblique forms speakers actually use.

Russian names the containing period with a preposition and an oblique case:
"na proshloy nedele" is prepositional, "v etom mesyatse" and "v proshlom godu"
likewise. The nominative that the parser once accepted alone is the marked
register, not the ordinary one (Gramota.ru).

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
    ('на прошлой неделе', -1, 'week'),
    ('на этой неделе', 0, 'week'),
    ('на следующей неделе', 1, 'week'),
    ('в прошлом месяце', -1, 'month'),
    ('в этом месяце', 0, 'month'),
    ('в следующем месяце', 1, 'month'),
    ('в прошлом году', -1, 'year'),
    ('в этом году', 0, 'year'),
    ('в следующем году', 1, 'year'),
    ('прошлая неделя', -1, 'week'),
])
def test_oblique_rel_period(text, rel, unit):
    s = span(text)
    exp_s, exp_e = _expected(rel, unit)
    assert (s.start, s.end) == (exp_s, exp_e)
