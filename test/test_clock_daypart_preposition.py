# -*- coding: utf-8 -*-
"""A part of the day after a clock joins it behind pt "à" or "pela" and es
"por la", as it joins behind "da" and "de la".

pt "às 8 à noite" and es "a las 8 por la noche" name the evening hour 20:00,
the same as "às 8 da noite" and "a las 8 de la noche".  pt "à" is the
preposition "a" with the article ("marker_at"), and the frame words are in
"marker_dayframe" (RAE s.v. "por", Priberam s.v. "pela").

Every expected instant is worked out by hand from the anchor, Tuesday
2026-11-17 08:00: an evening or afternoon hour takes the pm half today, and a
morning hour that has passed (07:00) is tomorrow.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2026, 11, 17, 8, 0)

# text, language, expected instant
CLOCKS = [
    ("às 8 à noite", "pt", datetime(2026, 11, 17, 20, 0)),
    ("às 9 à noite", "pt", datetime(2026, 11, 17, 21, 0)),
    ("às 11 à noite", "pt", datetime(2026, 11, 17, 23, 0)),
    ("amanhã às 8 à noite", "pt", datetime(2026, 11, 18, 20, 0)),
    ("às 3 à tarde", "pt", datetime(2026, 11, 17, 15, 0)),
    ("às 8 horas à noite", "pt", datetime(2026, 11, 17, 20, 0)),
    ("às 8:30 à noite", "pt", datetime(2026, 11, 17, 20, 30)),
    ("às 8 e meia à noite", "pt", datetime(2026, 11, 17, 20, 30)),
    ("às 8 e 15 à noite", "pt", datetime(2026, 11, 17, 20, 15)),
    ("às 9 pela noite", "pt", datetime(2026, 11, 17, 21, 0)),
    ("às 7 pela manhã", "pt", datetime(2026, 11, 18, 7, 0)),
    ("a las 8 por la noche", "es", datetime(2026, 11, 17, 20, 0)),
    ("a las 3 por la tarde", "es", datetime(2026, 11, 17, 15, 0)),
    ("a las 7 por la mañana", "es", datetime(2026, 11, 18, 7, 0)),
    ("mañana a las 8 por la noche", "es", datetime(2026, 11, 18, 20, 0)),
    ("a las 8:30 por la noche", "es", datetime(2026, 11, 17, 20, 30)),
    ("a las 8 y media por la noche", "es", datetime(2026, 11, 17, 20, 30)),
    ("el lunes a las 10 por la mañana", "es", datetime(2026, 11, 23, 10, 0)),
]


@pytest.mark.parametrize("text,lang,expected", CLOCKS)
def test_the_part_of_the_day_joins_the_clock(text, lang, expected):
    found = extract_timespan(text, lang, ANCHOR)
    assert found.span.start.datetime() == expected
    assert found.span.end.datetime() == expected + timedelta(minutes=1)
    assert found.remainder == ""


@pytest.mark.parametrize("text,twin,lang", [
    ("às 8 à noite", "às 8 da noite", "pt"),
    ("às 3 à tarde", "às 3 da tarde", "pt"),
    ("às 8:30 à noite", "às 8:30 da noite", "pt"),
    ("às 8 e meia à noite", "às 8 e meia da noite", "pt"),
    ("às 1 à noite", "às 1 da noite", "pt"),
    ("às 12 à noite", "às 12 da noite", "pt"),
    ("a las 8 por la noche", "a las 8 de la noche", "es"),
    ("a las 7 por la mañana", "a las 7 de la mañana", "es"),
    ("a las 8 y media por la noche", "a las 8 y media de la noche", "es"),
    ("a la una por la noche", "a la una de la noche", "es"),
    ("a las 12 por la noche", "a las 12 de la noche", "es"),
])
def test_the_frame_reads_as_the_de_form(text, twin, lang):
    found = extract_timespan(text, lang, ANCHOR)
    other = extract_timespan(twin, lang, ANCHOR)
    assert found.span.start.datetime() == other.span.start.datetime()
    assert found.span.end.datetime() == other.span.end.datetime()


@pytest.mark.parametrize("text,lang,expected,remainder", [
    ("jantamos às 8 à noite com amigos", "pt",
     datetime(2026, 11, 17, 20, 0), "jantamos com amigos"),
    ("alarma para 8 por la noche", "es",
     datetime(2026, 11, 17, 20, 0), "alarma para"),
])
def test_the_clock_with_its_frame_inside_a_sentence(text, lang, expected,
                                                     remainder):
    found = extract_timespan(text, lang, ANCHOR)
    assert found.span.start.datetime() == expected
    assert found.remainder == remainder
