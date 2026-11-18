"""Dutch numbers read through numtag.

A Dutch number is one compound word ("drieëntwintig"), an ordinal century is
one word ("eenentwintigste"), and the clock fractions "half" and "kwart" stay
words the clock grammar reads.  Every expected value is written by hand or
computed with ``relativedelta`` / ``timedelta`` from the anchor.
"""
import pytest

from chronologia import extract_duration

from ._corpus import (ANCHOR, datetime, relativedelta, span, start_end,
                      timedelta)


@pytest.mark.parametrize("text,expected", [
    ("over drieëntwintig dagen", ANCHOR + timedelta(days=23)),
    ("over honderd dagen", ANCHOR + timedelta(days=100)),
    ("tweeduizend jaar geleden", ANCHOR - relativedelta(years=2000)),
    ("vijf seconden geleden", ANCHOR - timedelta(seconds=5)),
    ("over duizend dagen", ANCHOR + timedelta(days=1000)),
    ("duizend tweehonderd dagen geleden", ANCHOR - timedelta(days=1200)),
])
def test_count(text, expected):
    assert span(text).start == expected


def test_ordinal_century():
    assert start_end("de eenentwintigste eeuw") == (
        datetime(2000, 1, 1), datetime(2100, 1, 1))
    assert start_end("de 21e eeuw") == (
        datetime(2000, 1, 1), datetime(2100, 1, 1))


def test_spelled_year():
    assert start_end("in het jaar tweeduizend vijfentwintig") == (
        datetime(2025, 1, 1), datetime(2026, 1, 1))
    assert start_end("in het jaar duizend negenhonderdzeven") == (
        datetime(1907, 1, 1), datetime(1908, 1, 1))
    assert span("op eenentwintig mei tweeduizend vijfentwintig").start == \
        datetime(2025, 5, 21)


@pytest.mark.parametrize("text,day", [
    ("op de eenentwintigste mei 2025", 21),
    ("op de drieëntwintigste mei 2025", 23),
    ("op de eenendertigste mei 2025", 31),
])
def test_ordinal_day(text, day):
    assert span(text).start == datetime(2025, 5, day)


@pytest.mark.parametrize("text,expected", [
    # "half acht" is half an hour before eight: 7:30
    ("om half acht", datetime(2017, 6, 27, 19, 30)),
    ("om kwart over drie", datetime(2017, 6, 27, 15, 15)),
])
def test_clock_fractions(text, expected):
    assert span(text).start == expected


@pytest.mark.parametrize("text,length", [
    # one and a half weeks: 7 + 3.5 days
    ("over anderhalve week", timedelta(days=10, hours=12)),
    ("over anderhalf uur", timedelta(hours=1, minutes=30)),
])
def test_anderhalf(text, length):
    assert extract_duration(text, "nl").duration == length
