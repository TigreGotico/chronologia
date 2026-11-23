"""A business-day ordinal past the last weekday of its month names no day.

The weekday counts are taken from the calendar: February 2026 has 20 weekdays,
October 22, November 21 and December 23.
"""
import calendar
from datetime import date, datetime

import pytest

from chronologia import ImpossibleDateError
from chronologia.extract import extract_candidates, extract_timespan

ANCHOR = datetime(2026, 11, 22, 9, 0)

#: language -> (phrase with {n} the ordinal and {scope} the month scope,
#:              {month number: month name}, the scope of the anchor's month)
SURFACES = {
    "en": ("the {n}{en} business day of {scope}",
           {2: "february", 10: "october", 11: "november", 12: "december"}, "the month"),
    "de": ("der {n}. Werktag {scope}",
           {2: "im Februar", 10: "im Oktober", 11: "im November", 12: "im Dezember"},
           "des Monats"),
    "nl": ("de {n}e werkdag van {scope}",
           {2: "februari", 10: "oktober", 11: "november", 12: "december"}, "de maand"),
    "pt": ("o {n}.º dia útil {scope}",
           {2: "de fevereiro", 10: "de outubro", 11: "de novembro", 12: "de dezembro"},
           "do mês"),
    "es": ("el {n}.º día hábil {scope}",
           {2: "de febrero", 10: "de octubre", 11: "de noviembre", 12: "de diciembre"},
           "del mes"),
    "fr": ("le {n}e jour ouvrable {scope}",
           {2: "de février", 10: "d'octobre", 11: "de novembre", 12: "de décembre"},
           "du mois"),
}


def weekdays(year, month):
    return [date(year, month, d) for d in range(1, calendar.monthrange(year, month)[1] + 1)
            if date(year, month, d).weekday() < 5]


def fill(template, n, scope):
    suffix = {21: "st", 22: "nd", 23: "rd"}.get(n, "th")
    return template.format(n=n, en=suffix, scope=scope)


def cases():
    for lang, (template, names, current) in SURFACES.items():
        for month in (2, 10, 11, 12):
            days = weekdays(2026, month)
            scope = current if month == 11 else names[month]
            yield lang, fill(template, len(days), scope), days[-1]
            yield lang, fill(template, len(days) + 1, scope), None
        yield lang, fill(template, len(weekdays(2026, 11)) + 4, scope=current), None


CASES = list(cases())
IDS = [f"{lang}-{text}" for lang, text, _ in CASES]


def test_weekday_counts_by_hand():
    assert [len(weekdays(2026, m)) for m in (2, 10, 11, 12)] == [20, 22, 21, 23]


@pytest.mark.parametrize("lang,text,last", CASES, ids=IDS)
def test_last_business_day_is_kept_and_the_next_declined(lang, text, last):
    result = extract_timespan(text, lang, ANCHOR)
    if last is None:
        assert result is None
        assert not [c for c in extract_candidates(text, lang, ANCHOR)
                    if c.construction == "business_days"]
    else:
        start = result.span.start
        assert (start.year, start.month, start.day) == (last.year, last.month, last.day)


@pytest.mark.parametrize("lang,text,last", [c for c in CASES if c[2] is None],
                         ids=[i for i, c in zip(IDS, CASES) if c[2] is None])
def test_raise_mode_names_the_period(lang, text, last):
    with pytest.raises(ImpossibleDateError) as caught:
        extract_timespan(text, lang, ANCHOR, impossible="raise")
    assert " has no " in caught.value.reason
    assert caught.value.reason.endswith(" business day")


def test_raise_reason_is_exact():
    with pytest.raises(ImpossibleDateError) as caught:
        extract_timespan("the 23rd business day of the month", "en", ANCHOR,
                         impossible="raise")
    assert caught.value.reason == "November 2026 has no 23rd business day"
    with pytest.raises(ImpossibleDateError) as caught:
        extract_timespan("the 24th business day of may", "en", ANCHOR,
                         impossible="raise")
    assert caught.value.reason == "May 2026 has no 24th business day"


def test_next_month_counts_its_own_weekdays():
    # December 2026 has 23 weekdays, so the 23rd is 31 December and the 24th is none.
    assert extract_timespan("the 23rd business day of next month", "en",
                            ANCHOR).span.start.day == 31
    assert extract_timespan("the 24th business day of next month", "en", ANCHOR) is None
