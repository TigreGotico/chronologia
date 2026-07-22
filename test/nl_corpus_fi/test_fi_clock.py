"""Finnish clock times.  The spoken clock counts TOWARD the coming hour:
"puoli yhdeksän" is 8:30 (half before nine) -- the half-to family, handled
by bare_half_to.  Digit times, "kello H" whole hours and the
keskipäivä/keskiyö landmarks are also asserted.
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
    ("puoli yhdeksän", 8, 30),
    ("puoli kahdeksan", 7, 30),
    ("puoli kaksitoista", 11, 30),
    ("puoli kymmenen", 9, 30),
])
def test_half_toward_coming_hour(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text,h", [
    ("kello yhdeksän", 9),
    ("kello kymmenen", 10),
    ("kello kahdeksan", 8),
])
def test_whole_hour(text, h):
    assert start(text) == _next_time(h, 0)


@pytest.mark.parametrize("text,h,mi", [
    ("15:30", 15, 30),
    ("09:15", 9, 15),
    ("23:45", 23, 45),
    ("00:00", 0, 0),
])
def test_digit_clock(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text,h,mi", [
    ("keskipäivä", 12, 0),
    ("keskiyö", 0, 0),
])
def test_landmarks(text, h, mi):
    assert start(text) == _next_time(h, mi)
