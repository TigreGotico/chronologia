# -*- coding: utf-8 -*-
"""R171 (fr) -- the weekly frequency adverb "hebdomadairement" had NO
registered surface at all: unlike ``chronologia/locale/fr/`` which ships
``marker_freq_daily.voc`` (quotidiennement), ``marker_freq_monthly.voc``
(mensuellement) and ``marker_freq_yearly.voc`` (annuellement), there was no
``marker_freq_weekly.voc`` file, so ``ctx.freq`` (built by ``_freq_map`` in
chronologia/extract/nseries.py from the ``freq_weekly`` connector key) never
contained "hebdomadairement" and :func:`_recur_freq_word` silently refused
the whole phrase -- while en/de/es all ship the sibling weekly adverb
("weekly", "woechentlich"/"wöchentlich", "semanalmente") and read it fine.

FIX: added ``chronologia/locale/fr/marker_freq_weekly.voc`` containing
"hebdomadairement" -- a pure data addition (the ``.voc`` glob loader already
wires any ``marker_freq_weekly.voc`` file to the ``freq_weekly`` connector
key), no code change.

"mensuellement le lundi" stranding "le lundi" is a KNOWN, separate defect
(the monthly adverb path never learned a weekday qualifier to fold, unlike
the weekly one) and is explicitly OUT of this fix's scope -- pinned here as a
control so a future fix does not silently change its remainder.
"""
from datetime import datetime

import pytest

from chronologia.extract import extract_recurrence

LANG = "fr"
ANCHOR = datetime(2026, 8, 14, 10, 0)

_CASES = [
    # -- the defect: "hebdomadairement" must parse, both with and without
    # the "le" article before the weekday -----------------------------------
    ("hebdomadairement le lundi", "FREQ=WEEKLY;BYDAY=MO", ""),
    ("hebdomadairement lundi", "FREQ=WEEKLY;BYDAY=MO", ""),
    # -- control: bare adverb, no qualifier, unchanged ----------------------
    ("hebdomadairement", "FREQ=WEEKLY", ""),
    # -- control: the "chaque"-determiner sibling reading, unchanged --------
    ("chaque lundi", "FREQ=WEEKLY;BYDAY=MO", ""),
    # -- controls: the other three fr adverbs stay registered consistently -
    ("quotidiennement", "FREQ=DAILY", ""),
    ("annuellement", "FREQ=YEARLY", ""),
    # -- known, out-of-scope sibling defect: "mensuellement" folds no
    # weekday qualifier of its own -- pinned so it is not silently changed -
    ("mensuellement le lundi", "FREQ=MONTHLY", "le lundi"),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_hebdomadairement_registered(text, rrule, remainder):
    got = extract_recurrence(text, LANG, anchor=ANCHOR)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder
