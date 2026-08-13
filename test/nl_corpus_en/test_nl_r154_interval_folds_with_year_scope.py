# -*- coding: utf-8 -*-
"""R154 (en) -- a leading "every other"/"every Nth" INTERVAL prefix was
DROPPED (not folded, not stranded -- silently discarded) when combined with
the year-scope "of [the|this] year" tail added for R145/R151, shipping a rule
TWICE too frequent with the interval word left orphaned in the remainder.

``_recur_nth_weekday``'s ``start`` walk-back (the loop that widens the
consumed span leftward from the ordinal/"last" token over any leading
``ctx.articles``/``ctx.every`` tokens) never recognised an interval prefix
("other", or a bare cardinal count) sitting further left ("every **other**
last friday ..."/"every **2nd** last friday ...") -- it stopped at the first
non-article/non-every token, so the interval word was left OUTSIDE the
consumed span and read into the string remainder while the built rule quietly
used its default INTERVAL=1.

DECIDED SEMANTICS: unlike the ELLIPTICAL "every other last friday" (control,
no "of ... year" tail) and its month-scope sibling "every other last friday
of the month" -- where the base MONTHLY cadence already IS the elliptical
reading and the interval word is deliberately dropped as degenerate -- the
year-scope reading is a genuinely distinct, RFC-5545-expressible cadence
(FREQ=YEARLY;INTERVAL=N), so the fix folds the interval in rather than
dropping it.

Expected rrule strings verified by independent ``dateutil.rrulestr``
expansion (see the docstring on the assertion below) -- not read back from
this parser.

"every other"/"every 2nd" interval-prefix vocabulary
(``chronologia/locale/*/marker_recur_other.voc`` or equivalent) has NO de/es
surface at all (checked: neither locale ships an "other"/ordinal-interval
connector for recurrence), so this defect's de/es siblings are UNATTESTED
and skipped -- en only.
"""
from datetime import datetime

import pytest
from dateutil.rrule import rrulestr

from chronologia.extract import extract_recurrence

LANG = "en"

_CASES = [
    # -- the defect: interval must fold, not drop, with a year-scope tail --
    ("every other last friday of the year", "FREQ=YEARLY;INTERVAL=2;BYDAY=-1FR", ""),
    ("every other last friday of this year", "FREQ=YEARLY;INTERVAL=2;BYDAY=-1FR", ""),
    ("every 2nd last friday of the year", "FREQ=YEARLY;INTERVAL=2;BYDAY=-1FR", ""),
    # -- same fold applies to the business-day (BYSETPOS) sibling ----------
    ("every other last weekday of the year",
     "FREQ=YEARLY;INTERVAL=2;BYDAY=MO,TU,WE,TH,FR;BYSETPOS=-1", ""),
    # -- controls: the ELLIPTICAL bare/monthly readings intentionally drop
    # the interval (established base reading, must not regress) -----------
    ("every other last friday", "FREQ=MONTHLY;BYDAY=-1FR", ""),
    ("every other last friday of the month", "FREQ=MONTHLY;BYDAY=-1FR", ""),
    ("every other friday", "FREQ=WEEKLY;INTERVAL=2;BYDAY=FR", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_interval_prefix_folds_with_year_scope(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


def test_folded_yearly_interval_rrule_expands_correctly():
    # FREQ=YEARLY;INTERVAL=2;BYDAY=-1FR from a 2026-01-01 DTSTART: the last
    # Friday of every OTHER year -- 2026-12-25, 2028-12-29, 2030-12-27,
    # independently computed by dateutil's own rrule engine (not read back
    # from this parser).
    r = rrulestr("FREQ=YEARLY;INTERVAL=2;BYDAY=-1FR", dtstart=datetime(2026, 1, 1))
    got = [d.date().isoformat() for d in r[:3]]
    assert got == ["2026-12-25", "2028-12-29", "2030-12-27"]

    text_rrule = extract_recurrence(
        "every other last friday of the year", LANG)[0].to_string()
    assert text_rrule == "FREQ=YEARLY;INTERVAL=2;BYDAY=-1FR"
