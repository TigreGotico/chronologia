# -*- coding: utf-8 -*-
"""All seven Kabyle weekdays, bare -> next occurrence, or today.

Extends test_bare_weekday.py (which sampled two) to the full weekday_*.voc
table. When the anchor already is that weekday the span is the anchor day. Day-wide span; gold from independent arithmetic against
anchor Tue 2017-06-27.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, span

WD = {
    0: "letnayen", 1: "ttlata", 2: "laṛebɛa", 3: "lexmis",
    4: "lǧemɛa", 5: "ssebt", 6: "lḥedd",
}

_BASE = ANCHOR.replace(hour=0, minute=0, second=0, microsecond=0)


def _expected(idx):
    ahead = (idx - _BASE.weekday()) % 7
    s = _BASE + timedelta(days=ahead)
    e = s + timedelta(days=1)
    return (AstroDate(s.year, s.month, s.day),
            AstroDate(e.year, e.month, e.day))


@pytest.mark.parametrize("idx,text", list(WD.items()))
def test_bare_weekday_all(idx, text):
    sp = span(text)
    assert (sp.start, sp.end) == _expected(idx)
    assert sp.width == timedelta(days=1)
