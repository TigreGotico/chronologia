"""Deictic days, relative periods and weekday references.

The five deictic day words are CLDR's ``day.relative-type-*`` for be; the
this/last/next period phrases are its ``relative-type-*`` per field, which in
Belarusian put the determiner in the locative ("у мінулым месяцы", "на
наступным тыдні").
"""
from datetime import date, datetime, timedelta

import pytest

from ._corpus import ANCHOR, remainder, start, start_end

TODAY = ANCHOR.date()


@pytest.mark.parametrize("text,offset", [
    ("пазаўчора", -2), ("учора", -1), ("сёння", 0), ("заўтра", 1),
    ("паслязаўтра", 2),
])
def test_deictic_days(text, offset):
    s, e = start_end(text)
    assert s.date() == TODAY + timedelta(days=offset)
    assert e.date() == TODAY + timedelta(days=offset + 1)


@pytest.mark.parametrize("text,offset", [
    ("праз 1 дзень", 1), ("праз 3 дні", 3), ("праз 10 дзён", 10),
    ("1 дзень таму", -1), ("3 дні таму", -3), ("10 дзён таму", -10),
])
def test_day_offsets(text, offset):
    assert start(text).date() == TODAY + timedelta(days=offset)


@pytest.mark.parametrize("text,weekday", [
    ("панядзелак", 0), ("аўторак", 1), ("серада", 2), ("чацвер", 3),
    ("пятніца", 4), ("субота", 5), ("нядзеля", 6),
])
def test_bare_weekday_is_its_next_occurrence(text, weekday):
    s = start(text)
    assert s.date().weekday() == weekday
    assert s.date() > TODAY


@pytest.mark.parametrize("text,weekday", [
    ("мінулы панядзелак", 0), ("мінулы аўторак", 1), ("мінулая серада", 2),
    ("мінулы чацвер", 3), ("мінулая пятніца", 4), ("мінулая субота", 5),
    ("мінулая нядзеля", 6),
])
def test_last_weekday(text, weekday):
    s = start(text)
    assert s.date().weekday() == weekday
    assert s.date() < TODAY


@pytest.mark.parametrize("text,weekday", [
    ("наступны панядзелак", 0), ("наступны чацвер", 3),
    ("наступная пятніца", 4), ("наступная нядзеля", 6),
])
def test_next_weekday(text, weekday):
    s = start(text)
    assert s.date().weekday() == weekday
    assert s.date() > TODAY


@pytest.mark.parametrize("text,d0,d1", [
    ("мінулы тыдзень", date(2017, 6, 19), date(2017, 6, 26)),
    ("гэты тыдзень", date(2017, 6, 26), date(2017, 7, 3)),
    ("наступны тыдзень", date(2017, 7, 3), date(2017, 7, 10)),
])
def test_relative_week(text, d0, d1):
    s, e = start_end(text)
    assert (s.date(), e.date()) == (d0, d1)


@pytest.mark.parametrize("text,m0,m1", [
    ("мінулы месяц", 5, 6), ("гэты месяц", 6, 7), ("наступны месяц", 7, 8),
])
def test_relative_month(text, m0, m1):
    s, e = start_end(text)
    assert (s.month, s.day) == (m0, 1)
    assert e.month == m1


@pytest.mark.parametrize("text,year", [
    ("мінулы год", 2016), ("гэты год", 2017), ("наступны год", 2018),
])
def test_relative_year(text, year):
    s, e = start_end(text)
    assert (s.year, s.month, s.day) == (year, 1, 1)
    assert e.year == year + 1


#: CLDR's relative-type-* wording per field: a prepositional phrase whose head
#: is in the locative.  The week takes на, everything else у.
LOCATIVE_PERIODS = [
    ("у мінулым годзе", date(2016, 1, 1), date(2017, 1, 1)),
    ("у гэтым годзе", date(2017, 1, 1), date(2018, 1, 1)),
    ("у наступным годзе", date(2018, 1, 1), date(2019, 1, 1)),
    ("у мінулым месяцы", date(2017, 5, 1), date(2017, 6, 1)),
    ("у гэтым месяцы", date(2017, 6, 1), date(2017, 7, 1)),
    ("у наступным месяцы", date(2017, 7, 1), date(2017, 8, 1)),
    ("у мінулым квартале", date(2017, 1, 1), date(2017, 4, 1)),
    ("у гэтым квартале", date(2017, 4, 1), date(2017, 7, 1)),
    ("у наступным квартале", date(2017, 7, 1), date(2017, 10, 1)),
    ("на мінулым тыдні", date(2017, 6, 19), date(2017, 6, 26)),
    ("на гэтым тыдні", date(2017, 6, 26), date(2017, 7, 3)),
    ("на наступным тыдні", date(2017, 7, 3), date(2017, 7, 10)),
]


@pytest.mark.parametrize("text,d0,d1", LOCATIVE_PERIODS)
def test_the_locative_relative_phrase(text, d0, d1):
    s, e = start_end(text)
    assert (s.date(), e.date()) == (d0, d1)


@pytest.mark.parametrize("text,d0,d1", LOCATIVE_PERIODS)
def test_the_locative_preposition_is_consumed(text, d0, d1):
    """The whole phrase is the reading -- у/на is part of the wording CLDR
    gives, not a leftover word."""
    assert remainder(text) == ""


@pytest.mark.parametrize("text,d0,d1", [
    ("летась", date(2016, 1, 1), date(2017, 1, 1)),
    ("сёлета", date(2017, 1, 1), date(2018, 1, 1)),
])
def test_the_one_word_year_deictics(text, d0, d1):
    """CLDR's relative-type--1 and relative-type-0 for the year field are
    single words, not the periphrastic phrasing -- летась is the whole of last
    year and сёлета the whole of this one."""
    s, e = start_end(text)
    assert (s.date(), e.date()) == (d0, d1)
    assert remainder(text) == ""


@pytest.mark.parametrize("adverb,phrase", [
    ("летась", "у мінулым годзе"), ("сёлета", "у гэтым годзе"),
])
def test_the_year_deictic_matches_its_periphrastic_synonym(adverb, phrase):
    """The two wordings name the same span; neither displaces the other."""
    assert start_end(adverb) == start_end(phrase)


def test_the_year_deictics_at_a_second_anchor():
    """Read against a different year, so neither reading can be an accident of
    the corpus anchor."""
    other = datetime(2026, 8, 12, 13, 4)
    assert start("летась", other).year == 2025
    assert start("сёлета", other).year == 2026


@pytest.mark.parametrize("text,season,year", [
    ("вясна 2020", 3, 2020), ("лета 2020", 6, 2020),
    ("восень 2020", 9, 2020), ("зіма 2020", 12, 2020),
])
def test_season_with_a_year(text, season, year):
    s = start(text)
    assert s.month == season


@pytest.mark.parametrize("text", ["наступная зіма", "наступнае лета"])
def test_relative_season(text):
    assert start(text) > ANCHOR


@pytest.mark.parametrize("text,q0", [
    ("першы квартал 2020", 1), ("другі квартал 2020", 4),
    ("трэці квартал 2020", 7), ("чацвёрты квартал 2020", 10),
])
def test_calendar_quarter(text, q0):
    s = start(text)
    assert (s.year, s.month, s.day) == (2020, q0, 1)


@pytest.mark.parametrize("text,d", [
    ("апошні панядзелак ліпеня", date(2017, 7, 31)),
    ("першая серада мая", date(2017, 5, 3)),
    ("першы панядзелак 2027 года", date(2027, 1, 4)),
])
def test_scoped_ordinal_weekday(text, d):
    assert start(text).date() == d
