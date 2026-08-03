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
    ('przyszły tydzień', 1, 'week'),
    ('zeszły tydzień', -1, 'week'),
    ('przyszły miesiąc', 1, 'month'),
    ('przyszły rok', 1, 'year'),
]


@pytest.mark.parametrize("text,rel,unit", CASES)
def test_rel_period(text, rel, unit):
    sp = span(text)
    assert (sp.start, sp.end) == _expected(rel, unit)


# "last <plural-unit> of <period>" is not a supported construction: the plural
# unit vetoes the scoped-ordinal reading, so only a bare relative-period reading
# ("ostatnie dni" = the last days = yesterday) is left, stranding the genitive
# scope noun ("roku"/"miesiąca").  That partial must be refused -- honest None --
# the way en and the ten other locales already refuse the identical phrase,
# rather than leaking a yesterday span with the scope tail (r43).
@pytest.mark.parametrize("text", [
    'ostatnie dni roku',
    'ostatnie dni miesiąca',
])
def test_last_plural_unit_of_period_is_nomatch(text):
    nomatch(text)
