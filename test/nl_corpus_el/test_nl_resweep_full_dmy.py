# -*- coding: utf-8 -*-
"""Second-pass sweep: exhaustive "D <genitive-month> YYYY" over a fresh year
batch and a fresh day set, disjoint from ``test_el_full_date_sweep.py``
(which used days {1,7,14,21,28} and years drawn from
{1850,1900,1955,1975,1999-2001,2012,2020,2023,2024,1945,1969}).

An explicit year removes any prefer-future ambiguity, so the gold is a plain
``datetime(y, mo, d)`` computed independently of the parser. Days stay <= 28
so every (day, month) pair is valid in every year, including non-leap ones.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ad, start, start_end

GEN = {
    1: "ιανουαρίου", 2: "φεβρουαρίου", 3: "μαρτίου", 4: "απριλίου",
    5: "μαΐου", 6: "ιουνίου", 7: "ιουλίου", 8: "αυγούστου",
    9: "σεπτεμβρίου", 10: "οκτωβρίου", 11: "νοεμβρίου", 12: "δεκεμβρίου",
}

_DAYS = [2, 9, 16, 23]
_YEARS = [1868, 1889, 1917, 1933, 1958, 1972, 1986, 2006, 2029, 2033]

_DATE_CASES = [
    (f"{d} {GEN[mo]} {y}", y, mo, d)
    for y in _YEARS for mo in range(1, 13) for d in _DAYS
]


@pytest.mark.parametrize("text,y,mo,d", _DATE_CASES)
def test_full_date_sweep_fresh(text, y, mo, d):
    assert start(text) == ad(datetime(y, mo, d))


@pytest.mark.parametrize("text,y,mo,d", [
    (f"{d} {GEN[mo]} {y}", y, mo, d)
    for y, mo, d in [(1917, 11, 7), (1933, 1, 30), (1958, 10, 4),
                     (2006, 3, 8), (2029, 6, 21)]
])
def test_full_date_span_is_one_day_fresh(text, y, mo, d):
    s, e = start_end(text)
    assert s == ad(datetime(y, mo, d))
    assert e == ad(datetime(y, mo, d) + timedelta(days=1))
