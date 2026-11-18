# -*- coding: utf-8 -*-
"""A morning, afternoon or evening word after a clock fixes its half of the day.

de "früh" (DWDS, "früh", 2: "am Morgen, morgens"; "um fünf Uhr früh fahre ich
zurück"), nb "morgenen" and nn "morgonen" (ordbokene.no, "morgen" and
"morgon": "klokka sju om morgenen", "klokka sju om morgonen") are morning
words, and the nb and nn evening and afternoon words ("klokka ni om kvelden")
are pm words.  The lone-hour rule must not move such a clock to the other half.

Every expected instant is worked out by hand from the anchor, Tuesday
2017-06-27 13:04: a morning hour is already past, so it falls on 2017-06-28,
and an evening hour is still ahead on the anchor day.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)
TOMORROW = datetime(2017, 6, 28)
TODAY = datetime(2017, 6, 27)

# text, language, expected start
CLOCKS = [
    ("um 6 früh", "de", TOMORROW.replace(hour=6)),
    ("um sechs früh", "de", TOMORROW.replace(hour=6)),
    ("um 6:30 früh", "de", TOMORROW.replace(hour=6, minute=30)),
    ("um 6 Uhr früh", "de", TOMORROW.replace(hour=6)),
    ("um fünf Uhr früh", "de", TOMORROW.replace(hour=5)),
    ("klokka 6 om morgenen", "nb", TOMORROW.replace(hour=6)),
    ("klokka 6:30 om morgenen", "nb", TOMORROW.replace(hour=6, minute=30)),
    ("klokka seks om morgenen", "nb", TOMORROW.replace(hour=6)),
    ("klokka 6 om morgonen", "nn", TOMORROW.replace(hour=6)),
    ("klokka 6:30 om morgonen", "nn", TOMORROW.replace(hour=6, minute=30)),
    ("klokka 6 om kvelden", "nb", TODAY.replace(hour=18)),
    ("klokka 6:30 om kvelden", "nb", TODAY.replace(hour=18, minute=30)),
    ("klokka 8 i kveld", "nb", TODAY.replace(hour=20)),
    ("klokka 6 om ettermiddagen", "nb", TODAY.replace(hour=18)),
    ("klokka 6 om kvelden", "nn", TODAY.replace(hour=18)),
    ("klokka 8 i kveld", "nn", TODAY.replace(hour=20)),
    ("klokka 6 om ettermiddagen", "nn", TODAY.replace(hour=18)),
]


@pytest.mark.parametrize("text,lang,start", CLOCKS)
def test_the_part_of_the_day_fixes_the_half(text, lang, start):
    res = extract_timespan(text, lang, ANCHOR)
    assert res is not None
    assert res.span.start == start
    assert res.remainder == ""


@pytest.mark.parametrize("text,lang", [
    ("i kveld", "nb"), ("i kveld", "nn"), ("i ettermiddag", "nb")])
def test_a_part_of_the_day_alone_keeps_its_band(text, lang):
    res = extract_timespan(text, lang, ANCHOR)
    assert res is not None
    assert res.span.start.hour in (12, 18)
    assert res.span.start.day == 27
    assert res.remainder == "i"


def test_morgen_frueh_stays_tomorrow():
    res = extract_timespan("morgen früh", "de", ANCHOR)
    assert res.span.start.day == 28
