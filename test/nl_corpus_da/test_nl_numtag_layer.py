"""Danish numbers read through numtag.

A Danish number is one compound word ("enogtyve"), and a spelled year is one
or two words ("totusinde femogtyve"). Every expected value is written by
hand or computed with ``timedelta`` from the anchor.
"""
import pytest

from ._corpus import ANCHOR, datetime, span, start_end, timedelta


def test_spelled_year():
    assert start_end("i år totusinde femogtyve") == (
        datetime(2025, 1, 1), datetime(2026, 1, 1))
    assert span("den femogtyvende december totusinde femogtyve").start == \
        datetime(2025, 12, 25)


def test_hundred_year_form():
    assert start_end("i år tusind ni hundrede og syv") == (
        datetime(1907, 1, 1), datetime(1908, 1, 1))
    assert start_end("i år to tusinde og tolv") == (
        datetime(2012, 1, 1), datetime(2013, 1, 1))


@pytest.mark.parametrize("text,expected", [
    ("om enogtyve dage", ANCHOR + timedelta(days=21)),
    ("om hundrede og en dage", ANCHOR + timedelta(days=101)),
    ("for to hundrede og halvtreds dage siden",
     ANCHOR - timedelta(days=250)),
    ("om tusind dage", ANCHOR + timedelta(days=1000)),
    ("om to tusinde og femogtyve dage", ANCHOR + timedelta(days=2025)),
])
def test_count(text, expected):
    assert span(text).start == expected


def test_clock_half():
    # "halv otte" is half an hour before eight: 7:30
    assert span("klokken halv otte").start == datetime(2017, 6, 27, 19, 30)
