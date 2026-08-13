# -*- coding: utf-8 -*-
"""R141 -- an offset ("an hour before/after") in front of a relative-day-word
reference ("tomorrow"/"today"/"yesterday") followed by a clock ("at 9") was
silently dropped in en/es/fr/de, with the day sometimes wrong too.

ROOT CAUSE (two distinct bugs, both closed here):

1. Grammar ambiguity between the generic offset construction and the
   ``named_day_after``/``named_day_before`` idiom ("the day after tomorrow",
   "the day before yesterday"), whose grammar order was ``"UNIT after/before
   DAY_WORD"`` using the GENERIC ``UNIT`` slot (any unit surface: hour,
   minute, day, week...). "an hour before tomorrow" therefore ALSO matched
   this idiom construction with UNIT="hour" -- and being the LONGER span (it
   swallows "before"/"after" into the construction itself, rather than
   leaving it as a stranded pre-amble for a following construction), it won
   the matcher's longest-span contest over any competing parse. Its resolver
   (``resolver._named_day_offset``) declines to resolve (returns ``None``)
   for any unit other than "day" -- but the matcher had ALREADY committed to
   that (losing) span and never falls back to re-matching "tomorrow" alone
   as a bare ``named_day`` reference, so the whole phrase's tokens were
   dropped from ``resolved`` entirely, and the general anchored-offset pass
   (``anchored.apply_anchored_offset``) never saw "tomorrow" as a
   date-reference to compose the offset onto. Fixed by introducing a
   ``DAYUNIT`` slot (``matcher._bind``) that binds ONLY the "day" unit
   surface, and using it in the ``named_day_after``/``named_day_before``
   grammar orders (``base_grammar.py``) instead of the generic ``UNIT`` --
   "an hour before tomorrow" no longer matches that idiom at all, so the
   general offset construction (already working for weekday/calendar-date
   references, R134) picks it up correctly.

2. Spanish/Galician-specific: "mañana" is a genuine homograph of BOTH
   "tomorrow" (``named_day``) and "morning" (``DAYPART``). "de" is the
   ``marker_of.voc`` surface, so "de mañana" ALSO matches the ``daypart_ref``
   construction's "of DAYPART" order ("in the morning"), a 2-token span that
   beats the 1-token bare ``named_day`` reading of "mañana" alone in the
   matcher's longest-span contest -- even when "antes"/"después" (before/
   after) precedes it, where "de" is obviously the "antes DE" preposition
   glue, not the daypart's "of". Fixed by a new pre-selection veto,
   ``timespan._relday_daypart_homograph_veto`` (wired into
   ``_candidate_veto``): a ``daypart_ref`` match is declined when its
   DAYPART token surface is ALSO a DAY_WORD surface AND is immediately
   preceded by a "before"/"after" connector -- "antes de mañana" can never
   mean "before [in] the morning" in Spanish, so this is unambiguous. Bare
   "de mañana"/"esta mañana" (no preceding before/after marker) are
   untouched and still read as the morning daypart, as before.

Expected values are independently hand-computed against the anchor
(exact clock arithmetic), never read back from the parser.
"""
from datetime import datetime

import pytest

from chronologia.extract import extract_timespan

LANG = "en"
_A = datetime(2026, 8, 12, 10, 0)  # Wednesday


def _start_end(text, anchor=_A):
    r = extract_timespan(text, LANG, anchor)
    assert r is not None, f"{text!r} did not parse (expected a span)"
    return r[0].start, r[0].end


# -- the defect: offset composes onto a rel-day-word + adjacent clock -------

@pytest.mark.parametrize("text,start", [
    ("an hour before tomorrow at 9", datetime(2026, 8, 13, 8, 0)),
    ("an hour after tomorrow at 9", datetime(2026, 8, 13, 10, 0)),
    ("an hour before today at 9", datetime(2026, 8, 12, 8, 0)),
    ("an hour after today at 9", datetime(2026, 8, 12, 10, 0)),
    ("an hour before yesterday at 9", datetime(2026, 8, 11, 8, 0)),
    ("an hour after yesterday at 9", datetime(2026, 8, 11, 10, 0)),
])
def test_offset_composes_with_relday_clock(text, start):
    got_start, got_end = _start_end(text)
    assert got_start == start
    assert (got_end - got_start).total_seconds() == 60


def test_direction_is_not_silently_dropped():
    before = _start_end("an hour before tomorrow at 9")
    after = _start_end("an hour after tomorrow at 9")
    assert before != after


def test_remainder_is_empty_not_stranded():
    r = extract_timespan("an hour before tomorrow at 9", LANG, _A)
    assert r.remainder == ""
    r = extract_timespan("an hour before yesterday at 9", LANG, _A)
    assert r.remainder == ""


@pytest.mark.parametrize("text,start,end", [
    # midnight crossing BACKWARD: exact-instant subtraction must cross the
    # civil day boundary onto the *previous* day (not stay on "tomorrow").
    ("2 hours before tomorrow at 1am",
     datetime(2026, 8, 12, 23, 0), datetime(2026, 8, 12, 23, 1)),
    # midnight crossing FORWARD: exact-instant addition must cross onto the
    # *next* day (not stay on "yesterday").
    ("2 hours after yesterday at 11pm",
     datetime(2026, 8, 12, 1, 0), datetime(2026, 8, 12, 1, 1)),
])
def test_midnight_crossing_relday(text, start, end):
    got_start, got_end = _start_end(text)
    assert got_start == start
    assert got_end == end


# -- controls: pinned pre-existing behaviour this fix must NOT disturb ------

def test_control_clock_first_order_unaffected():
    # "before 9am tomorrow" (clock BEFORE the day word) already worked
    # (R134) and must keep working identically.
    got_start, got_end = _start_end("an hour before 9am tomorrow")
    assert got_start == datetime(2026, 8, 13, 8, 0)
    assert got_end == datetime(2026, 8, 13, 8, 1)


def test_control_weekday_ref_unaffected():
    # "before Monday at 9" (a weekday_ref, not a rel-day word) already
    # worked and must keep working identically. 2026-08-12 is a Wednesday;
    # the next Monday is 2026-08-17.
    got_start, got_end = _start_end("an hour before Monday at 9")
    assert got_start == datetime(2026, 8, 17, 8, 0)
    assert got_end == datetime(2026, 8, 17, 8, 1)


def test_control_named_day_after_idiom_unaffected():
    # the actual idiom this fix's DAYUNIT slot must keep matching: "the day
    # after tomorrow" / "the day before yesterday" ONLY fire for the "day"
    # unit, and still resolve to +/-2 days from the anchor.
    got_start, got_end = _start_end("the day after tomorrow")
    assert got_start == datetime(2026, 8, 14, 0, 0)
    assert got_end == datetime(2026, 8, 15, 0, 0)
    got_start, got_end = _start_end("the day before yesterday")
    assert got_start == datetime(2026, 8, 10, 0, 0)
    assert got_end == datetime(2026, 8, 11, 0, 0)


def test_control_no_clock_subday_offset_still_floors_to_day():
    # unchanged pre-existing (R134) rule: a sub-day offset on a rel-day
    # reference with NO clock in the sentence has no instant to do exact
    # arithmetic against, so it still floors to the whole shifted civil day.
    got_start, got_end = _start_end("half an hour before tomorrow")
    assert got_start == datetime(2026, 8, 12, 0, 0)
    assert got_end == datetime(2026, 8, 13, 0, 0)


def test_r147_day_grain_multi_count_relday_now_fixed():
    # Formerly a KNOWN SEPARATE BUG (R147, fixed): "2 days before tomorrow"
    # collides with the (day-only, R141-fixed) ``named_day_before`` idiom --
    # "days" is a DAY unit surface, so it also matches "DAYUNIT before
    # DAY_WORD" and used to win the matcher's longest-span contest over the
    # general NUM-aware offset construction. That idiom construction has no
    # NUM slot at all (it is built for the bare "the day before yesterday"
    # phrasing), so it silently ignored the "2" quantity and always shifted
    # by exactly one day, stranding "2" in the remainder.
    #
    # R147 fixes this by vetoing the idiom match whenever a NUM token
    # immediately precedes its DAYUNIT slot (``timespan.
    # _num_preamble_named_day_idiom_veto``), so the bare ``named_day`` match
    # for "tomorrow" wins instead and the generic anchored-offset
    # composition pass folds "2 days before" onto it correctly: anchor is
    # 2026-08-12, tomorrow is 2026-08-13, minus 2 days = 2026-08-11.
    r = extract_timespan("2 days before tomorrow", LANG, _A)
    assert r is not None
    assert r[0].start == datetime(2026, 8, 11, 0, 0)
    assert r[0].end == datetime(2026, 8, 12, 0, 0)
    assert r.remainder == ""
