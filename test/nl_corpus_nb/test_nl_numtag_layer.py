"""Bokmål numbers read through numtag.

A Bokmål number is one compound word ("tjuefem") or a run joined by "og", and a
spelled year is a run of such words.  Every expected value is written by hand
or computed with ``timedelta`` from the anchor.
"""
import pytest

from ._corpus import ANCHOR, datetime, span, start_end, timedelta


def test_spelled_year():
    assert start_end("år to tusen og tjuefem") == (
        datetime(2025, 1, 1), datetime(2026, 1, 1))
    assert start_end("år to tusen og en") == (
        datetime(2001, 1, 1), datetime(2002, 1, 1))
    assert start_end("år nitten hundre og nittini") == (
        datetime(1999, 1, 1), datetime(2000, 1, 1))
    assert span("den tjuefemte desember to tusen og tjuefem").start == \
        datetime(2025, 12, 25)


@pytest.mark.parametrize("text,expected", [
    ("om tjueen dager", ANCHOR + timedelta(days=21)),
    ("om hundre og en dager", ANCHOR + timedelta(days=101)),
    ("om tusen dager", ANCHOR + timedelta(days=1000)),
    ("for tusen to hundre dager siden", ANCHOR - timedelta(days=1200)),
    ("for hundre og en dager siden", ANCHOR - timedelta(days=101)),
])
def test_count(text, expected):
    assert span(text).start == expected


def test_ordinal_day():
    assert span("den tjuefemte desember").start == datetime(2017, 12, 25)
    assert span("første mandag i mai 2021").start == datetime(2021, 5, 3)
    assert span("annen mandag i mai 2021").start == datetime(2021, 5, 10)


def test_neuter_second_quarter():
    # "annet" is the neuter of the ordinal "annen"
    assert start_end("annet kvartal 2018") == (
        datetime(2018, 4, 1), datetime(2018, 7, 1))
    assert start_end("i annet kvartal") == (
        datetime(2017, 4, 1), datetime(2017, 7, 1))


def test_clock_half():
    # "halv åtte" is half an hour before eight: 7:30
    assert span("klokka halv åtte").start == datetime(2017, 6, 27, 19, 30)
    assert span("kvart over tre").start == datetime(2017, 6, 27, 15, 15)
