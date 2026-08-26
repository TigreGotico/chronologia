"""Coarse relative periods in the oblique forms speakers actually use.

Russian names the containing period with a preposition and an oblique case:
"na proshloy nedele" is prepositional, "v etom mesyatse" and "v proshlom godu"
likewise. The nominative that the parser once accepted alone is the marked
register, not the ordinary one (Gramota.ru).

The preposition is part of the phrase, so nothing of it may be left in the
remainder; the quarter is framed the same way and names the current one with
"tekushchiy" rather than "etot".

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
]

_QUARTERS = [
    ('в прошлом квартале', -1),
    ('в текущем квартале', 0),
    ('в следующем квартале', 1),
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
