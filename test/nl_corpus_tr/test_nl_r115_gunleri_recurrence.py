# -*- coding: utf-8 -*-
"""R115: the Turkish recurring-weekday day-word 'günleri' ("on <weekday>s",
the plural of 'günü') trailing a bare weekday must be CONSUMED as part of
the recurrence match, not stranded in ``extract_recurrence``'s remainder.

'cuma günleri' is the ordinary way to say "on Fridays" (a recurring weekly
rule) in Turkish: the weekday stays in its bare singular form ("cuma") and
it is the trailing PLURAL day-word "günleri" ("days") that marks the
reading as recurring, unlike a leading "on"/"every" marker (English "on
mondays", tr "her cuma"). Before the fix ``extract_recurrence`` had no
finder at all for this bare postposed-plural frame (it returned ``None``
outright), and the "her <weekday> günü" frame (already recognised via the
"her"/every finder) left the singular day-word 'günü' stranded in the
remainder the same way plain 'günü' did before PR #671 fixed the
single-span grammar engine's reading (nseries.py's hand-rolled recurrence
tokenizer is a SEPARATE code path from that grammar engine, per that PR's
"not fixed here" note).

Expected values are independent arithmetic against a fixed Monday anchor
(2026-06-15), matching the ISO weekday indices already used by
``test_tr_weekday_gunu.py`` (pazartesi=0 .. pazar=6).
"""
from datetime import datetime

import pytest

from chronologia.extract.nseries import extract_recurrence

ANCHOR = datetime(2026, 6, 15)  # Monday

WEEKDAY_IDX = {
    "pazartesi": 0,
    "salı": 1,
    "çarşamba": 2,
    "perşembe": 3,
    "cuma": 4,
    "cumartesi": 5,
    "pazar": 6,
}


def _recur(text):
    return extract_recurrence(text, "tr", anchor=ANCHOR)


# -- 'WEEKDAY günleri' -> WEEKLY;BYDAY=<weekday>, clean remainder. -------
PLURAL_CASES = [
    ("cuma günleri", "cuma"),
    ("pazartesi günleri", "pazartesi"),
    ("çarşamba günleri", "çarşamba"),
    ("cumartesi günleri", "cumartesi"),
    ("pazar günleri", "pazar"),
]


@pytest.mark.parametrize("text,weekday", PLURAL_CASES)
def test_gunleri_reads_as_weekly_recurrence(text, weekday):
    idx = WEEKDAY_IDX[weekday]
    r = _recur(text)
    assert r is not None, f"{text!r} did not parse as a recurrence"
    rec, remainder = r
    assert rec.freq == "WEEKLY"
    assert rec.interval == 1
    assert rec.byday == ((None, idx),)
    assert remainder.strip() == "", (
        f"{text!r} left a stranded remainder: {remainder!r}"
    )


# -- 'her WEEKDAY günü' ("every friday") already matched via the "her"
#    (every) finder before this fix -- but stranded the day-word 'günü'.
#    Same root cause (an un-skipped trailing day-word), same finder family
#    (weekday collection), so the fix that consumes it for the bare-plural
#    frame above must also close this stranding. --------------------------
def test_her_weekday_gunu_no_longer_strands_gunu():
    r = _recur("her cuma günü")
    assert r is not None
    rec, remainder = r
    assert rec.freq == "WEEKLY"
    assert rec.byday == ((None, WEEKDAY_IDX["cuma"]),)
    assert remainder.strip() == "", f"stranded remainder: {remainder!r}"


# -- controls: unaffected by the fix -------------------------------------
def test_bare_weekday_alone_stays_unread():
    # a bare weekday with neither 'her' nor a day-word names no recurrence
    # at all -- it is a single upcoming date, read (if at all) by
    # extract_timespan, not extract_recurrence.
    assert _recur("cuma") is None


def test_bare_weekday_gunu_singular_stays_unread():
    # the SINGULAR day-word ('günü', "on Friday" -- one specific date) must
    # NOT be mistaken for the plural recurring marker: extract_recurrence
    # must keep declining it exactly as it did before this fix.
    assert _recur("cuma günü") is None


def test_her_weekday_no_gunu_pin_unchanged():
    # control: 'her cuma' ("every friday") with no trailing day-word at all
    # already read correctly before this fix -- pin it stays that way.
    r = _recur("her cuma")
    assert r is not None
    rec, remainder = r
    assert rec.freq == "WEEKLY"
    assert rec.byday == ((None, WEEKDAY_IDX["cuma"]),)
    assert remainder.strip() == ""
