# -*- coding: utf-8 -*-
"""A led clock range keeps its daypart when a clause follows it.

"from two to six this afternoon" names 14:00 to 18:00.  A clause after a
comma ("..., so plan your swim for later") is not part of the right
endpoint, so the left hour still borrows the afternoon, and the "from" lead
still makes a range, not the clock "two minutes to six".  A clock point end
is end-exclusive by one minute.  Anchor: Tuesday 27 June 2017, 13:04.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)
START = datetime(2017, 6, 27, 14, 0)
END = datetime(2017, 6, 27, 18, 1)

ROWS = [
    ("en", "The pool will be closed from two to six this afternoon, so plan "
           "your swim for later.", "The pool will be closed so plan your swim for later"),
    ("en", "from two to six this afternoon, so", "so"),
    ("en", "from two to six this afternoon, then dinner", "then dinner"),
    ("en", "from 2 to 6 this afternoon, so plan", "so plan"),
    ("en", "from two to six, in the afternoon", ""),
    ("es", "de 2 a 6 esta tarde, así que", "así que"),
    ("fr", "de deux à six cet après-midi, donc nage plus tard",
           "donc nage plus tard"),
]


@pytest.mark.parametrize("lang,text,remainder", ROWS)
def test_range_survives_clause(lang, text, remainder):
    r = extract_timespan(text, lang, ANCHOR)
    assert (r.span.start, r.span.end) == (START, END)
    assert r.remainder == remainder


MORNING = datetime(2017, 6, 27, 6, 0)

CLOCKS = [
    ("en", "five to nine", datetime(2017, 6, 27, 8, 55)),
    ("en", "at ten to six", datetime(2017, 6, 27, 17, 50)),
    ("en", "five to nine, so we go", datetime(2017, 6, 27, 8, 55)),
]


@pytest.mark.parametrize("lang,text,start", CLOCKS)
def test_unled_minutes_to_stays_a_clock(lang, text, start):
    r = extract_timespan(text, lang, MORNING)
    assert r.span.start == start
