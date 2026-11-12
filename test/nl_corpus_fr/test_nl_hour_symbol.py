# -*- coding: utf-8 -*-
""""h" is the symbol of the hour, fr.

OQLF, Banque de dépannage linguistique, "Écriture des nombres exprimant une
durée": "2 heures 28 minutes (ou : 2 h 28 min)".  So "dans 2 h" is "dans 2
heures", and "9 h et quart" is "9 heures et quart".  Read as a clock, the
first answered 02:00 tomorrow with "dans" left over, and the second answered
09:00 with "et quart" left over.  Anchor 2017-06-27 13:04: 09:00 has gone,
so a clock at 9 is tomorrow; two hours from 13:04 is 15:04.
"""
from datetime import datetime

import pytest

from ._corpus import parse, ad


@pytest.mark.parametrize("text,hour,minute", [
    ("demain à 9 h et quart", 9, 15),
    ("demain à 9h et quart", 9, 15),
    ("à 9 h et demie", 9, 30),
    ("à 9 h moins le quart", 8, 45),
    ("demain à 9 heures et quart", 9, 15),
])
def test_clock_direction_after_the_hour_symbol(text, hour, minute):
    span, rest = parse(text)
    assert span.start == ad(datetime(2017, 6, 28, hour, minute))
    assert rest == ""


@pytest.mark.parametrize("text,expected", [
    ("dans 2 h", datetime(2017, 6, 27, 15, 4)),
    ("dans 2h", datetime(2017, 6, 27, 15, 4)),
    ("il y a 3 h", datetime(2017, 6, 27, 10, 4)),
    ("dans 2 heures", datetime(2017, 6, 27, 15, 4)),
])
def test_hour_symbol_after_a_counted_offset(text, expected):
    span, rest = parse(text)
    assert span.start == ad(expected)
    assert rest == ""


@pytest.mark.parametrize("text,hour", [("à 20h", 20), ("à 9 h", 9)])
def test_a_clock_with_the_symbol_is_unchanged(text, hour):
    span, rest = parse(text)
    day = 27 if hour > 13 else 28
    assert span.start == ad(datetime(2017, 6, day, hour, 0))
    assert rest == ""


@pytest.mark.parametrize("text,expected", [
    # 13:04 + 2 h 30 min = 15:34
    ("dans 2h30", datetime(2017, 6, 27, 15, 34)),
    ("dans 2 h 30", datetime(2017, 6, 27, 15, 34)),
    ("dans 2 h 30 min", datetime(2017, 6, 27, 15, 34)),
    ("dans 2 h et demie", datetime(2017, 6, 27, 15, 34)),
    ("dans 2 heures et demie", datetime(2017, 6, 27, 15, 34)),
    ("dans 2 heures 30", datetime(2017, 6, 27, 15, 34)),
    # 13:04 + 1 h 30 min = 14:34; 13:04 + 2 h 15 min = 15:19
    ("dans une heure et demie", datetime(2017, 6, 27, 14, 34)),
    ("dans 2 heures et quart", datetime(2017, 6, 27, 15, 19)),
    # 13:04 - 2 h 30 min = 10:34
    ("il y a 2h30", datetime(2017, 6, 27, 10, 34)),
])
def test_hours_and_minutes_after_a_counted_offset_are_one_length(text,
                                                                 expected):
    """"2 h 28 min" is a length (OQLF, as above); "Et demi(e) (après un
    nom) : et la moitié. Cinq heures et demie." (Le Robert, s.v. "demi");
    "Quart d'heure : quinze minutes." (Le Robert, s.v. "quart")."""
    span, rest = parse(text)
    assert span.start == ad(expected)
    assert rest == ""
