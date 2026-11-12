# -*- coding: utf-8 -*-
"""A bare hour inside a sentence with no clock marker is not a clock, fr.

Ruling 2 of 2026-11-12 (knowledge/wiki/audits/chronologia/
disagreement-classes.md): "20h", "21h30" and "3 heures" are a clock when they
are the whole utterance or follow a clock marker ("à").  Inside a sentence
with no marker they are as often a length ("un film de 2 heures") and are
not read.  Anchor 2017-06-27 13:04: 20:00 and 21:30 are still ahead today,
03:00 is tomorrow.
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
