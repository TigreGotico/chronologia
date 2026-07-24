"""Ukrainian eras: "до н. е." and "н. е.", the graphic abbreviations the
Ukrainian orthography lists, written after the year.  Both the spaced form
of the standard and the unspaced form people type are read.
"""
import pytest

from ._corpus import parse, start, AstroDate


# -- BC: astronomical year numbering (44 BC == year -43) ------------------

@pytest.mark.parametrize("text,astro_year", [
    ("Цезаря вбили у 44 до н. е.", -43),
    ("Цезаря вбили у 44 до н.е.", -43),
    ("Ольвію заснували у 647 до нашої ери.", -646),
])
def test_bc(text, astro_year):
    assert start(text).year == astro_year


# -- AD -------------------------------------------------------------------

@pytest.mark.parametrize("text,year", [
    ("Західна Римська імперія впала у 476 н. е.", 476),
    ("Хрещення Русі відбулося у 988 н.е.", 988),
    ("Собор зібрався у 325 нашої ери.", 325),
])
def test_ad(text, year):
    assert start(text) == AstroDate(year, 1, 1)


# -- a year without an era marker is an ordinary year ---------------------

def test_year_without_marker_stays_common_era():
    assert start("Зустріч відбулася у 1980 році.").year == 1980


# -- adversarial: nothing here may raise ----------------------------------

@pytest.mark.parametrize("text", [
    "Нашої ери це не стосується.",
    "до нашої ери",
    "фыва олдж пролджэ",
    "",
])
def test_no_crash(text):
    parse(text)
