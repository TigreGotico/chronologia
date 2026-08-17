"""Occitan vocabulary defects reported by a native speaker (r192), source:
https://github.com/OpenVoiceOS/ovos-date-parser/issues/300 -- a different
repo (ovos-date-parser); reused here only for the attested surfaces since
this repo (chronologia) carries its own oc locale.

Covers: the native "day before yesterday" forms that were previously
shadowed by the French-calque "abansièr" ('ièr' silently won and returned
yesterday); the native "last/previous" surfaces in marker_last.voc; the
afternoon meridiem multiword surfaces; the night clock band; and the two
spelling variants of the digit 8 ("uèit"/"uòch") the folder now reads via a
word_map pre-pass ahead of ovos_number_parser.numbers_oc.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, start, start_end, AstroDate

#: 2017-06-27 (Tuesday) is the corpus anchor; "ièr" is 06-26, the day before
#: yesterday ("davant-ièr" and its attested synonyms) is 06-25.
DAVANT_IER_DAY = AstroDate(2017, 6, 25)
IER_DAY = AstroDate(2017, 6, 26)


@pytest.mark.parametrize("text", [
    "davant-ièr", "davant ièr", "davant-ier", "davant ier",
    "ièr delà", "ièr delai", "passat ièr",
])
def test_davant_ier_day_before_yesterday(text):
    s, e = start_end(text)
    assert s == DAVANT_IER_DAY
    assert e - s == timedelta(days=1)


def test_abansier_control_still_parses():
    """The pre-existing French-calque form is kept (native speaker rejects
    it as a translation, but removing it would regress a form that already
    parses); it must still resolve to the same day."""
    s, e = start_end("abansièr")
    assert s == DAVANT_IER_DAY
    assert e - s == timedelta(days=1)


def test_ier_stays_yesterday():
    """Negative control: plain 'ièr' must not be shifted by the new -2 day
    surfaces -- it still names yesterday, one day after davant-ièr."""
    s, e = start_end("ièr")
    assert s == IER_DAY
    assert e - s == timedelta(days=1)


@pytest.mark.parametrize("text", ["lo darrèr an", "l'an darrièir"])
def test_marker_last_darrer_darrieir_year(text):
    s, e = start_end(text)
    assert s == AstroDate(2016, 1, 1)
    assert e == AstroDate(2017, 1, 1)


@pytest.mark.parametrize("text", ["lo precedent mes", "los precedents mes"])
def test_marker_last_precedent_month(text):
    s, e = start_end(text)
    assert s == AstroDate(2017, 5, 1)
    assert e == AstroDate(2017, 6, 1)


@pytest.mark.parametrize("text", [
    "tres oras après miègjorn", "tres oras après merende",
    "tres oras aprèp merende", "tres oras après dinnar",
    "tres oras aprèp dinnar", "tres oras vesprada",
])
def test_afternoon_meridiem_shifts_hour_plus_12(text):
    # mirrors the sibling-locale pm convention (see test_nl_dates_clock.py's
    # "sèt oras del ser" -> 19:00): a spoken 1..11 hour + a pm-band marker
    # shifts by +12h, same calendar day as the anchor.
    assert start(text) == AstroDate(2017, 6, 27, 15, 0)


@pytest.mark.parametrize("text,hour", [
    ("a las dètz de la nuèch", 22),
    ("a las dètz de la nuèit", 22),
    ("a las dètz de la nèit", 22),
    ("a las dètz de la nèt", 22),
    ("a las dètz de la nèch", 22),
    ("a las dètz de la nuòch", 22),
    ("a las dètz de la anuèch", 22),
    ("a las onze de la nèit", 23),
    ("a las dos de la nuèch", 2),
])
def test_night_band_surfaces(text, hour):
    # NIGHT is a midnight-crossing band (see clock_meridiem_night.voc): a
    # spoken hour 6..11 shifts +12 into the evening, matching es/ca/an.
    assert start(text) == AstroDate(2017, 6, 27 if hour >= 12 else 28, hour, 0)


@pytest.mark.parametrize("text", ["a uèch oras", "a uèit oras", "a uòch oras"])
def test_eight_oclock_spelling_variants(text):
    # "uèch" is the only spelling ovos_number_parser.numbers_oc reads;
    # "uèit"/"uòch" are attested variants folded via the new word_map
    # pre-pass in numfold_romance.py's fold_oc.
    assert start(text) == AstroDate(2017, 6, 28, 8, 0)
