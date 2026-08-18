"""The "at" preposition ("w", marker_at.voc) in front of a bare weekday.

"w niedzielę" names the same Sunday as the bare weekday alone; "w" is not
part of the answer and must be consumed by the match, not left stranded
in the remainder.
"""
from datetime import timedelta

from ._corpus import ANCHOR, parse, span


def test_bare_niedziele_is_sunday():
    s = span("niedzielę")
    assert (s.end - s.start) == timedelta(days=1)
    assert s.start.date().weekday() == 6


def test_w_niedziele_consumes_the_preposition():
    r = parse("w niedzielę")
    assert r is not None
    assert r[0].start.date().weekday() == 6
    assert r[0] == span("niedzielę", ANCHOR)
    assert r[1] == ""
