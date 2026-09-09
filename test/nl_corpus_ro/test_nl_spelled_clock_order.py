"""The spelled clock in Romanian puts the hour first.

Romanian says "nouă și zece" (nine and ten) for ten past nine and "nouă
fără zece" (nine without ten) for ten to nine: the hour leads, the minute
follows the direction word.  Wiktionary: *fără* "without", *și* "and".

Anchor 2017-06-27 13:04; 13:04 is past every hour below, so each resolves
to the following morning.  Expected values are the arithmetic of the idiom,
not the engine's output.
"""
import pytest

from ._corpus import AstroDate, parse, start


@pytest.mark.parametrize("text,hour,minute", [
    ("nouă și zece", 9, 10),
    ("nouă și cinci", 9, 5),
    ("opt și douăzeci", 8, 20),
    ("nouă fără zece", 8, 50),
    ("opt fără cinci", 7, 55),
    ("nouă fără douăzeci", 8, 40),
    ("la ora nouă și zece", 9, 10),
    ("ora nouă și cinci", 9, 5),
])
def test_hour_leads_the_minute(text, hour, minute):
    assert start(text) == AstroDate(2017, 6, 28, hour, minute)
    assert parse(text).remainder == ""


@pytest.mark.parametrize("text,hour,minute", [
    # the fraction forms could never swap, and must keep their readings
    ("trei fără un sfert", 2, 45),
    ("nouă și un sfert", 9, 15),
    ("nouă și jumătate", 9, 30),
])
def test_fraction_forms_are_unchanged(text, hour, minute):
    assert start(text) == AstroDate(2017, 6, 28, hour, minute)


@pytest.mark.parametrize("text", [
    "la ora douăzeci și unu",
    "la ora douăzeci și una",
])
def test_the_compound_hour_is_not_split_into_hour_and_minute(text):
    """21 is one numeral, not "twenty" plus a minute "one"."""
    assert start(text) == AstroDate(2017, 6, 27, 21, 0)
    assert parse(text).remainder == ""
