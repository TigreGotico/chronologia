"""Regression tests for three silent-wrong extraction defects:

A. "<hour> in the <daypart>" is a CLOCK HOUR, not the whole daypart band.
   A daypart/meridiem qualifier on a bare hour sets am vs pm (morning = am;
   afternoon/evening/pm => +12 when hour < 12).  Covered for en, es and fr.
B. Named sun events ("sunset today") compose the sun instant with the deictic
   day -- DEFERRED (extraction layer has no location contract; see module docs
   and the PR).  Documented here as xfail so the gap is visible.
C. A holiday-name "Night" ("Guy Fawkes Night") must not be hijacked as the
   night daypart, stranding the proper noun and returning tonight's band.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan, AstroDate

ANCHOR = datetime(2017, 6, 27, 13, 4)   # Tue 2017-06-27 13:04


# -- Defect A: "<hour> in the <daypart>" is a clock hour --------------------

# The daypart qualifier sets am vs pm on the bare hour; the resolved civil day
# then follows the engine's uniform prefer_future convention (identical to
# "at 3 am"/"at 3 pm"): a past AM time rolls to the next day, a future PM time
# stays on the anchor day.  What the defect fixed is the stranded numeral and
# the whole-band return -- the reading is now a minute-wide clock hour.
@pytest.mark.parametrize("text,expected", [
    ("3 in the morning", AstroDate(2017, 6, 28, 3, 0)),    # am, past -> +1 day
    ("7 in the morning", AstroDate(2017, 6, 28, 7, 0)),    # am, past -> +1 day
    ("3 in the afternoon", AstroDate(2017, 6, 27, 15, 0)),  # pm, future -> today
    ("5 in the evening", AstroDate(2017, 6, 27, 17, 0)),    # pm, future -> today
    ("at 3 in the afternoon", AstroDate(2017, 6, 27, 15, 0)),
])
def test_en_hour_in_the_daypart_is_clock(text, expected):
    span, rem = extract_timespan(text, "en", ANCHOR)
    assert span.start == expected
    assert span.width.total_seconds() == 60            # minute-wide, not a band
    assert "morning" not in rem and "afternoon" not in rem and "evening" not in rem


def test_es_pm_on_bare_hour():
    # "a las 3 pm" -> 15:00 (pm sets afternoon; meridiem no longer dropped)
    span, _ = extract_timespan("a las 3 pm", "es", ANCHOR)
    assert span.start == AstroDate(2017, 6, 27, 15, 0)


def test_es_de_la_tarde_still_works():
    span, _ = extract_timespan("a las 3 de la tarde", "es", ANCHOR)
    assert span.start == AstroDate(2017, 6, 27, 15, 0)


def test_fr_apres_midi_on_bare_hour():
    span, rem = extract_timespan("à trois heures de l'après-midi", "fr", ANCHOR)
    assert span.start == AstroDate(2017, 6, 27, 15, 0)
    assert "après-midi" not in rem


# -- Defect A must not disturb the existing clock/daypart readings ----------

def test_en_at_3_pm_unchanged():
    span, _ = extract_timespan("at 3 pm", "en", ANCHOR)
    assert span.start == AstroDate(2017, 6, 27, 15, 0)


def test_en_this_morning_still_band():
    span, _ = extract_timespan("this morning", "en", ANCHOR)
    assert span.start == AstroDate(2017, 6, 27, 6, 0)
    assert span.end == AstroDate(2017, 6, 27, 12, 0)


def test_en_bare_hour_is_not_a_clock():
    # a bare number must NOT be read as a clock time (no meridiem present)
    assert extract_timespan("3", "en", ANCHOR) is None


# -- Defect C: holiday-name "Night" is not the night daypart ----------------

@pytest.mark.parametrize("text", [
    "Guy Fawkes Night",
    "Bonfire Night",
    "Twelfth Night",
])
def test_en_proper_noun_night_not_daypart(text):
    # These holidays are not in the en holiday DB, so the result must be None,
    # never tonight's 21:00-06:00 band with the proper noun stranded.
    res = extract_timespan(text, "en", ANCHOR)
    assert res is None, f"{text!r} -> {res}"


def test_en_tonight_still_band():
    span, _ = extract_timespan("tonight", "en", ANCHOR)
    assert span.start == AstroDate(2017, 6, 27, 21, 0)
    assert span.end == AstroDate(2017, 6, 28, 6, 0)


# -- Defect B: sun-event instants (DEFERRED) --------------------------------

@pytest.mark.xfail(reason="B deferred: extraction layer has no location "
                          "contract; sun_events() needs lat/lon with no "
                          "safe default. See PR.", strict=True)
def test_en_sunset_today_is_instant():
    span, rem = extract_timespan("sunset today", "en", ANCHOR)
    assert span.width.total_seconds() < 3600          # an instant, not a day
    assert "sunset" not in rem
