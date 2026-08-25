"""Day-part bands and seasons.

CLDR draws the Vietnamese day in four bands -- sáng 04:00-12:00, chiều
12:00-18:00, tối 18:00-21:00, đêm 21:00-04:00 -- plus a noon point (trưa) that
falls inside the afternoon and adds no boundary of its own.  The same words
double as the meridiem that places a spoken hour, and they follow the whole
clock expression rather than preceding it.

Seasons are the transparent mùa ("season") compounds.
"""
import pytest

from ._corpus import parse, start, start_end


@pytest.mark.parametrize("text,h0,h1", [
    ("sáng", 4, 12),
    ("chiều", 12, 18),
    ("tối", 18, 21),
])
def test_daypart_bands(text, h0, h1):
    s, e = start_end(text)
    assert s.hour == h0
    assert e.hour == h1


def test_the_night_band_wraps_past_midnight():
    s, e = start_end("đêm")
    assert s.hour == 21
    assert e.hour == 4
    assert e.day != s.day


@pytest.mark.parametrize("text,month", [
    ("mùa xuân", 3),
    ("mùa hè", 6),
    ("mùa hạ", 6),
    ("mùa thu", 9),
    ("mùa đông", 12),
])
def test_seasons_north_of_the_equator(text, month):
    assert start(text).month == month


def test_the_weekend_is_saturday_and_sunday():
    s, e = start_end("cuối tuần")
    assert s.weekday() == 5
    assert (e - s).days == 2


@pytest.mark.parametrize("text", ["mùa", "cuối"])
def test_a_bare_head_noun_names_no_period(text):
    assert parse(text) is None
