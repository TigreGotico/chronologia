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
    ("the sixth monday of every other month", "en", "a month has no 6th Monday"),
    ("the sixth monday every month", "en", "a month has no 6th Monday"),
    ("every month on the sixth monday", "en", "a month has no 6th Monday"),
    ("the 24th business day of each month", "en", "a month has no 24th business day"),
    ("the 30th of february every year", "en", "February has no 30th"),
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


#: a date at the edge of what its period holds, a quarter (a period of three
#: months) and a monthly date followed by a weekday in the next clause: none is refused
_NOT_REFUSED = [
    ("every month on the fifth monday", "en"),
    ("the 23rd business day of each month", "en"),
    ("every year on the 53rd friday", "en"),
    ("the 262nd business day of every year", "en"),
    ("the sixth monday of every quarter", "en"),
    ("the 24th business day every quarter", "en"),
    ("pay rent every month on the 15th, monday or tuesday", "en"),
    ("every month on the 15th. monday is a holiday", "en"),
    ("every month on the 25th, business as usual", "en"),
    ("jeden Monat am 15., Montag oder Dienstag", "de"),
    ("elke maand op de 15e, maandag of dinsdag", "nl"),
    ("the 29th of february every year", "en"),
]


@pytest.mark.parametrize("text,lang", _NOT_REFUSED)
def test_a_date_the_period_holds_is_not_refused(text, lang):
    assert extract_recurrence(text, lang, _ANCHOR) is not None
    for extract in (extract_recurrence, extract_event):
        try:
            extract(text, lang, _ANCHOR, impossible="raise")
        except ImpossibleDateError as err:
            pytest.fail(f"raised {err.reason!r}")


@pytest.mark.parametrize("text,lang,day", [
    ("pay rent every month on the 15th, monday or tuesday", "en", 15),
    ("every month on the 15th. monday is a holiday", "en", 15),
    ("every month on the 25th, business as usual", "en", 25),
    ("jeden Monat am 15., Montag oder Dienstag", "de", 15),
    ("elke maand op de 15e, maandag of dinsdag", "nl", 15),
])
def test_a_monthly_day_keeps_its_rule_before_a_weekday_in_the_next_clause(text, lang, day):
    assert extract_recurrence(text, lang, _ANCHOR).recurrence.bymonthday == (day,)


@pytest.mark.parametrize("text", ["the 32nd of may every year", "the 100th of may every year"])
def test_a_number_above_31_beside_a_month_is_refused_without_a_reason(text):
    assert extract_recurrence(text, "en", _ANCHOR) is None
    assert extract_recurrence(text, "en", _ANCHOR, impossible="raise") is None
