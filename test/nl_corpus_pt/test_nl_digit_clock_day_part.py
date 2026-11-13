# -*- coding: utf-8 -*-
"""A digit clock takes the part of the day after it, pt.

A written clock with minutes is followed by the part of the day as a spoken
hour is: "São 7h30 da manhã" (Practice Portuguese, "Hours and Telling
Time").  So "11:55 da noite" is 23:55 as "11 da noite" is 23:00, and the
part of the day does not stay in the remainder.  Twelve in the night is
midnight, as in "doze e cinco da noite".  A clock that has passed is the
next one (class 3).  A clock past noon with "da manhã" or "da madrugada"
names no time, as the spoken "às 15 da manhã" does not.

Anchor Saturday 2024-06-15 10:00.
"""
from datetime import datetime

import pytest

from ._corpus import ad, parse

SATURDAY = datetime(2024, 6, 15, 10, 0)


@pytest.mark.parametrize("text,expected", [
    ("11:55 da noite", datetime(2024, 6, 15, 23, 55)),
    ("às 11:55 da noite", datetime(2024, 6, 15, 23, 55)),
    ("12:05 da noite", datetime(2024, 6, 16, 0, 5)),
    ("1:15 da tarde", datetime(2024, 6, 15, 13, 15)),
    ("7h30 da manhã", datetime(2024, 6, 16, 7, 30)),
    ("3:30 da madrugada", datetime(2024, 6, 16, 3, 30)),
    ("amanhã às 10:30 da manhã", datetime(2024, 6, 16, 10, 30)),
])
def test_a_digit_clock_with_a_part_of_the_day(text, expected):
    r = parse(text, SATURDAY)
    assert r is not None, f"{text!r} did not parse"
    assert r.span.start == ad(expected)
    assert r.remainder == ""


def test_a_preposition_with_no_part_of_the_day_stays():
    r = parse("às 10:30 de", SATURDAY)
    assert r.span.start == ad(datetime(2024, 6, 15, 10, 30))
    assert r.remainder == "de"


@pytest.mark.parametrize("text", [
    "15:00 da manhã",
    "às 23:00 da manhã",
    "13:30 da manhã",
    "às 15h da manhã",
    "14:00 da madrugada",
])
def test_a_clock_past_noon_in_the_morning_is_no_time(text):
    assert parse(text, SATURDAY) is None
