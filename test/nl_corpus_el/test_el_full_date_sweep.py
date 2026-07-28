# -*- coding: utf-8 -*-
"""Exhaustive DMY sweep: "D <genitive-month> YYYY" pins the civil date outright.

An explicit year removes any prefer-future ambiguity, so the gold is a plain
``datetime(y, mo, d)`` computed independently of the parser. Days are kept
<= 28 so every (day, month) pair is valid in every year. Both the day-native
genitive ("15 Μαρτίου") and the article-genitive ("15 του Μαρτίου") are the
forms a Greek speaker actually writes.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ad, start, start_end

# genitive month forms, index == calendar month number
GEN = {
    1: "ιανουαρίου", 2: "φεβρουαρίου", 3: "μαρτίου", 4: "απριλίου",
    5: "μαΐου", 6: "ιουνίου", 7: "ιουλίου", 8: "αυγούστου",
    9: "σεπτεμβρίου", 10: "οκτωβρίου", 11: "νοεμβρίου", 12: "δεκεμβρίου",
}

_DAYS = [1, 7, 14, 21, 28]
_YEARS = [1850, 1900, 1955, 1999, 2000, 2012, 2023, 2024]

_DATE_CASES = [
    (f"{d} {GEN[mo]} {y}", y, mo, d)
    for y in _YEARS for mo in range(1, 13) for d in _DAYS
]


@pytest.mark.parametrize("text,y,mo,d", _DATE_CASES)
def test_full_date_sweep(text, y, mo, d):
    assert start(text) == ad(datetime(y, mo, d))


_ARTICLE_CASES = [
    (f"{d} του {GEN[mo]} {y}", y, mo, d)
    for y in (1975, 2001, 2020) for mo in range(1, 13) for d in (3, 17)
]


@pytest.mark.parametrize("text,y,mo,d", _ARTICLE_CASES)
def test_full_date_article_sweep(text, y, mo, d):
    assert start(text) == ad(datetime(y, mo, d))


@pytest.mark.parametrize("text,y,mo,d", [
    (f"9 {GEN[5]} 1945", 1945, 5, 9),
    (f"20 {GEN[7]} 1969", 1969, 7, 20),
    (f"25 {GEN[12]} 2000", 2000, 12, 25),
])
def test_full_date_span_is_one_day(text, y, mo, d):
    s, e = start_end(text)
    assert s == ad(datetime(y, mo, d))
    assert e == ad(datetime(y, mo, d) + timedelta(days=1))
