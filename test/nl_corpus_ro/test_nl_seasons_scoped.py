"""Romanian seasons (northern hemisphere) and scoped ordinals."""
from datetime import timedelta

import pytest

from ._corpus import start, start_end, AstroDate


@pytest.mark.parametrize("text,sm,em", [
    ("primăvara", 3, 6),
    ("vara", 6, 9),
    ("toamna", 9, 12),
    ("iarna", 12, 3),
])
def test_season_current(text, sm, em):
    s, e = start_end(text)
    assert (s.month, e.month) == (sm, em)


@pytest.mark.parametrize("text,y,sm", [
    ("primăvara 1969", 1969, 3),
    ("vara 1969", 1969, 6),
    ("toamna 2001", 2001, 9),
    ("iarna 1889", 1889, 12),
])
def test_season_of_year(text, y, sm):
    s = start(text)
    assert (s.year, s.month) == (y, sm)


@pytest.mark.parametrize("text,y,mo,d,wide", [
    ("a doua săptămână din iulie", 2017, 7, 10, 7),
    ("a treia săptămână din iulie", 2017, 7, 17, 7),
    ("ultima zi din iulie", 2017, 7, 31, 1),
    ("a treia zi din martie", 2017, 3, 3, 1),
])
def test_scoped_ordinal(text, y, mo, d, wide):
    s, e = start_end(text)
    assert s == AstroDate(y, mo, d)
    assert e - s == timedelta(days=wide)
