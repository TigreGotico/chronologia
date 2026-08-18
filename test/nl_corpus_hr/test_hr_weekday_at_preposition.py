"""The "at" preposition ("u", marker_at.voc) in front of a bare weekday.

"u nedjelju" names the same Sunday as the bare weekday alone; "u" is not
part of the answer and must be consumed by the match, not left stranded
in the remainder.
"""
from datetime import timedelta

from ._corpus import ANCHOR, parse, span


def test_bare_nedjelju_is_sunday():
    s = span("nedjelju")
    assert (s.end - s.start) == timedelta(days=1)
    assert s.start.date().weekday() == 6


def test_u_nedjelju_consumes_the_preposition():
    r = parse("u nedjelju")
    assert r is not None
    assert r[0].start.date().weekday() == 6
    assert r[0] == span("nedjelju", ANCHOR)
    assert r[1] == ""
