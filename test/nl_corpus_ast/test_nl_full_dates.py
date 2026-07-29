"""Full calendar dates and bare day-of-month phrasings.

``27 de xunu 2015`` pins the exact civil day.  ``15 de marzu`` (no year)
resolves to the next occurrence on/after the anchor date (2017-06-27): March is
already past, so it lands in 2018; a July day stays in 2017.
"""
from datetime import date, datetime, timedelta

import pytest

from ._corpus import start_end, ad
from ._gen import MON, last_dom

_ANCHOR_DATE = date(2017, 6, 27)


def _full_cases():
    out = []
    for y in (1900, 1985, 2010, 2020, 2050, 2077):
        for m, word in MON.items():
            for d in (1, 15, last_dom(y, m)):
                out.append((f"{d} de {word} {y}", datetime(y, m, d)))
    return out


@pytest.mark.parametrize("text,expected", _full_cases())
def test_full_date(text, expected):
    s, e = start_end(text)
    assert s == ad(expected)
    assert e - s == timedelta(days=1)


def _day_month_cases():
    out = []
    for m, word in MON.items():
        for d in (1, 10, 20):
            y = 2017 if date(2017, m, d) >= _ANCHOR_DATE else 2018
            out.append((f"{d} de {word}", datetime(y, m, d)))
    return out


@pytest.mark.parametrize("text,expected", _day_month_cases())
def test_day_of_month_next_occurrence(text, expected):
    s, e = start_end(text)
    assert s == ad(expected)
    assert e - s == timedelta(days=1)
