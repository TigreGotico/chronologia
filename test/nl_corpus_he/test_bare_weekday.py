# -*- coding: utf-8 -*-
"""A bare full weekday name resolves to its next strictly-future occurrence.

Only the unambiguous "יום ..." forms and שבת bind bare; the single-word
ordinal homographs (ראשון "first", שני "second" ...) stay out of the bare
order and need a relative marker.  A day-wide span, expected values from
independent arithmetic against this corpus's anchor.  The compound "יום ראשון"
folds to one token through the multiword merge before it binds.  Monday
("יום שני") is omitted: the number parser folds שני to the digit 2 (a
homograph with the cardinal "two"), a pre-existing limitation."""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, parse, span


CASES = [
    ('יום ראשון', 6),
    ('יום שלישי', 1),
    ('יום שישי', 4),
    ('שבת', 5),
]


@pytest.mark.parametrize("text,idx", CASES)
def test_bare_full_weekday(text, idx):
    ahead = (idx - ANCHOR.weekday()) % 7 or 7
    s = (ANCHOR + timedelta(days=ahead)).date()
    e = s + timedelta(days=1)
    sp = span(text)
    assert (sp.start.year, sp.start.month, sp.start.day) == (s.year, s.month, s.day)
    assert (sp.end.year, sp.end.month, sp.end.day) == (e.year, e.month, e.day)


BE_CASES = [
    ('ביום שלישי', 1),
    ('ביום רביעי', 2),
    ('ביום חמישי', 3),
    ('ביום שישי', 4),
    ('בשבת', 5),
    ('ביום ראשון', 6),
]


@pytest.mark.parametrize("text,idx", BE_CASES)
def test_be_prefixed_weekday_consumes_fully(text, idx):
    """The preposition-fused 'on <weekday>' form (ב + יום/שבת) is one word in
    Hebrew orthography; it must bind whole with an empty remainder.  Monday
    ('ביום שני') is omitted for the same שני/2 homograph as above."""
    ahead = (idx - ANCHOR.weekday()) % 7 or 7
    s = (ANCHOR + timedelta(days=ahead)).date()
    sp, remainder = parse(text)
    assert remainder == ''
    assert (sp.start.year, sp.start.month, sp.start.day) == (s.year, s.month, s.day)
