"""The German spoken clock names the minute after "Uhr".

"sieben Uhr dreißig" is half past seven: the hour, the word Uhr, then the
minute, with the digit and spelled forms interchangeable and a second Uhr
sometimes closing the phrase.

Anchor 2017-06-27 13:04; every hour below is behind it, so each resolves to
the following morning unless stated.
"""
import pytest

from ._corpus import AstroDate, parse, start


@pytest.mark.parametrize("text,day,hour,minute", [
    ("um 7 uhr 30", 28, 7, 30),
    ("7 uhr 30", 28, 7, 30),
    ("um 7 uhr 30 uhr", 28, 7, 30),
    ("um sieben uhr dreißig", 28, 7, 30),
    # 19:30 is still ahead of the 13:04 anchor, so it stays today
    ("um 19 uhr 30", 27, 19, 30),
])
def test_the_minute_after_uhr(text, day, hour, minute):
    assert start(text) == AstroDate(2017, 6, day, hour, minute)
    assert parse(text).remainder == ""


@pytest.mark.parametrize("text,hour,minute", [
    # the bare hour and the fraction forms must keep their readings
    ("um 7 uhr", 7, 0),
    ("halb acht", 7, 30),
    ("viertel acht", 7, 15),
])
def test_the_forms_that_already_read(text, hour, minute):
    assert start(text) == AstroDate(2017, 6, 28, hour, minute)
