"""es and gl "de mañana" after a noun is tomorrow, and es "entre semana" is no range.

"mañana" is the adverb for the day after today (Wikcionario s.v. "mañana",
adverbio de tiempo, 4) and, in gl "mañá", also the noun for the morning
(Galizionario s.v. "mañá").  After a day word, or with nothing before it, the
"de" opens the morning ("lunes de mañana", "de mañana").  After a noun it
joins the noun to tomorrow ("las alarmas de mañana").  "entre semana" is "En
cualquiera de los días comprendidos entre el lunes y el viernes" (Wikcionario
s.v. "entre semana"), so its "entre" opens no range.  Every instant is worked
out by hand from the anchor, Tuesday 2017-06-27 13:04: tomorrow is Wednesday
2017-06-28, and the next Monday is 2017-07-03.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2017, 6, 27, 13, 4)
TOMORROW = (datetime(2017, 6, 28), datetime(2017, 6, 29))


def _span(text, lang):
    found = extract_timespan(text, lang, ANCHOR)
    return (found.span.start.datetime(), found.span.end.datetime()), found.remainder


@pytest.mark.parametrize("text,lang,remainder", [
    ("léeme las alarmas de mañana", "es", "léeme las alarmas de"),
    ("las alarmas de mañana", "es", "las alarmas de"),
    ("el vuelo de mañana", "es", "el vuelo de"),
    ("a partir de mañana", "es", "a partir de"),
    ("el día de mañana", "es", "el día de"),
    ("amósame as alarmas de mañá", "gl", "amósame as alarmas de"),
])
def test_de_manana_after_a_noun_is_tomorrow(text, lang, remainder):
    assert _span(text, lang) == (TOMORROW, remainder)


@pytest.mark.parametrize("text,lang,start,end", [
    ("lunes de mañana", "es", datetime(2017, 7, 3, 6), datetime(2017, 7, 3, 12)),
    ("luns de mañá", "gl", datetime(2017, 7, 3, 6), datetime(2017, 7, 3, 12)),
    ("mañana por la mañana", "es", datetime(2017, 6, 28, 6), datetime(2017, 6, 28, 12)),
    ("de mañana", "es", datetime(2017, 6, 27, 6), datetime(2017, 6, 27, 12)),
    ("de mañá", "gl", datetime(2017, 6, 27, 6), datetime(2017, 6, 27, 12)),
])
def test_the_morning_keeps_its_reading_after_a_day(text, lang, start, end):
    assert _span(text, lang) == ((start, end), "")


def test_entre_semana_before_a_clock_opens_no_range():
    text = "recuérdame ir al trabajo entre semana por la mañana a las 8"
    assert _span(text, "es") == (
        (datetime(2017, 6, 28, 8), datetime(2017, 6, 28, 8, 1)),
        "recuérdame ir al trabajo entre semana")


def test_entre_two_days_is_still_a_range():
    assert _span("entre lunes y viernes", "es") == (
        (datetime(2017, 7, 3), datetime(2017, 7, 8)), "")
