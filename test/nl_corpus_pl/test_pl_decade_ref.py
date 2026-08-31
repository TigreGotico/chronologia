"""Polish spoken decades: "lata osiemdziesiąte" (the eighties). The decade
word is the ordinal ADJECTIVE, plural nominative agreeing with "lata"
(years) -- spelled differently from the cardinal ("osiemdziesiąte" vs
"osiemdziesiąt"), so it survives the Slavic number fold untouched and binds
through its own closed ``DECADE`` vocabulary, mirroring the mechanism
already shipped for German ("die achtziger Jahre") and English ("the
eighties"). "lata" is registered as a dedicated plural year word, distinct
from the singular "rok" already used for a bare calendar year, so the two
readings never collide.
"""
from datetime import datetime

import pytest

from chronologia.astrodate import AstroDate
from ._corpus import start_end, start

ANCHOR = datetime(2026, 6, 15, 12, 0)


@pytest.mark.parametrize("text,y0", [
    ("lata osiemdziesiąte", 1980),
    ("lata dziewięćdziesiąte", 1990),
    ("lata dwudzieste", 2020),
])
def test_decade(text, y0):
    assert start_end(text, anchor=ANCHOR) == (
        AstroDate(y0, 1, 1), AstroDate(y0 + 10, 1, 1))


def test_decade_vs_bare_year_is_not_the_same_reading():
    # "lata osiemdziesiąte" (plural "lata") is the whole 1980s decade;
    # "rok 1980" (singular "rok") is the single calendar year 1980.
    decade_start, decade_end = start_end("lata osiemdziesiąte", anchor=ANCHOR)
    assert decade_start == AstroDate(1980, 1, 1)
    assert decade_end == AstroDate(1990, 1, 1)

    year_start, year_end = start_end("rok 1980", anchor=ANCHOR)
    assert year_start == AstroDate(1980, 1, 1)
    assert year_end == AstroDate(1981, 1, 1)


def test_bare_singular_year_still_a_single_year():
    assert start("rok 1969", anchor=ANCHOR) == AstroDate(1969, 1, 1)
