# -*- coding: utf-8 -*-
"""A part of the day after a clock joins the clock (rulings 17, 23 and 27).

A part of the day keeps a spoken hour as said: es "a las 6 de la tarde" is
18:00 (ruling 17).  A digit clock from speech reads the same as the spoken hour
(ruling 23), so "a las 6:30 de la tarde" is 18:30 and the part of the day is
part of the reading, not left over.  An evening word gives the pm half, a
morning word keeps the written hour (ruling 27).

Every expected instant is worked out by hand from the anchor.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_timespan

AFTER_NOON = datetime(2017, 6, 27, 13, 4)
LATE = datetime(2017, 6, 27, 23, 0)
EARLY = datetime(2017, 6, 27, 5, 0)

# text, language, anchor, expected instant
PM = [
    ("a las 6:30 de la tarde", "es", AFTER_NOON, datetime(2017, 6, 27, 18, 30)),
    ("a las 8:30 de la noche", "es", AFTER_NOON, datetime(2017, 6, 27, 20, 30)),
    ("a les 8:30 del vespre", "ca", AFTER_NOON, datetime(2017, 6, 27, 20, 30)),
    ("at 6:30 in the evening", "en", AFTER_NOON, datetime(2017, 6, 27, 18, 30)),
    ("um 6:30 Uhr abends", "de", AFTER_NOON, datetime(2017, 6, 27, 18, 30)),
    ("at 6 o'clock in the evening", "en", AFTER_NOON,
     datetime(2017, 6, 27, 18, 0)),
    ("a las 6:30 de la tarde", "es", LATE, datetime(2017, 6, 28, 18, 30)),
    ("a las seis de la tarde", "es", AFTER_NOON, datetime(2017, 6, 27, 18, 0)),
    ("at six in the evening", "en", AFTER_NOON, datetime(2017, 6, 27, 18, 0)),
]

# a morning part of the day keeps the written hour: the next such hour
AM = [
    ("a las 6:30 de la mañana", "es", AFTER_NOON, datetime(2017, 6, 28, 6, 30)),
    ("a las 6:30 de la mañana", "es", EARLY, datetime(2017, 6, 27, 6, 30)),
    ("a las 6:30 de la madrugada", "es", AFTER_NOON,
     datetime(2017, 6, 28, 6, 30)),
    ("a les 6:30 del matí", "ca", AFTER_NOON, datetime(2017, 6, 28, 6, 30)),
    ("at 6:30 in the morning", "en", AFTER_NOON, datetime(2017, 6, 28, 6, 30)),
    ("um 6:30 Uhr morgens", "de", AFTER_NOON, datetime(2017, 6, 28, 6, 30)),
    ("a las seis de la mañana", "es", AFTER_NOON, datetime(2017, 6, 28, 6, 0)),
    ("at six in the morning", "en", AFTER_NOON, datetime(2017, 6, 28, 6, 0)),
]

# language, template: "6" is the spoken hour, "6:30" the digit clock
TWINS = [
    ("es", "a las {} de la tarde"),
    ("es", "a las {} de la noche"),
    ("ca", "a les {} del vespre"),
    ("ca", "a les {} de la tarda"),
    ("gl", "ás {} da tarde"),
    ("en", "at {} in the evening"),
    ("en", "at {} in the afternoon"),
    ("de", "um {} Uhr abends"),
    ("de", "um {} Uhr nachmittags"),
    ("nl", "om {} uur 's avonds"),
    ("fr", "à {} heures du soir"),
    ("pt", "às {} horas da tarde"),
    ("ru", "в {} часов вечера"),
    ("cs", "v {} hodin večer"),
    ("sk", "o {} hodine večer"),
    ("sl", "ob {} uri zvečer"),
    ("hr", "u {} sati navečer"),
    ("bg", "в {} часа вечерта"),
    ("uk", "о {} годині вечора"),
    ("mk", "во {} часот попладне"),
    ("sv", "klockan {} på kvällen"),
    ("sv", "klockan {} på eftermiddagen"),
    ("da", "klokken {} om aftenen"),
    ("da", "klokken {} om eftermiddagen"),
    ("hu", "{} órakor este"),
    ("el", "στις {} το απόγευμα"),
]


@pytest.mark.parametrize("text,lang,anchor,expected", PM)
def test_an_evening_part_of_the_day_joins_the_clock(text, lang, anchor,
                                                     expected):
    found = extract_timespan(text, lang, anchor)
    assert found.span.start.datetime() == expected
    assert found.remainder == ""


@pytest.mark.parametrize("text,lang,anchor,expected", AM)
def test_a_morning_part_of_the_day_keeps_the_written_hour(text, lang, anchor,
                                                          expected):
    found = extract_timespan(text, lang, anchor)
    assert found.span.start.datetime() == expected


@pytest.mark.parametrize("lang,template", TWINS)
def test_a_digit_clock_reads_like_the_spoken_hour(lang, template):
    spoken = extract_timespan(template.format("6"), lang, AFTER_NOON)
    digit = extract_timespan(template.format("6:30"), lang, AFTER_NOON)
    assert spoken.span.start.datetime() == datetime(2017, 6, 27, 18, 0)
    assert digit.span.start.datetime() == (spoken.span.start.datetime()
                                           + timedelta(minutes=30))
