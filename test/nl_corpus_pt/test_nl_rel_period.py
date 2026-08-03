"""Wave 2 -- coarse relative periods: next/this/last week, month, year.

The whole calendar period that contains the anchor, shifted by the
relative marker (next=+1, this=0, last=-1).  Expected spans come from
independent calendar arithmetic against this corpus's anchor -- the week
tiles from its ISO-Monday start, the month/year/decade/century from their
first day -- never by pinning the parser's own output.
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from chronologia.astrodate import AstroDate

from ._corpus import ANCHOR, nomatch, span

_MIDNIGHT = dict(hour=0, minute=0, second=0, microsecond=0)


def _expected(rel, unit):
    if unit == "week":
        base = ANCHOR.replace(**_MIDNIGHT)
        s = base - timedelta(days=base.weekday()) + timedelta(weeks=rel)
        e = s + timedelta(days=7)
    elif unit == "month":
        s = ANCHOR.replace(day=1, **_MIDNIGHT) + relativedelta(months=rel)
        e = s + relativedelta(months=1)
    elif unit == "year":
        s = ANCHOR.replace(month=1, day=1, **_MIDNIGHT) + relativedelta(years=rel)
        e = s + relativedelta(years=1)
    elif unit in ("decade", "century"):
        step = 10 if unit == "decade" else 100
        y = (ANCHOR.year // step) * step + rel * step
        s = ANCHOR.replace(year=y, month=1, day=1, **_MIDNIGHT)
        e = s.replace(year=y + step)
    else:
        raise AssertionError(unit)
    return AstroDate(s.year, s.month, s.day), AstroDate(e.year, e.month, e.day)


CASES = [
    ('próxima semana', 1, 'week'),
    ('esta semana', 0, 'week'),
    ('semana passada', -1, 'week'),
    ('próximo mês', 1, 'month'),
    ('este mês', 0, 'month'),
    ('mês passado', -1, 'month'),
    ('próximo ano', 1, 'year'),
    ('este ano', 0, 'year'),
    ('ano passado', -1, 'year'),
]


@pytest.mark.parametrize("text,rel,unit", CASES)
def test_rel_period(text, rel, unit):
    sp = span(text)
    assert (sp.start, sp.end) == _expected(rel, unit)


# "last <plural-unit> of <period>" is not a supported construction: the plural
# unit vetoes the scoped-ordinal reading, so only a bare relative-period reading
# ("os últimos dias" = the last days = yesterday) is left, stranding the scope
# noun ("do ano"/"do mês").  That partial must be refused -- honest None -- the
# way en and the ten other locales already refuse the identical phrase, rather
# than leaking a yesterday span with the scope tail in the remainder (r43).
@pytest.mark.parametrize("text", [
    'os últimos dias do ano',
    'últimos dias do ano',
    'os últimos dias do mês',
    'últimos dias do mês',
])
def test_last_plural_unit_of_period_is_nomatch(text):
    nomatch(text)
