"""The spelled clock in Italian puts the hour first.

Italian says "nove e dieci" (nine and ten) for ten past nine and "nove meno
dieci" (nine less ten) for ten to nine: the hour leads, the minute follows
the direction word, with or without the preposition that usually opens the
phrase.

Anchor 2017-06-27 13:04; 13:04 is past every hour below, so each resolves to
the following morning.  Expected values are the arithmetic of the idiom.
"""
import pytest

from ._corpus import AstroDate, parse, start


@pytest.mark.parametrize("text,hour,minute", [
    ("nove e dieci", 9, 10),
    ("nove e venti", 9, 20),
    ("nove meno dieci", 8, 50),
    ("otto meno cinque", 7, 55),
    # the prepositional and article forms already read correctly
    ("alle nove e dieci", 9, 10),
    ("le nove e venti", 9, 20),
])
def test_hour_leads_the_minute(text, hour, minute):
    assert start(text) == AstroDate(2017, 6, 28, hour, minute)
    assert parse(text).remainder == ""


@pytest.mark.parametrize("text,hour,minute", [
    ("nove e un quarto", 9, 15),
    ("nove e mezza", 9, 30),
    ("alle nove e un quarto", 9, 15),
])
def test_the_bare_fraction_forms_resolve(text, hour, minute):
    assert start(text) == AstroDate(2017, 6, 28, hour, minute)
    assert parse(text).remainder == ""
