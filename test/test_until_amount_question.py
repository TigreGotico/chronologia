""""hasta cuántos grados" asks for an amount, so "hasta" opens no range.

In es "¿Hasta cuántos grados va a subir la temperatura hoy?", pt "Até quantos
graus ... hoje?" and nl "Tot hoeveel graden koelt het vanavond af?" the word for
"until" governs an amount, not a day, and the sentence names the day word only
("hoy", "hoje", "vanavond").  A true limit ("hasta mañana", "tot vrijdag") is
still the open range from the anchor.  Every date is worked out by hand from the
anchor, Tuesday 2017-06-27 13:04: today ends at 2017-06-28 00:00, tomorrow ends
on 2017-06-29, and Friday 2017-06-30 ends on 2017-07-01 for the Saturday week.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan, extract_timespans

ANCHOR = datetime(2017, 6, 27, 13, 4)
MIDNIGHT = datetime(2017, 6, 28)

QUESTIONS = [
    ("¿Hasta cuántos grados va a subir la temperatura hoy?", "es"),
    ("Até quantos graus vai subir a temperatura hoje?", "pt"),
    ("Tot hoeveel graden koelt het vanavond af?", "nl"),
]

LIMITS = [
    ("hasta mañana", "es", datetime(2017, 6, 29)),
    ("até amanhã", "pt", datetime(2017, 6, 29)),
    ("tot morgen", "nl", datetime(2017, 6, 29)),
]


@pytest.mark.parametrize("text,lang", QUESTIONS)
def test_an_amount_after_until_opens_no_range(text, lang):
    found = extract_timespan(text, lang, ANCHOR)
    assert found.span.start.datetime() >= datetime(2017, 6, 27)
    assert found.span.start.datetime() != ANCHOR
    assert found.span.end.datetime() == MIDNIGHT


@pytest.mark.parametrize("text,lang", QUESTIONS)
def test_the_mention_is_the_day_word(text, lang):
    mentions = extract_timespans(text, lang, ANCHOR)
    assert len(mentions) == 1
    assert mentions[0].span.end.datetime() == MIDNIGHT


@pytest.mark.parametrize("text,lang,end", LIMITS)
def test_a_time_after_until_is_still_an_open_range(text, lang, end):
    found = extract_timespan(text, lang, ANCHOR)
    assert found.span.start.datetime() == ANCHOR
    assert found.span.end.datetime() == end
