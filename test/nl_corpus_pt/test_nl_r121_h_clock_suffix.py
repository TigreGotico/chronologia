# -*- coding: utf-8 -*-
"""Regression for defect R121: Portuguese digital-clock "Nh"/"NhMM" notation
half-matched -- the digits bound HOUR but the "h" grain letter was stranded
as unconsumed remainder ("às 15h" -> 15:00 span, remainder "h").

French/Occitan already fold "20h30"/"20h" into an ``HH:MM`` CLOCK literal
before the grammar ever sees it (``_collapse_h_clock`` in
``chronologia/extract/numfold_romance.py``, wired through ``h_clock=True``
in ``_romance_prepass_fold``).  Portuguese's ``fold_pt`` never called that
collapse, so "15h" tokenized to HOUR="15" + word="h" and no pt ``clock_time``
order has a slot for a bare "h" -- it fell through the grammar untouched.
The fix calls ``_collapse_h_clock`` at the top of ``fold_pt`` too, exactly
mirroring the French pipeline, so the "h" is folded into the CLOCK token
and never reaches the grammar as an orphan word.

Anchor for extract_timespan cases is the shared pt corpus anchor,
2017-06-27 13:04 (Tuesday) -- see ``test/nl_corpus_pt/_corpus.py``.
"""
from chronologia import extract_recurrence

from ._corpus import ANCHOR, parse, span


# -- extract_timespan: the "h"/"hMM" clock literal must fully consume,
#    leaving a clean remainder -----------------------------------------------

def test_bare_hour_h_suffix():
    r = parse("às 15h")
    assert r is not None
    s, remainder = r
    assert (s.start.hour, s.start.minute) == (15, 0)
    assert "h" not in remainder.split()


def test_hour_minute_h_suffix():
    r = parse("15h30")
    assert r is not None
    s, remainder = r
    assert (s.start.hour, s.start.minute) == (15, 30)
    assert remainder == ""


def test_single_digit_hour_h_suffix():
    r = parse("9h")
    assert r is not None
    s, remainder = r
    assert (s.start.hour, s.start.minute) == (9, 0)
    assert "h" not in remainder.split()


def test_zero_padded_hour_and_minute_h_suffix():
    r = parse("09h00")
    assert r is not None
    s, remainder = r
    assert (s.start.hour, s.start.minute) == (9, 0)
    assert remainder == ""


def test_h_suffix_with_trailing_meridiem_phrase():
    r = parse("às 9h da manhã")
    assert r is not None
    s, remainder = r
    assert (s.start.hour, s.start.minute) == (9, 0)
    assert "h" not in remainder.split()


def test_embedded_h_suffix_in_full_sentence():
    r = parse(
        "reunião toda segunda-feira às 15h para revisar o orçamento"
    )
    assert r is not None
    s, remainder = r
    assert (s.start.hour, s.start.minute) == (15, 0)
    assert "h" not in remainder.split()


# -- extract_recurrence: the same "Nh" suffix inside a weekly rule ----------

def test_recurrence_h_suffix_clean_remainder():
    got = extract_recurrence("toda terça às 15h", "pt", anchor=ANCHOR)
    assert got is not None
    rule, remainder = got
    assert rule.to_string() == "FREQ=WEEKLY;BYDAY=TU;BYHOUR=15"
    assert remainder == ""


# -- control: French handles the identical "Nh" surface already; the fix
#    must not regress it -----------------------------------------------------

def test_french_control_still_clean():
    got = extract_recurrence("chaque mardi à 15h", "fr", anchor=ANCHOR)
    assert got is not None
    rule, remainder = got
    assert rule.to_string() == "FREQ=WEEKLY;BYDAY=TU;BYHOUR=15"
    assert remainder == ""


# -- adversarial: a bare "h" that is NOT a clock suffix must not be
#    swallowed as a stray digital-clock literal -----------------------------

def test_bare_h_word_not_swallowed():
    assert parse("a hora h") is None
