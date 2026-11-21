# -*- coding: utf-8 -*-
"""A digit clock written with a space reads as the hour and its minutes.

Speech recognition writes a spoken "ten thirty" as "10 30".  After the clock
preposition the second number is the minutes of the first, so "às 10 30" reads
as "às 10:30" (ruling 17 for the hour, ruling 23 for the half of the day).
Without the preposition two numbers stay a count.

Every expected instant is worked out by hand from the anchor, Tuesday
2017-06-27 13:04: the next 10:30 after 13:04 is 22:30, the next 15:15 is today.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)

# text, language, expected start
SPACED = [
    ("às 10 30", "pt", datetime(2017, 6, 27, 22, 30)),
    ("ás 10 30", "gl", datetime(2017, 6, 27, 22, 30)),
    ("a las 10 30", "es", datetime(2017, 6, 27, 22, 30)),
    ("a les 10 30", "ca", datetime(2017, 6, 27, 22, 30)),
    ("à 10 30", "fr", datetime(2017, 6, 27, 22, 30)),
    ("alle 10 30", "it", datetime(2017, 6, 27, 22, 30)),
    ("um 10 30", "de", datetime(2017, 6, 27, 22, 30)),
    ("om 10 30", "nl", datetime(2017, 6, 27, 22, 30)),
    ("в 10 30", "ru", datetime(2017, 6, 27, 22, 30)),
    ("در ساعت 10 30", "fa", datetime(2017, 6, 27, 22, 30)),
    ("às 3 15", "pt", datetime(2017, 6, 27, 15, 15)),
    ("às 22 30", "pt", datetime(2017, 6, 27, 22, 30)),
    ("às 10 30 da manhã", "pt", datetime(2017, 6, 28, 10, 30)),
]


@pytest.mark.parametrize("text,lang,start", SPACED)
def test_spaced_digit_clock_reads_hour_and_minutes(text, lang, start):
    res = extract_timespan(text, lang, ANCHOR)
    assert res is not None
    assert res.span.start == start
    assert res.span.end == start + timedelta(minutes=1)


@pytest.mark.parametrize("text,lang", [
    ("às 10 30", "pt"), ("a las 10 30", "es"), ("om 10 30", "nl")])
def test_spaced_digit_clock_leaves_no_minutes_behind(text, lang):
    assert extract_timespan(text, lang, ANCHOR).remainder == ""


@pytest.mark.parametrize("text,lang", [
    ("tenho 10 30 reais", "pt"),
    ("hay 10 30 personas", "es"),
    ("às 5 99", "pt"),
])
def test_two_numbers_without_a_clock_preposition_are_no_clock(text, lang):
    assert extract_timespan(text, lang, ANCHOR) is None
