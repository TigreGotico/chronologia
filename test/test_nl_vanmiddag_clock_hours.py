# -*- coding: utf-8 -*-
"""nl "vanmiddag" is the afternoon of today, and "om 8 uur" is a clock time.

Wiktionary, "vanmiddag": "this afternoon, the afternoon of the current day".
The CLDR nl afternoon is [12:00, 18:00).  A clock time with its preposition
("om 8 uur", fr "à 8 heures", pt "às 8 horas") is no length, so
``extract_duration`` leaves it out; a count after another preposition ("voor
8 uur") and a count with no clock preposition in the language ("a 8 horas",
es: eight hours away) stay lengths.

Every expected instant is worked out by hand from the anchor, Tuesday
2017-06-27 13:04.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_duration, extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)


def test_vanmiddag_is_the_afternoon_of_today():
    res = extract_timespan(
        "laat me vanmiddag weten dat ik de loodgieter moet bellen", "nl",
        ANCHOR)
    assert res.span.start == datetime(2017, 6, 27, 12, 0)
    assert res.span.end == datetime(2017, 6, 27, 18, 0)
    assert res.remainder == "laat me weten dat ik de loodgieter moet bellen"


@pytest.mark.parametrize("text,hour", [
    ("vanmiddag om 3 uur", 15), ("vanmiddag om 5 uur", 17),
    ("vanmiddag om 15:00", 15)])
def test_vanmiddag_with_a_clock_is_today(text, hour):
    res = extract_timespan(text, "nl", ANCHOR)
    assert res.span.start == datetime(2017, 6, 27, hour, 0)
    assert res.remainder == ""


@pytest.mark.parametrize("text,lang", [
    ("om 8 uur", "nl"),
    ("om 8 uur 's ochtends", "nl"),
    ("herinner me eraan elke weekendochtend om 8 uur de planten water te "
     "geven", "nl"),
    ("à 8 heures", "fr"),
    ("às 8 horas", "pt"),
])
def test_a_clock_time_is_no_length(text, lang):
    assert extract_duration(text, lang) is None


@pytest.mark.parametrize("text,lang,hours,rest", [
    ("8 uur", "nl", 8, ""),
    ("voor 8 uur", "nl", 8, "voor"),
    ("over 8 uur", "nl", 8, "over"),
    ("ik wacht 8 uur", "nl", 8, "ik wacht"),
    ("a 8 horas", "es", 8, "a"),
])
def test_a_count_of_hours_without_a_clock_preposition_is_a_length(
        text, lang, hours, rest):
    got = extract_duration(text, lang)
    assert got.duration == timedelta(hours=hours)
    assert got.remainder == rest
