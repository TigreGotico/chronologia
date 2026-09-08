"""Phrases the legacy extractor answers wrongly stay unanswered.

Galician has no reading for these, and the older ovos-date-parser produced a
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
    ('blah 500x blah', '2017-06-28T05:00'),  # nonsense answering a time
]

#: phrase -> the value Galician really does resolve, at the same anchor.
CONTROLS = [
    ('ás 5', '2017-06-28T05:00:00'),
]


@pytest.mark.parametrize("text,legacy_value", LEGACY_INVENTED)
def test_the_invented_reading_is_refused(text, legacy_value):
    nomatch(text)


@pytest.mark.parametrize("text,expected", CONTROLS)
def test_the_locale_still_reads_its_neighbour(text, expected):
    assert str(start(text)) == expected
