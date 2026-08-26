"""Coarse relative periods in the oblique forms speakers actually use.

Polish names the containing period with "w" and the locative --
"w zeszlym tygodniu", "w tym miesiacu", "w przyszlym roku" -- which is the
only ordinary way to say it (PWN).

The preposition is part of the phrase, so nothing of it may be left in the
remainder. The quarter is framed the same way, in the locative "kwartale".

Expected spans come from independent calendar arithmetic against the corpus
anchor -- the week from its ISO-Monday start, the month and year from their
first day -- never from the parser's own output.
"""
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta

from chronologia.astrodate import AstroDate

from ._corpus import ANCHOR, parse, span

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


_CASES = [
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
]

_QUARTERS = [
    ('w zeszłym kwartale', -1),
    ('w tym kwartale', 0),
    ('w przyszłym kwartale', 1),
]


@pytest.mark.parametrize("text,rel,unit", _CASES)
def test_oblique_rel_period(text, rel, unit):
    s = span(text)
    exp_s, exp_e = _expected(rel, unit)
    assert (s.start, s.end) == (exp_s, exp_e)


@pytest.mark.parametrize("text,rel,unit", _CASES)
def test_the_preposition_belongs_to_the_phrase(text, rel, unit):
    """The framing preposition is part of the phrase, not leftover text."""
    assert parse(text)[1] == ""


@pytest.mark.parametrize("text,rel", _QUARTERS)
def test_oblique_quarter(text, rel):
    s = span(text)
    q = ANCHOR.replace(month=(ANCHOR.month - 1) // 3 * 3 + 1, day=1, **_MIDNIGHT)
    q += relativedelta(months=3 * rel)
    e = q + relativedelta(months=3)
    assert (s.start, s.end) == (AstroDate(q.year, q.month, q.day),
                                AstroDate(e.year, e.month, e.day))
    assert parse(text)[1] == ""
