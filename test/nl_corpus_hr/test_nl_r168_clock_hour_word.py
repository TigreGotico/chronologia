"""R168 (hr): a digit clock followed by the spoken hour noun ("u 9 sati")
must consume that noun into the CLOCK construction, not strand it in the
remainder -- including when a day-part meridiem ("popodne") follows and
composes the hour to its afternoon reading (9 -> 21:00).  Croatian names the
hour after "u" with the fixed count noun "sati", regardless of the numeral.
"""
from datetime import timedelta

from ._corpus import ANCHOR, ad, parse


def test_digit_clock_consumes_hour_word():
    r = parse("u 9 sati")
    assert r is not None
    assert r.span.start == ad(ANCHOR.replace(day=28, hour=9, minute=0,
                                             second=0, microsecond=0))
    assert r.span.width == timedelta(minutes=1)
    assert r.remainder == ""


def test_digit_clock_consumes_hour_word_then_daypart():
    r = parse("u 9 sati popodne")
    assert r is not None
    assert r.span.start == ad(ANCHOR.replace(hour=21, minute=0, second=0,
                                             microsecond=0))
    assert r.span.width == timedelta(minutes=1)
    assert r.remainder == ""
