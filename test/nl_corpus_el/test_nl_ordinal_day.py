# -*- coding: utf-8 -*-
"""Greek written day-of-month as a digit ordinal: "Nη <genitive-month> YYYY".

The everyday Greek written date puts an ordinal ending on the day numeral --
"5η Μαρτίου 2019" = the 5th of March 2019 -- because the day-of-month agrees
with the feminine ημέρα.  Before the ordinal-ending fold the "η" sheared off
the digit and the frame collapsed to the whole month; these pins hold the
single-day reading.  The genitive form "της Nης <month>" is the same date
written after a genitive article.

An explicit year removes any prefer-future ambiguity, so the gold is a plain
``datetime(y, mo, d)`` computed independently of the parser; days are kept
<= 28 so every (day, month) pair is valid in every year.  The two national
holidays that happen to be written as digit ordinals (25η Μαρτίου, 28η
Οκτωβρίου) keep resolving to their exact civil date and are pinned too.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ad, span, start, start_end

# genitive month forms, index == calendar month number
GEN = {
    1: "ιανουαρίου", 2: "φεβρουαρίου", 3: "μαρτίου", 4: "απριλίου",
    5: "μαΐου", 6: "ιουνίου", 7: "ιουλίου", 8: "αυγούστου",
    9: "σεπτεμβρίου", 10: "οκτωβρίου", 11: "νοεμβρίου", 12: "δεκεμβρίου",
}

_DAYS = [1, 3, 5, 12, 21, 28]
_YEARS = [1900, 1955, 1999, 2012, 2019, 2020, 2024]

# "Nη <genitive-month> YYYY" -- the digit-ordinal day, explicit year.
_ORD_CASES = [
    (f"{d}η {GEN[mo]} {y}", y, mo, d)
    for y in _YEARS for mo in range(1, 13) for d in _DAYS
]


@pytest.mark.parametrize("text,y,mo,d", _ORD_CASES)
def test_ordinal_day_sweep(text, y, mo, d):
    assert start(text) == ad(datetime(y, mo, d))


@pytest.mark.parametrize("text,y,mo,d", _ORD_CASES)
def test_ordinal_day_is_one_day(text, y, mo, d):
    s, e = start_end(text)
    assert s == ad(datetime(y, mo, d))
    assert e == ad(datetime(y, mo, d) + timedelta(days=1))


# the reported silent-wrong surfaces, verbatim.
@pytest.mark.parametrize("text,y,mo,d", [
    ("5η Μαρτίου 2019", 2019, 3, 5),
    ("12η Ιουνίου 2020", 2020, 6, 12),
    ("1η Μαΐου 2018", 2018, 5, 1),
])
def test_reported_surfaces(text, y, mo, d):
    assert start(text) == ad(datetime(y, mo, d))
    assert span(text).width == timedelta(days=1)


# genitive article + genitive ordinal: "της 5ης Μαρτίου 2019".
@pytest.mark.parametrize("text,y,mo,d", [
    ("της 5ης Μαρτίου 2019", 2019, 3, 5),
    ("της 21ης Ιουλίου 1969", 1969, 7, 21),
])
def test_genitive_ordinal_day(text, y, mo, d):
    assert start(text) == ad(datetime(y, mo, d))
    assert span(text).width == timedelta(days=1)


# the two digit-ordinal national holidays keep their exact civil date and
# stay a single day -- the fold must not disturb them.
@pytest.mark.parametrize("text,ymd", [
    ("25η μαρτίου 2019", (2019, 3, 25)),
    ("28η οκτωβρίου 2018", (2018, 10, 28)),
])
def test_holiday_digit_ordinals_unchanged(text, ymd):
    assert start(text) == ad(datetime(*ymd))
    assert span(text).width == timedelta(days=1)
