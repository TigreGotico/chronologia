# -*- coding: utf-8 -*-
"""extract_duration leaves a clock in "heures" alone.

"à 18 heures" and "alarme pour 7 heures" name a time of day, and
extract_timespan reads them as clocks (07:00 and 18:00).  A caller that tries a
length first must get None there, or it sets an alarm 18 hours from now.  A
count of hours with no clock marker before it stays a length: "pour 7 heures",
"il reste 3 heures", "un film de 2 heures".

Anchor: Tuesday 2017-06-27 13:04, so "demain" is Wednesday 2017-06-28.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_duration, extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)

CLOCKS = [
    ("mets une alarme pour 7 heures demain matin", datetime(2017, 6, 28, 7)),
    ("crée un rappel pour appeler maman demain à 18 heures",
     datetime(2017, 6, 28, 18)),
    ("à 18 heures", datetime(2017, 6, 27, 18)),
    ("réveille-moi à 6 heures demain", datetime(2017, 6, 28, 6)),
]

LENGTHS = [
    ("pour 7 heures", timedelta(hours=7), ""),
    ("il reste 3 heures", timedelta(hours=3), "il reste"),
    ("un film de 2 heures", timedelta(hours=2), "un film de"),
    ("mets un minuteur pour 7 heures", timedelta(hours=7), "mets un minuteur"),
    ("3 heures", timedelta(hours=3), ""),
    ("rendez-vous à 18 heures pour 2 heures", timedelta(hours=2),
     "rendez-vous à 18 heures"),
    ("réunion de 2 heures demain à 18 heures", timedelta(hours=2),
     "réunion de demain à 18 heures"),
]


@pytest.mark.parametrize("text,instant", CLOCKS)
def test_clock_is_no_length(text, instant):
    assert extract_duration(text, "fr", anchor=ANCHOR) is None
    assert extract_timespan(text, "fr", ANCHOR).span.start.datetime() == instant


@pytest.mark.parametrize("text,length,remainder", LENGTHS)
def test_count_without_clock_marker_is_a_length(text, length, remainder):
    found = extract_duration(text, "fr", anchor=ANCHOR)
    assert found.duration == length
    assert found.remainder == remainder
