"""West Frisian numbers read through numtag.

A Frisian number is one compound word ("fiifentweintich") or a run of words, and
an ordinal day ends in "ste" or "de".  Every expected value is written by hand
or computed with ``timedelta`` from the anchor.
"""
import pytest

from ._corpus import ANCHOR, datetime, span, start_end, timedelta


@pytest.mark.parametrize("text,day", [
    ("de sânde maaie 2025", 7),
    ("de ienentweintichste maaie 2025", 21),
    ("de fiifentweintichste maaie 2025", 25),
    ("de njoggenentweintichste maaie 2025", 29),
    ("de ienentritichste maaie 2025", 31),
])
def test_ordinal_day(text, day):
    assert span(text).start == datetime(2025, 5, day)


def test_spelled_year():
    assert start_end("it jier twatûzenfiifentweintich") == (
        datetime(2025, 1, 1), datetime(2026, 1, 1))


@pytest.mark.parametrize("text,expected", [
    ("oer ienentweintich dagen", ANCHOR + timedelta(days=21)),
    ("oer twahûndertfyftich dagen", ANCHOR + timedelta(days=250)),
    ("ienentweintich dagen lyn", ANCHOR - timedelta(days=21)),
])
def test_count(text, expected):
    assert span(text).start == expected


def test_digit_ordinal_century():
    assert start_end("de 21e ieu") == (datetime(2000, 1, 1), datetime(2100, 1, 1))


def test_clock_inflected_hour():
    # "healwei fiven" is half an hour before five: 4:30
    assert span("healwei fiven").start == datetime(2017, 6, 27, 16, 30)
    assert span("kertier oer fjouweren").start == datetime(2017, 6, 27, 16, 15)
