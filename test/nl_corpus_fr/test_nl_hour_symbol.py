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

from chronologia.extract.loader import load_lang_spec
from chronologia.extract.pipeline import prematch_tokens

from ._corpus import parse, ad


@pytest.mark.parametrize("text,hour,minute", [
    ("demain à 9 h et quart", 9, 15),
    ("demain à 9h et quart", 9, 15),
    ("à 9 h et demie", 9, 30),
    ("à 9 h moins le quart", 8, 45),
    ("à 2h moins le quart", 1, 45),
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
    """"2 h 28 min" is a length (OQLF, as above); "et demi" adds "la valeur
    d'une moitié" (TLFi, s.v. "demi", I.A); a quarter of an hour is "quinze
    minutes" (TLFi, s.v. "quart", B.1.a)."""
    span, rest = parse(text)
    assert span.start == ad(expected)
    assert rest == ""


@pytest.mark.parametrize("text,expected", [
    # 13:04 + (2 h - 15 min) = 13:04 + 1 h 45 min = 14:49
    ("dans 2h moins le quart", datetime(2017, 6, 27, 14, 49)),
    ("dans 2 heures moins le quart", datetime(2017, 6, 27, 14, 49)),
    ("dans 2 h moins un quart", datetime(2017, 6, 27, 14, 49)),
    # 13:04 + (2 h - 10 min) = 13:04 + 1 h 50 min = 14:54
    ("dans 2 h moins 10", datetime(2017, 6, 27, 14, 54)),
    ("dans 2 h moins 10 minutes", datetime(2017, 6, 27, 14, 54)),
    # 13:04 + (1 h - 15 min) = 13:49
    ("dans 1h moins le quart", datetime(2017, 6, 27, 13, 49)),
    # 13:04 - 1 h 45 min = 11:19
    ("il y a 2h moins le quart", datetime(2017, 6, 27, 11, 19)),
])
def test_moins_after_a_counted_offset_shortens_the_length(text, expected):
    """"moins" before minutes is "Pour indiquer une soustraction" (TLFi,
    s.v. "moins", II.A).  After "dans" the hours are a length, so the
    minutes come off the length; read as a clock, the phrase answered 01:45
    tomorrow with "dans" left over."""
    span, rest = parse(text)
    assert span.start == ad(expected)
    assert rest == ""


@pytest.mark.parametrize("text,expected", [
    # 13:04 + (2 h - 10 s) = 13:04 + 1 h 59 min 50 s = 15:03:50
    ("dans 2 heures moins 10 secondes", datetime(2017, 6, 27, 15, 3, 50)),
    ("dans 2 heures moins 10 sec", datetime(2017, 6, 27, 15, 3, 50)),
    # 13:04 + (2 h - 1 s) = 15:03:59
    ("dans 2 heures moins 1 seconde", datetime(2017, 6, 27, 15, 3, 59)),
    # 13:04 - 1 h 59 min 50 s = 11:04:10
    ("il y a 2 heures moins 10 secondes", datetime(2017, 6, 27, 11, 4, 10)),
    # 13:04 + 2 h 10 s = 15:04:10
    ("dans 2 heures 10 secondes", datetime(2017, 6, 27, 15, 4, 10)),
    ("dans 2 h et 10 secondes", datetime(2017, 6, 27, 15, 4, 10)),
    ("dans 2h10 secondes", datetime(2017, 6, 27, 15, 4, 10)),
    # 13:04 + 2 h 30 s = 15:04:30
    ("dans 2 h 30 s", datetime(2017, 6, 27, 15, 4, 30)),
])
def test_seconds_after_the_count_are_seconds(text, expected):
    """A count after the hours is in the unit that follows it: "10 min 35 s"
    (OQLF, "Écriture des nombres exprimant une durée"), and "sec" is a
    symbol of the second (Wiktionnaire, s.v. "sec").  Read as minutes, the
    first phrase answered 14:54 and the plain counts 15:14."""
    span, rest = parse(text)
    assert span.start == ad(expected)
    assert rest == ""


def test_a_count_before_another_unit_is_not_taken_away():
    """"5 jours" is not a part of an hour, so the length stays "2 heures" and
    "moins 5 jours" is left over; read as minutes, it answered 14:59 the next
    day.  13:04 + 2 h = 15:04."""
    span, rest = parse("dans 2 heures moins 5 jours")
    assert span.start == ad(datetime(2017, 6, 27, 15, 4))
    assert rest == "moins 5 jours"


@pytest.mark.parametrize("text,kept", [
    # "10" counts days, not minutes: the length is not rewritten.
    ("dans 2 heures 10 jours", ["dans", "2", "heures", "10", "jours"]),
    # 0 h less 10 min is no length; rewritten, it is "-1 h et 50 minutes"
    # and "dans" answers 12:54, ten minutes before the anchor.
    ("dans 0 h moins 10", ["dans", "0", "h", "moins", "10"]),
])
def test_the_length_rewrite_leaves_the_phrase(text, kept):
    spec = load_lang_spec("fr")
    assert [t.text for t in prematch_tokens(text, spec)] == kept


@pytest.mark.parametrize("text,rest", [
    ("rappelle-moi le 3 juillet de partir dans 2 heures moins 5",
     "rappelle-moi de partir dans 2 heures moins 5"),
    ("le 3 juillet, dans 2 heures moins 10 secondes",
     "dans 2 heures moins 10 secondes"),
])
def test_the_remainder_keeps_the_words_the_user_wrote(text, rest):
    """The length rewrite works on tokens; the remainder still slices the
    sentence, so the user's own words come back."""
    _, left = parse(text)
    assert left == rest
