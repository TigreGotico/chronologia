# -*- coding: utf-8 -*-
"""R141 (French) -- same offset-before-a-relative-day-word-plus-clock defect
as ``test/nl_corpus_en/test_nl_r141_offset_relday_clock.py`` (see that file's
docstring for the full root-cause writeup: the ``DAYUNIT``-slot fix to the
``named_day_after``/``named_day_before`` idiom grammar).

FRENCH-SPECIFIC AMBIGUITY -- "avant-hier"/"après-demain" idioms:

French spells "the day before yesterday" and "the day after tomorrow" as
their OWN two-word ``named_day`` vocabulary surfaces ("avant hier"/"avant-
hier", "après demain"/"après-demain" -- see ``named_day_-2.voc``/
``named_day_2.voc``), not through the ``named_day_before``/``named_day_after``
grammar construction this fix touches. When an offset marker's own surface
happens to be the FIRST WORD of one of those idioms ("avant" + "hier",
"après" + "demain"), a preceding quantified unit ("une heure avant hier")
is genuinely ambiguous between:

  (a) "one hour before YESTERDAY" -- "avant" as the offset marker, "hier" as
      the bare DAY_WORD reference (the reading a human almost always means
      here, since "avant avant-hier" would be needed to say "one hour before
      THE-DAY-BEFORE-YESTERDAY"), and
  (b) "one hour" + the "avant-hier" idiom read as its own fixed phrase.

Unlike the Spanish "mañana" collision (a grammar-construction-level tie this
fix resolves with a veto), the French idiom is matched through the tokenizer/
prematch multi-word vocabulary fold -- BEFORE the grammar/matcher stage the
veto mechanism operates at -- so "avant hier"/"après demain" are already
fused into a single ``named_day`` match by the time any offset-aware pass
could tell "avant"/"après" apart from the idiom's own first word. Resolving
that ambiguity would require reworking the multi-word idiom fold itself, a
strictly larger change than R141's scope (composing an offset onto an
ALREADY-resolved rel-day reference). It is left UNFIXED and documented here:
"une heure avant hier à 9h" and "une heure après demain à 9h" still
mis-resolve (the idiom wins the fold, then the leading unit is stranded /
misread) -- these two tests pin the CURRENT shape as a regression guard, not
as a claim of correctness. Every OTHER before/after x tomorrow/today/
yesterday combination in French has no such collision ("avant demain",
"après aujourd'hui", "avant aujourd'hui", "après hier" are none of them a
French idiom's own first two words) and is fixed and asserted correct below.

Expected values are independently hand-computed against the anchor, never
read back from the parser.
"""
from datetime import datetime

import pytest

from chronologia.extract import extract_timespan

LANG = "fr"
_A = datetime(2026, 8, 12, 10, 0)  # Wednesday


def _start_end(text, anchor=_A):
    r = extract_timespan(text, LANG, anchor)
    assert r is not None, f"{text!r} did not parse (expected a span)"
    return r[0].start, r[0].end


@pytest.mark.parametrize("text,start", [
    ("une heure avant demain à 9h", datetime(2026, 8, 13, 8, 0)),
    ("une heure avant aujourd'hui à 9h", datetime(2026, 8, 12, 8, 0)),
    ("une heure après aujourd'hui à 9h", datetime(2026, 8, 12, 10, 0)),
    ("une heure après hier à 9h", datetime(2026, 8, 11, 10, 0)),
])
def test_offset_composes_with_relday_clock_no_idiom_collision(text, start):
    got_start, got_end = _start_end(text)
    assert got_start == start
    assert (got_end - got_start).total_seconds() == 60


@pytest.mark.parametrize("text,start,end", [
    # midnight crossing BACKWARD ("avant demain" has no idiom collision).
    ("deux heures avant demain à 1h",
     datetime(2026, 8, 12, 23, 0), datetime(2026, 8, 12, 23, 1)),
    # midnight crossing FORWARD ("après hier" has no idiom collision).
    ("deux heures après hier à 23h",
     datetime(2026, 8, 12, 1, 0), datetime(2026, 8, 12, 1, 1)),
])
def test_midnight_crossing_relday(text, start, end):
    got_start, got_end = _start_end(text)
    assert got_start == start
    assert got_end == end


def test_remainder_is_empty_not_stranded():
    r = extract_timespan("une heure avant demain à 9h", LANG, _A)
    assert r.remainder == ""


# -- controls: pinned pre-existing behaviour this fix must NOT disturb ------

def test_control_clock_first_order_unaffected():
    got_start, got_end = _start_end("une heure avant 9h demain")
    assert got_start == datetime(2026, 8, 13, 8, 0)
    assert got_end == datetime(2026, 8, 13, 8, 1)


def test_control_weekday_ref_unaffected():
    # 2026-08-12 is a Wednesday; the next Monday is 2026-08-17.
    got_start, got_end = _start_end("une heure avant lundi à 9h")
    assert got_start == datetime(2026, 8, 17, 8, 0)
    assert got_end == datetime(2026, 8, 17, 8, 1)


def test_control_no_clock_subday_offset_still_floors_to_day():
    got_start, got_end = _start_end("une demi-heure avant demain")
    assert got_start == datetime(2026, 8, 12, 0, 0)
    assert got_end == datetime(2026, 8, 13, 0, 0)


@pytest.mark.parametrize("text,start,end", [
    ("avant-hier", datetime(2026, 8, 10, 0, 0), datetime(2026, 8, 11, 0, 0)),
    ("avant hier", datetime(2026, 8, 10, 0, 0), datetime(2026, 8, 11, 0, 0)),
    ("après-demain", datetime(2026, 8, 14, 0, 0), datetime(2026, 8, 15, 0, 0)),
    ("après demain", datetime(2026, 8, 14, 0, 0), datetime(2026, 8, 15, 0, 0)),
])
def test_control_bare_idiom_unaffected(text, start, end):
    # the idiom itself, bare (no leading offset marker at all), is
    # completely untouched by this fix -- hyphenated and space-separated
    # spellings both resolve to the same +/-2-day idiom reading.
    got_start, got_end = _start_end(text)
    assert got_start == start
    assert got_end == end


# -- documented, UNFIXED ambiguity: "avant hier" / "après demain" ----------

def test_known_unfixed_ambiguity_avant_hier_with_offset_and_clock():
    # KNOWN SEPARATE issue, explicitly out of scope for R141 (see module
    # docstring): the "avant-hier" idiom's multi-word fold wins over the
    # "avant" + bare "hier" + offset reading, before the offset pass ever
    # runs. This pins the CURRENT (mis-resolved) shape as a regression
    # guard only -- not a claim that this is the right answer.
    r = extract_timespan("une heure avant hier à 9h", LANG, _A)
    assert r is not None
    assert r[0].start == datetime(2026, 8, 13, 1, 0)
    assert r.remainder == "avant hier à 9:00"


def test_known_unfixed_ambiguity_apres_demain_with_offset_and_clock():
    # same idiom-fold collision, mirrored for "après-demain".
    r = extract_timespan("une heure après demain à 9h", LANG, _A)
    assert r is not None
    assert r[0].start == datetime(2026, 8, 13, 1, 0)
    assert r.remainder == "après demain à 9:00"
