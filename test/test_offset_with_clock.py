# -*- coding: utf-8 -*-
"""A day-or-coarser offset followed by a clock reads the clock on the day the
offset names ("in two days at 3 pm").  A sub-day offset keeps its own minute.

Anchor Tuesday 27 June 2017 13:04.  Each expected instant is hand arithmetic:
+2 days is 29 June, +3 days is 30 June, +5 days is 2 July, +2 weeks is
11 July, +1 month is 27 July, -3 days is 24 June.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)

OFFSET_WITH_CLOCK = [
    ("en", "in two days at three in the afternoon",
     datetime(2017, 6, 29, 15, 0)),
    ("en", "in two days at 3 pm", datetime(2017, 6, 29, 15, 0)),
    ("en", "remind me in 3 days at 9:30", datetime(2017, 6, 30, 9, 30)),
    ("en", "in two weeks at 9 am", datetime(2017, 7, 11, 9, 0)),
    ("en", "in a month at 9 am", datetime(2017, 7, 27, 9, 0)),
    ("en", "3 days ago at 9 am", datetime(2017, 6, 24, 9, 0)),
    ("de", "in zwei tagen um 15 uhr", datetime(2017, 6, 29, 15, 0)),
    ("de", "in zwei wochen um 9 uhr", datetime(2017, 7, 11, 9, 0)),
    ("de", "setze den termin in 5 tagen um halb 10",
     datetime(2017, 7, 2, 9, 30)),
    ("es", "dentro de dos días a las tres de la tarde",
     datetime(2017, 6, 29, 15, 0)),
    ("es", "en dos semanas a las 9 de la mañana", datetime(2017, 7, 11, 9, 0)),
    ("pt", "daqui a dois dias às três da tarde", datetime(2017, 6, 29, 15, 0)),
    ("pt", "daqui a duas semanas às 9 da manhã", datetime(2017, 7, 11, 9, 0)),
    ("pt", "dentro de três dias às 15:30", datetime(2017, 6, 30, 15, 30)),
    ("fr", "dans deux jours à 15 heures", datetime(2017, 6, 29, 15, 0)),
    ("fr", "dans deux semaines à 9 heures", datetime(2017, 7, 11, 9, 0)),
    ("it", "tra due giorni alle 15", datetime(2017, 6, 29, 15, 0)),
    ("it", "fra due settimane alle 9", datetime(2017, 7, 11, 9, 0)),
    ("nl", "over twee dagen om 15 uur", datetime(2017, 6, 29, 15, 0)),
    ("nl", "over twee weken om 9 uur", datetime(2017, 7, 11, 9, 0)),
    ("ca", "d'aquí a dos dies a les tres de la tarda",
     datetime(2017, 6, 29, 15, 0)),
    ("ca", "d'aquí a dues setmanes a les 9 del matí",
     datetime(2017, 7, 11, 9, 0)),
    ("gl", "dentro de dous días ás tres da tarde",
     datetime(2017, 6, 29, 15, 0)),
    ("ro", "peste două zile la ora 15", datetime(2017, 6, 29, 15, 0)),
    ("pl", "za dwa dni o 15:00", datetime(2017, 6, 29, 15, 0)),
    ("cs", "za dva dny v 15:00", datetime(2017, 6, 29, 15, 0)),
    ("ru", "через два дня в 15:00", datetime(2017, 6, 29, 15, 0)),
    ("uk", "через два дні о 15:00", datetime(2017, 6, 29, 15, 0)),
    ("sv", "om två dagar klockan 15", datetime(2017, 6, 29, 15, 0)),
    ("da", "om to dage klokken 15", datetime(2017, 6, 29, 15, 0)),
    ("nb", "om to dager klokken 15", datetime(2017, 6, 29, 15, 0)),
    ("fi", "kahden päivän päästä kello 15", datetime(2017, 6, 29, 15, 0)),
    ("he", "בעוד שלושה ימים בשעה 15:30", datetime(2017, 6, 30, 15, 30)),
    ("tr", "2 gün sonra saat 15:00", datetime(2017, 6, 29, 15, 0)),
    ("hu", "két nap múlva 15 órakor", datetime(2017, 6, 29, 15, 0)),
    ("el", "σε δύο μέρες στις 3 το απόγευμα", datetime(2017, 6, 29, 15, 0)),
]


@pytest.mark.parametrize("lang,text,expected", OFFSET_WITH_CLOCK)
def test_the_clock_lands_on_the_offset_day(lang, text, expected):
    assert extract_timespan(text, lang, ANCHOR).span.start.datetime() \
        == expected


# no clock in the text, or an hour offset: the offset keeps the anchor minute
OFFSET_ALONE = [
    ("en", "in 2 hours at 3 pm", datetime(2017, 6, 27, 15, 4)),
    ("de", "in 2 stunden um 15 uhr", datetime(2017, 6, 27, 15, 4)),
    ("en", "in 3 days", datetime(2017, 6, 30, 13, 4)),
    ("pt", "daqui a três dias", datetime(2017, 6, 30, 13, 4)),
    ("es", "dentro de tres días", datetime(2017, 6, 30, 13, 4)),
]


@pytest.mark.parametrize("lang,text,expected", OFFSET_ALONE)
def test_the_offset_keeps_the_anchor_clock(lang, text, expected):
    assert extract_timespan(text, lang, ANCHOR).span.start.datetime() \
        == expected


@pytest.mark.parametrize("lang,text,anchor,expected", [
    # 3 September 2117 + 3 days is 6 September; 5 June 2018 + 3 days is 8 June
    ("de", "in 3 tagen um 15 uhr", datetime(2117, 9, 3, 13, 30),
     datetime(2117, 9, 6, 15, 0)),
    ("he", "תזכיר לי בעוד שלושה ימים בשעה 15:30", datetime(2018, 6, 5, 9, 0),
     datetime(2018, 6, 8, 15, 30)),
])
def test_the_clock_lands_on_the_offset_day_from_any_anchor(
        lang, text, anchor, expected):
    assert extract_timespan(text, lang, anchor).span.start.datetime() \
        == expected
