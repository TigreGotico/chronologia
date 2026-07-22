"""Finnish calendar dates in DMY order with the partitive month
("5. kesäkuuta 2020" = the 5th of June) and the ordinal dot on the day.  A
bare day+month with no year rolls to the next occurrence (prefer_future).
"""
from datetime import datetime

import pytest

from ._corpus import ad, start, start_end


@pytest.mark.parametrize("text,y,mo,d", [
    ("5. kesäkuuta 2020", 2020, 6, 5),
    ("15. maaliskuuta 1999", 1999, 3, 15),
    ("1. tammikuuta 2000", 2000, 1, 1),
    ("25. joulukuuta 2021", 2021, 12, 25),
    ("14. heinäkuuta 1789", 1789, 7, 14),
    ("9. toukokuuta 1945", 1945, 5, 9),
    ("20. heinäkuuta 1969", 1969, 7, 20),
    ("6. joulukuuta 1917", 1917, 12, 6),
    ("11. syyskuuta 2001", 2001, 9, 11),
    ("30. marraskuuta 2016", 2016, 11, 30),
])
def test_full_date(text, y, mo, d):
    assert start(text) == ad(datetime(y, mo, d))


def test_full_date_span_is_one_day():
    s, e = start_end("5. kesäkuuta 2020")
    assert s == ad(datetime(2020, 6, 5))
    assert e == ad(datetime(2020, 6, 6))


@pytest.mark.parametrize("text,y,mo,d", [
    ("5. kesäkuuta", 2018, 6, 5),
    ("15. maaliskuuta", 2018, 3, 15),
    ("1. tammikuuta", 2018, 1, 1),
    ("25. joulukuuta", 2017, 12, 25),
    ("28. heinäkuuta", 2017, 7, 28),
])
def test_bare_day_month_rolls_future(text, y, mo, d):
    assert start(text) == ad(datetime(y, mo, d))
