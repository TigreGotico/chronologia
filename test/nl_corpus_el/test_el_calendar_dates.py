"""Greek calendar dates in their real DMY order, with the genitive month
("5 Ιουνίου" = the 5th of June) and the optional genitive article
("5 του Ιουνίου").  A day+month with no year rolls to the next occurrence
(prefer_future), so the oracle uses independent arithmetic off the anchor.
"""
from datetime import datetime

import pytest

from ._corpus import ad, start, start_end


# day-month-year: an explicit year pins the date outright.
@pytest.mark.parametrize("text,y,mo,d", [
    ("5 ιουνίου 2020", 2020, 6, 5),
    ("5 του ιουνίου 2020", 2020, 6, 5),
    ("15 μαρτίου 1999", 1999, 3, 15),
    ("1 ιανουαρίου 2000", 2000, 1, 1),
    ("25 δεκεμβρίου 2021", 2021, 12, 25),
    ("31 οκτωβρίου 1517", 1517, 10, 31),
    ("14 ιουλίου 1789", 1789, 7, 14),
    ("28 φεβρουαρίου 2019", 2019, 2, 28),
    ("9 μαΐου 1945", 1945, 5, 9),
    ("20 ιουλίου 1969", 1969, 7, 20),
    ("12 απριλίου 1961", 1961, 4, 12),
    ("8 αυγούστου 1974", 1974, 8, 8),
    ("11 σεπτεμβρίου 2001", 2001, 9, 11),
    ("30 νοεμβρίου 2016", 2016, 11, 30),
])
def test_full_date(text, y, mo, d):
    assert start(text) == ad(datetime(y, mo, d))


def test_full_date_span_is_one_day():
    s, e = start_end("5 ιουνίου 2020")
    assert s == ad(datetime(2020, 6, 5))
    assert e == ad(datetime(2020, 6, 6))


# bare day+month with no year: rolls to the next occurrence from the anchor
# (2017-06-27); June 5 has passed, so it lands in 2018, but January is ahead.
@pytest.mark.parametrize("text,y,mo,d", [
    ("5 ιουνίου", 2018, 6, 5),
    ("15 μαρτίου", 2018, 3, 15),
    ("1 ιανουαρίου", 2018, 1, 1),
    ("25 δεκεμβρίου", 2017, 12, 25),
    ("28 ιουλίου", 2017, 7, 28),
])
def test_bare_day_month_rolls_future(text, y, mo, d):
    assert start(text) == ad(datetime(y, mo, d))
