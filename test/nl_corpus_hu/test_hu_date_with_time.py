"""A full Hungarian written date carrying a daypart clock time
("2019. március 5. délután 3 órakor").  The date fixes the calendar day and
the "délután/délelőtt/este N órakor" tail fixes the minute; the result is a
one-minute point on that exact day.  Both the day and the resolved hour are
computed here independently, never read back from the parser.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ad, start_end

MONTHS = [
    "január", "február", "március", "április", "május", "június",
    "július", "augusztus", "szeptember", "október", "november", "december",
]

# (year, month, day, daypart, N, resolved-hour)
_CASES = [
    (2019, 3, 5, "délután", 3, 15),
    (2020, 6, 5, "délelőtt", 10, 10),
    (2021, 12, 24, "este", 8, 20),
    (2018, 1, 1, "délután", 6, 18),
    (2022, 8, 20, "délelőtt", 9, 9),
    (2000, 2, 29, "délután", 2, 14),
    (1999, 11, 30, "este", 11, 23),
    (2025, 5, 1, "délután", 5, 17),
    (2017, 7, 4, "délelőtt", 11, 11),
    (2024, 10, 23, "délután", 1, 13),
]


@pytest.mark.parametrize("y,mo,d,part,n,h", _CASES)
def test_full_date_with_daypart_clock(y, mo, d, part, n, h):
    text = f"{y}. {MONTHS[mo - 1]} {d}. {part} {n} órakor"
    p = datetime(y, mo, d, h, 0)
    assert start_end(text) == (ad(p), ad(p + timedelta(minutes=1)))
