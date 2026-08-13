# -*- coding: utf-8 -*-
"""R147 -- a numeral heading "N days after/before <rel-day-word>" was
silently dropped: "two days after tomorrow" resolved to tomorrow+1
(the fixed ``named_day_after`` idiom's answer) with "two" stranded in the
remainder, instead of tomorrow+2.

ROOT CAUSE (per issue #701's report): the ``named_day_after``/
``named_day_before`` idiom orders (``base_grammar.py``, "DAYUNIT after/
before DAY_WORD", carrying no ``NUM`` slot since R141 gave them a
day-only ``DAYUNIT`` slot) still win the matcher's longest-span overlap
contest against the generic NUM-aware offset construction even when a
numeral heads the phrase -- the idiom's span (DAYUNIT + marker + DAY_WORD)
is longer than the bare ``named_day`` match (DAY_WORD alone) the generic
anchored-offset composition pass needs to fold "N days after/before" onto.
So the numeral is stranded and the idiom's fixed +/-1-day answer wins.

Spanish routes around this by accident: "dos dias despues DE mañana" has an
intervening "de" the idiom's own contiguous grammar order does not allow,
so the idiom never matches there at all, and the numeral always composes
correctly through the generic pass (``anchored.apply_anchored_offset``).

FIX: ``timespan._num_preamble_named_day_idiom_veto`` vetoes a
``named_day_after``/``named_day_before`` match whenever a NUM token
immediately precedes its ``DAYUNIT`` slot, forcing the bare ``named_day``
match to win instead -- exactly the shape Spanish already produces -- so
the generic anchored-offset pass folds the numeral-scaled offset on
correctly.

Expected values are independently hand-computed against the anchor
(plain calendar-day arithmetic), never read back from the parser.
"""
from datetime import datetime

import pytest

from chronologia.extract import extract_timespan

LANG = "en"
_A = datetime(2026, 8, 13, 10, 0)  # Thursday
_TOMORROW = datetime(2026, 8, 14, 0, 0)
_YESTERDAY = datetime(2026, 8, 12, 0, 0)


def _span(text, anchor=_A):
    r = extract_timespan(text, LANG, anchor)
    assert r is not None, f"{text!r} did not parse (expected a span)"
    return r[0].start, r[0].end, r.remainder


# -- the defect: numeral must multiply the day-idiom offset -----------------

@pytest.mark.parametrize("n_word,n", [("two", 2), ("2", 2),
                                       ("three", 3), ("3", 3)])
def test_num_days_after_tomorrow(n_word, n):
    from datetime import timedelta
    expected = _TOMORROW + timedelta(days=n)          # independent arithmetic
    start, end, remainder = _span(f"{n_word} days after tomorrow")
    assert start == expected
    assert end == expected + timedelta(days=1)
    assert remainder == ""


@pytest.mark.parametrize("n_word,n", [("two", 2), ("2", 2),
                                       ("three", 3), ("3", 3)])
def test_num_days_before_tomorrow(n_word, n):
    from datetime import timedelta
    expected = _TOMORROW - timedelta(days=n)
    start, end, remainder = _span(f"{n_word} days before tomorrow")
    assert start == expected
    assert end == expected + timedelta(days=1)
    assert remainder == ""


@pytest.mark.parametrize("n_word,n", [("two", 2), ("2", 2),
                                       ("three", 3), ("3", 3)])
def test_num_days_after_yesterday(n_word, n):
    from datetime import timedelta
    expected = _YESTERDAY + timedelta(days=n)
    start, end, remainder = _span(f"{n_word} days after yesterday")
    assert start == expected
    assert end == expected + timedelta(days=1)
    assert remainder == ""


@pytest.mark.parametrize("n_word,n", [("two", 2), ("2", 2),
                                       ("three", 3), ("3", 3)])
def test_num_days_before_yesterday(n_word, n):
    from datetime import timedelta
    expected = _YESTERDAY - timedelta(days=n)
    start, end, remainder = _span(f"{n_word} days before yesterday")
    assert start == expected
    assert end == expected + timedelta(days=1)
    assert remainder == ""


# -- independent-arithmetic double-check: "N days after X" == X's day + N ---

def test_careful_semantics_two_days_after_tomorrow_is_anchor_plus_3():
    # "two days after tomorrow" = tomorrow+2 = anchor+3 (anchor is midnight
    # -distinct from the day-word's own semantic offset -- both readings
    # must agree independently).
    start, end, remainder = _span("two days after tomorrow")
    from datetime import timedelta
    assert start == datetime(2026, 8, 13, 0, 0) + timedelta(days=3)
    assert remainder == ""


def test_careful_semantics_the_day_after_tomorrow_is_anchor_plus_2():
    # the bare IDIOM ("the day after tomorrow") is a lexicalised whole,
    # fixed at +2 from the anchor -- NOT "tomorrow" + a further "+1" step,
    # and NOT scaled by any numeral.
    from datetime import timedelta
    start, end, remainder = _span("the day after tomorrow")
    assert start == datetime(2026, 8, 13, 0, 0) + timedelta(days=2)
    assert remainder == ""


# -- idiom controls: must NOT change ----------------------------------------

def test_control_the_day_after_tomorrow_unchanged():
    start, end, remainder = _span("the day after tomorrow")
    assert start == datetime(2026, 8, 15, 0, 0)
    assert end == datetime(2026, 8, 16, 0, 0)
    assert remainder == ""


def test_control_the_day_before_yesterday_unchanged():
    start, end, remainder = _span("the day before yesterday")
    assert start == datetime(2026, 8, 11, 0, 0)
    assert end == datetime(2026, 8, 12, 0, 0)
    assert remainder == ""


# -- R141 non-regression: sub-day offset + clock composition unaffected -----

def test_control_r141_hour_before_tomorrow_at_9_unchanged():
    r = extract_timespan("an hour before tomorrow at 9", LANG, _A)
    assert r is not None
    assert r[0].start == datetime(2026, 8, 14, 8, 0)
    assert r.remainder == ""


def test_control_r141_hour_after_tomorrow_at_9_unchanged():
    r = extract_timespan("an hour after tomorrow at 9", LANG, _A)
    assert r is not None
    assert r[0].start == datetime(2026, 8, 14, 10, 0)
    assert r.remainder == ""


# -- weekday offsets unaffected ----------------------------------------------

def test_control_weekday_offset_unaffected():
    # "two weeks from tuesday" -- an unrelated NUM UNIT "from" WEEKDAY
    # construction, must keep matching exactly as before.
    r = extract_timespan("two weeks from tuesday", LANG, _A)
    assert r is not None
    # 2026-08-13 is a Thursday; the next Tuesday is 2026-08-18, +2 weeks.
    assert r[0].start == datetime(2026, 9, 1, 0, 0)
