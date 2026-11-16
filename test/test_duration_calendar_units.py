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
    ("en", "two decades", {"years": 20}),
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
    assert extract_duration("10000 years", "en",
                            anchor=END_OF_JANUARY) is None


def test_a_fraction_of_a_year_in_whole_months_is_read():
    got = extract_duration("1.5 years", "en", anchor=END_OF_JANUARY)
    assert got.duration == _length(END_OF_JANUARY, months=18)


@pytest.mark.parametrize("lang, text", [
    # a century or millennium names the ordinal century, not a length
    ("en", "the XII century"),
    ("fr", "XVe siècle"),
    ("it", "il 20 secolo"),
    ("ru", "20 век"),
    ("ru", "второе столетие"),
    ("en", "two centuries"),
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
    # a demonstrative names this month or year
    ("ast", "esti mes"),
    # a four-digit year before or after a year word names that year
    ("ru", "в 1980 году"),
    ("ha", "shekarar 2024"),
    ("ko", "2024년 3월 15일"),
    ("en", "the 2024 year"),
    # a year of fewer than four digits before a singular year word
    ("ru", "в 988 году"),
    ("ru", "988 год"),
    ("pl", "w 988 roku"),
    # the same in the other languages whose year noun has a plural
    # (en.wiktionary declension tables: uk "роки", bg and mk "години",
    # sw "miaka", ha "shekaru")
    ("uk", "у 988 році"),
    ("uk", "988 рік"),
    # a count of 101 or 102 takes "год" or "года", but not in the locative,
    # and a count of 111 or 112 takes "лет"
    ("ru", "в 101 году"),
    ("ru", "в 102 году"),
    ("ru", "111 год"),
    ("ru", "112 года"),
    ("uk", "у 101 році"),
    ("uk", "111 рік"),
    ("bg", "през 988 година"),
    ("bg", "988 година"),
    ("mk", "988 година"),
    ("ha", "shekarar 988"),
    ("sw", "mwaka 980"),
    # ro "luni" is both "months" and "Monday": next to a clock it is the day
    ("ro", "la ora 9 luni dimineața"),
])
def test_a_calendar_unit_without_a_plain_count_names_no_length(lang, text):
    assert extract_duration(text, lang, anchor=END_OF_JANUARY) is None


@pytest.mark.parametrize("lang, text, delta", [
    ("ru", "через 988 лет", {"years": 988}),
    ("en", "988 years", {"years": 988}),
    ("pt", "em 988 anos", {"years": 988}),
    ("de", "seit 988 jahren", {"years": 988}),
    ("it", "988 anni", {"years": 988}),
    ("ro", "988 ani", {"years": 988}),
    ("uk", "988 років", {"years": 988}),
    ("bg", "988 години", {"years": 988}),
    ("sw", "miaka 980", {"years": 980}),
    # a spelled number is no written year, whatever digits it folds to
    ("pt", "mil e quinhentos anos", {"years": 1500}),
    # a year noun with no plural of its own counts with its one form
    ("ko", "100년 전", {"years": 100}),
    ("vi", "một trăm năm trước", {"years": 100}),
    ("is", "hundrað ár", {"years": 100}),
    ("mt", "tliet mitt sena ilu", {"years": 300}),
    ("ro", "9 luni", {"months": 9}),
    ("ro", "timp de 3 luni", {"months": 3}),
])
def test_a_count_of_years_is_still_a_length(lang, text, delta):
    got = extract_duration(text, lang, anchor=END_OF_JANUARY)
    assert got.duration == _length(END_OF_JANUARY, **delta)


@pytest.mark.parametrize("lang, text, years", [
    ("ru", "101 год назад", 101),
    ("ru", "это было 121 год назад", 121),
    ("ru", "через 101 год", 101),
    ("ru", "102 года назад", 102),
    ("ru", "через 122 года", 122),
    ("ru", "через 104 года", 104),
    ("uk", "101 рік тому", 101),
    ("uk", "121 рік тому", 121),
    ("uk", "через 101 рік", 101),
])
def test_a_count_of_years_agrees_with_its_last_word(lang, text, years):
    """An East Slavic count agrees with the last word of its number.  ru
    "один" and its compounds (21, 101) "govern the singular", and два, три,
    четыре and their compounds (22, 102) "govern the genitive" singular
    (en.wiktionary "один" and "два", Russian usage notes): "101 год",
    "102 года".  In uk "the nouns agree with the last number in any compound
    number" (en.wikipedia "Ukrainian grammar"): "101 рік".  So by these
    counts the singular is no written year."""
    got = extract_duration(text, lang, anchor=END_OF_JANUARY)
    assert got.duration == _length(END_OF_JANUARY, years=years)


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


@pytest.mark.parametrize("text, start, delta", [
    ("vacation tomorrow for a month and a half", datetime(2026, 1, 31),
     {"months": 1, "days": 15}),
    ("trip on monday for a year and a half", datetime(2026, 2, 2),
     {"months": 18}),
])
def test_an_event_keeps_the_half_of_a_calendar_length(text, start, delta):
    # the date reader must not take "and a half" from the length
    from chronologia import extract_event
    got = extract_event(text, "en", anchor=datetime(2026, 1, 30, 10, 0))
    assert got.span.start == start
    assert got.span.end == start + relativedelta(**delta)
    assert got.summary == text.split()[0]


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


@pytest.mark.parametrize("lang, text, count", [
    # the first occurrence is day 0.  From 31 January 2026 a year is 365
    # days: days 0, 2, ..., 364 are 183 occurrences.  A month ends on 28
    # February, 28 days: every 3 days is days 0, 3, ..., 27, 10 occurrences
    ("en", "every 2 days for a year", 183),
    ("en", "every 3 days for a month", 10),
    ("en", "every other day for a month", 14),
    ("pt", "a cada 2 dias durante um mês", 14),
    # the same for a fixed length: days 0, 3, 6 and 9 of 10
    ("en", "every 2 days for 10 days", 5),
    ("en", "every 3 days for 10 days", 4),
])
def test_a_recurrence_count_steps_by_its_interval(lang, text, count):
    from chronologia import extract_recurrence
    got = extract_recurrence(text, lang, anchor=END_OF_JANUARY)
    assert got.recurrence.count == count


@pytest.mark.parametrize("text", [
    "every day for a third of a year",
    "every day for a third of a month",
])
def test_a_recurrence_bound_by_a_part_of_a_unit_has_no_count(text):
    # "a third of" names no whole count, so the bound stays unread
    from chronologia import extract_recurrence
    got = extract_recurrence(text, "en", anchor=END_OF_JANUARY)
    assert got.recurrence.count is None
    assert got.remainder == text[len("every day "):]


@pytest.mark.parametrize("text, start_words", [
    ("every day starting march 1 for a month", "starting march 1"),
    ("every day for a month starting march 1", "starting march 1"),
    ("every day from march 1 for a month", "from march 1"),
])
def test_a_recurrence_with_its_own_start_counts_no_calendar_length(
        text, start_words):
    # a month counts from the anchor, and the text names another start, so
    # the bound stays unread rather than give the wrong number of days
    from chronologia import extract_recurrence
    got = extract_recurrence(text, "en", anchor=datetime(2026, 1, 30, 10, 0))
    assert got.recurrence.count is None
    assert start_words in got.remainder
    assert "for a month" in got.remainder


@pytest.mark.parametrize("text, freq_days, months", [
    ("every day at 9 am for a month", 1, 1),
    ("every monday at 6pm for 3 months", 7, 3),
])
def test_a_clock_time_in_a_recurrence_names_no_other_start(
        text, freq_days, months):
    # a clock time names when in the day, so the length still counts from
    # the anchor
    from chronologia import extract_recurrence
    anchor = datetime(2026, 1, 30, 10, 0)
    got = extract_recurrence(text, "en", anchor=anchor)
    assert got.recurrence.count == _length(anchor, months=months).days \
        // freq_days
    assert got.remainder == ""


@pytest.mark.parametrize("lang, text, years", [
    ("da", "for et år siden", 1),
    ("nb", "for ti år siden", 10),
    ("nn", "for eit år sidan", 1),
])
def test_a_length_inside_a_date_stays_the_date(lang, text, years):
    # Danish and Norwegian "for <length> siden" is "<length> ago", so the
    # length is a part of the date and not the width of the event
    from chronologia import extract_event
    anchor = datetime(2026, 1, 30, 10, 0)
    got = extract_event(text, lang, anchor=anchor)
    assert got.span.start == anchor - relativedelta(years=years)
    assert got.duration is None
