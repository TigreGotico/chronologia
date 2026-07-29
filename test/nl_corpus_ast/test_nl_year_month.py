"""Bare years, ``<month> <year>`` (juxtaposed) and bare months.

Anchor is Tuesday 2017-06-27 13:04.  A bare year spans the whole civil year;
``xunu 2020`` spans that month of that explicit year; a bare month resolves to
that month of the anchor year.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import start_end, ad
from ._gen import MON


def _first_next_month(y, m):
    return datetime(y + 1, 1, 1) if m == 12 else datetime(y, m + 1, 1)


# --- bare civil year ---------------------------------------------------------
@pytest.mark.parametrize("year", list(range(1700, 2201)))
def test_bare_year(year):
    s, e = start_end(str(year))
    assert (s, e) == (ad(datetime(year, 1, 1)), ad(datetime(year + 1, 1, 1)))


# --- <month> <year> (juxtaposed, no "de") ------------------------------------
_MY_YEARS = [1900, 1950, 1969, 1985, 1999, 2000, 2010, 2020, 2035, 2100]


@pytest.mark.parametrize("year", _MY_YEARS)
@pytest.mark.parametrize("m,word", sorted(MON.items()))
def test_month_year(year, m, word):
    s, e = start_end(f"{word} {year}")
    assert s == ad(datetime(year, m, 1))
    assert e == ad(_first_next_month(year, m))


# --- <month> de <year> (connector "de") --------------------------------------
@pytest.mark.parametrize("year", _MY_YEARS)
@pytest.mark.parametrize("m,word", sorted(MON.items()))
def test_month_de_year(year, m, word):
    s, e = start_end(f"{word} de {year}")
    assert s == ad(datetime(year, m, 1))
    assert e == ad(_first_next_month(year, m))


# --- bare month resolves to the anchor year ----------------------------------
@pytest.mark.parametrize("m,word", sorted(MON.items()))
def test_bare_month_anchor_year(m, word):
    s, e = start_end(word)
    assert s == ad(datetime(2017, m, 1))
    assert e == ad(_first_next_month(2017, m))
    assert e > s and (e - s) >= timedelta(days=28)
