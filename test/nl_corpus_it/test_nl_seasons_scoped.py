"""Italian seasons (meteorological, northern hemisphere) and scoped
ordinals ("la seconda settimana di luglio", "l'ultimo giorno di luglio")."""
from datetime import timedelta

import pytest

from ._corpus import start, start_end, AstroDate


@pytest.mark.parametrize("text,sm,em", [
    ("in primavera", 3, 6),
    ("in estate", 6, 9),
    ("in autunno", 9, 12),
    ("in inverno", 12, 3),
])
def test_season_current(text, sm, em):
    s, e = start_end(text)
    assert (s.month, e.month) == (sm, em)


@pytest.mark.parametrize("text,y,sm", [
    ("la primavera 1969", 1969, 3),
    ("l'estate 1969", 1969, 6),
    ("l'autunno 2001", 2001, 9),
    ("l'inverno 1889", 1889, 12),
])
def test_season_of_year(text, y, sm):
    s = start(text)
    assert (s.year, s.month) == (y, sm)


@pytest.mark.parametrize("text,y,mo,d,wide", [
    ("la seconda settimana di luglio", 2017, 7, 10, 7),
    ("la terza settimana di luglio", 2017, 7, 17, 7),
    ("il primo giorno di luglio", 2017, 7, 1, 1),
    ("l'ultimo giorno di luglio", 2017, 7, 31, 1),
    ("il secondo giorno di marzo", 2017, 3, 2, 1),
])
def test_scoped_ordinal(text, y, mo, d, wide):
    s, e = start_end(text)
    assert s == AstroDate(y, mo, d)
    assert e - s == timedelta(days=wide)
