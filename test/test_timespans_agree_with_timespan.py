# -*- coding: utf-8 -*-
"""``extract_timespans`` and ``extract_timespan`` read one text one way.

A token that a fold builds from written tokens ("après-demain", "il y a",
"14h") covers what was written, so its mention has a ``char_span``. A bare
"jul" is Christmas on both edges (Den Danske Ordbog and Svenska Akademiens
ordbok, "jul"). A word before "to" is no left end of a range that borrows its
partner's part of the day.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan, extract_timespans

ANCHOR = datetime(2017, 6, 27, 13, 4)  # a Tuesday

#: (lang, text, (start, end) of the mention in the text). Each bound is
#: counted by hand from the text.
CHAR_SPANS = [
    ("fr", "après-demain", (0, 12)),
    ("fr", "avant-hier", (0, 10)),
    ("fr", "il y a 3 jours", (0, 14)),
    ("fr", "il y a une semaine", (0, 18)),
    ("pt-PT", "lembra-me amanhã às 14h", (10, 23)),
    ("pt-PT", "amanhã às 14h", (0, 13)),
    ("pt-PT", "amanhã às 14h30", (0, 15)),
    ("fr-FR", "rappelle-moi demain à 14h", (13, 25)),
    ("fr-FR", "demain à 14h30", (0, 14)),
    ("fr-FR", "à 9h", (0, 4)),
]


@pytest.mark.parametrize("lang,text,expected", CHAR_SPANS)
def test_a_folded_token_keeps_the_extent_of_what_was_written(
        lang, text, expected):
    (mention,) = extract_timespans(text, lang, ANCHOR)
    assert mention.char_span == expected
    assert mention.text == text[expected[0]:expected[1]]


CHRISTMAS = (datetime(2017, 12, 25), datetime(2017, 12, 26))


@pytest.mark.parametrize("lang", ["da", "sv"])
@pytest.mark.parametrize("text", ["jul", "jul."])
def test_a_bare_jul_is_christmas_on_both_edges(lang, text):
    (mention,) = extract_timespans(text, lang, ANCHOR)
    found = extract_timespan(text, lang, ANCHOR)
    assert (mention.span.start_datetime, mention.span.end_datetime) == CHRISTMAS
    assert (found.span.start_datetime, found.span.end_datetime) == CHRISTMAS


@pytest.mark.parametrize("lang,text,month_day", [
    ("da", "4. jul", datetime(2017, 7, 4)),
    ("sv", "4 jul", datetime(2017, 7, 4)),
])
def test_jul_with_a_day_stays_the_month(lang, text, month_day):
    (mention,) = extract_timespans(text, lang, ANCHOR)
    assert mention.span.start_datetime == month_day


FRIDAY_ONE = (datetime(2017, 6, 30, 13, 0), datetime(2017, 6, 30, 13, 1))


@pytest.mark.parametrize("text,remainder", [
    ("how is the weather supposed to look this Friday at one in the afternoon",
     "how is the weather supposed to look"),
    ("look to friday at 1 in the afternoon", "look to"),
])
def test_a_word_before_to_borrows_no_part_of_the_day(text, remainder):
    found = extract_timespan(text, "en", ANCHOR)
    assert (found.span.start_datetime, found.span.end_datetime) == FRIDAY_ONE
    assert found.remainder == remainder
    (mention,) = extract_timespans(text, "en", ANCHOR)
    assert (mention.span.start_datetime, mention.span.end_datetime) == FRIDAY_ONE


def test_a_range_still_borrows_the_part_of_the_day_for_its_hour():
    found = extract_timespan("between 3 and 5 pm", "en", ANCHOR)
    assert (found.span.start_datetime, found.span.end_datetime) == (
        datetime(2017, 6, 27, 15, 0), datetime(2017, 6, 27, 17, 1))
