"""Dutch spoken decades: "de jaren tachtig" (the eighties). Dutch decade
words ("tachtig", "negentig", ...) are spelled identically to the plain
cardinal numbers they double as, so the shared Germanic number fold turns
them into digit tokens before the grammar ever sees the word -- the same
fold trap that excludes "půl"/"пів"/"pola" from their languages' cardinal
runs. Reading them back through the digit slot (as the parser already does
for "80er" spellings) rather than a spoken ``DECADE`` token sidesteps the
trap. The construction is gated on the *plural* year word ("jaren"), never
the singular ("jaar"), so it cannot claim the ordinary single-year reading.
"""
from datetime import datetime

import pytest

from chronologia.astrodate import AstroDate
from ._corpus import start_end, start, nomatch

ANCHOR = datetime(2026, 6, 15, 12, 0)


@pytest.mark.parametrize("text,y0", [
    ("de jaren tachtig", 1980),
    ("de jaren negentig", 1990),
    ("de jaren twintig", 2020),
    ("jaren 80", 1980),
    ("de jaren 1980", 1980),
])
def test_decade(text, y0):
    assert start_end(text, anchor=ANCHOR) == (
        AstroDate(y0, 1, 1), AstroDate(y0 + 10, 1, 1))


def test_decade_vs_bare_year_is_not_the_same_reading():
    # "de jaren tachtig" (plural "jaren") is the whole 1980s decade; "het
    # jaar 1980" (singular "jaar") is the single calendar year 1980 -- the
    # plural/singular distinction on the year word is what tells them apart.
    decade_start, decade_end = start_end("de jaren tachtig", anchor=ANCHOR)
    assert decade_start == AstroDate(1980, 1, 1)
    assert decade_end == AstroDate(1990, 1, 1)

    year_start, year_end = start_end("het jaar 1980", anchor=ANCHOR)
    assert year_start == AstroDate(1980, 1, 1)
    assert year_end == AstroDate(1981, 1, 1)


def test_bare_singular_year_still_a_single_year():
    assert start("het jaar 1969", anchor=ANCHOR) == AstroDate(1969, 1, 1)
