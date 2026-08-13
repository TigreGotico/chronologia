# -*- coding: utf-8 -*-
"""R150 (de) -- "vor <event>" ("before <event>") on a recurrence tail must
bind ``UNTIL`` exactly the way "bis <event>" ("until <event>") already does.
See test_nl_r150_recur_before_binds_until.py (en) for the full root-cause
writeup; this pins the same fix for German's "vor"/"bis" connectors,
attested via the existing "vor weihnachten" bare-timespan corpus
(test_nl_anchored_offset.py, test_nl_r120_week_after_event.py).
"""
from datetime import datetime

import pytest

from chronologia.extract import extract_recurrence

LANG = "de"
ANCHOR = datetime(2026, 8, 13, 10, 0)

_CASES = [
    ("jeden montag bis weihnachten",
     "FREQ=WEEKLY;UNTIL=20261225T000000;BYDAY=MO", ""),
    ("jeden montag vor weihnachten",
     "FREQ=WEEKLY;UNTIL=20261225T000000;BYDAY=MO", ""),
    ("jeden montag bis ostern",
     "FREQ=WEEKLY;UNTIL=20270328T000000;BYDAY=MO", ""),
    ("jeden montag vor ostern",
     "FREQ=WEEKLY;UNTIL=20270328T000000;BYDAY=MO", ""),
    ("jeden montag", "FREQ=WEEKLY;BYDAY=MO", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_vor_binds_until(text, rrule, remainder):
    got = extract_recurrence(text, LANG, anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder
