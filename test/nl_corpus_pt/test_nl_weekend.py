# -*- coding: utf-8 -*-
"""Wave 2 -- the weekend: this/next/last weekend, a named two-day span.

The Saturday-Sunday of the anchor's week, shifted a whole week per the
relative marker.  The surface is Priberam's "fim de semana",
"periodo composto pelos dias de sabado e domingo", alongside the equally
lemmatised "final de semana" of Brazilian usage.
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
    ('Vamos à praia este fim de semana', 0),
    ('O concerto é no próximo fim de semana', 1),
    ('Estivemos em Lisboa no fim de semana passado', -1),
    ('A gente se fala no final de semana', 0),
    ('O show é no próximo final de semana', 1),
    ('Trabalho aos fins de semana', 0),
    ('fim de semana', 0),
]

#: near misses built from the same words: they may well resolve, but the
#: span they resolve to is never the two-day rest period.
_NOT_THE_WEEKEND = [
    'fim de mês',
    'semana',
    'de semana',
    'fim',
    'o fim do mundo',
]

_FUZZ = [
    'fim fim fim de semana',
    'o fim de semana de semana',
    'fim de semana 🎉',
    'próximo próximo fim de semana',
    'de fim',
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
