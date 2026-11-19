"""Russian "every morning" before a lone hour keeps the spoken hour.

"каждое утро" names the morning band, so the lone hour 9 is 09:00 and the next
09:00 after the anchor (Tuesday 2017-06-27 13:04) is 2017-06-28.  The expected
values are written by hand from the calendar.
"""
import pytest

from ._corpus import AstroDate, parse, start


@pytest.mark.parametrize("text", [
    "каждое утро в девять",
    "каждое утро в 9",
    "каждое утро в девять напоминай мне проверить почту",
])
def test_every_morning_lone_hour(text):
    assert start(text) == AstroDate(2017, 6, 28, 9, 0)


def test_every_morning_alone_names_the_morning():
    result = parse("каждое утро")
    assert result.span.start == AstroDate(2017, 6, 27, 4, 0)
    assert result.span.end == AstroDate(2017, 6, 27, 12, 0)
