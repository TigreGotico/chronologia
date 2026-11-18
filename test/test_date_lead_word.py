# -*- coding: utf-8 -*-
"""The preposition, article or clock word that opens a date belongs to it.

"at 11:55 pm", "klokka 15:30", "om 9:00" and "el siguiente viernes" name a
clock time or a day, and the opening word is part of that expression, so
nothing of it is left over.  A word that does not open the date stays: "wake
me at half past 8 am please" keeps "wake me please", and "switch it on at 7"
keeps "switch it on", because "on" belongs to the verb.  A clock word opens a
clock time only, so "um Montag" keeps "um".  Anchor Tuesday 2017-06-27 13:04.
Every expected value is read off the calendar by hand: 30 June 2017 is a
Friday, 29 June a Thursday, 2 July a Sunday, 3 July a Monday.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_timespan
from ruling17 import moved

ANCHOR = datetime(2017, 6, 27, 13, 4)


@pytest.mark.parametrize("lang,text,start,rest", [
    ("en", "at 11:55 pm", datetime(2017, 6, 27, 23, 55), ""),
    ("en", "wake me at half past 8 am please", datetime(2017, 6, 28, 8, 30),
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
    ("de", "um halb neun abends", datetime(2017, 6, 27, 20, 30), ""),
    ("nl", "om middernacht", datetime(2017, 6, 28), ""),
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
    ("es", "ponme una alarma a las siete y cuarto de la mañana",
     datetime(2017, 6, 28, 7, 15), "ponme una alarma"),
    ("es", "cuándo es el siguiente viernes", datetime(2017, 6, 30), "cuándo es"),
    ("de", "an diesem Freitag", datetime(2017, 6, 30), ""),
    ("de", "ruf mich an diesem Freitag", datetime(2017, 6, 30), "ruf mich"),
    ("de", "treffen wir uns am nächsten Freitag", datetime(2017, 6, 30),
     "treffen wir uns"),
])
def test_the_opening_word_goes_with_the_date(lang, text, start, rest):
    span, remainder = extract_timespan(text, lang, ANCHOR)
    assert span.start_datetime == moved(start, ANCHOR)
    assert remainder == rest


@pytest.mark.parametrize("lang,text,rest", [
    ("en", "look at the stars on monday", "look at the stars"),
    ("nl", "ik wacht om je op donderdag", "ik wacht om je"),
    # a verb particle in front of the clock word stays with the verb
    ("en", "switch it on at 7", "switch it on"),
    ("en", "remind me to turn the lights on at 7",
     "remind me to turn the lights on"),
    ("de", "ruf mich an um 7", "ruf mich an"),
    ("de", "mach das Licht an um 7 Uhr", "mach das Licht an"),
    ("nb", "skru lyset på klokka 7", "skru lyset på"),
    # a clock word opens a clock time, not a day
    ("de", "um Montag", "um"),
    ("de", "es geht um morgen", "es geht um"),
    ("nl", "ik vraag om morgen vrij", "ik vraag om vrij"),
    ("nb", "klokka i morgen", "klokka"),
    ("et", "kell homme", "kell"),
    # a named day takes no preposition, so the word belongs to the verb
    ("en", "turn the lights on tomorrow", "turn the lights on"),
    ("en", "what's on tonight", "what's on"),
    ("sv", "tänd lampan på i morgon", "tänd lampan på"),
    # "ab" opens a span that chronologia does not read, so it stays
    ("de", "ab Montag arbeite ich", "ab arbeite ich"),
    # English puts no preposition in front of a this-phrase of a daypart or
    # a period, so the word in front of it belongs to the verb
    ("en", "turn it on this evening", "turn it on"),
    ("en", "is anything on this evening", "is anything on"),
    ("en", "what is on this weekend", "what is on"),
    ("en", "turn it on next friday", "turn it on"),
    ("en", "is anything on next friday", "is anything on"),
    ("en", "what is on this saturday", "what is on"),
    ("en", "look at next monday", "look at"),
    ("en", "switch it on next tuesday at 7", "switch it on"),
    # the article of a Spanish this-phrase belongs to the date, and the
    # Portuguese contraction does too; the verb keeps all of its own words
    ("es", "enciéndelo el próximo viernes", "enciéndelo"),
    ("es", "pon la tele el próximo lunes", "pon la tele"),
    ("pt", "liga-o na próxima sexta", "liga-o"),
    ("pt", "desliga a luz na próxima segunda", "desliga a luz"),
    # "um" in front of a year means "around": the reading is not a clock
    ("de", "das Haus wurde um 1900 gebaut", "das Haus wurde um gebaut"),
    ("de", "um 2030", "um"),
    # "an" governs the dative in a time phrase: a bare accusative phrase takes
    # no preposition, so the "an" before it is the particle of the verb
    ("de", "ruf mich an nächsten Freitag", "ruf mich an"),
    ("de", "ruf mich an diesen Freitag", "ruf mich an"),
    ("de", "mach das Licht an nächsten Montag", "mach das Licht an"),
    ("de", "mach das Licht an nächste Woche", "mach das Licht an"),
    # "um" in front of a dated day is not a clock word
    ("de", "um 8. Mai", "um"),
])
def test_a_word_that_does_not_touch_the_date_stays(lang, text, rest):
    _, remainder = extract_timespan(text, lang, ANCHOR)
    assert remainder == rest


@pytest.mark.parametrize("lang,text", [
    ("de", "um 8"),
    ("de", "um halb neun"),
    ("nl", "om kwart over negen"),
])
def test_a_clock_word_folds_in_front_of_a_clock(lang, text):
    _, remainder = extract_timespan(text, lang, ANCHOR)
    assert remainder == ""


@pytest.mark.xfail(strict=True, reason=(
    "tokens are casefolded, so the noun 'Morgen' (morning) matches the named "
    "day 'morgen' (tomorrow): chronologia reads tomorrow and 'am' stays"))
def test_am_morgen_is_the_morning():
    span, remainder = extract_timespan("am Morgen", "de", ANCHOR)
    assert span.end_datetime - span.start_datetime < timedelta(days=1)
    assert remainder == ""
