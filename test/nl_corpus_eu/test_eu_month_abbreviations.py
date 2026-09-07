"""Basque abbreviated month names (CLDR 47 ``months.format.abbreviated``).

Basque could not read an abbreviated month at all before this file's
companion fix to ``locale/eu/month_*.voc`` -- ``extract_timespan("11 urt",
"eu", anchor=...)`` returned ``None`` for all twelve abbreviations.  CLDR
ships the abbreviated surface with a trailing dot ("urt."); the tokenizer
strips a trailing dot before vocabulary matching, so both the dotted and
bare spelling must resolve identically.  Expected dates are computed by
hand, independent of the parser.
"""
from datetime import datetime

import pytest

from ._corpus import ad, parse, start


ANCHOR = datetime(2017, 6, 27, 13, 4)

# day-of-month + abbreviated month, no year -> rolls to the next occurrence
# after the anchor (2017-06-27), same "prefer_future" rule as the full names.
@pytest.mark.parametrize("text,y,mo,d", [
    ("11 urt", 2018, 1, 11),
    ("11 urt.", 2018, 1, 11),
    ("11 ots", 2018, 2, 11),
    ("11 mar", 2018, 3, 11),
    ("11 api", 2018, 4, 11),
    ("11 mai", 2018, 5, 11),
    ("11 eka", 2018, 6, 11),
    ("11 uzt", 2017, 7, 11),
    ("11 abu", 2017, 8, 11),
    ("11 ira", 2017, 9, 11),
    ("11 urr", 2017, 10, 11),
    ("11 aza", 2017, 11, 11),
    ("11 abe", 2017, 12, 11),
])
def test_bare_month_day_abbreviated(text, y, mo, d):
    assert start(text) == ad(datetime(y, mo, d))


@pytest.mark.parametrize("text", [
    "11 urt", "11 urt.", "11 abe", "11 abe.",
])
def test_abbreviated_month_leaves_no_remainder(text):
    assert parse(text).remainder == ""


def test_full_month_name_unaffected_by_abbreviation():
    # "abendua" (December, full) must not be shadowed by the new "abe".
    assert start("2020ko abenduaren 25ean") == ad(datetime(2020, 12, 25))
    assert start("2020ko martxoaren 1ean") == ad(datetime(2020, 3, 1))
