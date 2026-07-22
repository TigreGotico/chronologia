"""Greek eras (π.Χ. / μ.Χ.), the year reference ("το έτος 1969") and deep
time ("πριν από 66 εκατομμύρια χρόνια").  BC years land on the astronomical
year (44 BC == -43); AD/plain years span the whole civil year.
"""
from datetime import datetime

import pytest

from ._corpus import ad, start, start_end


@pytest.mark.parametrize("text,astro_year", [
    ("44 π.χ.", -43),
    ("753 π.χ.", -752),
    ("323 π.χ.", -322),
    ("1 π.χ.", 0),
])
def test_bc_year(text, astro_year):
    s, e = start_end(text)
    assert s.year == astro_year and e.year == astro_year + 1
    assert (s.month, s.day) == (1, 1)


@pytest.mark.parametrize("text,year", [
    ("2024 μ.χ.", 2024),
    ("476 μ.χ.", 476),
    ("1453 μ.χ.", 1453),
])
def test_ad_year(text, year):
    s, e = start_end(text)
    assert s.year == year and e.year == year + 1


@pytest.mark.parametrize("text,year", [
    ("το έτος 1969", 1969),
    ("1969", 1969),
    ("2000", 2000),
    ("το έτος 1453", 1453),
])
def test_year_ref(text, year):
    s, e = start_end(text)
    assert (s.year, e.year) == (year, year + 1)
    assert (s.month, s.day) == (1, 1)


@pytest.mark.parametrize("text", [
    "πριν από 66 εκατομμύρια χρόνια",
    "66 εκατομμύρια χρόνια πριν",
])
def test_deep_time(text):
    s, e = start_end(text)
    assert s.year == -65998050 and e.year == -64998050
