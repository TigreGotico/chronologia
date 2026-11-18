"""The Catalan article and "dia" that open a date belong to it.

"Per expressar el dia en què s’esdevé un fet s’utilitza l’article masculí el
o bé l’expressió el dia" (Universitat de Barcelona, Llibre d'estil, criteri
2800).  The dates are calendar arithmetic: 2026-10-17 is a Saturday and
2026-10-16 a Friday.
"""
from datetime import datetime

import pytest

from chronologia import AstroDate, extract_timespan

SAT = datetime(2026, 10, 17, 12, 0)
FRI = datetime(2026, 10, 16, 10, 0)
JUNE = datetime(2017, 6, 27)


@pytest.mark.parametrize("text, anchor, day, rest", [
    ("recorda de trucar a la mare el dia 3 d'agost", JUNE, (2017, 8, 3),
     "recorda de trucar a la mare"),
    ("gasta diners el dia 13 de maig", JUNE, (2018, 5, 13), "gasta diners"),
    ("el vinent dilluns", SAT, (2026, 10, 19), ""),
    ("el vinent dimarts", SAT, (2026, 10, 20), ""),
    ("el vinent dimecres", SAT, (2026, 10, 21), ""),
    ("el vinent divendres", SAT, (2026, 10, 23), ""),
    ("el vinent diumenge", SAT, (2026, 10, 18), ""),
    ("el pròxim divendres", SAT, (2026, 10, 23), ""),
    ("el següent divendres", SAT, (2026, 10, 23), ""),
    ("el proper divendres", SAT, (2026, 10, 23), ""),
    ("el passat divendres", SAT, (2026, 10, 16), ""),
    ("quan és el vinent divendres", SAT, (2026, 10, 23), "quan és"),
    ("el vinent divendres", FRI, (2026, 10, 23), ""),
    ("el pròxim dilluns", FRI, (2026, 10, 19), ""),
])
def test_the_article_opens_the_date(text, anchor, day, rest):
    span, remainder = extract_timespan(text, "ca", anchor)
    assert (span.start, remainder) == (AstroDate(*day), rest)


def test_el_before_a_verb_stays():
    # "el" is the pronoun "him" here; the next word is no part of the date
    _, remainder = extract_timespan("el truco dilluns", "ca", SAT)
    assert remainder == "el truco"
