# -*- coding: utf-8 -*-
"""R159 (en) -- "weekly on <plural weekday>" ("weekly on mondays") stranded
the leading "weekly" adverb in the remainder instead of folding it away.

Root cause: :func:`~chronologia.extract.nseries._recur_on_weekdays` (the
dedicated "on <weekday>" finder) runs BEFORE the bare-adverb path
(:func:`_recur_freq_word`) and already reads the plural weekday correctly
into ``BYDAY`` -- :func:`_collect_weekdays` is called with ``plural_ok=True``
there, same as everywhere else the plural is licensed. But it only ever
consumed a REDUNDANT leading RATE ("3 times a week on monday") via
:func:`_leading_rate_span`, never a redundant leading bare WEEKLY ADVERB
("weekly on mondays") -- so "weekly" won the finder race, its own tokens
were never claimed, and it was left stranded verbatim in the remainder even
though ``BYDAY`` was already correctly grounded.

Fixed by also swallowing an immediately-leading bare "weekly" (interval 1)
token in :func:`_recur_on_weekdays`, the same way the redundant rate span
already is.

Singular "weekly on monday" was NEVER affected -- :func:`_recur_on_weekdays`
declines a lone singular weekday with no leading rate (it reads as a single
coming date, not a rule), so that surface falls through to the bare-adverb
path (:func:`_recur_freq_word` -> :func:`_weekly_byday_qualifier_loose`),
which already folded it correctly and is unchanged by this fix.
"""
from datetime import datetime

import pytest

from chronologia.extract import extract_recurrence

LANG = "en"
ANCHOR = datetime(2026, 8, 13, 10, 0)

_CASES = [
    # -- the defect: PLURAL weekday after "weekly on" -----------------------
    ("weekly on mondays", "FREQ=WEEKLY;BYDAY=MO", ""),
    ("weekly on tuesdays", "FREQ=WEEKLY;BYDAY=TU", ""),
    ("weekly on wednesdays", "FREQ=WEEKLY;BYDAY=WE", ""),
    ("weekly on thursdays", "FREQ=WEEKLY;BYDAY=TH", ""),
    ("weekly on fridays", "FREQ=WEEKLY;BYDAY=FR", ""),
    ("weekly on saturdays", "FREQ=WEEKLY;BYDAY=SA", ""),
    ("weekly on sundays", "FREQ=WEEKLY;BYDAY=SU", ""),
    # -- composes with a multi-day list --------------------------------------
    ("weekly on mondays, wednesdays and fridays",
     "FREQ=WEEKLY;BYDAY=MO,WE,FR", ""),
    # -- composes with a trailing clock ---------------------------------------
    ("weekly on mondays at 9", "FREQ=WEEKLY;BYDAY=MO;BYHOUR=9", ""),
    # -- control: singular weekday, must not regress -------------------------
    ("weekly on monday", "FREQ=WEEKLY;BYDAY=MO", ""),
    # -- control: MONTHLY qualifier path unaffected --------------------------
    ("monthly on the 15th", "FREQ=MONTHLY;BYMONTHDAY=15", ""),
    # -- control: bare adverb, no qualifier ----------------------------------
    ("weekly", "FREQ=WEEKLY", ""),
    # -- control: bare "on <plural weekday>" (no leading "weekly"), the
    # dedicated finder's own original reading, must not regress -------------
    ("on mondays", "FREQ=WEEKLY;BYDAY=MO", ""),
    # -- control: "every <weekday>" bare recurrence, a DIFFERENT finder ------
    ("every monday", "FREQ=WEEKLY;BYDAY=MO", ""),
]


def test_bare_plural_weekday_alone_unattested():
    # a lone plural weekday with no marker at all ("mondays") carries no
    # recurrence determiner in English and is correctly refused -- distinct
    # from "on mondays" above, which the "on" marker licenses. Pinned as a
    # control so this fix is never mistaken for having changed it.
    assert extract_recurrence("mondays", LANG, anchor=ANCHOR) is None


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_weekly_plural_qualifier_folds(text, rrule, remainder):
    got = extract_recurrence(text, LANG, anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


def test_every_2_weeks_on_monday_interval_reading_unaffected():
    # a DIFFERENT finder (the "every N weeks on <weekday>" interval reading)
    # -- must not be swallowed by this fix, which only touches a BARE
    # (interval-1) leading "weekly" adverb.
    got = extract_recurrence("every 2 weeks on monday", LANG, anchor=ANCHOR)
    assert got is not None
    assert got[0].to_string() == "FREQ=WEEKLY;INTERVAL=2;BYDAY=MO"
    assert got[1] == ""
