"""Hungarian calendar dates in their real YEAR-MONTH-DAY order
("2020. június 5.") -- the year leads, marked with the ordinal dot -- plus
the bare month+day that rolls to the next occurrence (prefer_future) and the
inessive month form ("júniusban") used for a whole-month reference.
"""
from datetime import datetime

import pytest

from ._corpus import ad, start, start_end


@pytest.mark.parametrize("text,y,mo,d", [
    ("2020. június 5.", 2020, 6, 5),
    ("1999. március 15.", 1999, 3, 15),
    ("2000. január 1.", 2000, 1, 1),
    ("2021. december 25.", 2021, 12, 25),
    ("1789. július 14.", 1789, 7, 14),
    ("1945. május 9.", 1945, 5, 9),
    ("1969. július 20.", 1969, 7, 20),
    ("2001. szeptember 11.", 2001, 9, 11),
    ("1848. március 15.", 1848, 3, 15),
    ("2016. november 30.", 2016, 11, 30),
])
def test_year_first_date(text, y, mo, d):
    assert start(text) == ad(datetime(y, mo, d))


def test_full_date_span_is_one_day():
    s, e = start_end("2020. június 5.")
    assert s == ad(datetime(2020, 6, 5))
    assert e == ad(datetime(2020, 6, 6))


@pytest.mark.parametrize("text,y,mo,d", [
    ("június 5", 2018, 6, 5),
    ("március 15", 2018, 3, 15),
    ("január 1", 2018, 1, 1),
    ("december 25", 2017, 12, 25),
    ("július 28", 2017, 7, 28),
])
def test_bare_month_day_rolls_future(text, y, mo, d):
    assert start(text) == ad(datetime(y, mo, d))
