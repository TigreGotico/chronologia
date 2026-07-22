"""Finnish eras (eKr./jKr., also eaa./jaa.), the bare year, deep time and
seasons.  BC years land on the astronomical year (44 BC == -43).
"""
from datetime import datetime

import pytest

from ._corpus import ad, start_end


@pytest.mark.parametrize("text,astro_year", [
    ("44 ekr.", -43),
    ("753 ekr.", -752),
    ("323 eaa.", -322),
    ("1 ekr.", 0),
])
def test_bc_year(text, astro_year):
    s, e = start_end(text)
    assert s.year == astro_year and e.year == astro_year + 1
    assert (s.month, s.day) == (1, 1)


@pytest.mark.parametrize("text,year", [
    ("2024 jkr.", 2024),
    ("476 jaa.", 476),
    ("1453 jkr.", 1453),
])
def test_ad_year(text, year):
    s, e = start_end(text)
    assert s.year == year and e.year == year + 1


@pytest.mark.parametrize("text,year", [
    ("1969", 1969),
    ("2000", 2000),
    ("1453", 1453),
])
def test_year_ref(text, year):
    s, e = start_end(text)
    assert (s.year, e.year) == (year, year + 1)
    assert (s.month, s.day) == (1, 1)


@pytest.mark.parametrize("text", [
    "66 miljoonaa vuotta sitten",
])
def test_deep_time(text):
    s, e = start_end(text)
    assert s.year == -65998050 and e.year == -64998050


@pytest.mark.parametrize("text,y,smo,emo", [
    ("kesä 2020", 2020, 6, 9),
    ("kevät 2021", 2021, 3, 6),
    ("talvi 2020", 2020, 12, 3),
    ("syksy 2019", 2019, 9, 12),
])
def test_season_year(text, y, smo, emo):
    s, e = start_end(text)
    assert (s.year, s.month, s.day) == (y, smo, 1)
    ey = y + 1 if emo < smo else y
    assert (e.year, e.month, e.day) == (ey, emo, 1)


def test_winter_wraps_year():
    s, e = start_end("talvi 2020")
    assert s == ad(datetime(2020, 12, 1))
    assert e == ad(datetime(2021, 3, 1))
