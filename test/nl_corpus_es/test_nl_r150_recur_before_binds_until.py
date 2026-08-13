# -*- coding: utf-8 -*-
"""R150 (es) -- "antes de <event>" ("before <event>") on a recurrence tail
must bind ``UNTIL`` exactly the way "hasta <event>" ("until <event>")
already does. See test_nl_r150_recur_before_binds_until.py (en) for the full
root-cause writeup; this pins the same fix for Spanish's "antes"/"hasta"
connectors, attested via the existing "antes de navidad" bare-timespan
corpus (test_nl_anchored_offset.py, test_es_r146_before_after_holiday.py).
"""
from datetime import datetime

import pytest

from chronologia.extract import extract_recurrence

LANG = "es"
ANCHOR = datetime(2026, 8, 13, 10, 0)

_CASES = [
    ("cada lunes hasta navidad",
     "FREQ=WEEKLY;UNTIL=20261225T000000;BYDAY=MO", ""),
    ("cada lunes antes de navidad",
     "FREQ=WEEKLY;UNTIL=20261225T000000;BYDAY=MO", ""),
    ("cada lunes hasta pascua",
     "FREQ=WEEKLY;UNTIL=20270328T000000;BYDAY=MO", ""),
    ("cada lunes antes de pascua",
     "FREQ=WEEKLY;UNTIL=20270328T000000;BYDAY=MO", ""),
    ("cada lunes", "FREQ=WEEKLY;BYDAY=MO", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_antes_binds_until(text, rrule, remainder):
    got = extract_recurrence(text, LANG, anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder
