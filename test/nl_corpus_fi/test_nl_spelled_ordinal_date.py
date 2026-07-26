"""Finnish spelled-ordinal day-of-month ("viidestoista huhtikuuta" = the
fifteenth of April).  The single-token ordinal (which the cardinal back-end
does not read in date position) must fold to the exact day, not strand and
leave the whole month.  Spread across the teens and the compound tens, where
the bugs hide.  Days 1..30 on April (30-day), 31 on a 31-day month.
"""
from datetime import datetime

import pytest

from ._corpus import ad, start


@pytest.mark.parametrize("ordinal,d", [
    ("ensimmäinen", 1),
    ("viides", 5),
    ("yhdestoista", 11),
    ("viidestoista", 15),
    ("kahdeskymmenesensimmäinen", 21),
    ("kahdeskymmeneskolmas", 23),
    ("kolmaskymmenes", 30),
])
def test_spelled_ordinal_of_april(ordinal, d):
    assert start(f"{ordinal} huhtikuuta") == ad(datetime(2018, 4, d))


def test_spelled_thirty_first_of_march():
    assert start("kolmaskymmenesensimmäinen maaliskuuta") == ad(
        datetime(2018, 3, 31))
