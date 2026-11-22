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
