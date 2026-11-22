"""A weekday ordinal no year holds never occurs; the readers decline it instead of raising."""
import calendar
from datetime import datetime

import pytest

from chronologia import extract_event
from chronologia.extract import extract_recurrence

_ANCHOR = datetime(2026, 11, 19, 10, 0)

_BEYOND = [
    ("the sixtieth monday of the year", "en"),
    ("the fifty-fourth monday of the year", "en"),
    ("the 54th monday of the year", "en"),
    ("el sexagésimo lunes del año", "es"),
    ("el quincuagésimo cuarto lunes del año", "es"),
    ("a sexagésima segunda-feira do ano", "pt"),
    ("der sechzigste Montag des Jahres", "de"),
    ("der vierundfünfzigste Montag des Jahres", "de"),
    ("le soixantième lundi de l'année", "fr"),
    ("le cinquante-quatrième lundi de l'année", "fr"),
]


def _count(year, keep):
    return sum(1 for m in range(1, 13)
               for d in calendar.Calendar().itermonthdays2(year, m)
               if d[0] and keep(d[1]))


def test_no_year_holds_more_than_53_of_a_weekday_or_262_weekdays():
    years = range(1900, 2300)
    assert max(_count(y, lambda w, k=k: w == k) for y in years for k in range(7)) == 53
    assert max(_count(y, lambda w: w < 5) for y in years) == 262


@pytest.mark.parametrize("text,lang", _BEYOND)
def test_weekday_beyond_the_year_is_declined(text, lang):
    assert extract_recurrence(text, lang, anchor=_ANCHOR) is None
    assert extract_event(text, lang, _ANCHOR) is None


# 2029 starts on a Monday, so it holds 53 Mondays and the 53rd is 31 December.
# 2026 starts on a Thursday, so its 52nd Monday is 28 December.
@pytest.mark.parametrize("text,when,ordn", [
    ("the 52nd monday of the year", datetime(2026, 12, 28), 52),
    ("the 53rd monday of the year", datetime(2029, 12, 31), 53),
])
def test_last_mondays_of_the_year_still_read(text, when, ordn):
    got = extract_event(text, "en", _ANCHOR)
    assert got.recurrence.byday == ((ordn, 0),)
    assert got.span.start.datetime() == when


# 2032 is a leap year starting on a Thursday: its two extra days are Thursday and
# Friday, so it holds 52 * 5 + 2 = 262 weekdays and the 262nd is 31 December.
def test_262nd_weekday_of_the_year_still_reads():
    text = "the 262nd weekday of the year"
    got = extract_event(text, "en", _ANCHOR)
    assert got.recurrence.to_string() == "FREQ=YEARLY;BYDAY=MO,TU,WE,TH,FR;BYSETPOS=262"
    assert got.span.start.datetime() == datetime(2032, 12, 31)


def test_263rd_weekday_of_the_year_is_declined():
    text = "the 263rd weekday of the year"
    assert extract_recurrence(text, "en", anchor=_ANCHOR) is None
    assert extract_event(text, "en", _ANCHOR) is None
