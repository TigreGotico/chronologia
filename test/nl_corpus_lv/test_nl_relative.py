"""Anchor-relative Latvian: named days, determiners, dayparts and seasons."""
from datetime import date, timedelta

import pytest

from ._corpus import ANCHOR, ad, nomatch, parse, start, start_end


@pytest.mark.parametrize("text,offset", [
    ("šodien", 0), ("rīt", 1), ("vakar", -1), ("parīt", 2), ("aizvakar", -2),
])
def test_named_days(text, offset):
    expected = (ANCHOR + timedelta(days=offset)).date()
    s, e = start_end(text)
    assert date(s.year, s.month, s.day) == expected
    assert date(e.year, e.month, e.day) == expected + timedelta(days=1)


@pytest.mark.parametrize("text,delta", [
    ("pirms stundas", timedelta(hours=-1)),
    ("pirms dienas", timedelta(days=-1)),
    ("pirms nedēļas", timedelta(weeks=-1)),
    ("pirms minūtes", timedelta(minutes=-1)),
    ("pēc stundas", timedelta(hours=1)),
    ("pēc dienas", timedelta(days=1)),
    ("pēc nedēļas", timedelta(weeks=1)),
    ("pēc minūtes", timedelta(minutes=1)),
])
def test_bare_singular_offsets(text, delta):
    """"pirms gada" and friends: the unit alone, with the count of one left
    implicit, in the genitive singular the marker governs."""
    assert start(text) == ad(ANCHOR + delta)


def test_a_year_back_and_forward():
    assert start("pirms gada").year == ANCHOR.year - 1
    assert start("pēc gada").year == ANCHOR.year + 1


def test_a_month_back_and_forward():
    assert start("pirms mēneša").month == ANCHOR.month - 1
    assert start("pēc mēneša").month == ANCHOR.month + 1


# -- determiners over the calendar units ------------------------------------

def test_this_week_is_the_anchor_week():
    """The week starts on Monday, so the anchor's Tuesday sits inside it."""
    s, e = start_end("šajā nedēļā")
    monday = ANCHOR.date() - timedelta(days=ANCHOR.weekday())
    assert date(s.year, s.month, s.day) == monday
    assert date(e.year, e.month, e.day) == monday + timedelta(days=7)


def test_last_week_precedes_this_one():
    monday = ANCHOR.date() - timedelta(days=ANCHOR.weekday())
    s, _ = start_end("pagājušajā nedēļā")
    assert date(s.year, s.month, s.day) == monday - timedelta(days=7)


def test_next_week_follows_this_one():
    monday = ANCHOR.date() - timedelta(days=ANCHOR.weekday())
    s, _ = start_end("nākamajā nedēļā")
    assert date(s.year, s.month, s.day) == monday + timedelta(days=7)


@pytest.mark.parametrize("text,year", [
    ("pagājušajā gadā", 2016), ("šajā gadā", 2017), ("nākamajā gadā", 2018),
])
def test_determiners_over_the_year(text, year):
    assert start(text).year == year


@pytest.mark.parametrize("text,month", [
    ("pagājušajā mēnesī", 5), ("šajā mēnesī", 6), ("nākamajā mēnesī", 7),
])
def test_determiners_over_the_month(text, month):
    assert start(text).month == month


@pytest.mark.parametrize("text,weekday,forward", [
    ("nākamajā pirmdienā", 0, True),
    ("nākamajā piektdienā", 4, True),
    ("pagājušajā otrdienā", 1, False),
    ("pagājušajā sestdienā", 5, False),
])
def test_determiners_over_a_weekday(text, weekday, forward):
    s, _ = start_end(text)
    assert date(s.year, s.month, s.day).weekday() == weekday
    if forward:
        assert date(s.year, s.month, s.day) > ANCHOR.date()
    else:
        assert date(s.year, s.month, s.day) < ANCHOR.date()


# -- dayparts: CLDR lv bands, evening closing at 23:00 ----------------------

@pytest.mark.parametrize("text,h0,h1", [
    ("rītā", 6, 12), ("pēcpusdienā", 12, 18), ("vakarā", 18, 23),
])
def test_daypart_bands(text, h0, h1):
    s, e = start_end(text)
    assert (s.hour, e.hour) == (h0, h1)


def test_the_night_band_crosses_midnight():
    """CLDR puts the Latvian night at 23:00-06:00, an hour later than the
    Lithuanian one."""
    s, e = start_end("naktī")
    assert (s.hour, e.hour) == (23, 6)
    assert e > s


@pytest.mark.parametrize("text,h", [("pusnaktī", 0), ("pusdienlaikā", 12)])
def test_day_anchors(text, h):
    assert start(text).hour == h


# -- seasons ----------------------------------------------------------------

@pytest.mark.parametrize("text,month", [
    ("pavasarī", 3), ("vasarā", 6), ("rudenī", 9), ("ziemā", 12),
])
def test_seasons_open_on_their_meteorological_month(text, month):
    assert start(text).month == month


@pytest.mark.parametrize("text,year,month", [
    ("vasara 2020", 2020, 6), ("ziema 2019", 2019, 12),
])
def test_season_with_a_year(text, year, month):
    s, _ = start_end(text)
    assert (s.year, s.month) == (year, month)


def test_next_winter():
    s, _ = start_end("nākamā ziema")
    assert (s.year, s.month) == (2017, 12)


# -- centuries and decades --------------------------------------------------

@pytest.mark.parametrize("text,y0,y1", [
    ("20. gadsimts", 1900, 2000), ("20. gadsimtā", 1900, 2000),
    ("19. gadsimts", 1800, 1900),
])
def test_century_scope(text, y0, y1):
    s, e = start_end(text)
    assert (s.year, e.year) == (y0, y1)


@pytest.mark.parametrize("text,n", [
    ("pirms 2 gadsimtiem", 200), ("pirms gadsimta", 100),
])
def test_century_offsets(text, n):
    assert start(text).year == ANCHOR.year - n


# -- what an incomplete phrase must not become ------------------------------

@pytest.mark.parametrize("text", [
    "pirms", "pēc", "dienas", "gadi", "nedēļas",
])
def test_a_bare_marker_or_unit_is_not_an_offset(text):
    res = parse(text)
    assert res is None or res[0].start.date() == ANCHOR.date()


@pytest.mark.parametrize("text", [
    "trīs dienas", "piecas dienas", "divas nedēļas", "desmit gadi", "3 dienas",
])
def test_a_count_without_a_marker_is_a_quantity(text):
    nomatch(text)
