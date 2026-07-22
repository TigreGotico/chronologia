"""Basque clock times.  Unlike the Finnic/Hungarian half-toward-the-hour,
Basque "eta erdi" is half PAST ("bostak eta erdi" = 5:30) and "eta laurden"
is quarter past, built on the -ak hour numerals ("bostak" = five o'clock).
Digit times and the eguerdia/gauerdia landmarks are also asserted.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, start


def _next_time(h, mi):
    cand = ANCHOR.replace(hour=h, minute=mi, second=0, microsecond=0)
    if cand <= ANCHOR:
        cand += timedelta(days=1)
    return ad(cand)


@pytest.mark.parametrize("text,h,mi", [
    ("bostak eta erdi", 5, 30),
    ("hirurak eta erdi", 3, 30),
    ("laurak eta erdi", 4, 30),
    ("bostak eta laurden", 5, 15),
    ("laurak eta laurden", 4, 15),
    ("hamarrak eta erdi", 10, 30),
])
def test_spoken_clock_past(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text,h,mi", [
    ("15:30", 15, 30),
    ("09:15", 9, 15),
    ("23:45", 23, 45),
    ("00:00", 0, 0),
])
def test_digit_clock(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text,h,mi", [
    ("eguerdia", 12, 0),
    ("gauerdia", 0, 0),
])
def test_landmarks(text, h, mi):
    assert start(text) == _next_time(h, mi)
