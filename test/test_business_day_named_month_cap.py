"""A business-day ordinal inside a named month is capped by that month's length."""
import calendar
from datetime import datetime

import pytest

from chronologia import ImpossibleDateError, extract_event
from chronologia.extract import extract_recurrence

_ANCHOR = datetime(2026, 11, 22, 9, 0)


def _most_weekdays(month):
    return max(
        sum(1 for day, weekday in calendar.Calendar().itermonthdays2(year, month)
            if day and weekday < 5)
        for year in range(2000, 2400))


def test_caps_over_the_gregorian_cycle():
    assert _most_weekdays(2) == 21
    assert {_most_weekdays(m) for m in (4, 6, 9, 11)} == {22}
    assert {_most_weekdays(m) for m in (1, 3, 5, 7, 8, 10, 12)} == {23}


_NAMES = {
    "en": {2: "february", 4: "april", 5: "may"},
    "de": {2: "Februar", 4: "April", 5: "Mai"},
    "nl": {2: "februari", 4: "april", 5: "mei"},
}
_PHRASE = {
    "en": "the {n}{suf} weekday of {m}",
    "de": "der {n}. Werktag im {m}",
    "nl": "de {n}e werkdag van {m}",
}


def _suffix(n):
    return "th" if 10 < n % 100 < 14 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


def _phrase(lang, n, month):
    return _PHRASE[lang].format(n=n, suf=_suffix(n), m=_NAMES[lang][month])


_ORDINAL_NAME = {21: "21st", 22: "22nd", 23: "23rd", 24: "24th"}
_REASON_MONTH = {2: "February", 4: "April", 5: "May"}


@pytest.mark.parametrize("lang", sorted(_NAMES))
@pytest.mark.parametrize("month", [2, 4, 5])
def test_last_valid_ordinal_resolves(lang, month):
    last = _most_weekdays(month)
    text = _phrase(lang, last, month)
    rec = extract_recurrence(text, lang, _ANCHOR)
    assert rec.recurrence.to_string() == (
        f"FREQ=YEARLY;BYMONTH={month};BYDAY=MO,TU,WE,TH,FR;BYSETPOS={last}")
    assert extract_event(text, lang, _ANCHOR) is not None


@pytest.mark.parametrize("lang", sorted(_NAMES))
@pytest.mark.parametrize("month", [2, 4, 5])
def test_first_invalid_ordinal_is_declined(lang, month):
    n = _most_weekdays(month) + 1
    text = _phrase(lang, n, month)
    assert extract_recurrence(text, lang, _ANCHOR) is None
    assert extract_event(text, lang, _ANCHOR) is None
    reason = f"{_REASON_MONTH[month]} has no {_ORDINAL_NAME[n]} business day"
    for extract in (extract_recurrence, extract_event):
        with pytest.raises(ImpossibleDateError) as caught:
            extract(text, lang, _ANCHOR, impossible="raise")
        assert caught.value.reason == reason


@pytest.mark.parametrize("text", [
    "the 23rd weekday of the month",
    "the 23rd weekday of every month",
])
def test_unnamed_month_keeps_the_cap_of_23(text):
    assert extract_recurrence(text, "en", _ANCHOR).recurrence.to_string() == (
        "FREQ=MONTHLY;BYDAY=MO,TU,WE,TH,FR;BYSETPOS=23")
    assert extract_recurrence(text.replace("23rd", "24th"), "en", _ANCHOR) is None
