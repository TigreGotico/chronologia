"""Slovene clock times opened by "ob" and closed by "ponoči".

"ob" opens a clock time ("ob 17:30" = at 17:30) as it already does before a
spoken hour ("ob 9 uri"), so the preposition belongs to the time.

"ponoči" is "v času teme od sončnega zahoda do vzhoda" (SSKJ², s.v. ponoči,
with the example "ob dvanajstih ponoči"): the dark from sunset to sunrise
covers both the late evening and the small hours.  So a late hour is the
evening one, a small hour stays before dawn, and twelve is midnight.  At the
13:04 anchor, 23:00 is still today and every small hour is tomorrow.
"""
import pytest

from ._corpus import ANCHOR, ad, parse


def _at(day, hour, minute=0):
    return ad(ANCHOR.replace(day=day, hour=hour, minute=minute, second=0,
                             microsecond=0))


@pytest.mark.parametrize("text,remainder", [
    ("ob 17:30", ""),
    ("sestanek ob 17:30", "sestanek"),
])
def test_ob_before_digit_clock(text, remainder):
    r = parse(text)
    assert r is not None
    assert r.span.start == _at(27, 17, 30)
    assert r.remainder == remainder


@pytest.mark.parametrize("text,day,hour", [
    ("ob enih ponoči", 28, 1),
    ("ob dveh ponoči", 28, 2),
    ("ob 3 ponoči", 28, 3),
    ("ob dvanajstih ponoči", 28, 0),
    ("ob desetih ponoči", 27, 22),
    ("ob enajstih ponoči", 27, 23),
])
def test_ponoci_after_an_hour(text, day, hour):
    r = parse(text)
    assert r is not None
    assert r.span.start == _at(day, hour)
    assert r.remainder == ""
