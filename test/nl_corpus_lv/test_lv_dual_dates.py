"""The two Latvian date constructions, which differ in the month's case.

A date standing alone as a heading or dateline names its month in the
NOMINATIVE, after the government-regulated "YYYY. gada" prefix: "2017. gada
29. maijs".  The same date inside a sentence names its month in the LOCATIVE
and drops the nominative day: "3. maijā", "10. aprīlī".  Both ship, and both
are pinned here against the other's shape, because a locale that read only
one of them would silently mis-parse half of ordinary Latvian.

The gold is the calendar itself: the date named is the date asserted, with
the year supplied by hand where the construction leaves it out and the
future-preferring convention picks it.
"""
from datetime import date, datetime, timedelta

import pytest

from ._corpus import ANCHOR, ad, nomatch, parse, remainder, span, start_end


def _day(y, m, d):
    return (ad(datetime(y, m, d)), ad(datetime(y, m, d) + timedelta(days=1)))


# -- dateline: "<year>. gada <day>. <month-nominative>" ----------------------

@pytest.mark.parametrize("text,y,m,d", [
    ("2017. gada 29. maijs", 2017, 5, 29),
    ("2024. gada 15. marts", 2024, 3, 15),
    ("2020. gada 25. decembris", 2020, 12, 25),
    ("1990. gada 4. maijs", 1990, 5, 4),
    ("2017. gada 1. janvāris", 2017, 1, 1),
    ("2005. gada 30. septembris", 2005, 9, 30),
    ("1918. gada 18. novembris", 1918, 11, 18),
    ("2021. gada 8. februāris", 2021, 2, 8),
    ("2019. gada 12. augusts", 2019, 8, 12),
    ("2022. gada 3. jūlijs", 2022, 7, 3),
])
def test_dateline_names_the_month_in_the_nominative(text, y, m, d):
    assert start_end(text) == _day(y, m, d)


def test_dateline_consumes_the_whole_phrase():
    assert remainder("2017. gada 29. maijs") == ""


# -- adverbial: "<day>. <month-locative>", year from the anchor -------------
# The anchor is 2017-06-27, and the locale prefers the future, so a date
# already past in 2017 lands in 2018 and one still ahead stays in 2017.

@pytest.mark.parametrize("text,y,m,d", [
    ("3. maijā", 2018, 5, 3),
    ("10. aprīlī", 2018, 4, 10),
    ("1. janvārī", 2018, 1, 1),
    ("25. decembrī", 2017, 12, 25),
    ("30. jūnijā", 2017, 6, 30),
    ("14. jūlijā", 2017, 7, 14),
    ("2. septembrī", 2017, 9, 2),
    ("11. novembrī", 2017, 11, 11),
    ("28. februārī", 2018, 2, 28),
    ("9. martā", 2018, 3, 9),
    ("31. augustā", 2017, 8, 31),
    ("5. oktobrī", 2017, 10, 5),
])
def test_adverbial_names_the_month_in_the_locative(text, y, m, d):
    assert start_end(text) == _day(y, m, d)


@pytest.mark.parametrize("text,y,m,d", [
    ("2017. gada 3. maijā", 2017, 5, 3),
    ("2020. gada 25. decembrī", 2020, 12, 25),
])
def test_the_year_prefix_also_heads_the_adverbial(text, y, m, d):
    assert start_end(text) == _day(y, m, d)


# -- the two shapes name the same day when the year is stated ---------------

def test_nominative_and_locative_agree_on_the_day():
    assert span("2017. gada 29. maijs").start == span("2017. gada 29. maijā").start


# -- a bare month, in either case ------------------------------------------

@pytest.mark.parametrize("text,m", [
    ("maijs", 5), ("maijā", 5), ("decembris", 12), ("decembrī", 12),
    ("janvāris", 1), ("janvārī", 1), ("jūlijs", 7), ("jūlijā", 7),
])
def test_bare_month_spans_that_month(text, m):
    s, e = start_end(text)
    assert (s.month, s.day) == (m, 1)
    assert e > s


@pytest.mark.parametrize("text,m", [
    ("2019. gada maijs", 5), ("2019. gada decembris", 12),
])
def test_month_with_a_stated_year(text, m):
    s, _ = start_end(text)
    assert (s.year, s.month, s.day) == (2019, m, 1)


# -- the spelled day-of-month ordinal --------------------------------------

@pytest.mark.parametrize("text,y,m,d", [
    ("2017. gada piektais maijs", 2017, 5, 5),
    ("2017. gada divdesmit piektais maijs", 2017, 5, 25),
    ("2017. gada vienpadsmitais maijs", 2017, 5, 11),
])
def test_spelled_day_ordinal(text, y, m, d):
    assert start_end(text) == _day(y, m, d)


# -- the ISO and numeric literals the tokenizer keeps whole -----------------

@pytest.mark.parametrize("text,y,m,d", [
    ("2017-06-30", 2017, 6, 30), ("2020-12-25", 2020, 12, 25),
])
def test_iso_date(text, y, m, d):
    assert start_end(text) == _day(y, m, d)


def test_bare_year():
    s, e = start_end("2019")
    assert (s.year, s.month, s.day) == (2019, 1, 1)
    assert (e.year, e.month, e.day) == (2020, 1, 1)


def test_weekday_and_date_together():
    """"pirmdien, 10. aprīlī" -- the adverbial weekday leading the adverbial
    date, the phrasing the construction is attested in."""
    s, e = start_end("pirmdien, 10. aprīlī")
    assert (s.month, s.day) == (4, 10)


@pytest.mark.parametrize("text,weekday", [
    ("pirmdiena", 0), ("otrdiena", 1), ("trešdiena", 2), ("ceturtdiena", 3),
    ("piektdiena", 4), ("sestdiena", 5), ("svētdiena", 6),
])
def test_bare_weekday_names_its_next_occurrence(text, weekday):
    ahead = (weekday - ANCHOR.weekday()) % 7 or 7
    expected = (ANCHOR + timedelta(days=ahead)).date()
    s, e = start_end(text)
    assert date(s.year, s.month, s.day) == expected
    assert date(e.year, e.month, e.day) == expected + timedelta(days=1)


@pytest.mark.parametrize("text,weekday", [
    ("pirmdienā", 0), ("otrdienā", 1), ("trešdienā", 2), ("ceturtdienā", 3),
    ("piektdienā", 4), ("sestdienā", 5), ("svētdienā", 6),
])
def test_locative_weekday_is_the_adverbial_form(text, weekday):
    ahead = (weekday - ANCHOR.weekday()) % 7 or 7
    expected = (ANCHOR + timedelta(days=ahead)).date()
    s, _ = start_end(text)
    assert date(s.year, s.month, s.day) == expected
