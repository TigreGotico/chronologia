# -*- coding: utf-8 -*-
"""Extra Polish holiday coverage for the two surfaces registered in this fix:
Boże Ciało (Corpus Christi, movable = Western computus Easter + 60) and the
Dec-26 second Christmas day (Boxing Day) idioms.

Gold is computed by independent arithmetic -- ``dateutil.easter`` for the
computus and a literal ``(12, 26)`` for the fixed date -- never read back from
the parser. Swept across a decade disjoint from the other pl holiday sweeps.

Anchor: Tuesday 2017-06-27 13:04.
"""
from datetime import date, timedelta

import pytest
from dateutil.easter import easter

from ._corpus import AstroDate, parse, span, start

_YEARS = list(range(2036, 2046))

_BOZE_CIALO = [(f"boże ciało {y}", easter(y) + timedelta(days=60)) for y in _YEARS]

_BOXING_SURFACES = (
    "drugi dzień świąt",
    "drugi dzień bożego narodzenia",
    "drugi dzień świąt bożego narodzenia",
    "drugie święto bożego narodzenia",
    "święty szczepan",
)
_BOXING = [(f"{s} {y}", date(y, 12, 26)) for y in _YEARS for s in _BOXING_SURFACES]


@pytest.mark.parametrize("text,gold", _BOZE_CIALO, ids=[c[0] for c in _BOZE_CIALO])
def test_boze_cialo_computus(text, gold):
    assert start(text) == AstroDate(gold.year, gold.month, gold.day)
    assert parse(text)[1] == ""
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,gold", _BOXING, ids=[c[0] for c in _BOXING])
def test_second_christmas_day(text, gold):
    assert start(text) == AstroDate(gold.year, gold.month, gold.day)
    assert parse(text)[1] == ""
    assert span(text).width == timedelta(days=1)
