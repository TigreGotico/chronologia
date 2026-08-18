"""The "at" preposition ("у", marker_at.voc) in front of a bare weekday.

"у неділю" names the same Sunday as the bare weekday alone; "у" is not
part of the answer and must be consumed by the match, not left stranded
in the remainder.
"""
from datetime import timedelta

from ._corpus import ANCHOR, parse, span


def test_bare_nedilyu_is_sunday():
    s = span("неділю")
    assert (s.end - s.start) == timedelta(days=1)
    assert s.start.date().weekday() == 6


def test_u_nedilyu_consumes_the_preposition():
    r = parse("у неділю")
    assert r is not None
    assert r[0].start.date().weekday() == 6
    assert r[0] == span("неділю", ANCHOR)
    assert r[1] == ""
