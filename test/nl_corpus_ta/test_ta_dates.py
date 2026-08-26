# -*- coding: utf-8 -*-
"""Calendar dates and years.

Tamil writes the date day-month-year, and its Gregorian month names are
transliterations of the Latin ones.  Its own solar-calendar month names are a
second live register; they are deliberately NOT shipped, because converting one
to a Gregorian date needs calendar arithmetic no source consulted closes -- see
``test_ta_refusals``.
"""
import pytest

from ._corpus import day, remainder, span, start


@pytest.mark.parametrize("text,expected", [
    ("15 ஜனவரி 2026", day(2026, 1, 15)),
    ("1 பிப்ரவரி 2030", day(2030, 2, 1)),
    ("29 பிப்ரவரி 2028", day(2028, 2, 29)),
    ("31 டிசம்பர் 1999", day(1999, 12, 31)),
    ("6 ஜூன் 2044", day(2044, 6, 6)),
])
def test_a_full_date_reads_day_month_year(text, expected):
    assert (span(text).start, span(text).end) == expected


@pytest.mark.parametrize("text,expected", [
    # no year: the anchor is 2027-05-12, and the construction prefers the
    # future, so a month already past rolls to the next year.
    ("15 மார்ச்", day(2028, 3, 15)),
    ("20 ஜூன்", day(2027, 6, 20)),
    ("1 நவம்பர்", day(2027, 11, 1)),
])
def test_a_yearless_date_prefers_the_future(text, expected):
    assert (span(text).start, span(text).end) == expected


@pytest.mark.parametrize("text,ym", [
    ("ஜனவரி 2026", (2026, 1)),
    ("ஆகஸ்ட் 2031", (2031, 8)),
    ("அக்டோபர் 1984", (1984, 10)),
])
def test_a_month_and_year_is_the_whole_month(text, ym):
    s = span(text)
    assert (s.start.year, s.start.month, s.start.day) == (ym[0], ym[1], 1)
    assert s.end.month == ym[1] % 12 + 1


@pytest.mark.parametrize("text,month", [
    ("ஜன. 2026", 1), ("பிப். 2026", 2), ("மார். 2026", 3), ("ஏப். 2026", 4),
    ("ஆக. 2026", 8), ("செப். 2026", 9), ("அக். 2026", 10), ("நவ. 2026", 11),
    ("டிச. 2026", 12),
])
def test_the_abbreviated_months(text, month):
    assert (start(text).year, start(text).month) == (2026, month)


@pytest.mark.parametrize("text,year", [
    ("2026", 2026),
    ("1984", 1984),
    ("இரண்டு ஆயிரம் இருபது", 2020),
    ("ஆயிரம் தொள்ளாயிரம் நாற்பது", 1940),
])
def test_a_year_reads_whole(text, year):
    s = span(text)
    assert (s.start.year, s.start.month, s.start.day) == (year, 1, 1)
    assert s.end.year == year + 1


@pytest.mark.parametrize("text,expected", [
    ("2027-05-20", day(2027, 5, 20)),
    ("20/05/2027", day(2027, 5, 20)),
])
def test_the_numeric_literals_read_day_first(text, expected):
    """Tamil is a day-month-year locale, so 20/05 is the twentieth of May."""
    assert (span(text).start, span(text).end) == expected


def test_the_native_digits_read_as_numbers():
    """Tamil digits ௦-௯ are ordinary Unicode decimal digits, so the shared
    tokenizer reads them with no locale pass of its own."""
    assert (start("௧௫ ஜனவரி ௨௦௨௬").year,
            start("௧௫ ஜனவரி ௨௦௨௬").month,
            start("௧௫ ஜனவரி ௨௦௨௬").day) == (2026, 1, 15)


def test_a_date_inside_a_sentence_leaves_the_rest_alone():
    text = "கூட்டம் 15 ஜனவரி 2026 அன்று"
    assert (span(text).start, span(text).end) == day(2026, 1, 15)
    assert "கூட்டம்" in remainder(text)
