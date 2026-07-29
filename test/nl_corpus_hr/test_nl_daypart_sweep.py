# -*- coding: utf-8 -*-
"""Dayparts and clock-with-daypart (hr).

Canonical daypart windows (anchor-relative): ujutro 04:00-12:00, popodne
12:00-18:00, navečer 18:00-21:00, noću 21:00-04:00(+1).  A daypart word may be
prefixed by a deictic day (sutra/jučer/danas) to shift the whole window.  A
clock hour disambiguated by a daypart word ("u 9 navečer" -> 21:00, "u 3
popodne" -> 15:00) yields a minute-wide span.

Gold windows are the fixed daypart definitions, not the parser.  Anchor
2017-06-27 13:04 (Tuesday).
"""
import pytest

from ._corpus import AstroDate, start_end

# bare + deictic dayparts: (phrase, start, end)
_WINDOWS = [
    ("ujutro", AstroDate(2017, 6, 27, 4, 0), AstroDate(2017, 6, 27, 12, 0)),
    ("popodne", AstroDate(2017, 6, 27, 12, 0), AstroDate(2017, 6, 27, 18, 0)),
    ("navečer", AstroDate(2017, 6, 27, 18, 0), AstroDate(2017, 6, 27, 21, 0)),
    ("noću", AstroDate(2017, 6, 27, 21, 0), AstroDate(2017, 6, 28, 4, 0)),
    ("danas popodne", AstroDate(2017, 6, 27, 12, 0), AstroDate(2017, 6, 27, 18, 0)),
    ("sutra ujutro", AstroDate(2017, 6, 28, 4, 0), AstroDate(2017, 6, 28, 12, 0)),
    ("sutra popodne", AstroDate(2017, 6, 28, 12, 0), AstroDate(2017, 6, 28, 18, 0)),
    ("sutra navečer", AstroDate(2017, 6, 28, 18, 0), AstroDate(2017, 6, 28, 21, 0)),
    ("jučer ujutro", AstroDate(2017, 6, 26, 4, 0), AstroDate(2017, 6, 26, 12, 0)),
    ("jučer navečer", AstroDate(2017, 6, 26, 18, 0), AstroDate(2017, 6, 26, 21, 0)),
]


@pytest.mark.parametrize("phrase,s,e", _WINDOWS, ids=[c[0] for c in _WINDOWS])
def test_daypart_window(phrase, s, e):
    assert start_end(phrase) == (s, e), phrase


# clock hour, minute-wide, disambiguated future-preferring: (phrase, start)
_CLOCK = [
    ("u 15 sati", AstroDate(2017, 6, 27, 15, 0)),
    ("u 9 sati", AstroDate(2017, 6, 28, 9, 0)),
    ("u 9 ujutro", AstroDate(2017, 6, 28, 9, 0)),
    ("u 9 navečer", AstroDate(2017, 6, 27, 21, 0)),
    ("u 3 popodne", AstroDate(2017, 6, 27, 15, 0)),
    ("u 15:30", AstroDate(2017, 6, 27, 15, 30)),
    ("u podne", AstroDate(2017, 6, 28, 12, 0)),
]


@pytest.mark.parametrize("phrase,s", _CLOCK, ids=[c[0] for c in _CLOCK])
def test_clock_daypart(phrase, s):
    st, en = start_end(phrase)
    assert st == s, phrase
    assert (en - st).total_seconds() == 60, phrase
