"""pt "três quartos" after an hour is 45 minutes.

Priberam s.v. "quarto", 3: "Quarta parte da hora; quinze minutos (ex.: são
três e um quarto; falta um quarto para as nove)".  So "e um quarto" is 15
minutes and "e três quartos" is 45, as a clock minute ("duas e três quartos")
and as the rest of a length ("duas horas e três quartos" is 2 h 45 min).
Every value is worked out by hand from the anchor, Friday 2026-01-30 10:00:
the lone hour 2 takes its next twelve-hour reading, 14:00 (ruling 17).
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_duration, extract_event, extract_timespan

ANCHOR = datetime(2026, 1, 30, 10, 0)

CLOCKS = [
    ("duas horas e três quartos", datetime(2026, 1, 30, 14, 45)),
    ("duas e três quartos", datetime(2026, 1, 30, 14, 45)),
    ("às duas e três quartos", datetime(2026, 1, 30, 14, 45)),
    ("uma hora e três quartos", datetime(2026, 1, 30, 13, 45)),
    ("duas e um quarto", datetime(2026, 1, 30, 14, 15)),
]


@pytest.mark.parametrize("text,expected", CLOCKS)
def test_three_quarters_after_the_hour_is_45_minutes(text, expected):
    found = extract_timespan(text, "pt", ANCHOR)
    assert found.span.start.datetime() == expected
    assert found.remainder == ""


@pytest.mark.parametrize("text,expected", [
    ("duas horas e três quartos", timedelta(hours=2, minutes=45)),
    ("uma hora e três quartos", timedelta(hours=1, minutes=45)),
    ("três quartos de hora", timedelta(minutes=45)),
    ("uma hora e três quartos de hora", timedelta(hours=1, minutes=45)),
    ("duas horas e três quartos de hora", timedelta(hours=2, minutes=45)),
    ("meia hora e três quartos de hora", timedelta(hours=1, minutes=15)),
    ("duas horas e um quarto", timedelta(hours=2, minutes=15)),
])
def test_three_quarters_after_hours_is_part_of_a_length(text, expected):
    found = extract_duration(text, "pt", anchor=ANCHOR)
    assert found.duration == expected
    assert found.remainder == ""


def test_the_event_keeps_the_length_and_leaves_no_quarters():
    event = extract_event("reunião de duas horas e três quartos amanhã", "pt", anchor=ANCHOR)
    assert event.duration == timedelta(hours=2, minutes=45)
    assert event.summary == "reunião"
