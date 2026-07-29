"""Closed ranges: ``de <m1> a <m2>`` months and ``de/ente <y1> a/y <y2>`` years.

The span is inclusive of both endpoints: a month range ends at the first of the
month after m2; a year range ends at Jan 1 of the year after y2.
"""
from datetime import datetime

import pytest

from ._corpus import start_end, ad
from ._gen import MON


def _month_range_cases():
    out = []
    for m1 in range(1, 13):
        for m2 in range(m1, 13):
            end = datetime(2018, 1, 1) if m2 == 12 else datetime(2017, m2 + 1, 1)
            out.append((f"de {MON[m1]} a {MON[m2]}", datetime(2017, m1, 1), end))
    return out


@pytest.mark.parametrize("text,xs,xe", _month_range_cases())
def test_month_range_same_year(text, xs, xe):
    s, e = start_end(text)
    assert (s, e) == (ad(xs), ad(xe))


_YEAR_PAIRS = [(2010, 2020), (1990, 1995), (2000, 2005), (1985, 2017), (2019, 2023)]


@pytest.mark.parametrize("y1,y2", _YEAR_PAIRS)
def test_year_range_de_a(y1, y2):
    s, e = start_end(f"de {y1} a {y2}")
    assert (s, e) == (ad(datetime(y1, 1, 1)), ad(datetime(y2 + 1, 1, 1)))


@pytest.mark.parametrize("y1,y2", _YEAR_PAIRS)
def test_year_range_ente_y(y1, y2):
    s, e = start_end(f"ente {y1} y {y2}")
    assert (s, e) == (ad(datetime(y1, 1, 1)), ad(datetime(y2 + 1, 1, 1)))
