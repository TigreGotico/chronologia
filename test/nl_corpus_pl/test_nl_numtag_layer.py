"""Polish numbers read through numtag.

numtag reads the numbers of every case form: the counts, the spelled years,
the day ordinals ("dwudziestego trzeciego") and the clock hours.  Every
expected value is written by hand or computed with ``timedelta`` from the
anchor; a lone clock hour takes the next twelve-hour reading after the
anchor.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, ad, start


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
