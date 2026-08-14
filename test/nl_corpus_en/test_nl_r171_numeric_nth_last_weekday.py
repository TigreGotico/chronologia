# -*- coding: utf-8 -*-
"""R171 (en) -- "every <N>th last <weekday>" (numeric ordinal, no "to")
silently ignored N and always emitted the bare last-weekday-of-month reading
(BYDAY=-1) instead of reading N as a count backward from the month's end,
in BOTH shapes of this grammar in chronologia/extract/nseries.py:

* the elliptical "every <N> last <weekday>" branch in ``_recur_every`` (no
  "of the month" scope tail);
* the "<N> last <weekday> of the month" branch in ``_recur_nth_weekday``
  (explicit scope tail) -- ``_recur_nth_weekday`` runs BEFORE ``_recur_every``
  in ``_FINDERS`` (see the load-bearing order comment above ``_FINDERS``),
  so both call sites had to be fixed for the "of the month" form to actually
  read the numeric N.

DECIDED SEMANTICS, matching the word-form "<ordinal>-to-last" idiom this
mirrors (R114, test_nl_ntolast_weekday_of_month.py; ``_ntolast_ordn`` in
nseries.py):

* N=2 keeps the documented "second/last Friday" ELLIPSIS -- BYDAY=-1 -- since
  a genuine "N=2 counts back two" reading is indistinguishable from that
  ellipsis and changing it would break the pinned convention.
* N=3 and N=4 are UNAMBIGUOUS (no ellipsis competes with them): they count
  backward exactly like the word forms ("third-to-last" -> -3), giving
  BYDAY=-3FR / BYDAY=-4FR.
* N>=5 refuses (``None``) rather than inventing a reading past what the
  word-form idiom supports (bounded at -4; "fifth-to-last" itself refuses,
  per R114) -- mirrored here as N=5 refusing too, not silently falling back
  to bare "last".
* N=1 ("every 1st last friday") is not a form anyone writes and is also
  declined, rather than guessed into either -1 or -1-something.
"""
from datetime import datetime

import pytest

from chronologia.extract import extract_recurrence

LANG = "en"
ANCHOR = datetime(2026, 8, 14, 10, 0)

_CASES = [
    # -- control: the documented N=2 ellipsis must NOT change ---------------
    ("every 2nd last friday", "FREQ=MONTHLY;BYDAY=-1FR", ""),
    # -- the defect: N=3/N=4 must count backward, bare (no scope tail) ------
    ("every 3rd last friday", "FREQ=MONTHLY;BYDAY=-3FR", ""),
    ("every 4th last friday", "FREQ=MONTHLY;BYDAY=-4FR", ""),
    # -- the defect: same N=3/N=4 reading with the explicit scope tail,
    # a DIFFERENT code path (``_recur_nth_weekday``, which runs first) ------
    ("every 3rd last friday of the month", "FREQ=MONTHLY;BYDAY=-3FR", ""),
    ("every 4th last friday of the month", "FREQ=MONTHLY;BYDAY=-4FR", ""),
    # -- control: the word-form idiom this mirrors, unchanged ---------------
    ("every third-to-last friday of each month", "FREQ=MONTHLY;BYDAY=-3FR", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_numeric_nth_last_weekday(text, rrule, remainder):
    got = extract_recurrence(text, LANG, anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", [
    "every 5th last friday",
    "every 5th last friday of the month",
    "every 1st last friday",
])
def test_numeric_nth_last_weekday_refuses_beyond_the_cap(text):
    assert extract_recurrence(text, LANG, anchor=ANCHOR) is None
