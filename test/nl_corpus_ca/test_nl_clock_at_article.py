# -*- coding: utf-8 -*-
"""The word-hour clock frame "a les <hour>" combines two separate
marker_at tokens: the bare preposition "a" and the agreeing article
"les", which ``clock_time``'s bare-HOUR order treats as an alternative
at-marker on its own.  With only a single ``at`` slot, the match starts
at the article and strands the leading "a" as remainder.

Anchor is the shared ca corpus anchor, 2017-06-27 13:04 (Tuesday).
"""
from ._corpus import parse
from ._corpus import ANCHOR
from ruling17 import moved, moved_date


def test_a_les_consumed():
    r = parse("a les tres")
    assert r is not None
    s, remainder = r
    assert (s.start.year, s.start.month, s.start.day) == moved_date((2017, 6, 28), (3, 0), ANCHOR)
    assert (s.start.hour, s.start.minute) == moved((3, 0), ANCHOR)
    assert remainder == ""


def test_bare_article_form_still_works():
    r = parse("les tres")
    assert r is not None
    s, remainder = r
    assert (s.start.hour, s.start.minute) == moved((3, 0), ANCHOR)
    assert remainder == ""
