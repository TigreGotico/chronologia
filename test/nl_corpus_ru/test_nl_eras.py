"""Russian eras: the secular "до н. э." / "н. э." pair and the religious
"до Р. Х." / "по Р. Х." pair, both postposed to the year as Russian writes
them.  The abbreviations are spelled with a space after every letter in
edited prose and without one in everyday typing, so both are read.
"""
import pytest

from ._corpus import parse, start, AstroDate


# -- BC: astronomical year numbering (44 BC == year -43) ------------------

@pytest.mark.parametrize("text,astro_year", [
    ("Цезаря убили в 44 до н. э.", -43),
    ("Цезаря убили в 44 до н.э.", -43),
    ("Рим был основан в 753 до нашей эры.", -752),
    ("Парфенон достроили в 432 до р. х.", -431),
    ("Катулл родился в 87 до рождества христова.", -86),
])
def test_bc(text, astro_year):
    assert start(text).year == astro_year


# -- AD -------------------------------------------------------------------

@pytest.mark.parametrize("text,year", [
    ("Западная Римская империя пала в 476 н. э.", 476),
    ("Крещение Руси произошло в 988 н.э.", 988),
    ("Константинополь основали в 330 нашей эры.", 330),
    ("Первый Вселенский собор прошёл в 325 по р. х.", 325),
])
def test_ad(text, year):
    assert start(text) == AstroDate(year, 1, 1)


# -- a year without an era marker is an ordinary year ---------------------

def test_year_without_marker_stays_common_era():
    assert start("Встреча состоялась в 1980 году.").year == 1980


# -- adversarial: nothing here may raise ----------------------------------

@pytest.mark.parametrize("text", [
    "Нашей эры это никак не касается.",
    "до нашей эры",
    "Он говорил о рождестве христовом весь вечер.",
    "фыва олдж пролджэ",
    "",
])
def test_no_crash(text):
    parse(text)
