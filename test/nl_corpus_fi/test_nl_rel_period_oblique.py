# -*- coding: utf-8 -*-
"""Coarse relative periods in the local cases speakers actually use.

Finnish puts the unit noun of a relative-period phrase in a local case and
agrees the determiner with it: the week is adessive ("viime viikolla"), the
month inessive ("tässä kuussa"), the year and the quarter essive ("ensi
vuonna", "viime neljänneksenä").  The bare nominative is the marked form,
not the ordinary one.  Every surface below is CLDR 47's own wording for the
field (cldr-dates-full/main/fi/dateFields.json).

Expected spans come from independent calendar arithmetic against the corpus
anchor -- the week from its Monday start, the month, year and quarter from
their first day -- never from the parser's own output.
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
    elif unit == "quarter":
        q = (ANCHOR.month - 1) // 3
        s = ANCHOR.replace(month=q * 3 + 1, day=1, **_MIDNIGHT) + relativedelta(months=3 * rel)
        e = s + relativedelta(months=3)
    else:
        s = ANCHOR.replace(month=1, day=1, **_MIDNIGHT) + relativedelta(years=rel)
        e = s + relativedelta(years=1)
    return AstroDate(s.year, s.month, s.day), AstroDate(e.year, e.month, e.day)


_OBLIQUE = [
    ('viime viikolla', -1, 'week'),
    ('tällä viikolla', 0, 'week'),
    ('ensi viikolla', 1, 'week'),
    ('viime kuussa', -1, 'month'),
    ('tässä kuussa', 0, 'month'),
    ('ensi kuussa', 1, 'month'),
    ('viime vuonna', -1, 'year'),
    ('tänä vuonna', 0, 'year'),
    ('ensi vuonna', 1, 'year'),
    ('viime neljännesvuonna', -1, 'quarter'),
    ('tänä neljännesvuonna', 0, 'quarter'),
    ('ensi neljännesvuonna', 1, 'quarter'),
    ('viime neljänneksenä', -1, 'quarter'),
    ('tänä neljänneksenä', 0, 'quarter'),
    ('ensi neljänneksenä', 1, 'quarter'),
]

#: the nominative surfaces that already read -- a control that the case
#: forms were added beside them rather than in place of them.
_NOMINATIVE = [
    ('viime viikko', -1, 'week'),
    ('ensi viikko', 1, 'week'),
    ('tämä viikko', 0, 'week'),
    ('viime kuukausi', -1, 'month'),
    ('ensi kuukausi', 1, 'month'),
    ('viime vuosi', -1, 'year'),
    ('ensi vuosi', 1, 'year'),
]


@pytest.mark.parametrize("text,rel,unit", _OBLIQUE + _NOMINATIVE)
def test_rel_period_span(text, rel, unit):
    assert (span(text).start, span(text).end) == _expected(rel, unit)


@pytest.mark.parametrize("text,rel,unit", _OBLIQUE + _NOMINATIVE)
def test_rel_period_consumes_the_whole_phrase(text, rel, unit):
    assert parse(text)[1] == ""


def test_toissa_paivana_is_two_days_back():
    s = span('toissa päivänä')
    d = (ANCHOR - timedelta(days=2)).replace(**_MIDNIGHT)
    assert s.start == AstroDate(d.year, d.month, d.day)
    assert parse('toissa päivänä')[1] == ""


@pytest.mark.parametrize("text", ['viikolla', 'kuussa', 'vuonna'])
def test_a_bare_case_marked_unit_is_not_a_period(text):
    """The case ending alone names no period -- only a determiner does."""
    r = parse(text)
    assert r is None
