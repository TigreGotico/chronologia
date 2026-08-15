# -*- coding: utf-8 -*-
"""R175: two Romanian defects.

1. "luni dupa-amiaza" (afternoon) anchored noon as a POINT instead of the
   afternoon BAND, because the tokenizer splits the hyphen and the bare
   remaining word "amiaza" is ALSO this locale's word for noon
   (``clock_landmark_720.voc``). Fixed by shipping
   ``daypart_dupa_amiaza_ro.voc`` so the hyphen-split, loader-reglued surface
   binds the band (``chronologia/dayparts.py``, ``[12:00, 18:00)``, CLDR 47
   ro) before the bare "amiaza" noon reading can claim half of it -- exactly
   the fix French "après-midi" already got in
   ``test/nl_corpus_fr/test_nl_r165_apres_midi.py``. "luni la prânz" (noon)
   is a genuine point and must keep resolving as one.

2. "în fiecare luni" stranded the leading preposition "în" in the remainder
   ("fiecare" alone already absorbs into the WEEKLY;BYDAY rule the same way
   English "every" and Spanish "cada" do -- "în" is the idiomatic connector
   Romanian adds and carries no meaning of its own). Fixed in
   ``chronologia/extract/nseries.py``'s ``_recur_every`` weekday branch by
   absorbing an immediately-leading ``marker_in.voc`` token. Scoped to the
   plain "<in> fiecare <weekday>" frame only -- "în fiecare zi de luni" goes
   through the DAILY unit branch instead and is deliberately left unread here
   (a separate, native-review-pending FREQ question, not this defect).

Gold band bounds are the CLDR 47 ro transcription in
``chronologia/dayparts.py`` (dupa_amiaza ``[12:00, 18:00)``), the same
authority ``test_nl_daypart.py`` uses for dimineata/seara/noapte. The weekday
math is the shared corpus ANCHOR (Tuesday 2017-06-27 13:04) rolled forward to
the next Monday by hand: 2017-07-03.
"""
import pytest

from chronologia.astrodate import AstroDate
from chronologia.extract import extract_recurrence

from ._corpus import ANCHOR, span, start_end

LANG = "ro"


def test_weekday_afternoon_band():
    # 2017-06-27 (Tue) -> next Monday 2017-07-03; band [12:00, 18:00).
    assert start_end("luni dupa-amiaza") == (
        AstroDate(2017, 7, 3, 12, 0),
        AstroDate(2017, 7, 3, 18, 0),
    )


def test_weekday_afternoon_band_diacritics():
    assert start_end("luni după-amiaza") == (
        AstroDate(2017, 7, 3, 12, 0),
        AstroDate(2017, 7, 3, 18, 0),
    )


def test_bare_afternoon_band():
    s = span("dupa-amiaza")
    assert (s.start, s.end) == (
        AstroDate(ANCHOR.year, ANCHOR.month, ANCHOR.day, 12, 0),
        AstroDate(ANCHOR.year, ANCHOR.month, ANCHOR.day, 18, 0),
    )


def test_control_weekday_dimineata_composes():
    """Sibling daypart this file's fix must not regress."""
    assert start_end("luni dimineața") == (
        AstroDate(2017, 7, 3, 5, 0),
        AstroDate(2017, 7, 3, 12, 0),
    )


def test_control_weekday_seara_composes():
    assert start_end("luni seara") == (
        AstroDate(2017, 7, 3, 18, 0),
        AstroDate(2017, 7, 3, 22, 0),
    )


def test_control_la_pranz_stays_a_point():
    """"la prânz" (at noon) is a genuine minimal-width point, not a band."""
    assert start_end("luni la prânz") == (
        AstroDate(2017, 7, 3, 12, 0),
        AstroDate(2017, 7, 3, 12, 1),
    )


@pytest.mark.parametrize("text,rrule", [
    ('în fiecare luni', 'FREQ=WEEKLY;BYDAY=MO'),
    ('în fiecare vineri', 'FREQ=WEEKLY;BYDAY=FR'),
])
def test_leading_preposition_absorbed(text, rrule):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got.recurrence.to_string() == rrule
    assert got.remainder == ''


def test_control_bare_fiecare_luni_unaffected():
    """Sibling this file's fix must not regress: no leading preposition."""
    got = extract_recurrence('fiecare luni', LANG)
    assert got.recurrence.to_string() == 'FREQ=WEEKLY;BYDAY=MO'
    assert got.remainder == ''


def test_control_in_fiecare_zi_de_luni_unchanged():
    """"în fiecare zi de luni" is a separate, needs-native-check FREQ item;
    this file's leading-preposition fix is scoped to the weekday-only branch
    and must not touch this DAILY-unit reading or its remainder."""
    got = extract_recurrence('în fiecare zi de luni', LANG)
    assert got.recurrence.to_string() == 'FREQ=DAILY'
    assert got.remainder == 'în de luni'
