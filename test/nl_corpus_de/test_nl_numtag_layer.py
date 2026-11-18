"""German numbers read through numtag.

A German number is one compound word ("dreiundzwanzig"), a spelled year is one
word ("zweitausendfünfundzwanzig"), and the clock fractions "halb", "viertel"
and "dreiviertel" stay words the clock grammar reads.  Every expected value is
written by hand or computed with ``relativedelta`` / ``timedelta`` from the
anchor.
"""
import pytest
from dateutil.relativedelta import relativedelta

from chronologia import extract_duration

from ._corpus import ANCHOR, datetime, span, start_end, timedelta


@pytest.mark.parametrize("text,expected", [
    # a thousand years before the anchor
    ("vor tausend Jahren", ANCHOR - relativedelta(years=1000)),
    ("in zweitausend Jahren", ANCHOR + relativedelta(years=2000)),
    ("in dreiundzwanzig Tagen", ANCHOR + timedelta(days=23)),
    ("in hundert Tagen", ANCHOR + timedelta(days=100)),
    ("vor fünf Sekunden", ANCHOR - timedelta(seconds=5)),
    # the ASCII spelling of the umlaut word
    ("in fuenf Tagen", ANCHOR + timedelta(days=5)),
    ("in zwoelf Tagen", ANCHOR + timedelta(days=12)),
])
def test_count(text, expected):
    assert span(text).start == expected


def test_spelled_year():
    assert start_end("im Jahr zweitausendfünfundzwanzig") == (
        datetime(2025, 1, 1), datetime(2026, 1, 1))
    assert span("am ersten Mai zweitausendfünfundzwanzig").start == \
        datetime(2025, 5, 1)
    assert span("am einundzwanzigsten Mai zweitausendeinundzwanzig").start == \
        datetime(2021, 5, 21)


@pytest.mark.parametrize("text,expected", [
    # "halb acht" is half an hour before eight: 7:30, read as the next 12h
    # reading after 13:04
    ("um halb acht", datetime(2017, 6, 27, 19, 30)),
    ("um Viertel nach drei", datetime(2017, 6, 27, 15, 15)),
    # "dreiviertel zehn" is a quarter before ten: 9:45
    ("um dreiviertel zehn", datetime(2017, 6, 27, 21, 45)),
])
def test_clock_fractions(text, expected):
    assert span(text).start == expected


@pytest.mark.parametrize("text,length", [
    ("in anderthalb Stunden", timedelta(hours=1, minutes=30)),
    ("in einer halben Stunde", timedelta(minutes=30)),
    ("vor zwanzig Minuten", timedelta(minutes=20)),
])
def test_length_with_a_fraction(text, length):
    assert extract_duration(text, "de").duration == length
