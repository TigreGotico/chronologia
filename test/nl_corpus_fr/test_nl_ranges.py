"""French ranges: "de A à B" / "du A au B" / "entre A et B", plus the
scoped century that reads as a 100-year span.

Endpoints are two independent sub-parses; the span runs from the start of
the left to the end of the right.
"""
from datetime import timedelta

import pytest

from ._corpus import span, start_end, AstroDate


@pytest.mark.parametrize("text,s,e", [
    ("de juin à août", AstroDate(2017, 6, 1), AstroDate(2017, 9, 1)),
    ("du 5 juillet au 8 août", AstroDate(2017, 7, 5), AstroDate(2017, 8, 9)),
    ("entre juillet et septembre", AstroDate(2017, 7, 1), AstroDate(2017, 10, 1)),
    ("de 2018 à 2020", AstroDate(2018, 1, 1), AstroDate(2021, 1, 1)),
    ("du 1er juillet au 5 juillet", AstroDate(2017, 7, 1), AstroDate(2017, 7, 6)),
])
def test_range(text, s, e):
    gs, ge = start_end(text)
    assert (gs, ge) == (s, e)


def test_weekday_range():
    # a bare weekday is a range endpoint only: Monday..Friday of the week ahead
    s, e = start_end("de lundi à vendredi")
    assert e - s == timedelta(days=5)


def test_clock_range():
    s, e = start_end("du 10h au 12h")
    assert s == AstroDate(2017, 6, 28, 10, 0)
    assert e == AstroDate(2017, 6, 28, 12, 1)


# -- scoped century reads as a 100-year span ------------------------------

def test_century_span():
    s, e = start_end("le 20e siècle")
    assert s == AstroDate(1900, 1, 1)
    assert e == AstroDate(2000, 1, 1)
