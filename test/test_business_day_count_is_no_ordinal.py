"""A cardinal before a plural business noun counts days; it names no business day.

"5 working days of the month" is a length, so the nth-business-day reading and
its past-the-month refusal do not apply.  The ordinal forms keep both.
The 5th business day of November 2026 (Friday the 6th) is past, so "the month"
is December 2026: Tuesday the 1st to Monday the 7th.
"""
from datetime import datetime

import pytest

from chronologia import extract_event
from chronologia.extract import extract_candidates, extract_timespan

ANCHOR = datetime(2026, 11, 22, 9, 0)

COUNTS = [
    ("en", "5 business days of the month"),
    ("en", "25 business days of the month"),
    ("en", "5 working days of the month"),
    ("en", "5 workdays of the month"),
    ("nl", "5 werkdagen van de maand"),
    ("nl", "25 werkdagen van de maand"),
    ("de", "5 Werktage des Monats"),
    ("de", "25 Werktage des Monats"),
    ("de", "5 Arbeitstage des Monats"),
    ("pt", "5 dias úteis do mês"),
    ("pt", "25 dias úteis do mês"),
    ("es", "5 días hábiles del mes"),
    ("es", "25 días laborables del mes"),
    ("fr", "5 jours ouvrables du mois"),
    ("fr", "25 jours ouvrés du mois"),
    ("en", "in 5 business days of the month"),
    ("nl", "in 25 werkdagen van de maand"),
]

ORDINALS = [
    ("en", "the 5th business day of the month"),
    ("nl", "de 5e werkdag van de maand"),
    ("nl", "de vijfde werkdag van de maand"),
    ("de", "der 5. Werktag des Monats"),
    ("pt", "o 5.º dia útil do mês"),
    ("es", "el 5.º día hábil del mes"),
    ("fr", "le 5e jour ouvrable du mois"),
]


def span(text, lang, **kwargs):
    return extract_timespan(text, lang, anchor=ANCHOR, **kwargs)


@pytest.mark.parametrize("lang,text", COUNTS)
def test_a_count_is_no_business_day_in_either_mode(lang, text):
    assert span(text, lang) is None
    assert span(text, lang, impossible="raise") is None
    assert extract_candidates(text, lang, anchor=ANCHOR, impossible="raise") == []
    assert extract_event(text, lang, ANCHOR, impossible="raise") is None


@pytest.mark.parametrize("lang,text", ORDINALS)
def test_an_ordinal_is_the_fifth_business_day(lang, text):
    result = span(text, lang, impossible="raise")
    assert (result.span.start.year, result.span.start.month,
            result.span.start.day) == (2026, 12, 7)
