"""Italian ranges: "da A a B" / "dal A al B" / "tra A e B", plus the scoped
century 100-year span."""
from datetime import timedelta

import pytest

from ._corpus import start_end, AstroDate


@pytest.mark.parametrize("text,s,e", [
    ("da giugno ad agosto", AstroDate(2017, 6, 1), AstroDate(2017, 9, 1)),
    ("dal 5 luglio al 10 agosto", AstroDate(2017, 7, 5), AstroDate(2017, 8, 11)),
    ("tra luglio e settembre", AstroDate(2017, 7, 1), AstroDate(2017, 10, 1)),
    ("dal 2018 al 2020", AstroDate(2018, 1, 1), AstroDate(2021, 1, 1)),
    ("dal 1 luglio al 5 luglio", AstroDate(2017, 7, 1), AstroDate(2017, 7, 6)),
])
def test_range(text, s, e):
    assert start_end(text) == (s, e)


def test_weekday_range():
    s, e = start_end("da lunedì a venerdì")
    assert e - s == timedelta(days=5)


def test_century_span():
    s, e = start_end("il 20 secolo")
    assert (s, e) == (AstroDate(1900, 1, 1), AstroDate(2000, 1, 1))
