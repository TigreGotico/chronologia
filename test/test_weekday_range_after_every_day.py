"""'every day from WEEKDAY to WEEKDAY' reads as a weekday set in German and Dutch, as in English."""
from datetime import datetime

import pytest

from chronologia import extract_event
from chronologia.extract import extract_recurrence

_ANCHORS = (datetime(2026, 11, 22, 9, 0), datetime(2027, 3, 3, 15, 30))

_WEEKDAY_SET = [
    ("every day from monday to friday", "en", "FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR"),
    ("jeden Tag von Montag bis Freitag", "de", "FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR"),
    ("elke dag van maandag tot vrijdag", "nl", "FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR"),
    ("jeden Tag von Freitag bis Montag", "de", "FREQ=DAILY;BYDAY=FR,SA,SU,MO"),
    ("elke dag van vrijdag tot maandag", "nl", "FREQ=DAILY;BYDAY=FR,SA,SU,MO"),
    ("jeden Tag von Dienstag bis Dienstag", "de", "FREQ=DAILY;BYDAY=TU"),
    ("jeden Werktag von Montag bis Mittwoch", "de", "FREQ=WEEKLY;BYDAY=MO,TU,WE"),
    ("elke werkdag van maandag tot woensdag", "nl", "FREQ=WEEKLY;BYDAY=MO,TU,WE"),
    ("every weekday from monday to wednesday", "en", "FREQ=WEEKLY;BYDAY=MO,TU,WE"),
    ("jeden Werktag von Freitag bis Montag", "de", "FREQ=WEEKLY;BYDAY=FR,MO"),
    ("elke werkdag van vrijdag tot maandag", "nl", "FREQ=WEEKLY;BYDAY=FR,MO"),
    ("jeden Tag zwischen Montag und Freitag", "de", "FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR"),
    ("elke dag tussen maandag en vrijdag", "nl", "FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR"),
    ("tous les jours du lundi au vendredi", "fr", "FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR"),
    ("todos los días de lunes a viernes", "es", "FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR"),
    ("todos os dias de segunda a sexta", "pt", "FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR"),
    ("ogni giorno da lunedì a venerdì", "it", "FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR"),
    ("cada dia de dilluns a divendres", "ca", "FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR"),
    ("todos os días de luns a venres", "gl", "FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR"),
]


@pytest.mark.parametrize("anchor", _ANCHORS)
@pytest.mark.parametrize("text,lang,rule", _WEEKDAY_SET)
def test_weekday_range_is_a_weekday_set(text, lang, rule, anchor):
    got = extract_recurrence(text, lang, anchor)
    assert got.recurrence.to_string() == rule
    assert got.remainder == ""
    assert extract_event(text, lang, anchor).recurrence.to_string() == rule


@pytest.mark.parametrize("anchor", _ANCHORS)
@pytest.mark.parametrize("text,lang", [
    ("jeden Werktag von Samstag bis Sonntag", "de"),
    ("elke werkdag van zaterdag tot zondag", "nl"),
])
def test_range_outside_the_weekdays_is_declined(text, lang, anchor):
    assert extract_recurrence(text, lang, anchor) is None
    assert extract_event(text, lang, anchor) is None


@pytest.mark.parametrize("text,lang,until", [
    ("jeden Tag von Montag bis zum 30. November", "de", "20261130"),
    ("jeden Tag von heute bis Freitag", "de", "20261127"),
    ("jeden Tag bis Freitag", "de", "20261127"),
    ("elke dag tot vrijdag", "nl", "20261127"),
    ("elke dag van vandaag tot vrijdag", "nl", "20261127"),
])
def test_date_range_keeps_its_until(text, lang, until):
    got = extract_recurrence(text, lang, _ANCHORS[0])
    assert got.recurrence.byday == ()
    assert got.recurrence.to_string() == f"FREQ=DAILY;UNTIL={until}T000000"
