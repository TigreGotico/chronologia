"""Dates, both month widths, and the spelled numerals.

CLDR ships two month widths for be and the locale reads both: the stand-alone
nominative names a bare month ("сакавік"), the format genitive follows a day
number ("25 сакавіка").  The long date form is ``d MMMM y 'г'.`` -- day,
genitive month, year, and the literal skarot "г.".

The numerals are transcribed from Wiktionary's ``Module:number list/data/be``.
Expected values here are plain arithmetic on the anchor, never read back from
the parser.
"""
from datetime import date, timedelta

import pytest

from ._corpus import ANCHOR, parse, start, start_end

#: (stand-alone nominative, format genitive, month number) -- CLDR 47, be.
MONTHS = [
    ("студзень", "студзеня", 1), ("люты", "лютага", 2),
    ("сакавік", "сакавіка", 3), ("красавік", "красавіка", 4),
    ("май", "мая", 5), ("чэрвень", "чэрвеня", 6),
    ("ліпень", "ліпеня", 7), ("жнівень", "жніўня", 8),
    ("верасень", "верасня", 9), ("кастрычнік", "кастрычніка", 10),
    ("лістапад", "лістапада", 11), ("снежань", "снежня", 12),
]


@pytest.mark.parametrize("nom,gen,n", MONTHS)
def test_standalone_month_with_a_year(nom, gen, n):
    s, e = start_end(f"{nom} 2020")
    assert (s.year, s.month, s.day) == (2020, n, 1)
    assert (e.year, e.month) == (2020 + n // 12, n % 12 + 1)


@pytest.mark.parametrize("nom,gen,n", MONTHS)
def test_genitive_month_after_a_day_number(nom, gen, n):
    s = start(f"14 {gen} 2020")
    assert (s.year, s.month, s.day) == (2020, n, 14)


@pytest.mark.parametrize("nom,gen,n", MONTHS)
def test_the_long_date_form_with_the_year_skarot(nom, gen, n):
    s = start(f"3 {gen} 1999 г.")
    assert (s.year, s.month, s.day) == (1999, n, 3)


def test_travien_is_not_a_parsed_month():
    """CLDR names month 5 май only.  травень is live Belarusian vocabulary but
    is not the calendar-standard name, so it does not ship as a surface; a
    native confirmation that it is current for the calendar sense specifically
    is what would change that."""
    r = parse("травень 2021")
    assert r is None or "травень" in r[1]
    assert parse("5 траўня") is None


def test_may_does_ship():
    """The control for the pin above."""
    s = start("май 2021")
    assert (s.year, s.month) == (2021, 5)


#: (spelled cardinal, value) -- Wiktionary Module:number list/data/be.
CARDINALS = [
    ("адзін", 1), ("два", 2), ("тры", 3), ("чатыры", 4), ("пяць", 5),
    ("шэсць", 6), ("сем", 7), ("восем", 8), ("дзевяць", 9), ("дзесяць", 10),
    ("адзінаццаць", 11), ("дванаццаць", 12), ("трынаццаць", 13),
    ("чатырнаццаць", 14), ("пятнаццаць", 15), ("шаснаццаць", 16),
    ("сямнаццаць", 17), ("семнаццаць", 17), ("васямнаццаць", 18),
    ("дзевятнаццаць", 19), ("дваццаць", 20), ("дваццаць пяць", 25),
    ("трыццаць", 30), ("трыццаць адзін", 31), ("сорак", 40),
    ("пяцьдзясят", 50), ("шэсцьдзясят", 60), ("семдзесят", 70),
    ("восемдзесят", 80), ("дзевяноста", 90), ("сто", 100),
    ("сто дваццаць пяць", 125),
]


@pytest.mark.parametrize("word,value", CARDINALS)
def test_spelled_cardinal_day_offset(word, value):
    unit = "дзень" if value == 1 else "дні" if 2 <= value % 10 <= 4 \
        and not 12 <= value % 100 <= 14 else "дзён"
    s = start(f"{word} {unit} таму")
    assert s.date() == ANCHOR.date() - timedelta(days=value)


@pytest.mark.parametrize("word,value", [
    ("адна", 1), ("дзве", 2), ("тры", 3), ("пяць", 5), ("дваццаць", 20),
])
def test_the_feminine_cardinal_agrees_with_the_feminine_unit(word, value):
    """хвіліна is feminine, so a count ending in 1 or 2 takes адна / дзве --
    the masculine адзін / два never appear before it."""
    unit = "хвіліну" if value == 1 else "хвіліны" if 2 <= value <= 4 \
        else "хвілін"
    s = start(f"{word} {unit} таму")
    assert (s.hour * 60 + s.minute) == (ANCHOR.hour * 60 + ANCHOR.minute) - value


#: (spelled genitive-masculine day ordinal, day of month) -- the form a
#: Belarusian date puts the day in, agreeing with an elided "дня".
DAY_ORDINALS = [
    ("першага", 1), ("другога", 2), ("трэцяга", 3), ("чацвёртага", 4),
    ("пятага", 5), ("шостага", 6), ("сёмага", 7), ("восьмага", 8),
    ("дзявятага", 9), ("дзясятага", 10), ("адзінаццатага", 11),
    ("дванаццатага", 12), ("пятнаццатага", 15), ("дваццатага", 20),
    ("дваццаць першага", 21), ("дваццаць пятага", 25),
    ("трыццатага", 30), ("трыццаць першага", 31),
]


@pytest.mark.parametrize("word,day", DAY_ORDINALS)
def test_spelled_day_of_month(word, day):
    s = start(f"{word} студзеня 2020")
    assert (s.year, s.month, s.day) == (2020, 1, day)


@pytest.mark.parametrize("word,day", [("дваццаць першага", 21),
                                      ("дваццаць пятага", 25),
                                      ("трыццаць першага", 31)])
def test_a_compound_day_keeps_its_tens(word, day):
    """Folding only the unit would answer the fifth when the speaker said the
    twenty-fifth."""
    assert start(f"{word} студзеня 2020").day == day


@pytest.mark.parametrize("word,q", [("першы", 1), ("другі", 2), ("трэці", 3),
                                    ("чацвёрты", 4)])
def test_spelled_quarter_ordinal(word, q):
    s = start(f"{word} квартал 2020")
    assert (s.year, s.month, s.day) == (2020, 3 * (q - 1) + 1, 1)


@pytest.mark.parametrize("text,y,m,d", [
    ("25 сакавіка 2020 г.", 2020, 3, 25),
    ("1 студзеня 2000 г.", 2000, 1, 1),
    ("31 снежня 1999 г.", 1999, 12, 31),
    ("12.05.2020", 2020, 5, 12),
    ("2017-06-30", 2017, 6, 30),
])
def test_date_forms(text, y, m, d):
    s = start(text)
    assert (s.year, s.month, s.day) == (y, m, d)


@pytest.mark.parametrize("text,y", [("2019", 2019), ("1918", 1918),
                                    ("1863 г.", 1863), ("у 2020 годзе", 2020)])
def test_year_reference(text, y):
    s, e = start_end(text)
    assert (s.year, s.month, s.day) == (y, 1, 1)
    assert e.year == y + 1


@pytest.mark.parametrize("text,y0,y1", [
    ("20-е стагоддзе", 1900, 2000), ("21-е стагоддзе", 2000, 2100),
])
def test_century(text, y0, y1):
    s, e = start_end(text)
    assert (s.year, e.year) == (y0, y1)


@pytest.mark.parametrize("text,d0,d1", [
    ("з 5 да 12 ліпеня", date(2017, 7, 5), date(2017, 7, 13)),
    ("паміж 5 і 12 ліпеня", date(2017, 7, 5), date(2017, 7, 13)),
])
def test_closed_range(text, d0, d1):
    s, e = start_end(text)
    assert (s.date(), e.date()) == (d0, d1)
