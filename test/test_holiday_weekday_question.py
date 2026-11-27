"""A holiday name that is the subject of a question about its weekday is a
date: "is christmas on a saturday", "Capodanno cadrà di giovedì?".

The anchor is Saturday 2026-10-17.  The expected days are fixed calendar
dates, the next one after the anchor.  Spanish and Galician Mother's Day is
the first Sunday of May.  Nowruz 1406 SH starts on 21 March 2027 (Iranian
calendar, vernal equinox 20 March 2027 after Tehran noon).
"""
from datetime import date, datetime, timedelta

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2026, 10, 17, 12, 0)


def first_sunday_of_may(year):
    d = date(year, 5, 1)
    return d + timedelta(days=(6 - d.weekday()) % 7)


ROWS = [
    ("en", "does new year's eve fall on a thursday", date(2026, 12, 31)),
    ("en", "is valentine's day on a thursday", date(2027, 2, 14)),
    ("en", "is christmas on a saturday", date(2026, 12, 25)),
    ("es-ES", "san valentín cae en jueves este año", date(2027, 2, 14)),
    ("es-CO", "san valentín cae en jueves este año", date(2027, 2, 14)),
    ("it", "Capodanno cadrà di giovedì?", date(2027, 1, 1)),
    ("ru", "Новый год выпадет на четверг?", date(2027, 1, 1)),
    ("sv", "blir nyårsafton en torsdag", date(2026, 12, 31)),
    ("fi", "onko uudenvuodenaatto torstaina", date(2026, 12, 31)),
    ("fa", "سال نو پنجشنبه میفته؟", date(2027, 3, 21)),
    ("pt-BR", "o dia de Ano Novo vai cair numa quinta-feira", date(2027, 1, 1)),
    ("pt-PT", "o Dia de Ano Novo vai calhar a uma quinta-feira",
     date(2027, 1, 1)),
    ("gl", "o Día da Nai cae en xoves?", first_sunday_of_may(2027)),
    ("fa", "سال نو چه روزی از هفته میفته", date(2027, 3, 21)),
    ("en", "what day of the week is christmas", date(2026, 12, 25)),
    ("en", "christmas falls on which day of the week", date(2026, 12, 25)),
    ("es", "qué día de la semana cae navidad", date(2026, 12, 25)),
    ("es", "navidad cae en qué día de la semana", date(2026, 12, 25)),
    ("pt", "em que dia da semana cai o natal", date(2026, 12, 25)),
    ("pt", "o natal cai em que dia da semana", date(2026, 12, 25)),
    ("it", "che giorno della settimana è natale", date(2026, 12, 25)),
    ("de", "auf welchen Wochentag fällt Weihnachten", date(2026, 12, 25)),
    ("fr", "quel jour de la semaine tombe noël", date(2026, 12, 25)),
]


@pytest.mark.parametrize("lang,text,expected", ROWS)
def test_holiday_in_a_weekday_question_is_a_date(lang, text, expected):
    result = extract_timespan(text, lang=lang, anchor=ANCHOR)
    assert result.span.start.datetime() == datetime.combine(
        expected, datetime.min.time())


def test_holiday_modifier_before_a_weekday_keeps_its_date():
    result = extract_timespan("christmas party on friday", lang="en",
                              anchor=ANCHOR)
    assert result.span.start.datetime() == datetime(2026, 12, 25)


@pytest.mark.parametrize("text", ["christmas tree", "Christmas songs",
                                  "a valentine's card",
                                  "the new year resolutions"])
def test_holiday_modifier_without_a_weekday_is_no_date(text):
    assert extract_timespan(text, lang="en", anchor=ANCHOR) is None


@pytest.mark.parametrize("lang,text", [
    ("en", "christmas songs any day of the week"),
    ("en", "i love christmas trees every day of the week"),
    ("pt", "o natal é bonito em qualquer dia da semana"),
    ("it", "canzoni di natale ogni giorno della settimana"),
])
def test_weekday_phrase_without_a_question_word_is_no_date(lang, text):
    assert extract_timespan(text, lang=lang, anchor=ANCHOR) is None
