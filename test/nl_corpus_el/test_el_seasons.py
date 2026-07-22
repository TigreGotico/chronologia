"""Greek seasons, with and without a year, and the meteorological-quarter
span convention (summer = Jun-Aug on the northern hemisphere).
"""
from datetime import datetime

import pytest

from ._corpus import ad, start_end


@pytest.mark.parametrize("text,y,smo,emo", [
    ("καλοκαίρι 2020", 2020, 6, 9),
    ("άνοιξη 2021", 2021, 3, 6),
    ("χειμώνας 2020", 2020, 12, 3),
    ("φθινόπωρο 2019", 2019, 9, 12),
])
def test_season_year(text, y, smo, emo):
    s, e = start_end(text)
    assert (s.year, s.month, s.day) == (y, smo, 1)
    ey = y + 1 if emo < smo else y
    assert (e.year, e.month, e.day) == (ey, emo, 1)


def test_season_winter_wraps_year():
    s, e = start_end("χειμώνας 2020")
    assert s == ad(datetime(2020, 12, 1))
    assert e == ad(datetime(2021, 3, 1))
