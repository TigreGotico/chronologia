# -*- coding: utf-8 -*-
"""Wave 2 -- the weekend: this/next/last weekend, a named two-day span.

The Saturday-Sunday of the anchor's week, shifted a whole week per the
relative marker.  Catalan says "cap de setmana", not the Castilian
calque "fi de setmana", which is why the near-miss list below keeps the
calque out of the weekend reading.
Expected spans come from independent calendar arithmetic against this
corpus's anchor -- never by pinning the parser.
"""
from datetime import timedelta

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import ANCHOR, parse, span


def _expected(rel):
    base = ANCHOR.replace(hour=0, minute=0, second=0, microsecond=0)
    sat = (base - timedelta(days=base.weekday())
           + timedelta(days=5) + timedelta(weeks=rel))
    end = sat + timedelta(days=2)
    return (AstroDate(sat.year, sat.month, sat.day),
            AstroDate(end.year, end.month, end.day))


CASES = [
    ('Anem a la platja aquest cap de setmana', 0),
    ('El concert és el cap de setmana vinent', 1),
    ('Vam ser a Girona el cap de setmana passat', -1),
    ('Et truco el cap de setmana que ve', 1),
    ('Treballo els caps de setmana', 0),
    ('cap de setmana', 0),
    ('el pròxim cap de setmana', 1),
]

#: near misses built from the same words: they may well resolve, but the
#: span they resolve to is never the two-day rest period.
_NOT_THE_WEEKEND = [
    'fi de setmana',
    'setmana',
    'de setmana',
    'cap',
    'cap problema',
]

_FUZZ = [
    'cap cap cap de setmana',
    'el cap de setmana de setmana',
    'cap de setmana 🎉',
    'vinent vinent cap de setmana',
    'de cap',
]


@pytest.mark.parametrize("text,rel", CASES)
def test_weekend(text, rel):
    sp = span(text)
    assert (sp.start, sp.end) == _expected(rel)


@pytest.mark.parametrize("text", _NOT_THE_WEEKEND)
def test_near_miss_is_not_the_weekend(text):
    r = parse(text)
    if r is not None:
        assert (r[0].start, r[0].end) != _expected(0)


@pytest.mark.parametrize("text", _FUZZ)
def test_never_raises(text):
    parse(text)
