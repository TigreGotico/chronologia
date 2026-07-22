"""French seasons (meteorological, northern hemisphere) and scoped ordinals
("la deuxième semaine de juillet", "le dernier jour de juillet").
"""
from datetime import timedelta

import pytest

from ._corpus import span, start, start_end, nomatch, AstroDate


# -- seasons (month-aligned, northern hemisphere) -------------------------

@pytest.mark.parametrize("text,sm,em", [
    ("au printemps", 3, 6),
    ("en été", 6, 9),
    ("en automne", 9, 12),
    ("en hiver", 12, 3),
])
def test_season_current(text, sm, em):
    s, e = start_end(text)
    assert s.month == sm
    assert e.month == em


@pytest.mark.parametrize("text,y,sm", [
    ("au printemps 1969", 1969, 3),
    ("l'été 1969", 1969, 6),
    ("en automne 2001", 2001, 9),
    ("l'hiver 1889", 1889, 12),
])
def test_season_of_year(text, y, sm):
    s = start(text)
    assert (s.year, s.month) == (y, sm)


@pytest.mark.parametrize("text,sm", [
    ("l'hiver prochain", 12),
    ("le printemps dernier", 3),
])
def test_season_relative(text, sm):
    assert start(text).month == sm


# -- scoped ordinals ------------------------------------------------------

@pytest.mark.parametrize("text,y,mo,d,wide", [
    ("la deuxième semaine de juillet", 2017, 7, 10, 7),
    ("la troisième semaine de juillet", 2017, 7, 17, 7),
    ("le premier jour de juillet", 2017, 7, 1, 1),
    ("le dernier jour de juillet", 2017, 7, 31, 1),
    ("le deuxième jour de mars", 2017, 3, 2, 1),
])
def test_scoped_ordinal(text, y, mo, d, wide):
    s, e = start_end(text)
    assert s == AstroDate(y, mo, d)
    assert e - s == timedelta(days=wide)
