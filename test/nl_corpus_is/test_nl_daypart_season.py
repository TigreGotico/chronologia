"""Day parts, seasons and the weekend.

The day-part bands are the Icelandic rows of the CLDR day-period rule set, so
the evening runs to midnight and the night is the small hours -- unlike the
English default, where the night opens at 21:00.  CLDR's wide afternoon name
is two words ("eftir hádegi"); the single-token surface is the abbreviated
"síðdegis", which is what the deictic grammar can bind.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, ad, span, start, start_end

_MID = ANCHOR.replace(hour=0, minute=0)


@pytest.mark.parametrize("text,h0,h1", [
    ("morgunn", 6, 12),
    ("síðdegis", 12, 18),
    ("kvöld", 18, 0),
    ("nótt", 0, 6),
])
def test_daypart_bands(text, h0, h1):
    s, e = start_end(text)
    assert s.hour == h0
    assert e.hour == h1


def test_evening_runs_to_midnight():
    """CLDR is closes the evening at 24:00; the English default stops at
    21:00, so this is the band that must not fall back to the default."""
    s, e = start_end("kvöld")
    assert (s.hour, e.hour, e.day) == (18, 0, ANCHOR.day + 1)


def test_night_is_the_small_hours():
    s, e = start_end("nótt")
    assert (s.hour, e.hour) == (0, 6)


@pytest.mark.parametrize("text,m0,m1", [
    ("vor", 3, 6), ("sumar", 6, 9), ("haust", 9, 12),
])
def test_seasons(text, m0, m1):
    s, e = start_end(text)
    assert (s.month, e.month) == (m0, m1)


def test_winter_wraps_the_year():
    s, e = start_end("vetur")
    assert (s.year, s.month) == (2017, 12) and (e.year, e.month) == (2018, 3)


@pytest.mark.parametrize("text,y", [
    ("sumar 2020", 2020), ("vetur 2019", 2019), ("haust 2021", 2021),
])
def test_season_with_year(text, y):
    assert start(text).year == y


@pytest.mark.parametrize("text,m0,m1", [
    ("sumarið", 6, 9), ("vorið", 3, 6), ("haustið", 9, 12),
])
def test_definite_season_names_the_same_season(text, m0, m1):
    s, e = start_end(text)
    assert (s.month, e.month) == (m0, m1)


def test_bare_weekend_is_the_coming_one():
    s, e = start_end("helgi")
    assert s == ad(_MID + timedelta(days=4))       # Sat 2017-07-01
    assert (e - s).days == 2


def test_next_weekend():
    s, e = start_end("næsta helgi")
    assert (e - s).days == 2
    assert s > ad(_MID + timedelta(days=4))


@pytest.mark.parametrize("text,idx", [
    ("mánudagur", 0), ("þriðjudagur", 1), ("miðvikudagur", 2),
    ("fimmtudagur", 3), ("föstudagur", 4), ("laugardagur", 5),
    ("sunnudagur", 6),
])
def test_bare_weekday_names_its_next_occurrence(text, idx):
    ahead = (idx - ANCHOR.weekday()) % 7 or 7
    expected = (ANCHOR + timedelta(days=ahead)).date()
    s = span(text)
    assert (s.start.year, s.start.month, s.start.day) == (
        expected.year, expected.month, expected.day)
    assert (s.end - s.start).days == 1
