"""A duration range whose two ends each carry a unit reads as its upper bound.

``extract_duration`` returns one ``timedelta``, and a range with a shared unit
("3 to 5 days") already reads as its upper bound
(test/nl_corpus_en/test_nl_r135_duration_marker.py).  A range that repeats the
unit at both ends names the same lengths, so it reads the same, instead of the
two lengths added up ("8 days to 15 days" is not 23 days).  The expected values
are the upper bounds as written.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_duration

A = datetime(2026, 11, 26, 10, 0)


@pytest.mark.parametrize("text,lang,expected", [
    ("8 days to 15 days", "en", timedelta(days=15)),
    ("2 hours to 3 hours", "en", timedelta(hours=3)),
    ("1 hour to 90 minutes", "en", timedelta(minutes=90)),
    ("2 months to 3 months", "en", timedelta(days=92)),     # 26 Nov to 26 Feb
    ("un délai de 8 jours à 15 jours", "fr", timedelta(days=15)),
    ("de 6 horas a 8 horas", "pt", timedelta(hours=8)),
    ("von 2 Stunden bis 3 Stunden", "de", timedelta(hours=3)),
    ("2 ore a 3 ore", "it", timedelta(hours=3)),
])
def test_a_range_of_two_lengths_is_its_upper_bound(text, lang, expected):
    got = extract_duration(text, lang, anchor=A)
    assert got is not None and got.duration == expected


@pytest.mark.parametrize("text,expected", [
    ("2 days and 3 days", timedelta(days=5)),               # "and" adds
    ("2 hours 30 minutes", timedelta(hours=2, minutes=30)),
    ("3 to 5 days", timedelta(days=5)),                     # the shared unit, unchanged
])
def test_lengths_without_a_range_word_still_add(text, expected):
    got = extract_duration(text, "en", anchor=A)
    assert got is not None and got.duration == expected


def test_a_range_word_before_no_length_is_left_in_the_remainder():
    got = extract_duration("2 days to Paris", "en", anchor=A)
    assert got is not None
    assert (got.duration, got.remainder) == (timedelta(days=2), "to Paris")
