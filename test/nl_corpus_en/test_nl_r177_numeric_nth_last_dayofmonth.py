# -*- coding: utf-8 -*-
"""en -- "every <N>th last day of the month" (numeric ordinal before the
bare "day" unit noun, no weekday involved) counts backward from the month
end via RFC 5545's signed ``BYMONTHDAY``, mirroring the signed-``BYDAY``
convention of the "<N> last <weekday> of the month" idiom
(test_nl_r171_numeric_nth_last_weekday.py):

* "every last day of the month" (N omitted, bare "last") -> BYMONTHDAY=-1.
* "every 2nd last day of the month" -> BYMONTHDAY=-2. Unlike the weekday
  path, there is no competing "second/last day" convention to protect (that
  ambiguity is specific to the weekday idiom), so N=2 is NOT special-cased
  into the bare-last ellipsis here -- it counts backward like every other N.
* N in 3..31 counts backward unambiguously (BYMONTHDAY is valid over
  -31..-1 per RFC 5545) -- "every 3rd last day of the month" -> -3, "every
  31st last day of the month" -> -31 (the earliest possible day counting
  from the end, i.e. day 1 of a 31-day month).
* N=32 and beyond exceed RRULE's -31..-1 BYMONTHDAY range and refuse
  (``None``) rather than clamp or silently fall back to a wrong reading.
* The word-form idioms ("second-to-last day of the month", "penultimate
  day of the month") stay OUT of scope and refuse: unlike weekdays, there
  is no backward-scanning finder for the bare "day" noun
  (``_recur_nth_weekday`` only fires on an actual weekday/business-day
  token), so the "<ordinal>-to-last"/penultimate mechanism the weekday
  path reuses does not extend here.
"""
from datetime import datetime

import pytest

from chronologia.extract import extract_recurrence

LANG = "en"
ANCHOR = datetime(2026, 8, 14, 10, 0)

_CASES = [
    # -- the defect itself: numeric N binds the WRONG (positive) end -------
    ("every 3rd last day of the month", "FREQ=MONTHLY;BYMONTHDAY=-3", ""),
    ("every 5th last day of the month", "FREQ=MONTHLY;BYMONTHDAY=-5", ""),
    # -- N=2: no weekday-style ellipsis competes here, counts backward too --
    ("every 2nd last day of the month", "FREQ=MONTHLY;BYMONTHDAY=-2", ""),
    # -- bare "last" (N omitted), previously refused outright ---------------
    ("every last day of the month", "FREQ=MONTHLY;BYMONTHDAY=-1", ""),
    # -- boundary of RRULE's valid BYMONTHDAY range (-31..-1) ---------------
    ("every 31st last day of the month", "FREQ=MONTHLY;BYMONTHDAY=-31", ""),
    # -- control: named-weekday Nth-last path (nseries.py, different branch,
    # R171) stays untouched by this fix -------------------------------------
    ("every 3rd last friday of the month", "FREQ=MONTHLY;BYDAY=-3FR", ""),
    # -- control: the plain positive-count BYMONTHDAY ellipsis this defect
    # was stealing from must still resolve correctly with no trailing
    # "last" present -----------------------------------------------------
    ("every 3rd of the month", "FREQ=MONTHLY;BYMONTHDAY=3", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_numeric_nth_last_dayofmonth(text, rrule, remainder):
    got = extract_recurrence(text, LANG, anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", [
    # -- out of RRULE's -31..-1 BYMONTHDAY range -> whole reading refuses --
    "every 32nd last day of the month",
    "every 45th last day of the month",
    # -- word-form idioms: no bare-day backward-scanning finder exists to
    # extend the weekday mechanism to, stays out of scope -------------------
    "every second-to-last day of the month",
    "every third-to-last day of the month",
    "every penultimate day of the month",
])
def test_numeric_nth_last_dayofmonth_refuses_out_of_scope(text):
    assert extract_recurrence(text, LANG, anchor=ANCHOR) is None
