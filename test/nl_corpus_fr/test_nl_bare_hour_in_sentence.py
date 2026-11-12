# -*- coding: utf-8 -*-
"""A bare hour inside a sentence with no clock marker is not a clock, fr.

"20h", "21h30" and "3 heures" are a clock when they are the whole utterance
or follow a clock marker ("à").  Inside a sentence with no marker they are
as often a length ("un film de 2 heures") and are not read.  Anchor
2017-06-27 13:04: 20:00 and 21:30 are still ahead today, 03:00 is tomorrow.
"""
import pytest

from ._corpus import nomatch, parse, span


@pytest.mark.parametrize("text", [
    "un film de 2 heures",
    "un film de 2h",
    "il reste 3 heures",
    "3 heures de travail",
    "2h de route",
    "2 h de route",
    "mets le chapitre 3 heures",
])
def test_a_length_in_a_sentence_is_not_a_clock(text):
    nomatch(text)


@pytest.mark.parametrize("text,day,hour,minute", [
    ("20h", 27, 20, 0),
    ("21h30", 27, 21, 30),
    ("3 heures", 28, 3, 0),
    ("à 3 heures", 28, 3, 0),
    ("rendez-vous à 15h", 27, 15, 0),
    ("demain 20h", 28, 20, 0),
    ("du 10h au 12h", 28, 10, 0),
])
def test_a_clock_alone_or_after_a_marker_still_reads(text, day, hour, minute):
    s = span(text)
    assert (s.start.month, s.start.day) == (6, day)
    assert (s.start.hour, s.start.minute) == (hour, minute)


@pytest.mark.parametrize("text,day,hour", [
    ("il est 3 heures", 28, 3),
    ("c'est 3 heures", 28, 3),
    ("il est 20h", 27, 20),
])
def test_the_verb_that_states_the_hour_marks_a_clock(text, day, hour):
    """"Il est une heure, midi, etc., sert à indiquer l'heure." (Larousse,
    s.v. "être")."""
    s = span(text)
    assert (s.start.month, s.start.day) == (6, day)
    assert (s.start.hour, s.start.minute) == (hour, 0)


@pytest.mark.parametrize("text,hour", [
    ("il était 3 heures", 3),
    ("il est déjà 20h", 20),
])
def test_the_verb_that_states_the_hour_in_another_form(text, hour):
    """"était" is the same verb; "déjà" stands between the verb and the
    hour: "Il est déjà midi." (Le Robert, s.v. "déjà")."""
    s = span(text)
    assert (s.start.hour, s.start.minute) == (hour, 0)


@pytest.mark.parametrize("text,day,hour", [
    ("vers 20h", 27, 20),
    ("vers 3 heures", 28, 3),
    ("vers 15 heures", 27, 15),
    ("dès 20h", 27, 20),
    ("sur les 20h", 27, 20),
    ("aux alentours de 20h", 27, 20),
])
def test_a_word_of_approximation_or_start_marks_a_clock(text, day, hour):
    """"Vers (les) cinq heures." (Le Robert, s.v. "vers"); "sur" and "aux
    alentours de" point to "vers"; "dès": "Immédiatement, à partir de." """
    s = span(text)
    assert (s.start.month, s.start.day) == (6, day)
    assert (s.start.hour, s.start.minute) == (hour, 0)


def test_pour_before_a_count_of_hours_is_a_length():
    """"Pour six mois, pendant six mois" (Le Robert, s.v. "pour"): "pour"
    also opens a length, so it does not mark a clock."""
    nomatch("je pars pour 3 heures")


def test_a_day_period_after_the_hour_marks_a_clock():
    """"Dix heures du soir" (Le Robert, s.v. "soir"): a day period after the
    hour names a time of day.  20:00 is still ahead at 13:04."""
    s = span("20h ce soir")
    assert (s.start.month, s.start.day) == (6, 27)
    assert (s.start.hour, s.start.minute) == (20, 0)
