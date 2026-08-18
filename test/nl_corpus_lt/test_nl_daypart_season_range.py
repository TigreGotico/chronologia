"""Day parts, seasons, the weekend, and open and closed ranges.

The day-part bands are the Lithuanian rows of the CLDR day-period chart, so
the evening runs to midnight and the night is the small hours -- unlike the
English default, where the night opens at 21:00.  Seasons and periods take
the bare accusative as their in/during form ("vasarą" = in summer).
"""
from datetime import timedelta

import pytest

from chronologia.astrodate import AstroDate

from ._corpus import ANCHOR, ad, span, start, start_end

_MID = ANCHOR.replace(hour=0, minute=0)


@pytest.mark.parametrize("text,h0,h1", [
    ("rytą", 6, 12),
    ("popietę", 12, 18),
    ("vakare", 18, 0),
    ("naktį", 0, 6),
])
def test_daypart_bands(text, h0, h1):
    s, e = start_end(text)
    assert s.hour == h0
    assert e.hour == h1


def test_evening_runs_to_midnight():
    """CLDR lt closes the evening at 24:00; the English default stops at
    21:00, so this is the band that must not fall back to the default."""
    s, e = start_end("vakare")
    assert (s.hour, e.hour, e.day) == (18, 0, ANCHOR.day + 1)


@pytest.mark.parametrize("text,m0,m1", [
    ("pavasaris", 3, 6), ("vasara", 6, 9), ("ruduo", 9, 12),
])
def test_seasons(text, m0, m1):
    s, e = start_end(text)
    assert (s.month, e.month) == (m0, m1)


def test_winter_wraps_the_year():
    s, e = start_end("žiema")
    assert (s.year, s.month) == (2017, 12) and (e.year, e.month) == (2018, 3)


@pytest.mark.parametrize("text,y", [
    ("vasara 2020", 2020), ("žiema 2019", 2019),
])
def test_season_with_year(text, y):
    assert start(text).year == y


@pytest.mark.parametrize("text,m0,m1", [
    ("vasarą", 6, 9), ("žiemą", 12, 3), ("pavasarį", 3, 6),
])
def test_accusative_season_is_the_in_during_form(text, m0, m1):
    s, e = start_end(text)
    assert (s.month, e.month) == (m0, m1)


def test_bare_weekend_is_the_coming_one():
    s, e = start_end("savaitgalis")
    assert s == ad(_MID + timedelta(days=4))       # Sat 2017-07-01
    assert (e - s).days == 2


def test_next_weekend():
    s, e = start_end("kitą savaitgalį")
    assert (e - s).days == 2
    assert s > ad(_MID + timedelta(days=4))


@pytest.mark.parametrize("text,m0,m1", [
    ("nuo birželio iki rugpjūčio", 6, 9),
    ("nuo sausio iki kovo", 1, 4),
    ("tarp birželio ir rugsėjo", 6, 10),
])
def test_month_ranges(text, m0, m1):
    s, e = start_end(text)
    assert s.month == m0 and e.month == m1


def test_iso_literal_date():
    assert start("2017-06-30") == AstroDate(2017, 6, 30)


@pytest.mark.parametrize("text,expected_days", [
    ("šie metai", 365), ("praeiti metai", 366), ("kiti metai", 365),
])
def test_bare_nominative_year_period(text, expected_days):
    s = span(text)
    assert (s.end - s.start).days == expected_days
