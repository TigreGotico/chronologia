# -*- coding: utf-8 -*-
"""The preposition, article or clock word that opens a date belongs to it.

"at 11:55 pm", "klokka 15:30", "om 9:00" and "il 25 dicembre" name a clock
time or a day, and the opening word is part of that expression, so nothing of
it is left over.  A word that does not touch the date stays: "wake me at
half past 8 please" keeps "wake me please", and "call a friend on monday" keeps
"call a friend".  Anchor Tuesday 2017-06-27 13:04.  Every expected value is
read off the calendar by hand: 30 June 2017 is a Friday, 29 June a Thursday,
2 July a Sunday.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)


@pytest.mark.parametrize("lang,text,start,rest", [
    ("en", "at 11:55 pm", datetime(2017, 6, 27, 23, 55), ""),
    ("en", "wake me at half past 8 please", datetime(2017, 6, 28, 8, 30),
     "wake me please"),
    ("en", "meeting on June 15 at three in the afternoon",
     datetime(2018, 6, 15, 15, 0), "meeting"),
    ("en", "call me on 2017-06-30 at 5pm", datetime(2017, 6, 30, 17, 0),
     "call me"),
    ("nb", "klokka 15:30", datetime(2017, 6, 27, 15, 30), ""),
    ("nb", "møtet er på fredag klokka 14", datetime(2017, 6, 30, 14, 0),
     "møtet er"),
    ("nn", "klokka 15:30", datetime(2017, 6, 27, 15, 30), ""),
    ("nl", "om 9:00", datetime(2017, 6, 28, 9, 0), ""),
    ("nl", "laten we afspreken op donderdag", datetime(2017, 6, 29), "laten we afspreken"),
    ("de", "erinnere mich um 10:45 abends", datetime(2017, 6, 27, 22, 45),
     "erinnere mich"),
    ("de", "erinnere mich mama anzurufen am dritten august",
     datetime(2017, 8, 3), "erinnere mich mama anzurufen"),
    ("de", "wie ist das wetter an diesem donnerstag?", datetime(2017, 6, 29),
     "wie ist das wetter"),
    ("sv", "påminn mig att klippa mig på fredag", datetime(2017, 6, 30),
     "påminn mig att klippa mig"),
    ("da", "på søndag", datetime(2017, 7, 2), ""),
    ("bg", "в 23:30", datetime(2017, 6, 27, 23, 30), ""),
    ("bg", "среща на 15 август", datetime(2017, 8, 15), "среща"),
    ("el", "ραντεβού στις 5 Ιουνίου", datetime(2018, 6, 5), "ραντεβού"),
    ("he", "פגישה ב15 ביוני", datetime(2018, 6, 15), "פגישה"),
    ("fa", "ساعت ۱۴:۳۰", datetime(2017, 6, 27, 14, 30), ""),
    ("et", "kell 15:30", datetime(2017, 6, 27, 15, 30), ""),
    ("ro", "pe 15 august", datetime(2017, 8, 15), ""),
    ("es", "ponme una alarma a las siete y cuarto", datetime(2017, 6, 28, 7, 15),
     "ponme una alarma"),
    ("es", "cuándo es el siguiente viernes", datetime(2017, 6, 30), "cuándo es"),
])
def test_the_opening_word_goes_with_the_date(lang, text, start, rest):
    span, remainder = extract_timespan(text, lang, ANCHOR)
    assert span.start_datetime == start
    assert remainder == rest


@pytest.mark.parametrize("lang,text,rest", [
    ("en", "look at the stars on monday", "look at the stars"),
    ("nl", "ik wacht om je op donderdag", "ik wacht om je"),
])
def test_a_word_that_does_not_touch_the_date_stays(lang, text, rest):
    _, remainder = extract_timespan(text, lang, ANCHOR)
    assert remainder == rest
