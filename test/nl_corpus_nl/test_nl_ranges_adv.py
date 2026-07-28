"""nl: localized ranges and adversarial cases."""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, parse, start, start_end, span, nomatch, AstroDate


@pytest.mark.parametrize("text,s,e", [('van 5 juni tot 12 juni', (2018, 6, 5), (2018, 6, 13)), ('5 juni tot 12 juni', (2018, 6, 5), (2018, 6, 13)), ('van maart 2020 tot juni 2020', (2020, 3, 1), (2020, 7, 1)), ('van 1990 tot 2000', (1990, 1, 1), (2001, 1, 1)), ('tussen juni en augustus 2020', (2020, 6, 1), (2020, 9, 1))])
def test_range(text, s, e):
    assert start_end(text) == (AstroDate(*s), AstroDate(*e))


@pytest.mark.parametrize("text", ['ergens anders', 'in orde', 'naar huis gaan', 'goedemorgen samen'])
def test_prose_does_not_raise(text):
    parse(text)


@pytest.mark.parametrize("text", ["25:00", "24:61", "99:99", "15:99"])
def test_impossible_clock(text):
    res = parse(text)
    if res is not None:
        assert 0 <= res[0].start.hour <= 23


@pytest.mark.parametrize("text", ['30 februari 2019', '31 april 2020', '32 januari 2020'])
def test_impossible_date(text):
    res = parse(text)
    if res is not None:
        assert res[0].start.day <= 31


@pytest.mark.parametrize("text", ['van', 'tot', 'tussen'])
def test_lone_range_word(text):
    assert parse(text) is None


@pytest.mark.parametrize("text", ["", "   ", "..."])
def test_empty(text):
    assert parse(text) is None


def test_half_is_a_clock_not_a_range():
    assert span("half negen").width.total_seconds() == 60
