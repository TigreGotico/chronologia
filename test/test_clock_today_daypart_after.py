# -*- coding: utf-8 -*-
"""A clock followed by a today part-of-day phrase reads that phrase.

"um 8 Uhr heute Abend", "à 8 heures ce soir", "om 2 uur vannacht" and "a las
8 esta noche" name the evening of the anchor day, so each reads as the same
clock written before the phrase ("heute Abend um 8 Uhr").  The phrase leaves
the remainder, and the clock does not roll to tomorrow.

Every expected instant is worked out by hand from the anchor, Tuesday
2017-06-27 13:04.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)
EVENING = datetime(2017, 6, 27, 20, 0)

# lang, text, expected instant, expected remainder
CASES = [
    # the rows of the issues
    ("de", "um 8 Uhr heute Abend", EVENING, ""),
    ("fr", "à 8 heures ce soir", EVENING, ""),
    ("nl", "om 2 uur vannacht", datetime(2017, 6, 28, 2, 0), ""),
    # the same construction in the other user locales
    ("es", "a las 8 esta noche", EVENING, ""),
    ("pt", "às 8 hoje à noite", EVENING, ""),
    ("pt", "às 8 esta noite", EVENING, ""),
    ("ca", "a les 8 aquesta nit", EVENING, ""),
    ("gl", "ás 8 esta noite", EVENING, ""),
    # minutes, other bands, a hour already past
    ("de", "um 8:30 Uhr heute Abend", datetime(2017, 6, 27, 20, 30), ""),
    ("de", "um 3 Uhr heute Nachmittag", datetime(2017, 6, 27, 15, 0), ""),
    ("de", "um 9 Uhr heute früh", datetime(2017, 6, 27, 9, 0), ""),
    ("fr", "à 8h30 ce soir", datetime(2017, 6, 27, 20, 30), ""),
    ("fr", "à 3 heures cet après-midi", datetime(2017, 6, 27, 15, 0), ""),
    ("fr", "à 9 heures ce matin", datetime(2017, 6, 27, 9, 0), ""),
    ("nl", "om 11 uur vannacht", datetime(2017, 6, 27, 23, 0), ""),
    ("es", "a las 8:30 esta noche", datetime(2017, 6, 27, 20, 30), ""),
    ("es", "a las 2 esta noche", datetime(2017, 6, 28, 2, 0), ""),
    # words around the clock stay in the remainder
    ("de", "Termin um 8 Uhr heute Abend im Büro", EVENING, "Termin im Büro"),
    ("fr", "réunion à 8 heures ce soir au bureau", EVENING,
     "réunion au bureau"),
    # controls: the reversed order and the forms that already read right
    ("de", "heute Abend um 8 Uhr", EVENING, ""),
    ("de", "um 8 Uhr abends", EVENING, ""),
    ("fr", "ce soir à 8 heures", EVENING, ""),
    ("fr", "à 8 heures du soir", EVENING, ""),
    ("nl", "vannacht om 2 uur", datetime(2017, 6, 28, 2, 0), ""),
    ("nl", "om 8 uur vanavond", EVENING, ""),
    ("en", "tonight at 8", EVENING, ""),
    ("en", "at 8 this evening", EVENING, ""),
    ("es", "esta noche a las 8", EVENING, ""),
    ("pt", "hoje à noite às 8", EVENING, ""),
    ("ca", "aquesta nit a les 8", EVENING, ""),
    ("gl", "esta noite ás 8", EVENING, ""),
]


@pytest.mark.parametrize("lang,text,expected,remainder", CASES)
def test_a_today_part_of_day_after_a_clock(lang, text, expected, remainder):
    found = extract_timespan(text, lang, ANCHOR)
    assert found.span.start.datetime() == expected
    assert found.remainder == remainder


# A part of day in the next sentence leaves the clock alone: each reads as
# the clock with no part of day (the bare hour, rolled to tomorrow once past
# where the locale rolls a bare clock).
SENTENCE_BREAK = [
    ("fr", "Réveille-moi à 7 heures. Ce soir je sors.",
     datetime(2017, 6, 28, 7, 0)),
    ("es", "Despiértame a las 7. Esta noche salgo.",
     datetime(2017, 6, 28, 7, 0)),
    ("de", "Weck mich um 7 Uhr. Heute Abend gehe ich aus.",
     datetime(2017, 6, 27, 7, 0)),
    ("de", "Wecker um 7 Uhr. Nachmittag habe ich frei.",
     datetime(2017, 6, 28, 7, 0)),
    ("pt", "Acorda-me às 7. Esta noite vou sair.",
     datetime(2017, 6, 28, 7, 0)),
    ("ca", "Desperta'm a les 7. Aquesta nit surto.",
     datetime(2017, 6, 28, 7, 0)),
    ("gl", "Desperta-me ás 7. Esta noite saio.",
     datetime(2017, 6, 28, 7, 0)),
    ("nl", "Maak me wakker om 7 uur. Vannacht slaap ik.",
     datetime(2017, 6, 28, 7, 0)),
    ("en", "wake me at 7. This evening I go out.",
     datetime(2017, 6, 28, 7, 0)),
]


@pytest.mark.parametrize("lang,text,expected", SENTENCE_BREAK)
def test_a_sentence_end_keeps_the_part_of_day_off_the_clock(lang, text,
                                                            expected):
    found = extract_timespan(text, lang, ANCHOR)
    assert found.span.start.datetime() == expected


# Hour 12 before "this morning" is noon, the value of the reversed order
# ("esta mañana a las 12").  Anchor 07:00.
NOON = [
    ("es", "a las 12 esta mañana"),
    ("pt", "às 12 esta manhã"),
    ("gl", "ás 12 esta mañá"),
    ("de", "um 12 Uhr heute Vormittag"),
    ("fr", "à 12 heures ce matin"),
    ("en", "at 12 this morning"),
]


@pytest.mark.parametrize("lang,text", NOON)
def test_twelve_this_morning_is_noon(lang, text):
    found = extract_timespan(text, lang, datetime(2017, 6, 27, 7, 0))
    assert found.span.start.datetime() == datetime(2017, 6, 27, 12, 0)
    assert found.remainder == ""


# A German part-of-day noun after a bare number is no meridiem: the noun
# reads as its own band and the number stays in the remainder.
DE_NOUN = [
    ("am 3. Abend des Festivals", datetime(2017, 6, 27, 18, 0),
     "am 3. des Festivals"),
    ("der 24. Abend", datetime(2017, 6, 27, 18, 0), "der 24."),
    ("am zweiten Nachmittag", datetime(2017, 6, 27, 13, 0), "am zweiten"),
    ("Zimmer 12 Vormittag frei", datetime(2017, 6, 27, 10, 0),
     "Zimmer 12 frei"),
    ("Kapitel 5 Nachmittag", datetime(2017, 6, 27, 13, 0), "Kapitel 5"),
    ("es ist 8 Abend", datetime(2017, 6, 27, 18, 0), "es ist 8"),
]


@pytest.mark.parametrize("text,expected,remainder", DE_NOUN)
def test_a_german_part_of_day_noun_after_a_number(text, expected, remainder):
    found = extract_timespan(text, "de", ANCHOR)
    assert found.span.start.datetime() == expected
    assert found.remainder == remainder


# "this" part of day names the anchor day even when its hour has passed, as
# the reversed order does ("esta noche a las 8" at 21:00 is 20:00 today).
PASSED = [
    ("es", "a las 8 esta noche", datetime(2017, 6, 27, 21, 0),
     datetime(2017, 6, 27, 20, 0)),
    ("pt", "às 8 esta noite", datetime(2017, 6, 27, 21, 0),
     datetime(2017, 6, 27, 20, 0)),
    ("ca", "a les 8 aquesta nit", datetime(2017, 6, 27, 21, 0),
     datetime(2017, 6, 27, 20, 0)),
    ("gl", "ás 8 esta noite", datetime(2017, 6, 27, 21, 0),
     datetime(2017, 6, 27, 20, 0)),
    ("es", "a la 1 esta tarde", ANCHOR, datetime(2017, 6, 27, 13, 0)),
    ("pt", "à 1 hoje à tarde", ANCHOR, datetime(2017, 6, 27, 13, 0)),
    ("es", "a las 9 esta mañana", ANCHOR, datetime(2017, 6, 27, 9, 0)),
]


@pytest.mark.parametrize("lang,text,anchor,expected", PASSED)
def test_this_part_of_day_keeps_the_anchor_day(lang, text, anchor, expected):
    found = extract_timespan(text, lang, anchor)
    assert found.span.start.datetime() == expected
    assert found.remainder == ""
