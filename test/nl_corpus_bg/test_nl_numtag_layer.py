"""Bulgarian numbers read through numtag.

numtag reads the numbers of every case form: the counts, the spelled years,
the day ordinals ("двадесет и трети") and the clock hours.  Every expected
value is written by hand or computed with ``timedelta`` from the anchor; a
lone clock hour takes the next twelve-hour reading after the anchor.
"""
from datetime import datetime, timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ._corpus import ANCHOR, ad, parse, start


@pytest.mark.parametrize("text,expected", [
    ("след хиляда дни", ANCHOR + timedelta(days=1000)),
    ("преди хиляда и двеста дни", ANCHOR - timedelta(days=1200)),
    ("единадесети май 2025", datetime(2025, 5, 11)),
    ("двадесет и трети май 2025", datetime(2025, 5, 23)),
    ("в осем и половина", datetime(2017, 6, 27, 20, 30)),
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
    ("първи май две хиляди двадесет и шеста година", 5, 1),
])
def test_spelled_date_with_a_year_from_2000(text, month, day, anchor):
    result = parse(text, anchor)
    assert result.span.start == ad(datetime(2026, month, day))


@pytest.mark.parametrize("text,expected", [
    ("след половин час", ANCHOR + timedelta(minutes=30)),
    ("преди половин час", ANCHOR - timedelta(minutes=30)),
    ("след половин година", ANCHOR + relativedelta(months=6)),
])
def test_half_of_a_unit_offset(text, expected):
    assert start(text) == ad(expected)
