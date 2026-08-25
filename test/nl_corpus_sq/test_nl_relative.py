"""Anchor-relative Albanian: named days, offsets, determiners and seasons."""
from datetime import date, timedelta

import pytest

from ._corpus import ANCHOR, ad, nomatch, start, start_end


@pytest.mark.parametrize("text,offset", [
    ("sot", 0), ("nesër", 1), ("dje", -1), ("pasnesër", 2), ("pardje", -2),
])
def test_named_days(text, offset):
    expected = (ANCHOR + timedelta(days=offset)).date()
    s, e = start_end(text)
    assert date(s.year, s.month, s.day) == expected
    assert date(e.year, e.month, e.day) == expected + timedelta(days=1)


# -- "ago": the counted noun stays INDEFINITE, singular for one and plural
#    where the two differ (vit/vjet, minutë/minuta, sekondë/sekonda) ---------

@pytest.mark.parametrize("text,delta", [
    ("një ditë më parë", timedelta(days=-1)),
    ("dy ditë më parë", timedelta(days=-2)),
    ("tre ditë më parë", timedelta(days=-3)),
    ("dhjetë ditë më parë", timedelta(days=-10)),
    ("njëmbëdhjetë ditë më parë", timedelta(days=-11)),
    ("njëzet e pesë ditë më parë", timedelta(days=-25)),
    ("tridhjetë e një ditë më parë", timedelta(days=-31)),
    ("një javë më parë", timedelta(weeks=-1)),
    ("tri javë më parë", timedelta(weeks=-3)),
    ("një orë më parë", timedelta(hours=-1)),
    ("pesë orë më parë", timedelta(hours=-5)),
    ("një minutë më parë", timedelta(minutes=-1)),
    ("dhjetë minuta më parë", timedelta(minutes=-10)),
])
def test_ago_with_more_pare(text, delta):
    assert start(text) == ad(ANCHOR + delta)


@pytest.mark.parametrize("text,delta", [
    ("para dy ditësh", timedelta(days=-2)),
    ("para tri javësh", timedelta(weeks=-3)),
    ("para dhjetë orësh", timedelta(hours=-10)),
])
def test_ago_fronted_with_para(text, delta):
    """``para`` fronts the same backward offset and governs the ablative,
    where ``më parë`` trails it and leaves the noun indefinite."""
    assert start(text) == ad(ANCHOR + delta)


def test_a_year_and_a_month_back():
    assert start("një vit më parë").year == ANCHOR.year - 1
    assert start("dy vjet më parë").year == ANCHOR.year - 2
    assert start("tre muaj më parë").month == ANCHOR.month - 3


# -- "in/after": ``pas`` governs the ABLATIVE, singular for one and the
#    ``-sh`` plural otherwise ------------------------------------------------

@pytest.mark.parametrize("text,delta", [
    ("pas një dite", timedelta(days=1)),
    ("pas dy ditësh", timedelta(days=2)),
    ("pas dhjetë ditësh", timedelta(days=10)),
    ("pas njëmbëdhjetë ditësh", timedelta(days=11)),
    ("pas një jave", timedelta(weeks=1)),
    ("pas dy javësh", timedelta(weeks=2)),
    ("pas një ore", timedelta(hours=1)),
    ("pas gjashtë orësh", timedelta(hours=6)),
    ("pas një minute", timedelta(minutes=1)),
    ("pas dhjetë minutash", timedelta(minutes=10)),
])
def test_in_with_pas(text, delta):
    assert start(text) == ad(ANCHOR + delta)


def test_a_year_and_a_month_forward():
    assert start("pas një viti").year == ANCHOR.year + 1
    assert start("pas dy vjetësh").year == ANCHOR.year + 2
    assert start("pas dy muajsh").month == ANCHOR.month + 2


def test_the_two_directions_are_symmetric():
    """The same count, the same unit, opposite markers: equal distances
    either side of the anchor."""
    back = ANCHOR - start("tre ditë më parë").datetime()
    forward = start("pas tre ditësh").datetime() - ANCHOR
    assert back == forward == timedelta(days=3)


# -- determiners over the calendar units ------------------------------------

def test_this_week_is_the_anchor_week():
    """The week starts on Monday, so the anchor's Tuesday sits inside it."""
    s, e = start_end("këtë javë")
    monday = ANCHOR.date() - timedelta(days=ANCHOR.weekday())
    assert date(s.year, s.month, s.day) == monday
    assert date(e.year, e.month, e.day) == monday + timedelta(days=7)


def test_last_week_precedes_this_one():
    monday = ANCHOR.date() - timedelta(days=ANCHOR.weekday())
    s, _ = start_end("javën e kaluar")
    assert date(s.year, s.month, s.day) == monday - timedelta(days=7)


def test_next_week_follows_this_one():
    monday = ANCHOR.date() - timedelta(days=ANCHOR.weekday())
    s, _ = start_end("javën e ardhshme")
    assert date(s.year, s.month, s.day) == monday + timedelta(days=7)


@pytest.mark.parametrize("text,month", [
    ("muajin e kaluar", 5), ("këtë muaj", 6), ("muajin e ardhshëm", 7),
])
def test_determiners_over_the_month(text, month):
    s, _ = start_end(text)
    assert (s.year, s.month, s.day) == (2017, month, 1)


# -- the year's three unrelated words ---------------------------------------

@pytest.mark.parametrize("text,year", [
    ("vjet", 2016), ("sivjet", 2017), ("mot", 2018),
])
def test_the_year_adverbs(text, year):
    """``vjet``/``sivjet``/``mot`` are three separate lexical items, not a
    pattern over ``vit``: each names a whole calendar year of its own."""
    s, e = start_end(text)
    assert (s.year, s.month, s.day) == (year, 1, 1)
    assert (e.year, e.month, e.day) == (year + 1, 1, 1)


def test_a_counted_vjet_is_a_duration_not_last_year():
    """``vjet`` is also the plural of ``vit``, so a count in front of it turns
    it back into the unit of a backward offset."""
    assert start("dy vjet më parë").year == 2015
    assert start("pesë vjet më parë").year == 2012


# -- weekdays ---------------------------------------------------------------

@pytest.mark.parametrize("text,day", [
    ("e hënë", 3), ("e martë", 4), ("e mërkurë", 28), ("e enjte", 29),
    ("e premte", 30), ("e shtunë", 1), ("e diel", 2),
])
def test_bare_weekday_takes_the_next_occurrence(text, day):
    """The anchor is Tuesday 27 June 2017; a bare weekday reads forward, so
    Wednesday is the 28th and Monday has to wait until 3 July."""
    s, _ = start_end(text)
    assert s.day == day


@pytest.mark.parametrize("text,expected", [
    ("të hënën e kaluar", date(2017, 6, 26)),
    ("të premten e kaluar", date(2017, 6, 23)),
    ("të premten e ardhshme", date(2017, 6, 30)),
    ("këtë të hënë", date(2017, 6, 26)),
])
def test_weekday_with_a_marker(text, expected):
    s, _ = start_end(text)
    assert date(s.year, s.month, s.day) == expected


# -- seasons and day parts --------------------------------------------------

@pytest.mark.parametrize("text,month", [
    ("pranverë", 3), ("verë", 6), ("vjeshtë", 9), ("dimër", 12),
])
def test_seasons(text, month):
    s, _ = start_end(text)
    assert s.month == month


def test_a_season_with_a_year():
    s, e = start_end("vera 2020")
    assert (s.year, s.month) == (2020, 6)
    assert (e.year, e.month) == (2020, 9)


@pytest.mark.parametrize("text,band", [
    ("e mëngjesit", (4, 12)),
    ("e pasdites", (12, 18)),
    ("e mbrëmjes", (18, 24)),
    ("e natës", (0, 4)),
])
def test_dayparts_follow_the_cldr_bands(text, band):
    s, e = start_end(text)
    assert s.hour == band[0]
    assert (e.hour or 24) == band[1]


def test_tonight_is_todays_night_band():
    s, e = start_end("sonte")
    assert date(s.year, s.month, s.day) == ANCHOR.date()
    assert (s.hour, e.hour) == (0, 4)


def test_a_bare_preposition_is_not_a_date():
    nomatch("para")
