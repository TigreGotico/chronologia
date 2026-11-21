# -*- coding: utf-8 -*-
"""Spelled year ranges and the width of a long-scale deep-time count.

A range of two spelled years runs from the first January to the end of the
last year: "from 2000 to 2010" covers 2000 to 2010 inclusive, so it ends on
1 January 2011. A count of years before present is as wide as one unit of its
last digit in the unit of its scale word: "two and a half trillion" is
2.5 * 10^12 years wide to 10^11 years.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2026, 1, 30, 10, 0)

YEAR_RANGES = [
    ("pt", "entre dois mil e dois mil e dez", 2000, 2011),
    ("pt", "de dois mil e cinco a dois mil e dez", 2005, 2011),
    ("en", "two thousand to two thousand and ten", 2000, 2011),
    ("en", "between two thousand and two thousand and ten", 2000, 2011),
]


@pytest.mark.parametrize("lang,text,first,after_last", YEAR_RANGES)
def test_a_range_of_two_spelled_years_covers_both(lang, text, first,
                                                  after_last):
    found = extract_timespan(text, lang, ANCHOR)
    assert found.span.start_datetime == datetime(first, 1, 1)
    assert found.span.end_datetime == datetime(after_last, 1, 1)
    assert found.remainder == ""


#: 1950 is the Before Present epoch: a count of N years before present starts
#: at the astronomical year 1950 - N.
LONG_SCALE_COUNTS = [
    ("pt", "há dois bilhões e meio de anos", 2_500_000_000_000, 10 ** 11),
    ("pt", "há dois bilhões de anos", 2_000_000_000_000, 10 ** 12),
    ("en", "two and a half trillion years ago", 2_500_000_000_000, 10 ** 11),
]


@pytest.mark.parametrize("lang,text,years,width", LONG_SCALE_COUNTS)
def test_a_long_scale_count_is_one_unit_of_its_last_digit_wide(
        lang, text, years, width):
    found = extract_timespan(text, lang, ANCHOR)
    assert found.span.start.year == 1950 - years
    assert found.span.end.year == 1950 - years + width
