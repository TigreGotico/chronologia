# -*- coding: utf-8 -*-
"""R150 (pt) -- "antes do/da <event>" ("before <event>") on a recurrence
tail must bind ``UNTIL`` exactly the way "até <event>" ("until <event>")
already does. See test_nl_r150_recur_before_binds_until.py (en) for the full
root-cause writeup; this pins the same fix for Portuguese's "antes"/"até"
connectors, attested via the existing "antes do natal" bare-timespan corpus
(test_nl_anchored_offset.py, test_pt_r146_before_after_holiday.py).

"pascoa" (easter) is recognised both accented ("páscoa") and unaccented
("pascoa") in this locale's holiday vocabulary; see
test_nl_r171_movable_feast_unaccented.py for the unaccented-alias coverage.
"""
from datetime import datetime

import pytest

from chronologia.extract import extract_recurrence

LANG = "pt"
ANCHOR = datetime(2026, 8, 13, 10, 0)

_CASES = [
    ("toda segunda até o natal",
     "FREQ=WEEKLY;UNTIL=20261225T000000;BYDAY=MO", ""),
    ("toda segunda antes do natal",
     "FREQ=WEEKLY;UNTIL=20261225T000000;BYDAY=MO", ""),
    ("toda segunda até a páscoa",
     "FREQ=WEEKLY;UNTIL=20270328T000000;BYDAY=MO", ""),
    ("toda segunda antes da páscoa",
     "FREQ=WEEKLY;UNTIL=20270328T000000;BYDAY=MO", ""),
    ("toda segunda", "FREQ=WEEKLY;BYDAY=MO", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_antes_binds_until(text, rrule, remainder):
    got = extract_recurrence(text, LANG, anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder
