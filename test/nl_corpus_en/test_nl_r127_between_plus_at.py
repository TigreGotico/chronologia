# -*- coding: utf-8 -*-
"""R127 -- a recurrence naming BOTH a clock RANGE ("between 9 and 5") and a
separate trailing "at" pin ("and also at 7") used to silently swallow the
range: :func:`~chronologia.extract.nseries._apply_clock_range` grounds
``BYHOUR=9`` from the range and consumes "between 9 and 5", then
:func:`~chronologia.extract.nseries._apply_clock` runs afterwards, finds the
independent "at 7" clock, and unconditionally OVERWRITES ``BYHOUR`` with
``(7,)`` -- the range's own tokens stay consumed (so they don't even show up
in the remainder to hint anything was dropped) while the interval they named
("9 to 5") vanishes from the rule entirely: "daily between 9 and 5 and also
at 7" -> ``BYHOUR=7``, remainder "and also" -- a confidently wrong rule with
no trace of the swallowed range.

RFC 5545's ``BYHOUR`` is a set of discrete pins with no window-end part, and
this engine's own convention (:func:`_apply_clock_range`'s docstring) is
that a clock RANGE grounds only its START as one pin -- so a range clause and
an independent at-list clause name two structurally different things that
cannot both be honestly folded onto one ``BYHOUR``: merging them
("BYHOUR=9,7") reads as three unrelated pins and erases the interval
meaning "9 to 5" names, and picking either one silently discards the other.
Per the "claim then decline" convention this codebase already uses for
every other case where no field can honestly hold what the tokens name
(differing-minute BYHOUR lists, an empty weekday-range intersection, a
second stranded date-range clause), the fix makes the WHOLE extraction
decline (``None``) rather than silently pick a winner.
"""
from datetime import datetime

import pytest

from chronologia.extract import extract_recurrence

LANG = "en"
_A = datetime(2026, 8, 12, 12, 0)


@pytest.mark.parametrize("text", [
    # the defect as reported.
    "daily between 9 and 5 and also at 7",
    # the "at" pin coming first still names the same unresolvable clash.
    "daily at 7 and also between 9 and 5",
    # a weekday-scoped rule carries the same clash.
    "every monday between 9 and 5 and also at 7",
    # "from ... to ..." is the same range construction as "between ... and
    # ...", so it clashes with a trailing at-list exactly the same way.
    "daily from 9 to 5 and also at 7",
])
def test_range_plus_at_declines(text):
    assert extract_recurrence(text, LANG, anchor=_A) is None


# -- controls: constructions this fix must NOT disturb -----------------

@pytest.mark.parametrize("text,rrule,remainder", [
    # a bare clock range alone -- unaffected, still pins to the start hour.
    ("daily between 9 and 5", "FREQ=DAILY;BYHOUR=9", ""),
    ("daily from 9 to 5", "FREQ=DAILY;BYHOUR=9", ""),
    # a bare "at" pin alone -- unaffected.
    ("daily at 7", "FREQ=DAILY;BYHOUR=7", ""),
    # a genuine at-LIST (no range involved at all) still folds onto one
    # multi-valued BYHOUR exactly as R123 fixed it.
    ("daily at 9am and 5pm", "FREQ=DAILY;BYHOUR=9,17", ""),
    # a weekday-scoped rule with only a range, or only an at-pin, is
    # likewise unaffected.
    ("every monday between 9 and 5", "FREQ=WEEKLY;BYDAY=MO;BYHOUR=9", ""),
    ("every monday at 7", "FREQ=WEEKLY;BYDAY=MO;BYHOUR=7", ""),
])
def test_controls_unaffected(text, rrule, remainder):
    got = extract_recurrence(text, LANG, anchor=_A)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder
