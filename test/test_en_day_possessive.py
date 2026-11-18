"""An English day word with a possessive names the day: "today's forecast".

"today's", "tomorrow's" and "yesterday's" are adjectives of the day word
(Wiktionary, s.v. "today's").  Every expected instant is worked out by hand
from the anchor, Tuesday 2017-06-27 13:04: today starts at 00:00 on the 27th,
tomorrow on the 28th and yesterday on the 26th.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan, extract_timespans

ANCHOR = datetime(2017, 6, 27, 13, 4)

ROWS = [
    ("read me today's forecast", datetime(2017, 6, 27), "read me forecast"),
    ("today's weather", datetime(2017, 6, 27), "weather"),
    ("what is tomorrow's forecast", datetime(2017, 6, 28), "what is forecast"),
    ("show yesterday's news", datetime(2017, 6, 26), "show news"),
    ("it's tomorrow", datetime(2017, 6, 28), "it's"),
]


@pytest.mark.parametrize("text,day,remainder", ROWS)
def test_a_day_word_with_a_possessive_names_the_day(text, day, remainder):
    found = extract_timespan(text, "en", ANCHOR)
    assert found.span.start.datetime() == day
    assert found.remainder == remainder


MENTIONS = [
    ("read me today's forecast", datetime(2017, 6, 27), "today's"),
    ("today's weather", datetime(2017, 6, 27), "today's"),
    ("what is tomorrow's forecast", datetime(2017, 6, 28), "tomorrow's"),
    ("show yesterday's news", datetime(2017, 6, 26), "yesterday's"),
]


@pytest.mark.parametrize("text,day,word", MENTIONS)
def test_the_mention_is_the_possessive_word(text, day, word):
    found = extract_timespans(text, "en", ANCHOR)
    assert [m.span.start.datetime() for m in found] == [day]
    assert found[0].text == word


CLOCK_ROWS = [
    ("remind me of tomorrow's meeting at 9 am", datetime(2017, 6, 28, 9, 0), "remind me of meeting"),
    ("tomorrow's meeting at 5pm", datetime(2017, 6, 28, 17, 0), "meeting"),
    ("tomorrow\u2019s meeting at 5pm", datetime(2017, 6, 28, 17, 0), "meeting"),
    ("today's meeting at 5pm", datetime(2017, 6, 27, 17, 0), "meeting"),
    ("yesterday's flight at 10:30 pm", datetime(2017, 6, 26, 22, 30), "flight"),
    ("yesterday's game at 9 am", datetime(2017, 6, 26, 9, 0), "game"),
]


@pytest.mark.parametrize("text,instant,remainder", CLOCK_ROWS)
def test_a_clock_after_the_noun_joins_the_possessive_day(text, instant, remainder):
    found = extract_timespan(text, "en", ANCHOR)
    assert found.span.start.datetime() == instant
    assert found.remainder == remainder

