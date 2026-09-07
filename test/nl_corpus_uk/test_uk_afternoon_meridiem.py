# -*- coding: utf-8 -*-
"""The Ukrainian afternoon after a spoken hour.

CLDR 47 names the Ukrainian afternoon "дня", the genitive of "day", and it
is the form a spoken afternoon hour takes: "о 3 дня" is three in the
afternoon. Without it the hour read as three in the morning and left the
word behind.

The same genitive counts days after a bare numeral, so "3 дня" is three
days and names no time at all. That is why the surface is a meridiem and
not a part of the day: a meridiem binds only after a preposition or an
o'clock word, so the counting reading is never reachable from it.
"""
import pytest

from ._corpus import nomatch, parse


@pytest.mark.parametrize("text,hour", [("о 3 дня", 15), ("о 2 дня", 14)])
def test_a_spoken_afternoon_hour(text, hour):
    got = parse(text)
    assert got is not None, text
    assert got[0].start.hour == hour
    assert got[1] == ""


@pytest.mark.parametrize("text", ["3 дня", "два дня", "5 днів"])
def test_a_count_of_days_names_no_time(text):
    """"three days" is a length; answering an afternoon would drop the count."""
    nomatch(text)


def test_the_bare_afternoon_word_is_unchanged():
    got = parse("сьогодні вдень")
    assert got[0].start.hour == 12
    assert got[1] == ""
