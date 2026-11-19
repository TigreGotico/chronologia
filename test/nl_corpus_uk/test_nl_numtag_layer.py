"""Ukrainian numbers read through numtag.

numtag reads the numbers of every case form: the counts, the spelled years,
the day ordinals ("двадцять третього") and the clock hours.  Every expected
value is written by hand or computed with ``timedelta`` from the anchor; a
lone clock hour takes the next twelve-hour reading after the anchor.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, ad, parse, start


@pytest.mark.parametrize("text,expected", [
    ("тисяча двісті днів тому", ANCHOR - timedelta(days=1200)),
    ("через тисячу днів", ANCHOR + timedelta(days=1000)),
    ("двадцять третього травня 2025", datetime(2025, 5, 23)),
    ("о п’ятій", datetime(2017, 6, 27, 17, 0)),
    ("пів на дев’яту", datetime(2017, 6, 27, 20, 30)),
])
def test_numbers_read_through_numtag(text, expected):
    assert start(text) == ad(expected)


# The year of a spelled date is an ordinal that holds a scale word; the
# date keeps the year it names, whatever the anchor.
@pytest.mark.parametrize("anchor", [
    datetime(2026, 1, 10, 8, 0),
    datetime(2026, 12, 1, 8, 0),
    datetime(2028, 3, 1, 8, 0),
])
@pytest.mark.parametrize("text,month,day", [
    ("першого травня дві тисячі двадцять шостого року", 5, 1),
])
def test_spelled_date_with_a_year_from_2000(text, month, day, anchor):
    result = parse(text, anchor)
    assert result is not None
    assert result.span.start == ad(datetime(2026, month, day))


# An ordinal hour after the clock preposition keeps its clock when a word
# outside the vocabulary follows; the clock reads the same without it.
@pytest.mark.parametrize("text,expected", [
    ("о сьомій подзвони мамі", datetime(2017, 6, 27, 19, 0)),
    ("нагадай мені о дев'ятій перевірити пошту", datetime(2017, 6, 27, 21, 0)),
    ("завтра о восьмій зустріч з лікарем", datetime(2017, 6, 28, 8, 0)),
    ("о пів на дев'яту перевірити пошту", datetime(2017, 6, 27, 20, 30)),
    ("п'ятого травня о дев'ятій зустріч", datetime(2018, 5, 5, 9, 0)),
    ("вранці о дев'ятій нагадуй мені перевірити пошту",
     datetime(2017, 6, 28, 9, 0)),
])
def test_ordinal_hour_before_another_word(text, expected):
    assert start(text) == ad(expected)


def test_ordinal_before_a_noun_is_no_clock():
    assert parse("на другому поверсі") is None
