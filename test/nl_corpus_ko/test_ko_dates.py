"""The date line: year, month, day, each field carrying its own suffix."""
import pytest

from ._corpus import day, nomatch, remainder, start_end


@pytest.mark.parametrize("text,expected", [
    ("2024년 3월 15일", day(2024, 3, 15)),
    ("2027년 5월 12일", day(2027, 5, 12)),
    ("2020년 12월 25일", day(2020, 12, 25)),
    ("2030년 1월 1일", day(2030, 1, 1)),
    ("1918년 11월 11일", day(1918, 11, 11)),
    ("2027년 8월 15일", day(2027, 8, 15)),
])
def test_the_date_line_runs_year_month_day(text, expected):
    """Korean is big-endian: 년, 월 and 일 each close their own field, and
    the order is the reverse of the day-first locales."""
    assert start_end(text) == expected


@pytest.mark.parametrize("text,expected", [
    ("2024년 3월", (2024, 3)),
    ("2020년 12월", (2020, 12)),
    ("1999년 7월", (1999, 7)),
])
def test_a_year_and_month_with_no_day(text, expected):
    y, m = expected
    s, e = start_end(text)
    assert (s.year, s.month, s.day) == (y, m, 1)
    assert (e.year, e.month) == (y + 1, 1) if m == 12 else (e.month == m + 1)


@pytest.mark.parametrize("text,month", [
    ("1월", 1), ("2월", 2), ("3월", 3), ("4월", 4), ("5월", 5), ("6월", 6),
    ("7월", 7), ("8월", 8), ("9월", 9), ("10월", 10), ("11월", 11),
    ("12월", 12),
])
def test_every_month_name_is_a_number_plus_the_month_word(text, month):
    """There are no lexical month names in ordinary Korean: a month name IS
    a numeral, so recognising one is recognising a number in front of 월."""
    s, _ = start_end(text)
    assert (s.month, s.day) == (month, 1)


@pytest.mark.parametrize("text,expected", [
    ("3월 15일", (3, 15)),
    ("12월 25일", (12, 25)),
    ("1월 1일", (1, 1)),
    ("6월 6일", (6, 6)),
])
def test_a_month_and_day_with_no_year(text, expected):
    m, d = expected
    s, _ = start_end(text)
    assert (s.month, s.day) == (m, d)


@pytest.mark.parametrize("text", [
    "2027년 3월 15일에", "3월 15일에",
])
def test_the_particle_is_consumed_with_the_date(text):
    assert remainder(text) == ""


@pytest.mark.parametrize("text,expected", [
    ("2027", (2027, 1, 1)),
    ("1918", (1918, 1, 1)),
])
def test_a_bare_year(text, expected):
    s, _ = start_end(text)
    assert (s.year, s.month, s.day) == expected


@pytest.mark.parametrize("text", ["13월", "0월", "20월"])
def test_a_number_outside_the_year_is_not_a_month(text):
    """월 is a month LABEL, never a count, so a number the calendar has no
    month for names no month -- and there is no month-count reading to fall
    back on either, because that word is 개월."""
    nomatch(text)


@pytest.mark.parametrize("text", ["유월", "시월"])
def test_the_spelled_month_names_are_not_shipped(text):
    """June and October are spelled with an irregular syllable that the
    numeral table does not produce, and no source consulted for this locale
    tables the spelled month names at all.  Rather than ship ten regular
    guesses and two wrong ones, none is shipped and the spelled forms name
    no month."""
    nomatch(text)
