"""A weekday ordinal no month or year holds, and a weekday range with no weekday, are declined."""
import calendar
from datetime import datetime

import pytest

from chronologia import ImpossibleDateError, extract_event
from chronologia.extract import extract_recurrence

_ANCHOR = datetime(2026, 11, 22, 9, 0)


def _longest_year_in_weekdays():
    return max(
        sum(1 for month in range(1, 13)
            for day, weekday in calendar.Calendar().itermonthdays2(year, month)
            if day and weekday < 5)
        for year in range(1900, 2300))


def test_no_year_has_a_263rd_weekday():
    assert _longest_year_in_weekdays() == 262


_IMPOSSIBLE = [
    ("every 263rd weekday of the year at 9am", "en", "a year has no 263rd business day"),
    ("elke 263e werkdag van het jaar", "nl", "a year has no 263rd business day"),
    ("jeder 263. Werktag des Jahres", "de", "a year has no 263rd business day"),
    ("the second and sixth monday of every month", "en", "a month has no 6th Monday"),
    ("the second, fourth and sixth monday of every month", "en", "a month has no 6th Monday"),
    ("o segundo e sexto domingo de cada mês", "pt", "a month has no 6th Sunday"),
    ("el segundo y sexto lunes de cada mes", "es", "a month has no 6th Monday"),
    ("der zweite und sechste Montag jedes Monats", "de", "a month has no 6th Monday"),
    ("le deuxième et sixième lundi de chaque mois", "fr", "a month has no 6th Monday"),
    ("il secondo e sesto lunedì di ogni mese", "it", "a month has no 6th Monday"),
    ("de tweede en zesde maandag van elke maand", "nl", "a month has no 6th Monday"),
    ("el segon i sisè dilluns de cada mes", "ca", "a month has no 6th Monday"),
    ("o segundo e sexto luns de cada mes", "gl", "a month has no 6th Monday"),
    ("every weekday from saturday to sunday", "en",
     "the range from Saturday to Sunday holds no day the rule allows"),
]


@pytest.mark.parametrize("text,lang,reason", _IMPOSSIBLE)
def test_impossible_reading_is_declined(text, lang, reason):
    assert extract_recurrence(text, lang, _ANCHOR) is None
    assert extract_event(text, lang, _ANCHOR) is None


@pytest.mark.parametrize("text,lang,reason", _IMPOSSIBLE)
def test_impossible_reading_reports_its_reason(text, lang, reason):
    for extract in (extract_recurrence, extract_event):
        with pytest.raises(ImpossibleDateError) as caught:
            extract(text, lang, _ANCHOR, impossible="raise")
        assert caught.value.reason == reason


_POSSIBLE = [
    ("the second and fourth monday of every month", "en", "FREQ=MONTHLY;BYDAY=2MO,4MO"),
    ("de tweede en vierde maandag van elke maand", "nl", "FREQ=MONTHLY;BYDAY=2MO,4MO"),
    ("le deuxième et quatrième lundi de chaque mois", "fr", "FREQ=MONTHLY;BYDAY=2MO,4MO"),
    ("the second and fifth monday of every month", "en", "FREQ=MONTHLY;BYDAY=2MO,5MO"),
    ("every 262nd weekday of the year", "en",
     "FREQ=YEARLY;BYDAY=MO,TU,WE,TH,FR;BYSETPOS=262"),
    ("every weekday from monday to friday", "en", "FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR"),
]


@pytest.mark.parametrize("text,lang,rule", _POSSIBLE)
def test_possible_sibling_keeps_its_rule(text, lang, rule):
    assert extract_recurrence(text, lang, _ANCHOR).recurrence.to_string() == rule
    assert extract_event(text, lang, _ANCHOR).recurrence.to_string() == rule


_YEAR_TAIL = [
    ("the second and sixth monday of the year", "en"),
    ("the second and sixth monday of 2027", "en"),
    ("o segundo e sexto domingo de 2027", "pt"),
    ("der zweite und sechste Montag des Jahres", "de"),
]


@pytest.mark.parametrize("text,lang", _YEAR_TAIL)
def test_year_tail_never_reports_a_month_reason(text, lang):
    assert extract_recurrence(text, lang, _ANCHOR) is None
    for extract in (extract_recurrence, extract_event):
        try:
            extract(text, lang, _ANCHOR, impossible="raise")
        except ImpossibleDateError as err:
            pytest.fail(f"raised {err.reason!r}")
