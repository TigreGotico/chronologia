"""Shared semantic-parity block: a French phrase must resolve to the *same*
span as its English staple, tying the fr locale to the hand-checked English
reference spans rather than to the engine's own output.
"""
import pytest

from chronologia import extract_timespan

from ._corpus import ANCHOR


# (french, english) translation pairs that must land on the identical span
PAIRS = [
    ("aujourd'hui", "today"),
    ("demain", "tomorrow"),
    ("hier", "yesterday"),
    ("après-demain", "overmorrow"),
    ("avant-hier", "ereyesterday"),
    ("dans 3 jours", "in 3 days"),
    ("dans 5 jours", "in 5 days"),
    ("dans 2 semaines", "in 2 weeks"),
    ("dans 1 jour", "in 1 day"),
    ("dans 2 mois", "in 2 months"),
    ("dans 5 ans", "in 5 years"),
    ("dans 3 heures", "in 3 hours"),
    ("dans 15 minutes", "in 15 minutes"),
    ("vendredi prochain", "next friday"),
    ("lundi prochain", "next monday"),
    ("mardi dernier", "last tuesday"),
    ("ce jeudi", "this thursday"),
    ("15:30", "15:30"),
    ("09:30", "09:30"),
    ("00:00", "00:00"),
    ("midi", "noon"),
    ("minuit", "midnight"),
    ("2019", "2019"),
    ("1989", "1989"),
    ("2017-06-30", "2017-06-30"),
    ("de juin à août", "from june to august"),
    ("de janvier à mars", "from january to march"),
    ("entre juin et septembre", "between june and september"),
    ("l'été 2020", "summer 2020"),
    ("l'hiver prochain", "next winter"),
    ("44 avant jésus-christ", "44 bc"),
    ('la semaine prochaine', 'next week'),
    ('le mois dernier', 'last month'),
    ('ce week-end', 'this weekend'),
]


@pytest.mark.parametrize("fr_text,en_text", PAIRS)
def test_span_parity(fr_text, en_text):
    fr = extract_timespan(fr_text, "fr", ANCHOR)
    en = extract_timespan(en_text, "en", ANCHOR)
    assert fr is not None, f"fr {fr_text!r} did not parse"
    assert en is not None, f"en {en_text!r} did not parse"
    assert fr[0].start == en[0].start, (fr_text, en_text)
    assert fr[0].end == en[0].end, (fr_text, en_text)
