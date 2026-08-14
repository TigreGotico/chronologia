"""R168 (sl): a digit clock followed by the spoken hour noun ("ob 9 uri")
must consume that noun into the CLOCK construction, not strand it in the
remainder.  Slovenian names the hour after "ob" in the locative singular
("uri").
"""
from datetime import timedelta

from ._corpus import ANCHOR, ad, parse


def test_digit_clock_consumes_hour_word():
    r = parse("ob 9 uri")
    assert r is not None
    assert r.span.start == ad(ANCHOR.replace(day=28, hour=9, minute=0,
                                             second=0, microsecond=0))
    assert r.span.width == timedelta(minutes=1)
    assert r.remainder == ""
