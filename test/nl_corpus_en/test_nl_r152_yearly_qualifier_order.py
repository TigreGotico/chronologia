# -*- coding: utf-8 -*-
"""R152 (en) -- yearly adverb/determiner qualifier folding is ORDER-SENSITIVE:
a leading day-of-month qualifier blocks the month qualifier scan entirely.

Two independent finders carry this bug, both fixed the same way:

* ``_recur_freq_word`` (the bare-adverb path, "annually ...") tried ONLY
  ``_yearly_bymonth_qualifier`` right after the adverb. "annually in june on
  the 1st" folded (the month qualifier sat first, right where the scan
  looked) but "annually on the 1st in june" did not -- the day qualifier sat
  first, the month scan found nothing there, and the WHOLE tail (including
  the "in june" that would have matched on its own) was abandoned unread.
  Fixed by ``_yearly_recur_qualifiers``, which tries each qualifier kind in
  turn and advances past whichever matches, so either order is read.

* ``_recur_date_anchored`` (the "every year <date>" path) only looked for a
  TRAILING "on the Nth" after the month ("every year in june on the 15th"
  folded the day) -- a LEADING one ("every year on the 15th in june") broke
  the date-match gap check (a bare number in the gap was never tolerated) and
  the whole tail was stranded. Fixed by trying the leading qualifier first
  and resuming the date-match scan beyond it.

In both cases, when a month qualifier is present but no explicit day was
given, the day still defaults to 1 (the PRE-EXISTING "annually in june" ->
BYMONTHDAY=1 uniform encoding -- unchanged, still pinned as a control below).
An explicit day always overrides that default, in EITHER order.

A bare day qualifier with NO month at all ("annually on the 1st") is
deliberately left UNFOLDED -- which month it names is unspecified, and
inventing one would be a wrong guess, not honest degradation. This is pinned
as a control that must keep stranding.
"""
import pytest

from chronologia.extract import extract_recurrence

LANG = "en"

_CASES = [
    # -- the defect: order must not matter, adverb path --------------------
    ("annually on the 1st in june", "FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=1", ""),
    ("annually in june on the 1st", "FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=1", ""),
    ("annually on the 15th in june", "FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=15", ""),
    ("annually in june on the 15th", "FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=15", ""),
    # -- the defect: order must not matter, "every year" determiner path ---
    ("every year on the 15th in june", "FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=15", ""),
    ("every year in june on the 15th", "FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=15", ""),
    ("every year on the 1st in december",
     "FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=1", ""),
    ("every year in december on the 1st",
     "FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=1", ""),
    # -- controls: month-only, no explicit day -> uniform BYMONTHDAY=1 -----
    ("annually in june", "FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=1", ""),
    ("every year in june", "FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=1", ""),
    # -- control: bare day, no month -- must keep stranding, no invented
    # month; the qualifier is honestly left unread.
    ("annually on the 1st", "FREQ=YEARLY", "on the 1st"),
    # -- controls: pre-existing sibling readings, unaffected ---------------
    ("monthly on the 15th", "FREQ=MONTHLY;BYMONTHDAY=15", ""),
    ("weekly on monday", "FREQ=WEEKLY;BYDAY=MO", ""),
    ("every month on the 15th", "FREQ=MONTHLY;BYMONTHDAY=15", ""),
    ("every 10th of may", "FREQ=YEARLY;BYMONTH=5;BYMONTHDAY=10", ""),
    ("every year on may 10", "FREQ=YEARLY;BYMONTH=5;BYMONTHDAY=10", ""),
    ("every 29th of february", "FREQ=YEARLY;BYMONTH=2;BYMONTHDAY=29", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_yearly_qualifier_folding_is_order_independent(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder
