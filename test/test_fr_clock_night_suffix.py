# -*- coding: utf-8 -*-
"""fr "de la nuit" after an hour is the night band that crosses midnight.

"deux heures et demie de la nuit" read nothing, while "deux heures et demie du
matin" read 02:30.  "nuit" is a clock suffix of a night hour: "À deux heures
de nuit" (CNRTL, "nuit").  Small hours 1 to 5 are AM, hours 6 to 11 are PM, and
a night word never moves an hour from 13 to 17 (ruling 20).

Anchor: Friday 2026-01-30 10:00.  The next 02:30 is 2026-01-31; the next 23:30
is the same day; 03:00 and 02:15 follow the same arithmetic.  The night
reading of a word with no hour ("cette nuit") is not changed.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2026, 1, 30, 10)

CLOCKS = [
    ("deux heures et demie de la nuit", datetime(2026, 1, 31, 2, 30)),
    ("deux heures de la nuit", datetime(2026, 1, 31, 2)),
    ("trois heures de la nuit", datetime(2026, 1, 31, 3)),
    ("deux heures et quart de la nuit", datetime(2026, 1, 31, 2, 15)),
    ("2 heures et demie de la nuit", datetime(2026, 1, 31, 2, 30)),
    ("onze heures et demie de la nuit", datetime(2026, 1, 30, 23, 30)),
    ("à trois heures de nuit", datetime(2026, 1, 31, 3)),
    ("deux heures et demie du matin", datetime(2026, 1, 31, 2, 30)),
]


@pytest.mark.parametrize("text,instant", CLOCKS)
def test_night_suffix_reads_a_clock(text, instant):
    found = extract_timespan(text, "fr", ANCHOR)
    assert found is not None
    assert found.span.start.datetime() == instant
    assert found.remainder == ""
