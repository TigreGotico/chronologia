"""The "at" preposition ("v", marker_at.voc) in front of a bare weekday.

"v nedeljo" names the same Sunday as the bare weekday alone; "v" is not
part of the answer and must be consumed by the match, not left stranded
in the remainder.
"""
from datetime import timedelta

from ._corpus import ANCHOR, parse, span


def test_bare_nedeljo_is_sunday_sl():
    s = span("nedeljo")
    assert (s.end - s.start) == timedelta(days=1)
    assert s.start.date().weekday() == 6


def test_v_nedeljo_consumes_the_preposition_sl():
    r = parse("v nedeljo")
    assert r is not None
    assert r[0].start.date().weekday() == 6
    assert r[0] == span("nedeljo", ANCHOR)
    assert r[1] == ""
