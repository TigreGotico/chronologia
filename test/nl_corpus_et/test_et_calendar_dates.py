"""Estonian calendar dates in DMY order with the genitive month
("5. juuni 2020") and the ordinal dot on the day, plus the adessive/inessive
month forms used for whole-month references.  A bare day+month with no year
rolls to the next occurrence (prefer_future).
"""
from datetime import datetime

import pytest

from ._corpus import ad, start, start_end


@pytest.mark.parametrize("text,y,mo,d", [
    ("5. juuni 2020", 2020, 6, 5),
    ("15. märtsi 1999", 1999, 3, 15),
    ("1. jaanuari 2000", 2000, 1, 1),
    ("25. detsembri 2021", 2021, 12, 25),
    ("14. juuli 1789", 1789, 7, 14),
    ("9. mai 1945", 1945, 5, 9),
    ("20. juuli 1969", 1969, 7, 20),
    ("24. veebruari 1918", 1918, 2, 24),
    ("11. septembri 2001", 2001, 9, 11),
    ("30. novembri 2016", 2016, 11, 30),
])
def test_full_date(text, y, mo, d):
    assert start(text) == ad(datetime(y, mo, d))


def test_full_date_span_is_one_day():
    s, e = start_end("5. juuni 2020")
    assert s == ad(datetime(2020, 6, 5))
    assert e == ad(datetime(2020, 6, 6))


@pytest.mark.parametrize("text,y,mo,d", [
    ("5. juuni", 2018, 6, 5),
    ("15. märtsi", 2018, 3, 15),
    ("1. jaanuari", 2018, 1, 1),
    ("25. detsembri", 2017, 12, 25),
    ("28. juuli", 2017, 7, 28),
])
def test_bare_day_month_rolls_future(text, y, mo, d):
    assert start(text) == ad(datetime(y, mo, d))
