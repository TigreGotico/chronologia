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
