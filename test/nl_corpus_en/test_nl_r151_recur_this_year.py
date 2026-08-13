# -*- coding: utf-8 -*-
"""R151 (en) -- "every <ord|last> <weekday> of THIS year" silently downgraded
to a MONTHLY rule, unlike its "of the year" sibling (R145/PR #702).

``_recur_nth_weekday``'s "... of [every] (month|year)" tail (added by PR #702
for R145) only skipped ``ctx.articles`` ("the") and ``ctx.every`` tokens
between "of" and the unit noun, so "of the year" reached the units-is-"year"
branch but "of THIS year" did not -- "this" (a ``rel_markers`` deixis token,
value 0) sat where the units check expected "year" and matched neither the
``ctx.months`` branch nor the units-is-"year" branch. The tail fell through
unclaimed and a weaker finder read only "last monday"/"first tuesday" as a
bare MONTHLY rule with "of this year" stranded in the remainder -- silently
the WRONG frequency, not a refusal.

The SPAN reading (``extract_timespan``, see
``test_nl_r145_year_word_ordweekday.py``) already accepted "the"/"this"
interchangeably in front of "year"/"month" -- this defect is the recurrence
path failing to mirror that.

Expected rrule strings are hand-derived from RFC 5545: a signed ``BYDAY``
ordinal under bare ``FREQ=YEARLY`` with no ``BYMONTH`` means "the nth (or,
negative, last) matching weekday of the whole year" -- exactly "the
last/first <weekday> of this year"'s reading, identical to the "of the year"
control PR #702 already pinned.
"""
import pytest

from chronologia.extract import extract_recurrence

LANG = "en"

_CASES = [
    # -- the defect: "of this year" must be YEARLY, not MONTHLY -----------
    ("every last monday of this year", "FREQ=YEARLY;BYDAY=-1MO", ""),
    ("every first tuesday of this year", "FREQ=YEARLY;BYDAY=1TU", ""),
    # -- controls: "of the year" (R145/#702) must not regress --------------
    ("every last monday of the year", "FREQ=YEARLY;BYDAY=-1MO", ""),
    ("every first tuesday of the year", "FREQ=YEARLY;BYDAY=1TU", ""),
    # -- control: "of this month" (a DIFFERENT unit) must not regress ------
    ("every last monday of this month", "FREQ=MONTHLY;BYDAY=-1MO", ""),
    ("every last monday of every month", "FREQ=MONTHLY;BYDAY=-1MO", ""),
    # -- control: a named month must not be swallowed by the "this" fix ----
    ("every last monday of january", "FREQ=YEARLY;BYMONTH=1;BYDAY=-1MO", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recur_of_this_year_is_yearly(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder
