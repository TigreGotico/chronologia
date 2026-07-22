# -*- coding: utf-8 -*-
"""Relative periods and relative weekdays (mwl) -- base Romance parity newly
wired for Mirandese (this/next/last were absent in round 1).

Mirandese relative markers (Amadeu Ferreira orthography): este/esta (this),
que ben "that comes" / próssimo (next), passado/passada / redadeiro (last).
Anchor 2017-06-27 (Tuesday), week starts Monday."""
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start_end, start


@pytest.mark.parametrize("text,s,e", [
    ('esta sumana', (2017, 6, 26), (2017, 7, 3)),
    ('la sumana que ben', (2017, 7, 3), (2017, 7, 10)),
    ('la sumana passada', (2017, 6, 19), (2017, 6, 26)),
    ('l més que ben', (2017, 7, 1), (2017, 8, 1)),
    ('l anho que ben', (2018, 1, 1), (2019, 1, 1)),
])
def test_rel_period(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s)
    assert ee == AstroDate(*e)


@pytest.mark.parametrize("text,ymd", [
    ('la sesta feira que ben', (2017, 6, 30)),
    ('l segunda feira que ben', (2017, 7, 3)),
])
def test_relative_weekday(text, ymd):
    assert start(text) == AstroDate(*ymd)
