"""Swedish numbers read through numtag.

A Swedish number is one compound word ("tjugotre"), and an ordinal is one word
("tjugotredje").  Every expected value is written by hand or computed with
``timedelta`` from the anchor.
"""
from chronologia import extract_duration

from ._corpus import ANCHOR, datetime, span, timedelta


def test_ordinal_day_and_year():
    assert span("den tjugotredje maj tjugohundratjugofem").start == \
        datetime(2025, 5, 23)


def test_count():
    assert span("om tjugotre dagar").start == ANCHOR + timedelta(days=23)


def test_clock_half():
    # "halv åtta" is half an hour before eight: 7:30
    assert span("klockan halv åtta").start == datetime(2017, 6, 27, 19, 30)


def test_hour_and_a_half():
    assert extract_duration("om en och en halv timme", "sv").duration == \
        timedelta(hours=1, minutes=30)
