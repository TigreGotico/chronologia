# -*- coding: utf-8 -*-
"""Second-pass sweep: mixed fresh-area shapes not densely covered by the
first-pass corpus -- full "N de <month> de <year>" dates, hour-fraction
clock idioms ("e cuarto"/"e media"/"menos cuarto"/"en punto" crossed with
"da mañá"/"da tarde"/"da noite"), quarters ("<ordinal> trimestre de
<year>"), and month-thirds with an explicit trailing year.  Gold is
independent arithmetic in every case.  Anchor Tue 2017-06-27, 13:04.

"cuarto trimestre de <year>" once collapsed to Q1 -- "cuarto" (the ordinal
4th) is spelled like the clock quarter-hour fraction word and was withheld
from the number fold -- now FIXED: the ordinal reading is licensed directly
before the quarter noun "trimestre" while the clock/room readings stay intact.

"principios/finais de <month> de <year>" (month-thirds with a trailing
explicit year) used to ignore that year and resolve against the anchor year
(2017) instead -- FIXED. The equal-thirds boundaries below are computed by
independent date arithmetic (never consulting the parser); see
test_nl_month_thirds_year.py for the dedicated early/mid/late sweep.
"""
from datetime import datetime

import pytest

from ._corpus import AstroDate, ad, start, start_end

# -- full DMY, fresh years -----------------------------------------------
_DMY = [
    ('17 de xaneiro de 2030', (2030, 1, 17)),
    ('17 de xaneiro de 2032', (2032, 1, 17)),
    ('17 de xaneiro de 2034', (2034, 1, 17)),
    ('17 de xaneiro de 2036', (2036, 1, 17)),
    ('17 de xaneiro de 2038', (2038, 1, 17)),
    ('17 de febreiro de 2030', (2030, 2, 17)),
    ('17 de febreiro de 2032', (2032, 2, 17)),
    ('17 de febreiro de 2034', (2034, 2, 17)),
    ('17 de febreiro de 2036', (2036, 2, 17)),
    ('17 de febreiro de 2038', (2038, 2, 17)),
    ('17 de marzo de 2030', (2030, 3, 17)),
    ('17 de marzo de 2032', (2032, 3, 17)),
    ('17 de marzo de 2034', (2034, 3, 17)),
    ('17 de marzo de 2036', (2036, 3, 17)),
    ('17 de marzo de 2038', (2038, 3, 17)),
    ('17 de abril de 2030', (2030, 4, 17)),
    ('17 de abril de 2032', (2032, 4, 17)),
    ('17 de abril de 2034', (2034, 4, 17)),
    ('17 de abril de 2036', (2036, 4, 17)),
    ('17 de abril de 2038', (2038, 4, 17)),
    ('17 de maio de 2030', (2030, 5, 17)),
    ('17 de maio de 2032', (2032, 5, 17)),
    ('17 de maio de 2034', (2034, 5, 17)),
    ('17 de maio de 2036', (2036, 5, 17)),
    ('17 de maio de 2038', (2038, 5, 17)),
    ('17 de xuño de 2030', (2030, 6, 17)),
    ('17 de xuño de 2032', (2032, 6, 17)),
    ('17 de xuño de 2034', (2034, 6, 17)),
    ('17 de xuño de 2036', (2036, 6, 17)),
    ('17 de xuño de 2038', (2038, 6, 17)),
    ('17 de xullo de 2030', (2030, 7, 17)),
    ('17 de xullo de 2032', (2032, 7, 17)),
    ('17 de xullo de 2034', (2034, 7, 17)),
    ('17 de xullo de 2036', (2036, 7, 17)),
    ('17 de xullo de 2038', (2038, 7, 17)),
    ('17 de agosto de 2030', (2030, 8, 17)),
    ('17 de agosto de 2032', (2032, 8, 17)),
    ('17 de agosto de 2034', (2034, 8, 17)),
    ('17 de agosto de 2036', (2036, 8, 17)),
    ('17 de agosto de 2038', (2038, 8, 17)),
    ('17 de setembro de 2030', (2030, 9, 17)),
    ('17 de setembro de 2032', (2032, 9, 17)),
    ('17 de setembro de 2034', (2034, 9, 17)),
    ('17 de setembro de 2036', (2036, 9, 17)),
    ('17 de setembro de 2038', (2038, 9, 17)),
    ('17 de outubro de 2030', (2030, 10, 17)),
    ('17 de outubro de 2032', (2032, 10, 17)),
    ('17 de outubro de 2034', (2034, 10, 17)),
    ('17 de outubro de 2036', (2036, 10, 17)),
    ('17 de outubro de 2038', (2038, 10, 17)),
    ('17 de novembro de 2030', (2030, 11, 17)),
    ('17 de novembro de 2032', (2032, 11, 17)),
    ('17 de novembro de 2034', (2034, 11, 17)),
    ('17 de novembro de 2036', (2036, 11, 17)),
    ('17 de novembro de 2038', (2038, 11, 17)),
    ('17 de decembro de 2030', (2030, 12, 17)),
    ('17 de decembro de 2032', (2032, 12, 17)),
    ('17 de decembro de 2034', (2034, 12, 17)),
    ('17 de decembro de 2036', (2036, 12, 17)),
    ('17 de decembro de 2038', (2038, 12, 17)),
]


@pytest.mark.parametrize("text,ymd", _DMY)
def test_full_dmy_fresh_years(text, ymd):
    assert start(text) == AstroDate(*ymd)


# -- clock: hour-fraction x meridiem cross, hours 1-11 -------------------
def _clk(y, mo, d, h, mi):
    return AstroDate(y, mo, d, h, mi)


_CLOCK = [
    ('ás 1 e cuarto da mañá', (2017, 6, 28, 1, 15)),
    ('ás 1 e media da tarde', (2017, 6, 27, 13, 30)),
    ('ás 1 menos cuarto da noite', (2017, 6, 28, 12, 45)),
    ('ás 1 en punto da mañá', (2017, 6, 28, 1, 0)),
    ('ás 2 e cuarto da mañá', (2017, 6, 28, 2, 15)),
    ('ás 2 e media da tarde', (2017, 6, 27, 14, 30)),
    ('ás 2 menos cuarto da noite', (2017, 6, 27, 13, 45)),
    ('ás 2 en punto da mañá', (2017, 6, 28, 2, 0)),
    ('ás 3 e cuarto da mañá', (2017, 6, 28, 3, 15)),
    ('ás 3 e media da tarde', (2017, 6, 27, 15, 30)),
    ('ás 3 menos cuarto da noite', (2017, 6, 27, 14, 45)),
    ('ás 3 en punto da mañá', (2017, 6, 28, 3, 0)),
    ('ás 4 e cuarto da mañá', (2017, 6, 28, 4, 15)),
    ('ás 4 e media da tarde', (2017, 6, 27, 16, 30)),
    ('ás 4 menos cuarto da noite', (2017, 6, 27, 15, 45)),
    ('ás 4 en punto da mañá', (2017, 6, 28, 4, 0)),
    ('ás 5 e cuarto da mañá', (2017, 6, 28, 5, 15)),
    ('ás 5 e media da tarde', (2017, 6, 27, 17, 30)),
    ('ás 5 menos cuarto da noite', (2017, 6, 27, 16, 45)),
    ('ás 5 en punto da mañá', (2017, 6, 28, 5, 0)),
    ('ás 6 e cuarto da mañá', (2017, 6, 28, 6, 15)),
    ('ás 6 e media da tarde', (2017, 6, 27, 18, 30)),
    ('ás 6 menos cuarto da noite', (2017, 6, 27, 17, 45)),
    ('ás 6 en punto da mañá', (2017, 6, 28, 6, 0)),
    ('ás 7 e cuarto da mañá', (2017, 6, 28, 7, 15)),
    ('ás 7 e media da tarde', (2017, 6, 27, 19, 30)),
    ('ás 7 menos cuarto da noite', (2017, 6, 27, 18, 45)),
    ('ás 7 en punto da mañá', (2017, 6, 28, 7, 0)),
    ('ás 8 e cuarto da mañá', (2017, 6, 28, 8, 15)),
    ('ás 8 e media da tarde', (2017, 6, 27, 20, 30)),
    ('ás 8 menos cuarto da noite', (2017, 6, 27, 19, 45)),
    ('ás 8 en punto da mañá', (2017, 6, 28, 8, 0)),
    ('ás 9 e cuarto da mañá', (2017, 6, 28, 9, 15)),
    ('ás 9 e media da tarde', (2017, 6, 27, 21, 30)),
    ('ás 9 menos cuarto da noite', (2017, 6, 27, 20, 45)),
    ('ás 9 en punto da mañá', (2017, 6, 28, 9, 0)),
    ('ás 10 e cuarto da mañá', (2017, 6, 28, 10, 15)),
    ('ás 10 e media da tarde', (2017, 6, 27, 22, 30)),
    ('ás 10 menos cuarto da noite', (2017, 6, 27, 21, 45)),
    ('ás 10 en punto da mañá', (2017, 6, 28, 10, 0)),
    ('ás 11 e cuarto da mañá', (2017, 6, 28, 11, 15)),
    ('ás 11 e media da tarde', (2017, 6, 27, 23, 30)),
    ('ás 11 menos cuarto da noite', (2017, 6, 27, 22, 45)),
    ('ás 11 en punto da mañá', (2017, 6, 28, 11, 0)),
]


@pytest.mark.parametrize("text,ymdhm", _CLOCK)
def test_clock_hour_fraction_meridiem_cross(text, ymdhm):
    assert start(text) == _clk(*ymdhm)


# -- quarters, fresh years -------------------------------------------------
_QUARTER = [
    ('primeiro trimestre de 2040', (2040, 1, 1), (2040, 4, 1)),
    ('primeiro trimestre de 2041', (2041, 1, 1), (2041, 4, 1)),
    ('primeiro trimestre de 2042', (2042, 1, 1), (2042, 4, 1)),
    ('primeiro trimestre de 2043', (2043, 1, 1), (2043, 4, 1)),
    ('primeiro trimestre de 2044', (2044, 1, 1), (2044, 4, 1)),
    ('primeiro trimestre de 2045', (2045, 1, 1), (2045, 4, 1)),
    ('primeiro trimestre de 2046', (2046, 1, 1), (2046, 4, 1)),
    ('primeiro trimestre de 2047', (2047, 1, 1), (2047, 4, 1)),
    ('primeiro trimestre de 2048', (2048, 1, 1), (2048, 4, 1)),
    ('primeiro trimestre de 2049', (2049, 1, 1), (2049, 4, 1)),
    ('segundo trimestre de 2040', (2040, 4, 1), (2040, 7, 1)),
    ('segundo trimestre de 2041', (2041, 4, 1), (2041, 7, 1)),
    ('segundo trimestre de 2042', (2042, 4, 1), (2042, 7, 1)),
    ('segundo trimestre de 2043', (2043, 4, 1), (2043, 7, 1)),
    ('segundo trimestre de 2044', (2044, 4, 1), (2044, 7, 1)),
    ('segundo trimestre de 2045', (2045, 4, 1), (2045, 7, 1)),
    ('segundo trimestre de 2046', (2046, 4, 1), (2046, 7, 1)),
    ('segundo trimestre de 2047', (2047, 4, 1), (2047, 7, 1)),
    ('segundo trimestre de 2048', (2048, 4, 1), (2048, 7, 1)),
    ('segundo trimestre de 2049', (2049, 4, 1), (2049, 7, 1)),
    ('terceiro trimestre de 2040', (2040, 7, 1), (2040, 10, 1)),
    ('terceiro trimestre de 2041', (2041, 7, 1), (2041, 10, 1)),
    ('terceiro trimestre de 2042', (2042, 7, 1), (2042, 10, 1)),
    ('terceiro trimestre de 2043', (2043, 7, 1), (2043, 10, 1)),
    ('terceiro trimestre de 2044', (2044, 7, 1), (2044, 10, 1)),
    ('terceiro trimestre de 2045', (2045, 7, 1), (2045, 10, 1)),
    ('terceiro trimestre de 2046', (2046, 7, 1), (2046, 10, 1)),
    ('terceiro trimestre de 2047', (2047, 7, 1), (2047, 10, 1)),
    ('terceiro trimestre de 2048', (2048, 7, 1), (2048, 10, 1)),
    ('terceiro trimestre de 2049', (2049, 7, 1), (2049, 10, 1)),
]


@pytest.mark.parametrize("text,s,e", _QUARTER)
def test_quarter_fresh_years(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


# "cuarto trimestre de <year>" now folds correctly: the ordinal reading of the
# ordinal-fraction homograph "cuarto" is licensed directly before the quarter
# noun "trimestre" (fix: numfold._license_ordinal_fraction quarter-word frame).
# The clock/room readings of bare "cuarto" stay untouched (see
# test_nl_confusables and the "e cuarto"/"menos cuarto" clock rows above).
_QUARTER_Q4 = [
    ('cuarto trimestre de 2040', (2040, 10, 1), (2041, 1, 1)),
    ('cuarto trimestre de 2041', (2041, 10, 1), (2042, 1, 1)),
    ('cuarto trimestre de 2042', (2042, 10, 1), (2043, 1, 1)),
    ('cuarto trimestre de 2043', (2043, 10, 1), (2044, 1, 1)),
    ('cuarto trimestre de 2044', (2044, 10, 1), (2045, 1, 1)),
    ('cuarto trimestre de 2045', (2045, 10, 1), (2046, 1, 1)),
    ('cuarto trimestre de 2046', (2046, 10, 1), (2047, 1, 1)),
    ('cuarto trimestre de 2047', (2047, 10, 1), (2048, 1, 1)),
    ('cuarto trimestre de 2048', (2048, 10, 1), (2049, 1, 1)),
    ('cuarto trimestre de 2049', (2049, 10, 1), (2050, 1, 1)),
]


@pytest.mark.parametrize("text,s,e", _QUARTER_Q4)
def test_fourth_quarter_fresh_years(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


# -- month-thirds with an explicit trailing year ----------------------------
def _thirds(year, month):
    """(early, late) as independent (start, end) AstroDate pairs -- equal
    thirds of the Gregorian month, computed without consulting the parser."""
    first = datetime(year, month, 1)
    nxt = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)
    third = (nxt - first) / 3
    b1, b2 = first + third, first + 2 * third
    return {
        "principios": (ad(first), ad(b1)),
        "finais": (ad(b2), ad(nxt)),
    }


_MT = [
    (word, month, f'{word} de {name} de 2041')
    for month, name in enumerate(
        ('xaneiro', 'febreiro', 'marzo', 'abril', 'maio', 'xuño', 'xullo',
         'agosto', 'setembro', 'outubro', 'novembro', 'decembro'),
        start=1,
    )
    for word in ('principios', 'finais')
]


@pytest.mark.parametrize("word,month,text", _MT)
def test_month_thirds_explicit_year(word, month, text):
    assert start_end(text) == _thirds(2041, month)[word]
