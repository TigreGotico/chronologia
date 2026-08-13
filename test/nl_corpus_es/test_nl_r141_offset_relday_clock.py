# -*- coding: utf-8 -*-
"""R141 (Spanish) -- same offset-before-a-relative-day-word-plus-clock defect
as ``test/nl_corpus_en/test_nl_r141_offset_relday_clock.py`` (see that file's
docstring for the full root-cause writeup), PLUS a Spanish-specific
collision: "mañana" is a genuine homograph of both "tomorrow" (``named_day``)
and "morning" (``DAYPART``). "antes de mañana" ("before tomorrow") was
mis-read as "antes [de mañana]" ("before [in] the morning") because "de
mañana" (2 tokens, "of"+DAYPART) beat the bare 1-token "mañana" (tomorrow)
reading in the matcher's longest-span contest -- even directly after
"antes"/"después", where the "of the morning" reading makes no sense.
Fixed by ``timespan._relday_daypart_homograph_veto``.

Expected values are independently hand-computed against the anchor, never
read back from the parser.
"""
from datetime import datetime

import pytest

from chronologia.extract import extract_timespan

LANG = "es"
_A = datetime(2026, 8, 12, 10, 0)  # Wednesday


def _start_end(text, anchor=_A):
    r = extract_timespan(text, LANG, anchor)
    assert r is not None, f"{text!r} did not parse (expected a span)"
    return r[0].start, r[0].end


@pytest.mark.parametrize("text,start", [
    ("una hora antes de mañana a las 9", datetime(2026, 8, 13, 8, 0)),
    ("una hora despues de mañana a las 9", datetime(2026, 8, 13, 10, 0)),
    ("una hora antes de hoy a las 9", datetime(2026, 8, 12, 8, 0)),
    ("una hora despues de hoy a las 9", datetime(2026, 8, 12, 10, 0)),
    ("una hora antes de ayer a las 9", datetime(2026, 8, 11, 8, 0)),
    ("una hora despues de ayer a las 9", datetime(2026, 8, 11, 10, 0)),
])
def test_offset_composes_with_relday_clock(text, start):
    got_start, got_end = _start_end(text)
    assert got_start == start
    assert (got_end - got_start).total_seconds() == 60


def test_direction_is_not_silently_dropped():
    before = _start_end("una hora antes de mañana a las 9")
    after = _start_end("una hora despues de mañana a las 9")
    assert before != after


def test_remainder_is_empty_not_stranded():
    r = extract_timespan("una hora antes de mañana a las 9", LANG, _A)
    assert r.remainder == ""


@pytest.mark.parametrize("text,start,end", [
    # midnight crossing BACKWARD.
    ("dos horas antes de mañana a la 1am",
     datetime(2026, 8, 12, 23, 0), datetime(2026, 8, 12, 23, 1)),
    # midnight crossing FORWARD.
    ("dos horas despues de ayer a las 11pm",
     datetime(2026, 8, 12, 1, 0), datetime(2026, 8, 12, 1, 1)),
])
def test_midnight_crossing_relday(text, start, end):
    got_start, got_end = _start_end(text)
    assert got_start == start
    assert got_end == end


# -- the Spanish-specific "mañana" homograph veto ----------------------------

def test_manana_homograph_disambiguates_after_before_after_marker():
    # "antes de mañana"/"despues de mañana" are unambiguous ("before/after
    # TOMORROW"), never "before/after [in] the morning".
    got_start, _ = _start_end("una hora antes de mañana a las 9")
    assert got_start.day == 13   # tomorrow, not a daypart band on today


def test_manana_bare_daypart_reading_unaffected():
    # the veto is scoped to a PRECEDING before/after marker only -- bare
    # "de mañana"/"esta mañana" (no offset marker) must still read as the
    # morning daypart band, exactly as before this fix.
    for text in ("esta mañana", "de mañana"):
        got_start, got_end = _start_end(text)
        assert got_start == datetime(2026, 8, 12, 6, 0)
        assert got_end == datetime(2026, 8, 12, 12, 0)


# -- controls: pinned pre-existing behaviour this fix must NOT disturb ------

def test_control_clock_first_order_unaffected():
    got_start, got_end = _start_end("una hora antes de las 9am mañana")
    assert got_start == datetime(2026, 8, 13, 8, 0)
    assert got_end == datetime(2026, 8, 13, 8, 1)


def test_control_weekday_ref_unaffected():
    # 2026-08-12 is a Wednesday; the next Monday is 2026-08-17.
    got_start, got_end = _start_end("una hora antes del lunes a las 9")
    assert got_start == datetime(2026, 8, 17, 8, 0)
    assert got_end == datetime(2026, 8, 17, 8, 1)


def test_control_no_clock_subday_offset_still_floors_to_day():
    got_start, got_end = _start_end("media hora antes de mañana")
    assert got_start == datetime(2026, 8, 12, 0, 0)
    assert got_end == datetime(2026, 8, 13, 0, 0)
