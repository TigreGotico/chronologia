# -*- coding: utf-8 -*-
"""The clock frame "a las <hour>" combines two separate marker_at.voc
tokens: the bare preposition "a" and the agreeing article "las", which
``clock_time``'s bare-HOUR order treats as an alternative at-marker on
its own.  With only a single ``at`` slot, the match starts at the
article and strands the leading "a" as remainder.

Anchor is the shared an corpus anchor, 2018-06-05 13:04 (Tuesday).
"""
from ._corpus import parse


def test_a_las_consumed():
    r = parse("a las 3")
    assert r is not None
    s, remainder = r
    assert (s.start.year, s.start.month, s.start.day) == (2018, 6, 6)
    assert (s.start.hour, s.start.minute) == (3, 0)
    assert remainder == ""


def test_bare_article_form_still_works():
    r = parse("las 3")
    assert r is not None
    s, remainder = r
    assert (s.start.hour, s.start.minute) == (3, 0)
    assert remainder == ""
