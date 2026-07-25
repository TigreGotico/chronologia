"""Anchored arithmetic (feature 1) and the "prima" homograph, Italian.

Italian "prima" is at once the directional marker "before" and the feminine
ordinal "first"; the two readings are told apart by position.

* offset frame -- "N giorni prima/dopo <una data risolta>": a signed unit
  offset applied to an already-resolved calendar date, tolerating the
  article/"di" gap.  "prima" here is *before* and must survive the number
  fold intact.
* ordinal frame -- "(la) prima settimana di <mese>": "prima" here is the
  ordinal *first* and must fold to 1 so the nth-week-of-month construction
  binds it.

Anchor 2017-06-27; 5 aprile resolves forward to 2018-04-05.
"""
from datetime import date

import pytest

from ._corpus import AstroDate, parse, start


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


@pytest.mark.parametrize("text,expected", [
    ("3 giorni prima del 5 aprile", date(2018, 4, 2)),
    ("tre giorni prima del 5 aprile", date(2018, 4, 2)),
    ("3 giorni dopo il 5 aprile", date(2018, 4, 8)),
    ("una settimana prima del 5 aprile", date(2018, 3, 29)),
    ("2 settimane dopo il 5 aprile", date(2018, 4, 19)),
])
def test_offset_before_marker(text, expected):
    assert start(text) == _ad(expected)
    assert parse(text).remainder == ""


@pytest.mark.parametrize("text,expected", [
    ("la prima settimana di aprile", date(2017, 4, 3)),
    ("la prima settimana di marzo", date(2017, 3, 6)),
    ("prima settimana di gennaio", date(2017, 1, 2)),
])
def test_ordinal_first(text, expected):
    assert start(text) == _ad(expected)
    assert parse(text).remainder == ""
