# -*- coding: utf-8 -*-
"""R141 (German) -- same offset-before-a-relative-day-word-plus-clock defect
as ``test/nl_corpus_en/test_nl_r141_offset_relday_clock.py`` (see that file's
docstring for the full root-cause writeup: the ``DAYUNIT``-slot fix to the
``named_day_after``/``named_day_before`` idiom grammar, closing the
"<generic UNIT> before/after <DAY_WORD>" collision that stranded the offset).
German has no multi-word "the day before yesterday"/"the day after tomorrow"
idiom surface that doubles as marker + DAY_WORD (unlike French's
"avant-hier"/"après-demain") and no marker/DAYPART homograph (unlike Spanish
"mañana"), so every before/after x morgen/heute/gestern combination composes
correctly once the ``DAYUNIT`` fix lands -- no unresolved ambiguity to
document here.

Expected values are independently hand-computed against the anchor, never
read back from the parser.
"""
from datetime import datetime

import pytest

from chronologia.extract import extract_timespan

LANG = "de"
_A = datetime(2026, 8, 12, 10, 0)  # Wednesday


def _start_end(text, anchor=_A):
    r = extract_timespan(text, LANG, anchor)
    assert r is not None, f"{text!r} did not parse (expected a span)"
    return r[0].start, r[0].end


@pytest.mark.parametrize("text,start", [
    ("eine Stunde vor morgen um 9 Uhr", datetime(2026, 8, 13, 8, 0)),
    ("eine Stunde nach morgen um 9 Uhr", datetime(2026, 8, 13, 10, 0)),
    ("eine Stunde vor heute um 9 Uhr", datetime(2026, 8, 12, 8, 0)),
    ("eine Stunde nach heute um 9 Uhr", datetime(2026, 8, 12, 10, 0)),
    ("eine Stunde vor gestern um 9 Uhr", datetime(2026, 8, 11, 8, 0)),
    ("eine Stunde nach gestern um 9 Uhr", datetime(2026, 8, 11, 10, 0)),
])
def test_offset_composes_with_relday_clock(text, start):
    got_start, got_end = _start_end(text)
    assert got_start == start
    assert (got_end - got_start).total_seconds() == 60


def test_direction_is_not_silently_dropped():
    before = _start_end("eine Stunde vor morgen um 9 Uhr")
    after = _start_end("eine Stunde nach morgen um 9 Uhr")
    assert before != after


def test_remainder_is_empty_not_stranded():
    r = extract_timespan("eine Stunde vor morgen um 9 Uhr", LANG, _A)
    assert r.remainder == ""


@pytest.mark.parametrize("text,start,end", [
    # midnight crossing BACKWARD.
    ("zwei Stunden vor morgen um 1 Uhr",
     datetime(2026, 8, 12, 23, 0), datetime(2026, 8, 12, 23, 1)),
    # midnight crossing FORWARD.
    ("zwei Stunden nach gestern um 23 Uhr",
     datetime(2026, 8, 12, 1, 0), datetime(2026, 8, 12, 1, 1)),
])
def test_midnight_crossing_relday(text, start, end):
    got_start, got_end = _start_end(text)
    assert got_start == start
    assert got_end == end


# -- controls: pinned pre-existing behaviour this fix must NOT disturb ------

def test_control_clock_first_order_unaffected():
    got_start, got_end = _start_end("eine Stunde vor 9 Uhr morgen")
    assert got_start == datetime(2026, 8, 13, 8, 0)
    assert got_end == datetime(2026, 8, 13, 8, 1)


def test_control_weekday_ref_unaffected():
    # 2026-08-12 is a Wednesday; the next Monday is 2026-08-17.
    got_start, got_end = _start_end("eine Stunde vor Montag um 9 Uhr")
    assert got_start == datetime(2026, 8, 17, 8, 0)
    assert got_end == datetime(2026, 8, 17, 8, 1)


def test_control_no_clock_subday_offset_still_floors_to_day():
    got_start, got_end = _start_end("eine halbe Stunde vor morgen")
    assert got_start == datetime(2026, 8, 12, 0, 0)
    assert got_end == datetime(2026, 8, 13, 0, 0)
