# -*- coding: utf-8 -*-
"""R171 (en) -- "until before <event>" on a recurrence tail produced a
self-defeating zero-length rule: UNTIL was grounded to the ANCHOR instead of
the event, because :func:`~chronologia.extract.nseries._apply_bounds`'s
``until_words`` marker ("until") consumed only itself and handed the
UNGROUNDED tail "before christmas" straight to ``extract_timespan`` --
which reads a bare "before <holiday>" as an OPEN range (anchor -> holiday,
PR #707's bare-timespan semantics) and the grounder took the range's
``.start`` (the anchor), not its ``.end`` (the holiday).

DECIDED SEMANTICS: "until before <event>" binds UNTIL identically to
"before <event>" and "until <event>" (test_nl_r150_recur_before_binds_until.py)
-- the "before" after "until" is redundant emphasis, not a second bound.  The
fix strips a leading ``ctx.before_words`` token from the "until" marker's
payload before grounding, so the payload matches the bare-holiday form the
``before_words`` marker path itself already grounds correctly.
"""
from datetime import datetime

import pytest

from chronologia.extract import extract_recurrence

LANG = "en"
ANCHOR = datetime(2026, 8, 14, 10, 0)

_CASES = [
    # -- the defect: "until before X" must NOT ground UNTIL to the anchor --
    ("every day until before christmas",
     "FREQ=DAILY;UNTIL=20261225T000000", ""),
    ("every day until before easter",
     "FREQ=DAILY;UNTIL=20270328T000000", ""),
    ("every day until before halloween",
     "FREQ=DAILY;UNTIL=20261031T000000", ""),
    # -- controls: the two single-connector readings must be unchanged -----
    ("every day before christmas", "FREQ=DAILY;UNTIL=20261225T000000", ""),
    ("every day until christmas", "FREQ=DAILY;UNTIL=20261225T000000", ""),
    # -- weekday rule, same connector stack -------------------------------
    ("every monday until before christmas",
     "FREQ=WEEKLY;UNTIL=20261225T000000;BYDAY=MO", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_until_before_grounds_the_event_not_the_anchor(text, rrule, remainder):
    got = extract_recurrence(text, LANG, anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


def test_until_before_and_bare_before_ground_the_same_value():
    until_before = extract_recurrence(
        "every day until before christmas", LANG, anchor=ANCHOR)
    before = extract_recurrence(
        "every day before christmas", LANG, anchor=ANCHOR)
    assert until_before[0].until == before[0].until
    assert until_before[0].until != ANCHOR
