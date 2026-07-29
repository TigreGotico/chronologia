"""Asturian seasons, bare and with an explicit year.

Meteorological quarters: primavera Mar-Jun, branu Jun-Sep, seronda Sep-Dec,
iviernu Dec-Mar (wrapping into the next year).
"""
from datetime import datetime

import pytest

from ._corpus import start_end, ad
from ._gen import SEAS


def _expected(name, year):
    sm, em = SEAS[name]
    if name == "iviernu":
        return datetime(year, 12, 1), datetime(year + 1, 3, 1)
    return datetime(year, sm, 1), datetime(year, em, 1)


@pytest.mark.parametrize("name", sorted(SEAS))
def test_season_bare_anchor_year(name):
    s, e = start_end(name)
    xs, xe = _expected(name, 2017)
    assert (s, e) == (ad(xs), ad(xe))


@pytest.mark.parametrize("year", [1969, 1999, 2018, 2020, 2050])
@pytest.mark.parametrize("name", sorted(SEAS))
def test_season_of_year(name, year):
    s, e = start_end(f"{name} {year}")
    xs, xe = _expected(name, year)
    assert (s, e) == (ad(xs), ad(xe))
