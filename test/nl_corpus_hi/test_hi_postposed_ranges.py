"""Closed ranges, the genitive week join and the indefinite daypart.

Hindi closes a range with both markers postposed: "A से B तक".  से marks
the start (en.wiktionary, entry "से") and तक the limit (Kamtaprasad Guru,
Hindi Vyakaran, 1927, p. 172: तक "सीमा" के अर्थ में, "बालक से लेकर वृद्ध
तक").  The genitive के joins a week to its weekday (Guru, p. 265, row
संबंध: "बालक का-के-की").  एक before a daypart is indefinite (Guru, §184
(1), p. 133), so "सर्दियों की एक सुबह" names no date.

Every expected value is calendar arithmetic from the anchor, Tuesday
2017-06-27 13:04.  A clock-point end is one minute wide.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ANCHOR, ad, nomatch, parse, start_end

TODAY = ANCHOR.replace(hour=0, minute=0)
# the first Monday after the anchor Tuesday
NEXT_MONDAY = TODAY + timedelta(days=(0 - ANCHOR.weekday()) % 7)
MINUTE = timedelta(minutes=1)


def at(day, hour):
    return day.replace(hour=hour)


@pytest.mark.parametrize("text,lo,hi", [
    ("आज दोपहर चार बजे से शाम सात बजे तक",
     at(TODAY, 16), at(TODAY, 19) + MINUTE),
    # the right clock stays in the left one's daypart
    ("आज दोपहर चार बजे से पाँच बजे तक",
     at(TODAY, 16), at(TODAY, 17) + MINUTE),
    ("शाम छह बजे से रात दस बजे तक",
     at(TODAY, 18), at(TODAY, 22) + MINUTE),
    ("हमारी बैठक आज दोपहर तीन बजे से चार बजे तक चलेगी",
     at(TODAY, 15), at(TODAY, 16) + MINUTE),
])
def test_a_postposed_clock_range(text, lo, hi):
    assert start_end(text) == (ad(lo), ad(hi))


@pytest.mark.parametrize("text,first,last", [
    ("सोमवार से बुधवार तक", 0, 2),
    ("सोमवार से शुक्रवार तक", 0, 4),
    ("अगले हफ़्ते बुधवार से शनिवार तक", 2, 5),
])
def test_a_postposed_weekday_range(text, first, last):
    assert start_end(text) == (ad(NEXT_MONDAY + timedelta(days=first)),
                               ad(NEXT_MONDAY + timedelta(days=last + 1)))


def test_a_postposed_range_leaves_the_sentence_in_the_remainder():
    r = parse("हमारी बैठक आज दोपहर तीन बजे से चार बजे तक चलेगी")
    assert r[1] == "हमारी बैठक चलेगी"


@pytest.mark.parametrize("text,weekday", [
    ("अगले हफ़्ते के रविवार को", 6),
    ("अगले हफ़्ते के शुक्रवार को", 4),
    ("अगले हफ़्ते का रविवार", 6),
])
def test_the_genitive_joins_next_week_to_its_weekday(text, weekday):
    day = NEXT_MONDAY + timedelta(days=weekday)
    assert start_end(text) == (ad(day), ad(day + timedelta(days=1)))


def test_the_genitive_joins_last_week_to_its_weekday():
    day = NEXT_MONDAY - timedelta(days=7) - timedelta(days=3)
    assert start_end("पिछले हफ़्ते के शुक्रवार को") == (
        ad(day), ad(day + timedelta(days=1)))


@pytest.mark.parametrize("text", [
    "सर्दियों की एक सुबह दादी ने दीया जलाया",
    "सर्दियों की एक धुंधली सुबह, दादी ने चाय बनाई",
    "गर्मियों की एक शाम हम छत पर बैठे",
])
def test_an_indefinite_daypart_names_no_date(text):
    nomatch(text)


@pytest.mark.parametrize("text", [
    "मेरे घर में दो कमरे हैं",
    "वह से तक",
    "तक",
])
def test_no_date_controls(text):
    nomatch(text)


def test_one_oclock_in_the_morning_is_still_a_clock():
    """एक before बजे is the hour one, not the indefinite marker."""
    assert start_end("आज सुबह एक बजे") == (
        ad(at(TODAY, 1)), ad(at(TODAY, 1) + MINUTE))


def test_a_season_without_the_indefinite_still_reads():
    assert start_end("सर्दियों में")[0] == ad(datetime(2017, 12, 1))
