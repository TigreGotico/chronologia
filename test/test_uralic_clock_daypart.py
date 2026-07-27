"""Regression tests: "<daypart> <hour>" is a CLOCK HOUR in the Uralic /
agglutinative locales (hu, eu, fi), extending #281 (which fixed en/es/fr).

A daypart/meridiem qualifier on an explicit hour sets am vs pm (morning = am;
afternoon/evening = pm => +12 when hour < 12) instead of stranding the numeral
and returning the whole daypart band.  These languages put the daypart word
BEFORE the hour ("délután 3 órakor", "arratsaldeko hiruretan") and/or spell the
hour with a glued case suffix ("háromkor", "hiruretan", "kolmelta"); the fix
registers the daypart words as MERIDIEM surfaces, folds the case-suffixed hour
numerals to a digit, and adds the leading-daypart clock order each needs.

The resolved civil day follows the engine's uniform prefer_future convention
(identical to "at 3 am"/"at 3 pm"): a past AM time rolls to the next day, a
future PM time stays on the anchor day.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan, AstroDate

ANCHOR = datetime(2017, 6, 27, 13, 4)   # Tue 2017-06-27 13:04


# -- Hungarian --------------------------------------------------------------

@pytest.mark.parametrize("text,expected", [
    ("délután 3 órakor", AstroDate(2017, 6, 27, 15, 0)),     # pm, future -> today
    ("délután háromkor", AstroDate(2017, 6, 27, 15, 0)),     # spelled + -kor
    ("holnap délután háromkor", AstroDate(2017, 6, 28, 15, 0)),  # tomorrow
    ("délelőtt 9 órakor", AstroDate(2017, 6, 28, 9, 0)),     # am, past -> +1 day
])
def test_hu_daypart_hour_is_clock(text, expected):
    span, rem = extract_timespan(text, "hu", ANCHOR)
    assert span.start == expected
    assert span.width.total_seconds() == 60
    assert "délután" not in rem and "délelőtt" not in rem
    assert "órakor" not in rem and "kor" not in rem


# -- Basque -----------------------------------------------------------------

@pytest.mark.parametrize("text,expected", [
    ("arratsaldeko hiruretan", AstroDate(2017, 6, 27, 15, 0)),   # pm -> today
    ("bihar arratsaldeko hiruretan", AstroDate(2017, 6, 28, 15, 0)),  # tomorrow
    ("goizeko hamarretan", AstroDate(2017, 6, 28, 10, 0)),       # am, past -> +1
])
def test_eu_daypart_hour_is_clock(text, expected):
    span, rem = extract_timespan(text, "eu", ANCHOR)
    assert span.start == expected
    assert span.width.total_seconds() == 60
    assert "arratsaldeko" not in rem and "goizeko" not in rem
    assert "hiruretan" not in rem and "hamarretan" not in rem


# -- Finnish ----------------------------------------------------------------

@pytest.mark.parametrize("text,expected", [
    ("kello kolmelta iltapäivällä", AstroDate(2017, 6, 27, 15, 0)),    # pm
    ("huomenna kello kolmelta iltapäivällä", AstroDate(2017, 6, 28, 15, 0)),
    ("kello yhdeksältä aamupäivällä", AstroDate(2017, 6, 28, 9, 0)),   # am -> +1
])
def test_fi_daypart_hour_is_clock(text, expected):
    span, rem = extract_timespan(text, "fi", ANCHOR)
    assert span.start == expected
    assert span.width.total_seconds() == 60
    assert "iltapäivällä" not in rem and "aamupäivällä" not in rem
    assert "kolmelta" not in rem and "yhdeksältä" not in rem


# -- Estonian control: the "at HOUR MERIDIEM" order already resolved --------

def test_et_still_resolves_afternoon_hour():
    span, _ = extract_timespan("homme kell kolm pärastlõunal", "et", ANCHOR)
    assert span.start == AstroDate(2017, 6, 28, 15, 0)
    assert span.width.total_seconds() == 60
