# -*- coding: utf-8 -*-
"""A count of hours tied to a part of the day by "da" or "du" is a clock, even
after a noun and "de" (ruling 37).

The sources attest "da"/"du" plus a part of the day after an hour as the form
that names a clock: "Em textos para locução, prefira a forma: nove da manhã,
três da tarde" (Senado Federal, Manual de Comunicação, s.v. "Hora"); Priberam,
"manhã", sense 3 ("o avião chegou às 3 da manhã"); the Académie and Littré for
"onze heures du matin".  A period without an hour has its own forms: pt "de
manhã", "Entre o amanhecer e o meio-dia" (Priberam), and fr "le matin" in
absolute use (TLFi).  No source shows "N horas da noite" or "N heures du soir"
as a length.

So "le train de 8 heures du matin demain" is 08:00.  When "de" stands before a
bare pm hour and neither reading of the hour is inside the band of its part of
the day, no clock reading exists and the count is the length of an event in
that band: fr "dîner de deux heures du soir" (14:00 is no evening hour, and
the fr evening band opens at 18:00, CLDR day periods in
``chronologia/dayparts.py``).

Anchor: Friday 2026-01-30 10:00, so "demain" is 2026-01-31, "samedi" the same
day, "dimanche" 2026-02-01 and "ontem" 2026-01-29.  Clock hours are the written
hour moved to its half by the suffix word.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_event

ANCHOR = datetime(2026, 1, 30, 10)
SAT = datetime(2026, 1, 31)
SUN = datetime(2026, 2, 1)
FRI = datetime(2026, 1, 30)
THU = datetime(2026, 1, 29)

# lang, text, day, hour, minute
CLOCKS = [
    ("pt", "jantar de duas horas da noite amanhã", SAT, 2, 0),
    ("pt", "jantar de três horas da noite amanhã", SAT, 3, 0),
    ("pt", "festa de quatro horas da noite sábado", SAT, 4, 0),
    ("pt", "aula de três horas da manhã amanhã", SAT, 3, 0),
    ("pt", "estudei duas horas da manhã ontem", THU, 2, 0),
    ("fr", "cours de deux heures du matin demain", SAT, 2, 0),
    ("fr", "j'ai dormi deux heures du matin hier", THU, 2, 0),
    ("fr", "le train de 8 heures du matin demain", SAT, 8, 0),
    ("fr", "le vol de 7 heures du matin demain", SAT, 7, 0),
    ("fr", "la messe de 11 heures du matin dimanche", SUN, 11, 0),
    ("fr", "la séance de 9 heures du soir demain", SAT, 21, 0),
    ("fr", "le rendez-vous de 3 heures de l'après-midi demain", SAT, 15, 0),
    ("fr", "le train de 8h30 du matin demain", SAT, 8, 30),
    ("pt", "o comboio de 8 horas da noite amanhã", SAT, 20, 0),
    ("pt", "o autocarro de 7 horas da manhã amanhã", SAT, 7, 0),
    ("pt", "a missa de 10 horas da manhã domingo", SUN, 10, 0),
    ("pt", "o noticiário de 8 horas da noite", FRI, 20, 0),
    ("pt", "sessão de 9 horas da noite amanhã", SAT, 21, 0),
]

# lang, text, day, start hour, length in hours: no clock reading exists
BAND_LENGTHS = [
    ("fr", "dîner de deux heures du soir demain", SAT, 18, 2),
    ("fr", "dîner de trois heures du soir demain", SAT, 18, 3),
    ("fr", "soirée de quatre heures du soir samedi", SAT, 18, 4),
]

# lang, text, day, start hour, length in hours: a period with no hour
PERIODS = [
    ("pt", "reunião de duas horas de manhã amanhã", SAT, 6, 2),
    ("fr", "réunion de deux heures le matin demain", SAT, 4, 2),
]


@pytest.mark.parametrize("lang,text,day,hour,minute", CLOCKS)
def test_suffix_names_a_clock(lang, text, day, hour, minute):
    event = extract_event(text, lang, anchor=ANCHOR)
    assert event.duration is None
    assert event.span.start.datetime() == day + timedelta(hours=hour,
                                                          minutes=minute)


@pytest.mark.parametrize("lang,text,day,hour,length", BAND_LENGTHS)
def test_hour_outside_its_band_is_a_length_in_the_band(lang, text, day, hour,
                                                       length):
    event = extract_event(text, lang, anchor=ANCHOR)
    assert event.duration == timedelta(hours=length)
    assert event.span.start.datetime() == day + timedelta(hours=hour)


@pytest.mark.parametrize("lang,text,day,hour,length", PERIODS)
def test_period_form_carries_a_length(lang, text, day, hour, length):
    event = extract_event(text, lang, anchor=ANCHOR)
    assert event.duration == timedelta(hours=length)
    assert event.span.start.datetime() == day + timedelta(hours=hour)
