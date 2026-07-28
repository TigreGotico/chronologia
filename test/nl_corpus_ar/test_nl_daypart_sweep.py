# -*- coding: utf-8 -*-
"""Oracle sweep: DAYPART + DEICTIC-DAY.  A daypart word (صباح/مساء/ظهر/ليلة)
composed with a deictic day (اليوم/الغد/أمس) anchors the CLDR band onto that
day.  Bands (native-confirmed, #268): morning 06-12, evening 18-21, noon a
one-minute point at 12:00, night 21-06 (spilling into the next civil day).
Gold by independent arithmetic against the Tue 2017-06-27 anchor."""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)

# deictic day word -> day offset from anchor date
DAYS = {"اليوم": 0, "الغد": 1, "أمس": -1}

# daypart word -> (start hour, end hour, end-day spill)
PARTS = {
    "صباح": (6, 12, 0),
    "مساء": (18, 21, 0),
    "ظهر": (12, 12, 0),   # noon point -> +1 minute below
    "ليلة": (21, 6, 1),
}

# already asserted verbatim in test_nl_daypart.py -- do not duplicate
_SKIP = {("صباح", "اليوم"), ("مساء", "أمس")}


def _cases():
    out = []
    for part, (h0, h1, spill) in PARTS.items():
        for day, off in DAYS.items():
            if (part, day) in _SKIP:
                continue
            base = (ANCHOR + timedelta(days=off)).replace(
                hour=0, minute=0, second=0, microsecond=0)
            start = base.replace(hour=h0)
            if part == "ظهر":
                end = start + timedelta(minutes=1)
            else:
                end = base.replace(hour=h1) + timedelta(days=spill)
            out.append((f"{part} {day}", start, end))
    return out


@pytest.mark.parametrize("text,start,end", _cases())
def test_daypart_deictic_sweep(text, start, end):
    r = extract_timespan(text, "ar", ANCHOR)
    assert r is not None and r[1] == "", f"{text!r} -> {r!r}"
    s = r[0]
    assert s.start_datetime == start
    assert s.end_datetime == end
