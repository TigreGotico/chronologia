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


@pytest.mark.parametrize("text,day,remainder", ROWS[:4])
def test_the_mention_is_the_possessive_word(text, day, remainder):
    found = extract_timespans(text, "en", ANCHOR)
    assert [m.span.start.datetime() for m in found] == [day]
    assert found[0].text == text[found[0].char_span[0]:found[0].char_span[1]]
