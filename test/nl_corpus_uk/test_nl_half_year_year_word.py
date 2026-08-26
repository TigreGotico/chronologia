"""A half-year phrase that NAMES its year with the Ukrainian year word.

Spelling the year word out ("перша половина 2020 року") selects exactly
the same six months as the bare-year wording ("перша половина 2020") --
the year word scopes the half, it does not widen it to the whole year. The
bare year on its own still reads as all twelve months.
"""
import pytest

from chronologia.astrodate import AstroDate
from ._corpus import parse, start_end


@pytest.mark.parametrize("text,s,e", [
    ('перша половина 2020 року', (2020, 1, 1), (2020, 7, 1)),
    ('друга половина 2020 року', (2020, 7, 1), (2021, 1, 1)),
])
def test_half_year_with_the_year_word(text, s, e):
    assert start_end(text) == (AstroDate(*s), AstroDate(*e))


@pytest.mark.parametrize("text", [
    'перша половина 2020 року',
    'друга половина 2020 року',
])
def test_the_year_word_is_consumed(text):
    """The year word is part of the reading, not a leftover fragment."""
    assert parse(text)[1] == ""


def test_matches_the_bare_year_wording():
    """Naming the year changes nothing about which half is meant."""
    assert start_end('перша половина 2020 року') == start_end('перша половина 2020')


def test_the_bare_year_is_still_the_whole_year():
    """The half reading must not swallow a plain year reference."""
    assert start_end("2020") == (AstroDate(2020, 1, 1), AstroDate(2021, 1, 1))
