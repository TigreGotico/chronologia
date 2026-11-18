# -*- coding: utf-8 -*-
"""A noun, "de" and a count of hours is a length, whatever clock suffix follows.

pt "jantar de duas horas da noite amanhã" is a two-hour dinner in the evening
tomorrow, and fr "dîner de deux heures du soir demain" the same.  The "de"
joins the noun to the length it lasts (Priberam, "de": "Une ao nome o seu
complemento"; CNRTL, "de": "La durée. Une guerre de vingt ans.").  The clock
suffix ("da noite", "du soir") names the part of the day, and the part of the
day gives the start.  Without "de" the suffix ties the hour to the part of the
day: "jantar nove horas da noite" is 21:00.

Anchor: Friday 2026-01-30 10:00, so tomorrow is Saturday 2026-01-31.  The
start is the day period the locale lists for the suffix word: evening starts
at 19:00 in pt and 18:00 in fr, morning at 06:00 in pt and 04:00 in fr (CLDR
day periods, ``chronologia/dayparts.py``).
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_event

ANCHOR = datetime(2026, 1, 30, 10)
TOMORROW = datetime(2026, 1, 31)

LENGTHS = [
    ("pt", "jantar de duas horas da noite amanhã", 19, 2, "jantar"),
    ("pt", "jantar de três horas da noite amanhã", 19, 3, "jantar"),
    ("pt", "festa de quatro horas da noite sábado", 19, 4, "festa"),
    ("pt", "aula de três horas da manhã amanhã", 6, 3, "aula"),
    ("fr", "dîner de deux heures du soir demain", 18, 2, "dîner"),
    ("fr", "dîner de trois heures du soir demain", 18, 3, "dîner"),
    ("fr", "soirée de quatre heures du soir samedi", 18, 4, "soirée"),
    ("fr", "cours de deux heures du matin demain", 4, 2, "cours"),
]

CLOCKS = [
    ("pt", "jantar às duas da noite amanhã", 2),
    ("pt", "jantar nove horas da noite amanhã", 21),
    ("fr", "dîner à deux heures du matin demain", 2),
]


@pytest.mark.parametrize("lang,text,hour,length,summary", LENGTHS)
def test_noun_de_count_is_a_length(lang, text, hour, length, summary):
    event = extract_event(text, lang, anchor=ANCHOR)
    assert event.duration == timedelta(hours=length)
    assert event.span.start.datetime() == TOMORROW + timedelta(hours=hour)
    assert event.summary == summary


@pytest.mark.parametrize("lang,text,hour", CLOCKS)
def test_no_de_keeps_the_clock(lang, text, hour):
    event = extract_event(text, lang, anchor=ANCHOR)
    assert event.duration is None
    assert event.span.start.datetime() == TOMORROW + timedelta(hours=hour)
