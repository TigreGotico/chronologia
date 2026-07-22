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


# ==========================================================================
# EXPANDED SET — non-Christian / non-Western well-known holidays.
#
# Anchor stays 2017-06-27 (Tuesday); bare = next occurrence on or after it.
# Movable non-Gregorian dates are taken from independent published tables,
# cross-checked against this engine's own tabulated calendar data:
#
#   Umm al-Qura (Islamic):  Eid al-Fitr 2018 = 15 Jun, 2026 = 20 Mar;
#     Ramadan start 2018 = 16 May; Ashura 2017 = 30 Sep; Mawlid 2017 = 30 Nov;
#     Islamic New Year 2017 = 21 Sep; Eid al-Adha 2017 = 1 Sep.
#   Arithmetic Hebrew:  Rosh Hashanah 2017 = 21 Sep; Yom Kippur 2017 = 30 Sep;
#     Passover 2018 = 31 Mar, 2026 = 2 Apr; Hanukkah 2017 = 13 Dec, 2026 = 5 Dec.
#   Tabulated Chinese:  Chinese New Year 2018 = 16 Feb, 2026 = 17 Feb;
#     Mid-Autumn 2017 = 4 Oct.
#   Solar Hijri (Nowruz):  2018 = 21 Mar.  Orthodox Easter 2018 = 8 Apr.
#   Decree tables (no closed form here):  Diwali 2017 = 19 Oct, 2026 = 8 Nov,
#     2016 = 30 Oct;  Vesak 2018 = 29 May.
#   Secular / US-rule:  Halloween 31 Oct; Valentine's 14 Feb; St Patrick's
#     17 Mar; US Thanksgiving = 4th Thu Nov (2017 = 23 Nov, 2026 = 26 Nov);
#     Mother's Day = 2nd Sun May (US, 2018 = 13 May); Father's Day = 3rd Sun
#     Jun (US, 2018 = 17 Jun).
# ==========================================================================

_BARE_EXPANDED = [
    ("eid", (2018, 6, 15)),
    ("eid al-fitr", (2018, 6, 15)),
    ("eid al-adha", (2017, 9, 1)),
    ("islamic new year", (2017, 9, 21)),
    ("ashura", (2017, 9, 30)),
    ("mawlid", (2017, 11, 30)),
    ("rosh hashanah", (2017, 9, 21)),
    ("yom kippur", (2017, 9, 30)),
    ("passover", (2018, 3, 31)),
    ("hanukkah", (2017, 12, 13)),
    ("chanukah", (2017, 12, 13)),
    ("chinese new year", (2018, 2, 16)),
    ("lunar new year", (2018, 2, 16)),
    ("mid-autumn festival", (2017, 10, 4)),
    ("nowruz", (2018, 3, 21)),
    ("persian new year", (2018, 3, 21)),
    ("diwali", (2017, 10, 19)),
    ("vesak", (2018, 5, 29)),
    ("orthodox easter", (2018, 4, 8)),
    ("halloween", (2017, 10, 31)),
    ("valentine's day", (2018, 2, 14)),
    ("st patrick's day", (2018, 3, 17)),
    ("thanksgiving", (2017, 11, 23)),
    ("mother's day", (2018, 5, 13)),
    ("father's day", (2018, 6, 17)),
]


@pytest.mark.parametrize("text,ymd", _BARE_EXPANDED)
def test_bare_expanded(text, ymd):
    assert start(text) == AstroDate(*ymd)
    assert span(text).width == timedelta(days=1)


@pytest.mark.parametrize("text,ymd", [
    ("eid al-fitr 2026", (2026, 3, 20)),
    ("diwali 2026", (2026, 11, 8)),
    ("chinese new year 2026", (2026, 2, 17)),
    ("hanukkah 2026", (2026, 12, 5)),
    ("passover 2026", (2026, 4, 2)),
    ("thanksgiving 2026", (2026, 11, 26)),
])
def test_explicit_year_expanded(text, ymd):
    assert start(text) == AstroDate(*ymd)


@pytest.mark.parametrize("text,ymd", [
    ("next hanukkah", (2017, 12, 13)),
    ("last diwali", (2016, 10, 30)),
    ("when is eid", (2018, 6, 15)),
    ("when is thanksgiving", (2017, 11, 23)),
    ("when is chinese new year", (2018, 2, 16)),
])
def test_rel_and_when_expanded(text, ymd):
    assert start(text) == AstroDate(*ymd)


# -- negatives / confusables: no holiday word -> nothing binds -------------
@pytest.mark.parametrize("text", [
    "i love eating rice",
    "the moon festival lights",     # "moon festival" is not a bound surface
    "a bowl of noodles",
    "the price of turkey went up",  # no "thanksgiving" surface present
])
def test_expanded_no_match(text):
    nomatch(text)
