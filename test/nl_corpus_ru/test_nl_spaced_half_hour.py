"""Russian half hours with "пол" written apart from the hour.

The dictionary writes "полвосьмого" (half past seven, 7:30) solid and
"пол-одиннадцатого" (10:30) with a hyphen, because the hour starts with a
vowel (Русский орфографический словарь РАН, ред. В. В. Лопатин, О. Е.
Иванова).  Writers and speech recognisers also give the spaced "пол
восьмого".  Each form names the half hour before the ordinal hour.  The
anchor is Tuesday 2017-06-27 13:04; a lone clock hour takes the next
twelve-hour reading at or after it.
"""
from datetime import datetime

import pytest

from ._corpus import ad, nomatch, start


@pytest.mark.parametrize("text,expected", [
    ("в полвосьмого", datetime(2017, 6, 27, 19, 30)),
    ("в пол восьмого", datetime(2017, 6, 27, 19, 30)),
    ("пол восьмого", datetime(2017, 6, 27, 19, 30)),
    ("встретимся в пол восьмого вечера", datetime(2017, 6, 27, 19, 30)),
    ("в пол-одиннадцатого", datetime(2017, 6, 27, 22, 30)),
    ("в пол одиннадцатого", datetime(2017, 6, 27, 22, 30)),
    ("в пол девятого утра", datetime(2017, 6, 28, 8, 30)),
])
def test_half_hour(text, expected):
    assert start(text) == ad(expected)


@pytest.mark.parametrize("text", [
    "упал на пол восьмого этажа",
    "пол второго этажа",
])
def test_floor_of_a_storey_is_no_clock(text):
    nomatch(text)
