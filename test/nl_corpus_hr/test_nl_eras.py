"""Croatian eras.  Croatian keeps two live pairs side by side: the Christian
"pr. Kr." / "p. Kr." (the orthography also writes the latter "po. Kr.") and
the secular "pr. n. e." / "n. e.".  Both are read, and the year may carry the
ordinal dot Croatian puts on a date.
"""
import pytest

from ._corpus import parse, start, AstroDate


# -- BC: astronomical year numbering (44 BC == year -43) ------------------

@pytest.mark.parametrize("text,astro_year", [
    ("Cezar je ubijen 44. pr. Kr.", -43),
    ("Cezar je ubijen 44 pr.kr.", -43),
    ("Rim je osnovan 753 prije krista.", -752),
    ("Partenon je dovršen 432 pr. n. e.", -431),
    ("Aleksandar je umro 323 prije nove ere.", -322),
])
def test_bc(text, astro_year):
    assert start(text).year == astro_year


# -- AD -------------------------------------------------------------------

@pytest.mark.parametrize("text,year", [
    ("Zapadno Rimsko Carstvo palo je 476 p. Kr.", 476),
    ("Zapadno Rimsko Carstvo palo je 476 po. Kr.", 476),
    ("Sabor je zasjedao 325 poslije krista.", 325),
    ("Carigrad je osnovan 330 n. e.", 330),
])
def test_ad(text, year):
    assert start(text) == AstroDate(year, 1, 1)


# -- a year without an era marker is an ordinary year ---------------------

def test_year_without_marker_stays_common_era():
    assert start("Sastanak je održan 1980. godine.").year == 1980


# -- adversarial: nothing here may raise ----------------------------------

@pytest.mark.parametrize("text", [
    "Nova era s time nema nikakve veze.",
    "prije nove ere",
    "qwzx plkj mnbv",
    "",
])
def test_no_crash(text):
    parse(text)
