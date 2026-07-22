"""Estonian clock times.  The spoken clock counts TOWARD the coming hour:
"pool üheksa" is 8:30 (half before nine) -- the half-to family, handled by
bare_half_to.  Digit times, "kell H" whole hours and the keskpäev/kesköö
landmarks are also asserted.

The quarter/three-quarter counting forms ("veerand üheksa" 8:15,
"kolmveerand üheksa" 8:45) are a KNOWN ENGINE GAP: bare_half_to takes only
the half, so those are xfailed rather than asserted wrongly.
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
    ("pool üheksa", 8, 30),
    ("pool kaheksa", 7, 30),
    ("pool kaksteist", 11, 30),
    ("pool kümme", 9, 30),
])
def test_half_toward_coming_hour(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.parametrize("text,h", [
    ("kell üheksa", 9),
    ("kell kümme", 10),
    ("kell kaheksa", 8),
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
    ("keskpäev", 12, 0),
    ("kesköö", 0, 0),
])
def test_landmarks(text, h, mi):
    assert start(text) == _next_time(h, mi)


@pytest.mark.xfail(reason="bare_half_to only resolves the half; veerand/"
                          "kolmveerand counting-toward is unsupported",
                   strict=True)
@pytest.mark.parametrize("text,h,mi", [
    ("veerand üheksa", 8, 15),
    ("kolmveerand üheksa", 8, 45),
])
def test_quarter_toward_hour_gap(text, h, mi):
    assert start(text) == _next_time(h, mi)
