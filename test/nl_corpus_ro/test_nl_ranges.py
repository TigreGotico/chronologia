"""Romanian ranges: "din A pana in B" / "de la A la B" / "intre A si B",
plus the scoped century span."""
from datetime import timedelta

import pytest

from ._corpus import start_end, AstroDate


@pytest.mark.parametrize("text,s,e", [
    ("din iunie până în august", AstroDate(2017, 6, 1), AstroDate(2017, 9, 1)),
    ("din 5 iulie până în 10 august", AstroDate(2017, 7, 5), AstroDate(2017, 8, 11)),
    ("între iulie și septembrie", AstroDate(2017, 7, 1), AstroDate(2017, 10, 1)),
    ("din 2018 până în 2020", AstroDate(2018, 1, 1), AstroDate(2021, 1, 1)),
])
def test_range(text, s, e):
    assert start_end(text) == (s, e)


def test_weekday_range():
    s, e = start_end("de la luni la vineri")
    assert e - s == timedelta(days=5)


def test_century_span():
    s, e = start_end("al 20-lea secol")
    assert (s, e) == (AstroDate(1900, 1, 1), AstroDate(2000, 1, 1))
