"""Polish numbers read through numtag.

numtag reads the numbers of every case form: the counts, the spelled years,
the day ordinals ("dwudziestego trzeciego") and the clock hours.  Every
expected value is written by hand or computed with ``timedelta`` from the
anchor; a lone clock hour takes the next twelve-hour reading after the
anchor.
"""
from datetime import datetime, timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, parse, start


@pytest.mark.parametrize("text,expected", [
    ("tysiąc dwieście dni temu", ANCHOR - timedelta(days=1200)),
    ("za tysiąc dni", ANCHOR + timedelta(days=1000)),
    ("rok dwa tysiące dwudziesty piąty", datetime(2025, 1, 1)),
    ("dwudziestego trzeciego maja 2025", datetime(2025, 5, 23)),
    ("wpół do ósmej", datetime(2017, 6, 27, 19, 30)),
    ("kwadrans po dziewiątej", datetime(2017, 6, 27, 21, 15)),
])
def test_numbers_read_through_numtag(text, expected):
    assert start(text) == ad(expected)


# numtag reads no number in the ordinal 90, so the year reads 1900.
@pytest.mark.xfail(strict=True, reason="https://github.com/TigreGotico/numtag/issues/162")
def test_known_numtag_gap():
    assert start("rok tysiąc dziewięćset dziewięćdziesiąty pierwszy") == ad(
        datetime(1991, 1, 1))


# The year of a spelled date is an ordinal that holds a scale word; the
# date keeps the year it names, whatever the anchor.
@pytest.mark.parametrize("anchor", [
    datetime(2026, 1, 10, 8, 0),
    datetime(2026, 12, 1, 8, 0),
    datetime(2028, 3, 1, 8, 0),
])
@pytest.mark.parametrize("text,month,day", [
    ("pierwszego maja dwa tysiące dwudziestego szóstego roku", 5, 1),
])
def test_spelled_date_with_a_year_from_2000(text, month, day, anchor):
    result = parse(text, anchor)
    assert result is not None
    assert result.span.start == ad(datetime(2026, month, day))


@pytest.mark.parametrize("text,expected", [
    ("za pół godziny", ANCHOR + timedelta(minutes=30)),
    ("pół godziny temu", ANCHOR - timedelta(minutes=30)),
    ("za pół roku", ANCHOR + relativedelta(months=6)),
    ("pół roku temu", ANCHOR - relativedelta(months=6)),
])
def test_half_of_a_unit_offset(text, expected):
    assert start(text) == ad(expected)
