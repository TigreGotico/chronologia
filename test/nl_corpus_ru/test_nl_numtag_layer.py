"""Russian numbers read through numtag.

numtag reads the numbers of every case form: the counts, the spelled years,
the day ordinals ("двадцать третьего") and the clock hours.  Every expected
value is written by hand or computed with ``timedelta`` from the anchor; a
lone clock hour takes the next twelve-hour reading after the anchor.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, ad, parse, start


@pytest.mark.parametrize("text,expected", [
    ("тысяча двести дней назад", ANCHOR - timedelta(days=1200)),
    ("через тысячу дней", ANCHOR + timedelta(days=1000)),
    ("двадцать третьего мая 2025", datetime(2025, 5, 23)),
    ("пятнадцатое апреля 2025", datetime(2025, 4, 15)),
    ("в половине девятого", datetime(2017, 6, 27, 20, 30)),
])
def test_numbers_read_through_numtag(text, expected):
    assert start(text) == ad(expected)


# The year of a spelled date is an ordinal that holds a scale word; the
# date keeps the year it names, whatever the anchor.
@pytest.mark.parametrize("anchor", [
    datetime(2026, 1, 10, 8, 0),
    datetime(2026, 12, 1, 8, 0),
    datetime(2028, 3, 1, 8, 0),
])
@pytest.mark.parametrize("text,month,day", [
    ("первого мая две тысячи двадцать шестого года", 5, 1),
    ("двадцатого марта две тысячи двадцать шестого года", 3, 20),
])
def test_spelled_date_with_a_year_from_2000(text, month, day, anchor):
    result = parse(text, anchor)
    assert result.span.start == ad(datetime(2026, month, day))


# An ordinal after a locative preposition names a floor or a rank, not an hour.
def test_ordinal_after_a_locative_preposition_is_no_clock():
    assert parse("на втором этаже") is None


@pytest.mark.xfail(raises=AssertionError, strict=True, reason="https://github.com/TigreGotico/chronologia/issues/1192")
def test_known_gap_amount_of_a_thousand_is_no_year():
    assert start("за тысячу рублей вчера") == ad(datetime(2017, 6, 26))


@pytest.mark.xfail(raises=AssertionError, strict=True, reason="https://github.com/TigreGotico/chronologia/issues/1193")
def test_known_gap_hour_and_minute_clock():
    assert start("в девять тридцать") == ad(datetime(2017, 6, 27, 21, 30))


@pytest.mark.xfail(raises=AssertionError, strict=True, reason="https://github.com/TigreGotico/chronologia/issues/1194")
def test_known_gap_first_half_of_the_day():
    result = parse("в первой половине дня", datetime(2026, 11, 18, 8, 0))
    assert result is None or result.span.start != ad(datetime(2026, 11, 18, 13, 0))


@pytest.mark.parametrize("text", [
    "поговорим о втором варианте",
    "думаю о первой любви",
    "книга о третьем рейхе",
])
def test_ordinal_after_about_is_no_clock(text):
    assert parse(text) is None


@pytest.mark.xfail(raises=AssertionError, strict=True, reason="https://github.com/TigreGotico/chronologia/issues/1221")
@pytest.mark.parametrize("text,expected", [
    ("в половине девятого позвони маме", datetime(2017, 6, 27, 20, 30)),
    ("в четверть девятого позвони маме", datetime(2017, 6, 27, 20, 15)),
])
def test_known_gap_fraction_clock_before_another_word(text, expected):
    assert start(text) == ad(expected)


def test_ninth_hour_is_the_hour_before_nine():
    result = parse("в девятом часу позвони маме")
    assert result.span.start == ad(datetime(2017, 6, 27, 20, 0))
    assert result.span.end == ad(datetime(2017, 6, 27, 21, 0))
    assert result.remainder == "позвони маме"
