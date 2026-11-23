"""A sixth weekday of a month never occurs; the readers decline it instead of raising."""
import calendar
from datetime import datetime

import pytest

from chronologia import extract_event
from chronologia.extract import extract_recurrence

_ANCHOR = datetime(2026, 11, 19, 10, 0)

_SIXTH = [
    ("el sexto lunes de mayo", "es"),
    ("the sixth Monday of May", "en"),
    ("every sixth monday of may", "en"),
    ("the sixth monday of the month", "en"),
    ("o sexto domingo de maio", "pt"),
    ("der sechste Montag im Mai", "de"),
    ("le sixième lundi de mai", "fr"),
]

_FIFTH = [
    ("the fifth Monday of May", "en"),
    ("der fünfte Montag im Mai", "de"),
]


def test_no_month_has_a_sixth_weekday():
    most = max(
        sum(1 for d in calendar.Calendar().itermonthdays2(year, month)
            if d[0] and d[1] == weekday)
        for year in range(1900, 2300) for month in range(1, 13)
        for weekday in range(7))
    assert most == 5


@pytest.mark.parametrize("text,lang", _SIXTH)
def test_sixth_weekday_of_month_is_declined(text, lang):
    assert extract_recurrence(text, lang, anchor=_ANCHOR) is None
    assert extract_event(text, lang, _ANCHOR) is None


@pytest.mark.parametrize("text,lang", _FIFTH)
def test_fifth_weekday_of_month_still_reads(text, lang):
    got = extract_event(text, lang, _ANCHOR)
    assert got is not None
    assert got.recurrence.byday == ((5, 0),)
    assert got.recurrence.bymonth == (5,)


# December 2026 starts on a Tuesday, so its weekdays are the 1st to 4th, 7th, 8th ...
# and the sixth is the 8th.
_BUSINESS_SIXTH = [
    ("the 6th weekday of the month", "en"),
    ("der sechste Werktag im Monat", "de"),
    ("de zesde werkdag van de maand", "nl"),
]


@pytest.mark.parametrize("text,lang", _BUSINESS_SIXTH)
def test_sixth_weekday_of_month_in_business_days_still_reads(text, lang):
    got = extract_recurrence(text, lang, anchor=_ANCHOR)
    assert got is not None
    assert got.recurrence.to_string() == "FREQ=MONTHLY;BYDAY=MO,TU,WE,TH,FR;BYSETPOS=6"
    event = extract_event(text, lang, _ANCHOR)
    assert event.span.start.datetime() == datetime(2026, 12, 8)


def test_business_day_beyond_the_month_is_declined():
    text = "the 25th weekday of the month"
    assert extract_recurrence(text, "en", anchor=_ANCHOR) is None
    assert extract_event(text, "en", _ANCHOR) is None


_SIXTH_EVERY_MONTH = [
    ("the sixth monday of every month", "en"),
    ("every sixth monday of every month", "en"),
    ("cada sexto domingo de cada mês", "pt"),
    ("o sexto domingo de cada mês", "pt"),
    ("el sexto lunes de cada mes", "es"),
    ("le sixième lundi de chaque mois", "fr"),
    ("il sesto lunedì di ogni mese", "it"),
    ("de zesde maandag van elke maand", "nl"),
    ("el sisè dilluns de cada mes", "ca"),
    ("o sexto luns de cada mes", "gl"),
]

_FIFTH_EVERY_MONTH = [
    ("the fifth monday of every month", "en"),
    ("o quinto domingo de cada mês", "pt"),
    ("el quinto lunes de cada mes", "es"),
    ("le cinquième lundi de chaque mois", "fr"),
    ("il quinto lunedì di ogni mese", "it"),
    ("de vijfde maandag van elke maand", "nl"),
    ("el cinquè dilluns de cada mes", "ca"),
    ("o quinto luns de cada mes", "gl"),
]


@pytest.mark.parametrize("text,lang", _SIXTH_EVERY_MONTH)
def test_sixth_weekday_of_every_month_is_declined(text, lang):
    assert extract_recurrence(text, lang, anchor=_ANCHOR) is None
    assert extract_event(text, lang, _ANCHOR) is None


@pytest.mark.parametrize("text,lang", _FIFTH_EVERY_MONTH)
def test_fifth_weekday_of_every_month_keeps_its_rule(text, lang):
    weekday = 6 if lang == "pt" else 0
    got = extract_event(text, lang, _ANCHOR)
    assert got.recurrence.byday == ((5, weekday),)
    assert got.summary == ""
    # the first month on or after the anchor with five of that weekday
    first = next(
        datetime(2026, 11, d) for d in range(1, 31)
        if datetime(2026, 11, d).weekday() == weekday and d > 28)
    assert got.span.start.datetime() == first
