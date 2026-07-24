# -*- coding: utf-8 -*-
"""Recurrence in ms: extract_recurrence -> RRULE."""
import pytest

from chronologia.extract import extract_recurrence

LANG = "ms"

_CASES = [
    ('setiap jumaat', 'FREQ=WEEKLY;BYDAY=FR', ''),
    ('setiap isnin', 'FREQ=WEEKLY;BYDAY=MO', ''),
    ('harian', 'FREQ=DAILY', ''),
    ('mingguan', 'FREQ=WEEKLY', ''),
    ('bulanan', 'FREQ=MONTHLY', ''),
    ('tahunan', 'FREQ=YEARLY', ''),
    ('setiap 2 minggu', 'FREQ=WEEKLY;INTERVAL=2', ''),
    ('setiap 3 hari', 'FREQ=DAILY;INTERVAL=3', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CASES)
def test_recurrence(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ['jumaat', 'hari ini'])
def test_not_a_recurrence(text):
    assert extract_recurrence(text, LANG) is None


# -- the weekday classifier "hari" ------------------------------------------
# A day name normally travels with "hari" in front of it, which collides head
# on with "setiap hari" (every day).  Both readings are genuine Malay, so both
# have to come out right: the collision is grammatical, not a typo.
_CLASSIFIER_CASES = [
    ('setiap hari isnin', 'FREQ=WEEKLY;BYDAY=MO', ''),
    ('setiap hari selasa', 'FREQ=WEEKLY;BYDAY=TU', ''),
    ('setiap hari rabu', 'FREQ=WEEKLY;BYDAY=WE', ''),
    ('setiap hari khamis', 'FREQ=WEEKLY;BYDAY=TH', ''),
    ('setiap hari jumaat', 'FREQ=WEEKLY;BYDAY=FR', ''),
    ('setiap hari sabtu', 'FREQ=WEEKLY;BYDAY=SA', ''),
    ('setiap hari ahad', 'FREQ=WEEKLY;BYDAY=SU', ''),
    ('setiap hari minggu', 'FREQ=WEEKLY;BYDAY=SU', ''),
    ('tiap hari jumaat', 'FREQ=WEEKLY;BYDAY=FR', ''),
    # the classifier-less name keeps reading as it always did
    ('setiap isnin', 'FREQ=WEEKLY;BYDAY=MO', ''),
    # and "every day" with no day name after it is still daily
    ('setiap hari', 'FREQ=DAILY', ''),
    ('tiap hari', 'FREQ=DAILY', ''),
]


@pytest.mark.parametrize("text,rrule,remainder", _CLASSIFIER_CASES)
def test_weekday_classifier(text, rrule, remainder):
    got = extract_recurrence(text, LANG)
    assert got is not None, f"{text!r} did not parse as a recurrence"
    assert got[0].to_string() == rrule
    assert got[1] == remainder


@pytest.mark.parametrize("text", ['hari isnin', 'hari', 'hari hari', ''])
def test_classifier_without_every_is_not_a_recurrence(text):
    # The classifier names a day, it does not repeat one.
    assert extract_recurrence(text, LANG) is None
