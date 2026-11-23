"""Greek numbers read through numtag.

A count and a year with "χίλια"/"χιλιάδες" (thousand) read whole.  "τρίτη"
is Tuesday and the third: before a weekday name it is the ordinal ("την
τρίτη Δευτέρα του Μαΐου", the third Monday of May), alone it is Tuesday.
Every expected value is computed with ``timedelta`` or ``datetime``.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, ad, start


@pytest.mark.parametrize("text,days", [
    ("σε χίλια μέρες", 1000),
    ("πριν δύο χιλιάδες είκοσι πέντε μέρες", -2025),
])
def test_count(text, days):
    assert start(text) == ad(ANCHOR + timedelta(days=days))


@pytest.mark.parametrize("text,year", [
    ("το έτος χίλια εννιακόσια ενενήντα εννέα", 1999),
    ("το έτος δύο χιλιάδες δεκαεννέα", 2019),
])
def test_spelled_year(text, year):
    assert start(text) == ad(datetime(year, 1, 1))


def nth_weekday(year, month, weekday, n):
    first = datetime(year, month, 1)
    return first + timedelta(days=(weekday - first.weekday()) % 7 + 7 * (n - 1))


@pytest.mark.parametrize("text,year,month,weekday,n", [
    ("την τρίτη Δευτέρα του Μαΐου 2025", 2025, 5, 0, 3),
    ("την πρώτη Κυριακή του Ιουλίου", 2017, 7, 6, 1),
])
def test_ordinal_weekday_of_month(text, year, month, weekday, n):
    assert start(text) == ad(nth_weekday(year, month, weekday, n))


def test_tuesday_stays_a_weekday():
    # the anchor is Tuesday 2017-06-27
    assert start("Τρίτη") == ad(datetime(2017, 6, 27))
