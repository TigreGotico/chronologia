"""The "at" preposition ("в", marker_at.voc) in front of a bare weekday.

"в неделя" names the same Sunday as the bare weekday alone; "в" is not
part of the answer and must be consumed by the match, not left stranded
in the remainder.
"""
from datetime import timedelta

from ._corpus import ANCHOR, parse, span


def test_bare_nedelya_is_sunday_bg():
    s = span("неделя")
    assert (s.end - s.start) == timedelta(days=1)
    assert s.start.date().weekday() == 6


def test_v_nedelya_consumes_the_preposition_bg():
    r = parse("в неделя")
    assert r is not None
    assert r[0].start.date().weekday() == 6
    assert r[0] == span("неделя", ANCHOR)
    assert r[1] == ""
