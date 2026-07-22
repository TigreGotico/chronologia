"""Basque calendar dates -- the case-inflection machinery.

Basque marks the date word, not a preposition: the month takes the genitive
(-aren, "of June"), the day takes the inessive (-ean / -an, "on the 5th") or
the absolutive (-a), and the year takes the relational -ko ("2020ko").  The
canonical order is big-endian YEAR-ko MONTH-aren DAY-an
("2020ko ekainaren 5ean").  The number-fold strips the day/year case suffix
off the digit (5ean -> 5, 2020ko -> 2020) and the month surfaces carry their
inflections in the voc, so every case form binds the same date.
"""
from datetime import datetime

import pytest

from ._corpus import ad, start, start_end


# full YEAR-ko MONTH-aren DAY-an (canonical inessive day)
@pytest.mark.parametrize("text,y,mo,d", [
    ("2020ko ekainaren 5ean", 2020, 6, 5),
    ("1999ko martxoaren 15ean", 1999, 3, 15),
    ("2000ko urtarrilaren 1ean", 2000, 1, 1),
    ("2021eko abenduaren 25ean", 2021, 12, 25),
    ("1789ko uztailaren 14an", 1789, 7, 14),
    ("1945eko maiatzaren 9an", 1945, 5, 9),
    ("1969ko uztailaren 20an", 1969, 7, 20),
    ("2001eko irailaren 11n", 2001, 9, 11),
])
def test_full_inessive_date(text, y, mo, d):
    assert start(text) == ad(datetime(y, mo, d))


# absolutive day (-a) instead of the inessive
@pytest.mark.parametrize("text,y,mo,d", [
    ("2020ko ekainaren 5a", 2020, 6, 5),
    ("1936ko uztailaren 18a", 1936, 7, 18),
    ("2011ko urriaren 20a", 2011, 10, 20),
])
def test_full_absolutive_date(text, y, mo, d):
    assert start(text) == ad(datetime(y, mo, d))


def test_full_date_span_is_one_day():
    s, e = start_end("2020ko ekainaren 5ean")
    assert s == ad(datetime(2020, 6, 5))
    assert e == ad(datetime(2020, 6, 6))


# no year: MONTH-aren DAY rolls to the next occurrence (prefer_future)
@pytest.mark.parametrize("text,y,mo,d", [
    ("ekainaren 5ean", 2018, 6, 5),
    ("ekainaren 5a", 2018, 6, 5),
    ("martxoaren 15ean", 2018, 3, 15),
    ("urtarrilaren 1ean", 2018, 1, 1),
    ("abenduaren 25ean", 2017, 12, 25),
    ("uztailaren 28an", 2017, 7, 28),
])
def test_bare_month_day_rolls_future(text, y, mo, d):
    assert start(text) == ad(datetime(y, mo, d))


# a bare year-ko month is the whole month
@pytest.mark.parametrize("text,y,mo", [
    ("2020ko ekaina", 2020, 6),
    ("1999ko martxoa", 1999, 3),
])
def test_year_month_whole_month(text, y, mo):
    s, e = start_end(text)
    assert (s.year, s.month, s.day) == (y, mo, 1)
    assert e.month == (mo % 12) + 1
