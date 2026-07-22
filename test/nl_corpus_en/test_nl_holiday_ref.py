"""Holiday references: a named holiday resolves to its own day-wide span.

The construction under test is ``holiday_ref``: a well-known holiday spoken by
name ("christmas", "when is easter", "next christmas", "easter 2020") resolves
to the holiday's :class:`DateSpan`.  Every expected date is derived by hand.

Anchor is 2017-06-27 (a Tuesday).  Movable-feast dates are taken from an
independent Western (Gregorian) computus table, NOT from the engine:

    Easter Sunday   2016 = 27 Mar   2017 = 16 Apr   2018 = 1 Apr   2020 = 12 Apr

so Good Friday = Easter-2, Easter Monday = Easter+1, Ascension = Easter+39,
Pentecost = Easter+49, Corpus Christi = Easter+60, Carnival/Mardi Gras =
Easter-47.  The "bare" rule is *next occurrence on or after the anchor*: a
holiday already past in 2017 rolls to 2018.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, AstroDate, parse, span, start, nomatch

# -- bare name -> next occurrence on or after the anchor (2017-06-27) ------

_BARE = [
    ("christmas", (2017, 12, 25)),          # 25 Dec still ahead -> this year
    ("christmas day", (2017, 12, 25)),
    ("xmas", (2017, 12, 25)),
    ("christmas eve", (2017, 12, 24)),
    ("new year's eve", (2017, 12, 31)),
    ("new year's day", (2018, 1, 1)),       # 1 Jan already past -> next year
    ("assumption", (2017, 8, 15)),
    ("all saints day", (2017, 11, 1)),
    ("easter", (2018, 4, 1)),               # 2017 Easter (16 Apr) past -> 2018
    ("easter sunday", (2018, 4, 1)),
    ("good friday", (2018, 3, 30)),         # 1 Apr 2018 - 2
    ("easter monday", (2018, 4, 2)),        # 1 Apr 2018 + 1
    ("ascension", (2018, 5, 10)),           # 1 Apr 2018 + 39
    ("corpus christi", (2018, 5, 31)),      # 1 Apr 2018 + 60
    ("carnival", (2018, 2, 13)),            # 1 Apr 2018 - 47
    ("three kings day", (2018, 1, 6)),      # Epiphany, past in 2017 -> 2018
]


@pytest.mark.parametrize("text,ymd", _BARE)
def test_bare_holiday(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


# -- "when is ..." framing: the filler is ignored, the holiday still binds ---

@pytest.mark.parametrize("text,ymd", [
    ("when is christmas", (2017, 12, 25)),
    ("when is easter", (2018, 4, 1)),
    ("what day is good friday", (2018, 3, 30)),
    ("on christmas eve", (2017, 12, 24)),
])
def test_when_is(text, ymd):
    assert start(text) == AstroDate(*ymd)


# -- next / last: strictly future / strictly past occurrence --------------

@pytest.mark.parametrize("text,ymd", [
    ("next christmas", (2017, 12, 25)),     # 25 Dec 2017 is strictly future
    ("last christmas", (2016, 12, 25)),     # most recent past 25 Dec
    ("last easter", (2017, 4, 16)),         # most recent past Easter Sunday
    ("this christmas", (2017, 12, 25)),
])
def test_next_last(text, ymd):
    assert start(text) == AstroDate(*ymd)


# -- explicit year: that year's occurrence, no roll -----------------------

@pytest.mark.parametrize("text,ymd", [
    ("christmas 2020", (2020, 12, 25)),
    ("easter 2020", (2020, 4, 12)),
    ("good friday 2020", (2020, 4, 10)),    # 12 Apr 2020 - 2
])
def test_explicit_year(text, ymd):
    assert start(text) == AstroDate(*ymd)


# -- confusable that DOES bind (documented): "easter egg hunt ideas" ------
# The bare holiday word is present, so the reference binds easter and the rest
# is remainder.  This is the documented behaviour, not a bug.

def test_confusable_still_binds_easter():
    r = parse("easter egg hunt ideas")
    assert r is not None
    assert r[0].start == AstroDate(2018, 4, 1)
    assert "egg" in r[1]


# -- negatives: no holiday word -> nothing to bind ------------------------

@pytest.mark.parametrize("text", [
    "the price of eggs went up",
    "a meeting about the budget",
    "a plate of scrambled eggs",
])
def test_no_holiday_no_match(text):
    nomatch(text)


# -- homograph adversarial: a person/place named like a holiday ------------
# "Easter" is also a given name/surname; with no calendar cue the engine still
# binds the holiday.  Policy: homograph disambiguation is out of scope -> xfail.

@pytest.mark.xfail(reason="holiday/person homograph disambiguation out of scope")
def test_person_homograph_should_not_bind():
    nomatch("i met a woman named easter")
