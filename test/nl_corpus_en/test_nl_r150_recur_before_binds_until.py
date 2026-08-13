# -*- coding: utf-8 -*-
"""R150 (en) -- a "before <event>" tail on a recurrence rule stranded the
whole clause instead of binding it as ``UNTIL``.

Before the fix, "every monday before christmas" resolved to
``FREQ=WEEKLY;BYDAY=MO`` with "before christmas" left verbatim in the
remainder -- :func:`~chronologia.extract.nseries._apply_bounds` only scanned
``ctx.until_words`` ("until"/"till") for a trailing bound, never the
locale's "before" connector.

DECIDED SEMANTICS: "before <event>" in a recurrence tail binds ``UNTIL``
exactly the way "until <event>" already does -- both ground off the SAME
:func:`extract_timespan` call on the payload text (christmas's ``.start``),
so "every monday until christmas" and "every monday before christmas"
produce the byte-identical ``UNTIL``. This mirrors the bare-timespan side
(PR #707), where a bare "before <holiday>" is also an open range ending at
the holiday.

Movable feasts ("easter") ground through the exact same
:func:`extract_timespan` call the "until" path already used, so no special
casing was needed for them.

NOTE: this is the RECURRENCE extractor (``extract_recurrence``), a DIFFERENT
code path from the bare-timespan extractor (``extract_timespan``) pinned by
test_nl_r146_before_after_holiday.py's ``test_recurrence_before_holiday_unaffected``
-- that test exercises "every monday before christmas" through
``extract_timespan``, where "every" is an out-of-scope stranded word and the
holiday-relative weekday resolves to a single date. The two extractors are
independent and this fix touches only the recurrence one.
"""
from datetime import datetime

import pytest
from dateutil.rrule import rrulestr

from chronologia.extract import extract_recurrence

LANG = "en"
ANCHOR = datetime(2026, 8, 13, 10, 0)

_CASES = [
    # -- control: "until" already grounds UNTIL correctly ------------------
    ("every monday until christmas",
     "FREQ=WEEKLY;UNTIL=20261225T000000;BYDAY=MO", ""),
    # -- the defect: "before" must bind the IDENTICAL UNTIL -----------------
    ("every monday before christmas",
     "FREQ=WEEKLY;UNTIL=20261225T000000;BYDAY=MO", ""),
    # -- movable feast: UNTIL grounds to the NEXT easter relative to anchor -
    ("every monday before easter",
     "FREQ=WEEKLY;UNTIL=20270328T000000;BYDAY=MO", ""),
    ("every monday until easter",
     "FREQ=WEEKLY;UNTIL=20270328T000000;BYDAY=MO", ""),
    # -- control: bare "every monday", no bound, must not regress -----------
    ("every monday", "FREQ=WEEKLY;BYDAY=MO", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_before_binds_until(text, rrule, remainder):
    got = extract_recurrence(text, LANG, anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


def test_before_and_until_ground_the_same_value():
    before = extract_recurrence("every monday before christmas", LANG, anchor=ANCHOR)
    until = extract_recurrence("every monday until christmas", LANG, anchor=ANCHOR)
    assert before[0].until == until[0].until


def test_before_until_rrule_expands_to_last_monday_on_or_before_christmas():
    # Christmas 2026-12-25 is a Friday; UNTIL=20261225T000000 (midnight)
    # excludes any same-day 00:00 occurrence, so the last generated Monday is
    # the one strictly before it -- 2026-12-21. Independently verified by
    # dateutil's own rrule engine (not read back from this parser).
    r = rrulestr("FREQ=WEEKLY;UNTIL=20261225T000000;BYDAY=MO",
                 dtstart=datetime(2026, 8, 10))
    occ = list(r)
    assert occ[-1] == datetime(2026, 12, 21)
    assert all(o.weekday() == 0 for o in occ)
    assert all(o < datetime(2026, 12, 25) for o in occ)
