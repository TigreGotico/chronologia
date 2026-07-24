"""Bulgarian eras: the secular "пр.н.е." / "сл.н.е." pair and the religious
"пр.Хр." / "сл.Хр." pair.  Bulgarian orthography allows the abbreviations
with and without spaces between the shortened words, so both are read.
"""
import pytest

from ._corpus import parse, start, AstroDate


# -- BC: astronomical year numbering (44 BC == year -43) ------------------

@pytest.mark.parametrize("text,astro_year", [
    ("Цезар е убит през 44 пр.н.е.", -43),
    ("Цезар е убит през 44 пр. н. е.", -43),
    ("Рим е основан през 753 преди новата ера.", -752),
    ("Партенонът е завършен през 432 пр.хр.", -431),
    ("Александър умира през 323 преди христа.", -322),
])
def test_bc(text, astro_year):
    assert start(text).year == astro_year


# -- AD -------------------------------------------------------------------

@pytest.mark.parametrize("text,year", [
    ("Западната Римска империя пада през 476 сл.н.е.", 476),
    ("България е покръстена през 864 сл.хр.", 864),
    ("Съборът заседава през 325 след христа.", 325),
    ("Константинопол е основан през 330 от новата ера.", 330),
])
def test_ad(text, year):
    assert start(text) == AstroDate(year, 1, 1)


# -- a year without an era marker is an ordinary year ---------------------

def test_year_without_marker_stays_common_era():
    assert start("Срещата се проведе през 1980 година.").year == 1980


# -- adversarial: nothing here may raise ----------------------------------

@pytest.mark.parametrize("text", [
    "Новата ера няма нищо общо с това.",
    "преди новата ера",
    "фыва олдж пролджэ",
    "",
])
def test_no_crash(text):
    parse(text)
