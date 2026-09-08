"""The compound numerals 21, 31 ... 91 in Romanian.

Romanian builds them with the joiner "și": "douăzeci și unu" (masculine) and
"douăzeci și una" (feminine), the feminine agreeing with "zile" and with the
implied "ora".  Wiktionary: douăzeci și unu.  Anchor 2017-06-27 13:04;
expected dates computed by hand from the calendar, never read back from the
parser.
"""
from datetime import date

import pytest

from ._corpus import AstroDate, parse, start


def _ad(d):
    return AstroDate(d.year, d.month, d.day, 13, 4)


@pytest.mark.parametrize("text,expected", [
    # 27 June + 21 = 18 July (3 days left in June, 18 into July)
    ("peste douăzeci și una de zile", date(2017, 7, 18)),
    # + 31 = 28 July
    ("peste treizeci și una de zile", date(2017, 7, 28)),
    # + 41 = 7 August (3 in June, 31 in July, 7 into August)
    ("peste patruzeci și una de zile", date(2017, 8, 7)),
    # the control that already folded: "doi" is an ordinary number word
    ("peste douăzeci și doi de zile", date(2017, 7, 19)),
])
def test_counted_days(text, expected):
    assert start(text) == _ad(expected)
    assert parse(text).remainder == ""


@pytest.mark.parametrize("text", [
    "la ora douăzeci și una",
    "la ora douăzeci și unu",
])
def test_clock_hour(text):
    assert start(text) == AstroDate(2017, 6, 27, 21, 0)
    assert parse(text).remainder == ""
