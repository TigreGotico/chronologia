# -*- coding: utf-8 -*-
"""Wave 2 -- the weekend: this/next/last weekend, a named two-day span.

The Saturday-Sunday of the anchor's week, shifted a whole week per the
relative marker.  The surface is the RAE's "fin de semana",
"parte de la semana que comprende normalmente el sabado y el domingo",
and its plural "fines de semana".
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
    ('Nos vamos a la playa este fin de semana', 0),
    ('El concierto es el próximo fin de semana', 1),
    ('Estuvimos en Madrid el fin de semana pasado', -1),
    ('Te llamo el fin de semana que viene', 1),
    ('Trabajo los fines de semana', 0),
    ('fin de semana', 0),
    ('el último fin de semana', -1),
]

#: near misses built from the same words: they may well resolve, but the
#: span they resolve to is never the two-day rest period.
_NOT_THE_WEEKEND = [
    'fin de mes',
    'semana',
    'de semana',
    'fin',
    'el fin del mundo',
]

_FUZZ = [
    'fin fin fin de semana semana',
    'el fin de semana de semana',
    'fin de semana 🎉',
    'próximo próximo fin de semana',
    'de fin',
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
