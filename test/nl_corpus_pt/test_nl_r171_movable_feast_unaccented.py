# -*- coding: utf-8 -*-
"""R171 (pt) -- the unaccented spelling of easter ("pascoa", missing the
acute accent -- a common way pt speakers type without diacritics) was not a
registered holiday surface at all: only "páscoa" and the multi-word
"domingo de páscoa"/"domingo de pascoa" (the latter unaccented purely because
that is the literal spelling of PT's own official name in
``chronologia/holiday_data/pt.tab``, an unrelated data fact) were aliased in
``chronologia/holiday_data/i18n/well_known.tab``.  So "toda segunda-feira
antes da pascoa" fell all the way through the "before"-binds-UNTIL machinery
(R150, see test_nl_r150_recur_before_binds_until.py) because
``extract_timespan("pascoa", ...)`` had nothing to resolve, leaving the whole
"antes da pascoa" tail stranded as remainder with UNTIL never bound -- while
the ONLY difference from the working "antes do natal" control is that
"natal" (christmas) has no accented/unaccented split to fall into.

FIX: added the bare "pascoa" alias for the ``easter`` key under ``pt`` in
``well_known.tab``, alongside the existing "páscoa" and "domingo de páscoa"
surfaces -- a pure data addition, no code change.
"""
from datetime import datetime

import pytest

from chronologia.extract import extract_recurrence

LANG = "pt"
ANCHOR = datetime(2026, 8, 14, 10, 0)

# Easter 2027 = March 28 (independently verified, not read back from the
# parser).
_EASTER_2027 = "20270328T000000"

_CASES = [
    # -- the defect: unaccented "pascoa" must ground UNTIL like "páscoa" ---
    ("toda segunda-feira antes da pascoa",
     f"FREQ=WEEKLY;UNTIL={_EASTER_2027};BYDAY=MO", ""),
    # -- control: the accented spelling already worked ---------------------
    ("toda segunda-feira antes da páscoa",
     f"FREQ=WEEKLY;UNTIL={_EASTER_2027};BYDAY=MO", ""),
    # -- control: the sibling christmas ("natal") reading, unaffected ------
    ("toda segunda-feira antes do natal",
     "FREQ=WEEKLY;UNTIL=20261225T000000;BYDAY=MO", ""),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_unaccented_pascoa_binds_until(text, rrule, remainder):
    got = extract_recurrence(text, LANG, anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


def test_accented_and_unaccented_pascoa_ground_the_same_value():
    unaccented = extract_recurrence(
        "toda segunda-feira antes da pascoa", LANG, anchor=ANCHOR)
    accented = extract_recurrence(
        "toda segunda-feira antes da páscoa", LANG, anchor=ANCHOR)
    assert unaccented[0].until == accented[0].until
