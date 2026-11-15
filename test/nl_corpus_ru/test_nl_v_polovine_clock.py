"""Russian "в половине <genitive ordinal>": the half toward the named hour.

"Приходите в половине двенадцатого" (Pushkin, quoted in В. И. Максимов,
"Половина первого, полпервого?", 1973, p. 53) is the locative of the same
"половина третьего" (02:30) clock, after the clock preposition "в".  The
reading follows the bare clock "половина третьего"; a day period fixes it.
An ordinal that agrees with a following noun ("двадцатого века") is not an
hour.
"""
import pytest

from ._corpus import ANCHOR, ad, nomatch, parse, start


def _at(day, hour, minute):
    return ad(ANCHOR.replace(day=day, hour=hour, minute=minute, second=0,
                             microsecond=0))


@pytest.mark.parametrize("text,day,hour,minute,remainder", [
    ("в половине третьего", 28, 2, 30, ""),
    ("в половине третьего дня", 27, 14, 30, ""),
    ("завтра в половине девятого", 28, 8, 30, ""),
    ("в половине девятого вечера", 27, 20, 30, ""),
    ("встретимся в половине восьмого", 28, 7, 30, "встретимся"),
])
def test_locative_half_clock(text, day, hour, minute, remainder):
    r = parse(text)
    assert r is not None
    assert r.span.start == _at(day, hour, minute)
    assert r.remainder == remainder


def test_locative_half_agrees_with_the_nominative_half():
    assert start("в половине третьего") == start("половина третьего")


@pytest.mark.parametrize("text", [
    "в половине двадцатого века",
    "половина двадцатого века",
])
def test_half_of_a_century_is_not_a_clock(text):
    nomatch(text)
