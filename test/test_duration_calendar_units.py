"""A calendar unit in a duration is counted on the calendar from the anchor.

W3C XML Schema 1.1 Part 2, E.3.3 "Adding durations to dateTimes": "The
·months· value is added to the starting dateTime value first. If the day is
out of range for the new month value, it is pinned to be within range. Thus
April 31 turns into April 30. Then the ·seconds· value is added."

Expected values come from ``dateutil.relativedelta``, which adds months the
same way and is independent of chronologia. A half month is 15 days and a
quarter month 7, as the offset reader reads "in half a month".
"""
from datetime import date, datetime, timedelta

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


def test_with_no_anchor_a_calendar_unit_has_no_length():
    assert extract_duration("três meses", "pt") is None
    assert extract_duration("três meses e dois dias", "pt") is None
    assert extract_duration("dois dias", "pt").duration == timedelta(days=2)


def test_a_date_anchor_is_its_midnight():
    got = extract_duration("1 month and 3 hours", "en", anchor=date(2026, 1, 31))
    assert got.duration == timedelta(days=28, hours=3)


def test_a_length_past_the_last_year_is_refused():
    assert extract_duration("2 months", "en",
                            anchor=datetime(9999, 12, 1)) is None


def test_a_fraction_of_a_year_in_whole_months_is_read():
    got = extract_duration("1.5 years", "en", anchor=END_OF_JANUARY)
    assert got.duration == _length(END_OF_JANUARY, months=18)


@pytest.mark.parametrize("lang, text", [
    # a roman numeral or an ordinal names a century, not a count
    ("en", "the XII century"),
    ("fr", "XVe siècle"),
    # "of" between the count and the unit names a day of the month
    ("pt", "o dia 5 do mês"),
    # a definite article names the month, not one month
    ("en", "3 days into the month"),
    # an article after another length is a rate
    ("en", "2 hours a month"),
    ("en", "2 days a year"),
    # an article after "of" names a part of the unit
    ("en", "a third of a year"),
    # a fraction of a year that is not whole months
    ("en", "1.125 years"),
])
def test_a_calendar_unit_without_a_plain_count_names_no_length(lang, text):
    assert extract_duration(text, lang, anchor=END_OF_JANUARY) is None


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


@pytest.mark.parametrize("lang, text", [
    ("en", "vacation on january 30 for a month"),
    ("pt", "férias a 30 de janeiro durante um mês"),
])
def test_an_event_counts_the_calendar_length_from_its_start(lang, text):
    # a month from the start, 30 January, is 29 days; from its end, 31
    # January, 28 days; from the anchor, 15 January, 31 days
    from chronologia import extract_event
    got = extract_event(text, lang, anchor=datetime(2026, 1, 15, 10, 0))
    assert got.span.start == datetime(2026, 1, 30)
    assert got.duration == timedelta(days=29)
    assert got.summary in {"vacation", "férias"}


@pytest.mark.parametrize("lang, text, start", [
    ("en", "meeting in 3 months", datetime(2026, 4, 30, 10, 0)),
    ("pt", "reunião daqui a três meses", datetime(2026, 4, 30, 10, 0)),
    ("en", "trip a year from today", datetime(2027, 1, 31)),
])
def test_an_offset_in_an_event_stays_its_date(lang, text, start):
    from chronologia import extract_event
    got = extract_event(text, lang, anchor=END_OF_JANUARY)
    assert got.span.start == start
    assert got.duration is None


@pytest.mark.parametrize("text", [
    "meeting on december 1 9999 for 2 months",
    "battle on march 15 44 BC for 3 months",
])
def test_an_event_length_with_no_calendar_end_is_not_read(text):
    from chronologia import extract_event
    got = extract_event(text, "en", anchor=END_OF_JANUARY)
    assert got.duration is None
    assert "months" in got.summary


@pytest.mark.parametrize("lang, text, summary", [
    ("en", "3 months notice on june 1", "3 months notice"),
    ("pt", "pagar a renda de dois meses no dia 1 de junho",
     "pagar a renda de 2 meses"),
])
def test_an_event_reads_a_calendar_length_only_after_its_marker(
        lang, text, summary):
    # with no "for" or "durante", the length describes the event, not its span
    from chronologia import extract_event
    got = extract_event(text, lang, anchor=END_OF_JANUARY)
    assert got.span.start == datetime(2026, 6, 1)
    assert got.duration is None
    assert got.summary == summary
