"""The "at" preposition ("v", marker_at.voc) in front of a bare weekday.

"v nedeľu" names the same Sunday as the bare weekday alone; "v" is not
part of the answer and must be consumed by the match, not left stranded
in the remainder.
"""
from datetime import timedelta

from ._corpus import ANCHOR, parse, span


def test_bare_nedelu_is_sunday_sk():
    s = span("nedeľu")
    assert (s.end - s.start) == timedelta(days=1)
    assert s.start.date().weekday() == 6


def test_v_nedelu_consumes_the_preposition_sk():
    r = parse("v nedeľu")
    assert r is not None
    assert r[0].start.date().weekday() == 6
    assert r[0] == span("nedeľu", ANCHOR)
    assert r[1] == ""
