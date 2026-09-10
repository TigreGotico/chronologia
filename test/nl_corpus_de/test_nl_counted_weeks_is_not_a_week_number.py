"""A bare counted length is not a calendar week number.

German writes a week number in the singular -- "die 2. Woche", "KW 2",
"Kalenderwoche 2" -- while the plural "2 Wochen" counts weeks.  Listing the
plural as a week-number surface let the ordinal order read the bare counted
length as calendar week 2, so "2 wochen" answered 2017-01-09, a date six
months before the anchor.

Anchor 2017-06-27 13:04.
"""
from datetime import date

import pytest

from ._corpus import AstroDate, nomatch, start


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


def test_a_bare_counted_length_is_not_a_date():
    """Every other locale refuses this; German answered a past date."""
    nomatch("2 wochen")


@pytest.mark.parametrize("text", [
    "woche 2",
    "kalenderwoche 2",
    "kw 2",
    "die 2. woche",
])
def test_the_real_week_number_forms_still_resolve(text):
    assert start(text) == _ad(date(2017, 1, 9))


@pytest.mark.parametrize("text,expected", [
    # the counted readings the plural belongs to
    ("in 2 wochen", date(2017, 7, 11)),
    ("vor 2 wochen", date(2017, 6, 13)),
    ("2 wochen ab samstag", date(2017, 7, 15)),
])
def test_the_counted_readings_are_unchanged(text, expected):
    got = start(text)
    assert (got.year, got.month, got.day) == (expected.year, expected.month,
                                              expected.day)
