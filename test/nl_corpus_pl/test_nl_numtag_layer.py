"""Polish numbers read through numtag.

numtag reads the numbers of every case form: the counts, the spelled years,
the day ordinals ("dwudziestego trzeciego") and the clock hours.  Every
expected value is written by hand or computed with ``timedelta`` from the
anchor; a lone clock hour takes the next twelve-hour reading after the
anchor.
"""
from datetime import datetime, timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, parse, start


@pytest.mark.parametrize("text,expected", [
    ("tysiąc dwieście dni temu", ANCHOR - timedelta(days=1200)),
    ("za tysiąc dni", ANCHOR + timedelta(days=1000)),
    ("rok dwa tysiące dwudziesty piąty", datetime(2025, 1, 1)),
    ("dwudziestego trzeciego maja 2025", datetime(2025, 5, 23)),
    ("wpół do ósmej", datetime(2017, 6, 27, 19, 30)),
    ("kwadrans po dziewiątej", datetime(2017, 6, 27, 21, 15)),
])
def test_numbers_read_through_numtag(text, expected):
    assert start(text) == ad(expected)


def test_spelled_year_with_ordinal_90():
    assert start("rok tysiąc dziewięćset dziewięćdziesiąty pierwszy") == ad(
        datetime(1991, 1, 1))


# The year of a spelled date is an ordinal that holds a scale word; the
# date keeps the year it names, whatever the anchor.
@pytest.mark.parametrize("anchor", [
    datetime(2026, 1, 10, 8, 0),
    datetime(2026, 12, 1, 8, 0),
    datetime(2028, 3, 1, 8, 0),
])
@pytest.mark.parametrize("text,month,day", [
    ("pierwszego maja dwa tysiące dwudziestego szóstego roku", 5, 1),
])
def test_spelled_date_with_a_year_from_2000(text, month, day, anchor):
    result = parse(text, anchor)
    assert result.span.start == ad(datetime(2026, month, day))


@pytest.mark.parametrize("text,expected", [
    ("za pół godziny", ANCHOR + timedelta(minutes=30)),
    ("pół godziny temu", ANCHOR - timedelta(minutes=30)),
    ("za pół roku", ANCHOR + relativedelta(months=6)),
    ("pół roku temu", ANCHOR - relativedelta(months=6)),
])
def test_half_of_a_unit_offset(text, expected):
    assert start(text) == ad(expected)


@pytest.mark.parametrize("text,expected,left", [
    ("ustaw alarm na siódmą rano", datetime(2017, 6, 28, 7, 0), "ustaw alarm na"),
    ("zrób mi przypomnienie na ósmą wieczorem", datetime(2017, 6, 27, 20, 0),
     "zrób mi przypomnienie na"),
])
def test_spoken_hour_with_a_part_of_the_day(text, expected, left):
    result = parse(text)
    assert result.span.start == ad(expected)
    assert result.remainder == left


# An ordinal hour after the clock preposition keeps its clock when a word
# outside the vocabulary follows; the clock reads the same without it.
@pytest.mark.parametrize("text,expected", [
    ("o dziewiątej zadzwoń do mamy", datetime(2017, 6, 27, 21, 0)),
    ("przypomnij mi o siódmej wyłączyć piekarnik",
     datetime(2017, 6, 27, 19, 0)),
    ("jutro o ósmej spotkanie z lekarzem", datetime(2017, 6, 28, 8, 0)),
    ("piątego maja o dziewiątej spotkanie", datetime(2018, 5, 5, 9, 0)),
])
def test_ordinal_hour_before_another_word(text, expected):
    assert start(text) == ad(expected)


def test_ordinal_before_a_noun_is_no_clock():
    assert parse("na drugim piętrze") is None


def test_spelled_year_of_the_1950s():
    assert start("w roku tysiąc dziewięćset pięćdziesiątym szóstym") == ad(
        datetime(1956, 1, 1))


def test_masculine_ordinal_after_o_is_no_clock():
    assert parse("o drugim etapie") is None


@pytest.mark.xfail(raises=AssertionError, strict=True, reason="https://github.com/TigreGotico/chronologia/issues/1221")
@pytest.mark.parametrize("text,expected", [
    ("wpół do dziewiątej zadzwoń do mamy", datetime(2017, 6, 27, 20, 30)),
])
def test_known_gap_fraction_clock_before_another_word(text, expected):
    assert start(text) == ad(expected)


def test_spelled_date_of_the_1790s():
    assert start("trzeciego maja tysiąc siedemset dziewięćdziesiątego pierwszego roku") == ad(
        datetime(1791, 5, 3))
