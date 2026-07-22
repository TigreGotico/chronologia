"""Greek clock times: the idiomatic "H και μισή"/"H και τέταρτο" (past) and
"H παρά τέταρτο" (to) built on the feminine clock-hour numerals that agree
with the elided ώρα ("τρεις", "τέσσερις", "μία"), plus digit times and the
μεσημέρι/μεσάνυχτα landmarks.  Unlike the Continental-Germanic half, Greek
"και μισή" is half PAST, so no bare_half_to trap applies.

A bare time earlier than the 13:04 anchor rolls to the next day
(prefer_future); the oracle uses independent arithmetic.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, ad, start


def _next_time(h, mi):
    cand = ANCHOR.replace(hour=h, minute=mi, second=0, microsecond=0)
    if cand <= ANCHOR:
        cand += timedelta(days=1)
    return ad(cand)


@pytest.mark.parametrize("text,h,mi", [
    ("τρεις και μισή", 3, 30),
    ("πέντε και μισή", 5, 30),
    ("οκτώ και μισή", 8, 30),
    ("δέκα και μισή", 10, 30),
    ("τρεις και τέταρτο", 3, 15),
    ("εννέα και τέταρτο", 9, 15),
    ("τρεις παρά τέταρτο", 2, 45),
    ("οκτώ παρά τέταρτο", 7, 45),
    ("μία και μισή", 1, 30),
    ("τέσσερις και τέταρτο", 4, 15),
])
def test_spoken_clock(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text,h,mi", [
    ("15:30", 15, 30),
    ("09:15", 9, 15),
    ("23:45", 23, 45),
    ("00:00", 0, 0),
    ("6:07", 6, 7),
])
def test_digit_clock(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text,h,mi", [
    ("μεσημέρι", 12, 0),
    ("μεσάνυχτα", 0, 0),
])
def test_landmarks(text, h, mi):
    assert start(text) == _next_time(h, mi)
