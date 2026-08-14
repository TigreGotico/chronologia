"""Estonian day-of-month spelled out as an adessive ordinal ("viiendal
augustil" = on the 5th of August).  The date construction takes the ordinal
in the ADESSIVE case (genitive stem + "-l"), not the bare nominative
``pronounce_ordinal_et`` emits; before the fix the ordinal word matched
neither the month-word grammar nor the cardinal fold, so the DAY slot never
bound and the sentence fell back to the whole month with the ordinal
stranded in the remainder.  Expected day numbers are read directly off the
sentence (independent of the parser); the anchor is fixed ahead of every day
under test so the span never rolls into the following year.
"""
from datetime import datetime

import pytest

from ._corpus import ad, parse, span

ANCHOR_2026 = datetime(2026, 1, 1)


@pytest.mark.parametrize("text,day", [
    ("esimesel augustil", 1),
    ("teisel augustil", 2),
    ("kolmandal augustil", 3),
    ("neljandal augustil", 4),
    ("viiendal augustil", 5),
    ("kuuendal augustil", 6),
    ("seitsmendal augustil", 7),
    ("kaheksandal augustil", 8),
    ("üheksandal augustil", 9),
    ("kümnendal augustil", 10),
    ("üheteistkümnendal augustil", 11),
    ("kaheteistkümnendal augustil", 12),
    ("kolmeteistkümnendal augustil", 13),
    ("kahekümnendal augustil", 20),
    ("kahekümne esimesel augustil", 21),
    ("kolmekümnendal augustil", 30),
    ("kolmekümne esimesel augustil", 31),
])
def test_adessive_ordinal_day_of_month(text, day):
    assert span(text, ANCHOR_2026).start == ad(datetime(2026, 8, day))


@pytest.mark.parametrize("text", [
    "viiendal augustil",
    "kolmeteistkümnendal augustil",
    "üheksandal augustil",
    "kümnendal augustil",
    "üheteistkümnendal augustil",
    "kaheteistkümnendal augustil",
    "kahekümnendal augustil",
])
def test_adessive_ordinal_day_leaves_no_remainder(text):
    _, remainder = parse(text, ANCHOR_2026)
    assert remainder == ""


def test_digit_ordinal_day_control_still_binds_clock():
    result = span("15. augustil kell 9", ANCHOR_2026)
    assert result.start == ad(datetime(2026, 8, 15, 9))
    _, remainder = parse("15. augustil kell 9", ANCHOR_2026)
    assert remainder == ""
