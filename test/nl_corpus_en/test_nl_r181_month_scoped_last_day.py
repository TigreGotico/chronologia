# -*- coding: utf-8 -*-
"""en -- "every [Nth] last day of <month name>" left the month name unread
and kept firing every month, actively contradicting the input: "every last
day of june" resolved to FREQ=MONTHLY;BYMONTHDAY=-1 with "of june" stranded
in the remainder, a rule that fires in January, February, ... every month
except the one actually named.

:func:`~chronologia.extract.nseries._recur_every`'s "every [<N>] last day
[of the month]" ellipsis (R177) only ever read the GENERIC "of [the] month"
tail via :func:`~chronologia.extract.nseries._of_month_tail`. A new sibling,
:func:`~chronologia.extract.nseries._of_month_name_tail`, reads a NAMED
month in that same tail position; when present it scopes the rule to a
single calendar month -- a YEARLY rule with BYMONTH set -- mirroring the
shape ``_recur_freq_word``'s "annually in june" reading already produces
(FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=1). The named-month check runs BEFORE the
generic tail so a genuine month name always wins; the bare "of the month"
tail (or no tail at all) keeps today's every-month rule unchanged.

The POSITIVE-count sibling ("every 3rd day of june") is a DIFFERENT branch
(the generic day-unit interval reading, ``_UNIT_FREQ``) and mis-scopes the
same way -- it currently reads FREQ=DAILY;INTERVAL=3 with "of june"
stranded. That branch is shared by every unit (day/week/month/year) across
every locale, so widening it here would be a much larger, higher-risk
change; it is out of scope for this fix and stays pinned as a known,
disjoint gap rather than folded in.
"""
from datetime import datetime

import pytest

from chronologia.extract import extract_recurrence

LANG = "en"
ANCHOR = datetime(2026, 8, 14, 10, 0)

_CASES = [
    # -- the defect: a named month must scope the rule to that month, not
    # strand the name while still firing every month ------------------------
    ("every last day of june", "FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=-1", ""),
    ("every last day of december", "FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=-1", ""),
    ("every last day of february", "FREQ=YEARLY;BYMONTH=2;BYMONTHDAY=-1", ""),
    # -- the N-variant composes the same way --------------------------------
    ("every 2nd last day of june", "FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=-2", ""),
    ("every 3rd last day of june", "FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=-3", ""),
    # -- controls: the generic "of the month" tail, unaffected --------------
    ("every last day of the month", "FREQ=MONTHLY;BYMONTHDAY=-1", ""),
    ("every 2nd last day of the month", "FREQ=MONTHLY;BYMONTHDAY=-2", ""),
    # -- control: the shape this fix mirrors, a different finder ------------
    ("annually in june", "FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=1", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_month_scoped_last_day(text, rrule, remainder):
    got = extract_recurrence(text, LANG, anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.xfail(strict=True, reason=(
    "the POSITIVE-count sibling (generic day-unit interval branch, "
    "_UNIT_FREQ) does not yet scope to a named month -- correct gold is "
    "FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=3, remainder ''; currently reads "
    "FREQ=DAILY;INTERVAL=3 with 'of june' stranded, a different and "
    "disjoint code path from this fix"))
def test_positive_ordinal_day_of_named_month_not_yet_scoped():
    got = extract_recurrence("every 3rd day of june", LANG, anchor=ANCHOR)
    assert got is not None
    assert got[0].to_string() == "FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=3"
    assert got[1] == ""
