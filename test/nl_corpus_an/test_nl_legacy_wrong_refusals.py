"""Phrases the legacy extractor answers wrongly stay unanswered.

Aragonese has no reading for these, and the older ovos-date-parser produced a
value for each anyway. Refusing is the correct behaviour and these pin it, so
that a later widening cannot quietly restore the invented answer.

The controls are the point: each refused phrase has a minimally different
sibling that DOES resolve, so a green refusal here is a decision about the
phrase and not a locale that stopped parsing.
"""
import pytest

from ._corpus import nomatch, start

#: phrase -> the value the legacy extractor invented for it.
LEGACY_INVENTED = [
    ('2 semanas', '2017-07-11'),  # a bare counted length read as a date
]

#: phrase -> the value Aragonese really does resolve, at the same anchor.
CONTROLS = [
    ('fa 2 semanas', '2018-05-22T13:04:00'),
]


@pytest.mark.parametrize("text,legacy_value", LEGACY_INVENTED)
def test_the_invented_reading_is_refused(text, legacy_value):
    nomatch(text)


@pytest.mark.parametrize("text,expected", CONTROLS)
def test_the_locale_still_reads_its_neighbour(text, expected):
    assert str(start(text)) == expected
