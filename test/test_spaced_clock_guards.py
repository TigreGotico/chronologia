# -*- coding: utf-8 -*-
"""Readings that a fix for #1012 (a spaced digit clock, "às 10 30") must keep.

A clock with a spelled and a digit number, a clock before an undotted date,
and a clock count in Turkish read right on dev.  A bare "a" before two numbers
is no clock in pt and es.  Anchor: Tuesday 2017-06-27 13:04.  Each expected
instant is the next one after the anchor (ruling 17).
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)


@pytest.mark.parametrize("text,lang,expected", [
    ("at ten 30", "en", datetime(2017, 6, 27, 22, 30)),
    ("at 10 thirty", "en", datetime(2017, 6, 27, 22, 30)),
    ("at 10 thirty five", "en", datetime(2017, 6, 27, 22, 35)),
    ("a las 9 25 de diciembre", "es", datetime(2017, 12, 25, 9, 0)),
    ("à 9 25 décembre", "fr", datetime(2017, 12, 25, 9, 0)),
    ("alle 9 25 dicembre", "it", datetime(2017, 12, 25, 9, 0)),
    ("om 9 25 december", "nl", datetime(2017, 12, 25, 9, 0)),
    ("a les 9 25 de desembre", "ca", datetime(2017, 12, 25, 9, 0)),
    ("um 9 25 Dezember", "de", datetime(2017, 12, 25, 9, 0)),
    ("a las 8 5 de junio", "es", datetime(2018, 6, 5, 8, 0)),
    ("kell kaheksa 5. juuni", "et", datetime(2018, 6, 5, 8, 0)),
    ("saat üçe on kala", "tr", datetime(2017, 6, 27, 14, 50)),
    ("onu on geçe", "tr", datetime(2017, 6, 27, 22, 10)),
])
def test_a_clock_beside_other_numbers_keeps_its_reading(text, lang, expected):
    found = extract_timespan(text, lang, ANCHOR)
    assert found.span.start.datetime() == expected


@pytest.mark.parametrize("text,lang", [
    ("de 9 a 10 30", "pt"),
    ("chegou a 7 30", "pt"),
    ("vendido a 5 30 euros", "es"),
    ("ganamos 3 a 2 30", "es"),
    ("tenho 10 30 reais", "pt"),
])
def test_two_numbers_after_a_bare_a_are_no_clock(text, lang):
    found = extract_timespan(text, lang, ANCHOR)
    assert found is None or found.span.start.datetime().minute != 30
