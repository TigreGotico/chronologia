"""A calendar unit in a duration is counted on the calendar from the anchor.

W3C XML Schema 1.1 Part 2, E.3.3 "Adding durations to dateTimes": "The
·months· value is added to the starting dateTime value first. If the day is
out of range for the new month value, it is pinned to be within range. Thus
April 31 turns into April 30. Then the ·seconds· value is added."

Expected values come from ``dateutil.relativedelta``, which adds months the
same way and is independent of chronologia. A half month is 15 days and a
quarter month 7, as the offset reader reads "in half a month".
"""
from datetime import datetime, timedelta

import pytest
from dateutil.relativedelta import relativedelta

from chronologia import extract_duration

END_OF_JANUARY = datetime(2026, 1, 31, 10, 0)
LEAP_DAY = datetime(2024, 2, 29, 9, 30)


def _length(anchor, **delta):
    return anchor + relativedelta(**delta) - anchor


@pytest.mark.parametrize("anchor", [END_OF_JANUARY, LEAP_DAY])
@pytest.mark.parametrize("lang, text, delta", [
    ("pt", "três meses", {"months": 3}),
    ("pt", "um mês", {"months": 1}),
    ("pt", "um mês e meio", {"months": 1, "days": 15}),
    ("pt", "meio ano", {"months": 6}),
    ("pt", "um ano", {"years": 1}),
    ("pt", "dois anos e três meses", {"years": 2, "months": 3}),
    ("pt", "um ano e dois dias", {"years": 1, "days": 2}),
    ("pt", "durante três meses", {"months": 3}),
    ("en", "3 months and 2 days", {"months": 3, "days": 2}),
    ("en", "2 days and 3 months", {"months": 3, "days": 2}),
    ("en", "a year and a half", {"months": 18}),
    ("en", "a decade", {"years": 10}),
    ("en", "a quarter of a century", {"years": 25}),
    ("en", "1 month and 3 hours", {"months": 1, "hours": 3}),
    ("de", "zwei Monate", {"months": 2}),
    ("cs", "dva měsíce", {"months": 2}),
])
def test_calendar_units_count_from_the_anchor(anchor, lang, text, delta):
    got = extract_duration(text, lang, anchor=anchor)
    assert got is not None, text
    assert got.duration == _length(anchor, **delta), text
    assert got.remainder == ""


def test_the_same_words_give_the_calendar_length_of_each_anchor():
    feb = extract_duration("um mês", "pt", anchor=datetime(2026, 2, 1))
    mar = extract_duration("um mês", "pt", anchor=datetime(2026, 3, 1))
    assert feb.duration == timedelta(days=28)
    assert mar.duration == timedelta(days=31)


def test_a_fraction_of_a_month_with_no_day_count_is_refused():
    # the offset reader refuses "a third of a month" too
    assert extract_duration("um terço de mês", "pt",
                            anchor=END_OF_JANUARY) is None


def test_the_default_anchor_is_now():
    got = extract_duration("um ano", "pt")
    now = datetime.now()
    assert got.duration in {now + relativedelta(years=1) - now,
                            timedelta(days=365), timedelta(days=366)}


@pytest.mark.parametrize("lang, text, freq_days, delta", [
    ("en", "every day for a month", 1, {"months": 1}),
    ("pt", "todos os dias durante um mês", 1, {"months": 1}),
    ("en", "every week for 2 months", 7, {"months": 2}),
    ("en", "gym every monday for 3 months", 7, {"months": 3}),
])
def test_a_recurrence_counts_the_calendar_length_from_its_anchor(
        lang, text, freq_days, delta):
    from chronologia import extract_recurrence
    got = extract_recurrence(text, lang, anchor=END_OF_JANUARY)
    length = _length(END_OF_JANUARY, **delta)
    assert got.recurrence.count == length.days // freq_days


@pytest.mark.parametrize("lang, text, delta", [
    ("en", "meeting tomorrow for 3 months", {"months": 3}),
    ("pt", "reunião amanhã durante um mês", {"months": 1}),
])
def test_an_event_counts_the_calendar_length_from_its_start(lang, text, delta):
    # from 30 January a month is 29 days; from the event, 31 January, it is 28
    from chronologia import extract_event
    got = extract_event(text, lang, anchor=datetime(2026, 1, 30, 10, 0))
    start = datetime(2026, 1, 31)
    assert got.duration == _length(start, **delta)
