# -*- coding: utf-8 -*-
"""A bare full weekday name resolves to its next strictly-future occurrence.

Only the unambiguous definite forms (الجمعة, السبت, الأحد ...) bind bare; the
article-less number homographs (أحد "someone", اثنين "two") stay out of the
bare order and need a relative marker.  A day-wide span, expected values from
independent arithmetic against this corpus's anchor."""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, parse, span


CASES = [
    ('الإثنين', 0),
    ('الخميس', 3),
    ('الجمعة', 4),
    ('السبت', 5),
    ('الأحد', 6),
]


@pytest.mark.parametrize("text,idx", CASES)
def test_bare_full_weekday(text, idx):
    ahead = (idx - ANCHOR.weekday()) % 7 or 7
    s = (ANCHOR + timedelta(days=ahead)).date()
    e = s + timedelta(days=1)
    sp = span(text)
    assert (sp.start.year, sp.start.month, sp.start.day) == (s.year, s.month, s.day)
    assert (sp.end.year, sp.end.month, sp.end.day) == (e.year, e.month, e.day)


YAWM_CASES = [
    ('يوم الإثنين', 0),
    ('يوم الثلاثاء', 1),
    ('يوم الأربعاء', 2),
    ('يوم الخميس', 3),
    ('يوم الجمعة', 4),
    ('يوم السبت', 5),
    ('يوم الأحد', 6),
]


@pytest.mark.parametrize("text,idx", YAWM_CASES)
def test_yawm_compound_consumes_fully(text, idx):
    """The 'يوم + weekday' compound folds to one token: the day-word is part
    of the reference, so the remainder must be empty."""
    ahead = (idx - ANCHOR.weekday()) % 7 or 7
    s = (ANCHOR + timedelta(days=ahead)).date()
    sp, remainder = parse(text)
    assert remainder == ''
    assert (sp.start.year, sp.start.month, sp.start.day) == (s.year, s.month, s.day)
