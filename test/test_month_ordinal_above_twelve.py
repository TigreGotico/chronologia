"""A month ordinal above 12 in "the Nth month of YEAR" is refused, never read as the year.

Months 1 to 12 keep their values; a year has no 13th or 14th month, so
the default call returns ``None`` and ``impossible="raise"`` reports it.
Golds are the month number of the ordinal written in each phrase.
"""
from datetime import datetime

import pytest

from chronologia import ImpossibleDateError, extract_event
from chronologia.extract import extract_timespan

ANCHOR = datetime(2026, 11, 22, 9)

#: language, the 14th-month phrase, the 12th-month phrase, the 1st-month phrase
PHRASES = [
    ("en", "the fourteenth month of 2026", "the twelfth month of 2026", "the first month of 2026"),
    ("pt", "o décimo quarto mês de 2026", "o décimo segundo mês de 2026", "o primeiro mês de 2026"),
    ("es", "el decimocuarto mes de 2026", "el decimosegundo mes de 2026", "el primer mes de 2026"),
    ("gl", "o décimo cuarto mes de 2026", "o décimo segundo mes de 2026", "o primeiro mes de 2026"),
    ("ca", "el catorzè mes de 2026", "el dotzè mes de 2026", "el primer mes de 2026"),
    ("fr", "le quatorzième mois de 2026", "le douzième mois de 2026", "le premier mois de 2026"),
    ("it", "il quattordicesimo mese del 2026", "il dodicesimo mese del 2026", "il primo mese del 2026"),
    ("de", "der vierzehnte Monat von 2026", "der zwölfte Monat von 2026", "der erste Monat von 2026"),
    ("nl", "de veertiende maand van 2026", "de twaalfde maand van 2026", "de eerste maand van 2026"),
]


@pytest.mark.parametrize("lang,text", [(p[0], p[1]) for p in PHRASES])
def test_month_14_is_refused(lang, text):
    assert extract_timespan(text, lang, ANCHOR) is None
    assert extract_event(text, lang, ANCHOR) is None


@pytest.mark.parametrize("lang,text", [(p[0], p[1]) for p in PHRASES])
def test_month_14_reports_its_reason(lang, text):
    with pytest.raises(ImpossibleDateError) as caught:
        extract_timespan(text, lang, ANCHOR, impossible="raise")
    assert caught.value.reason == "2026 has no 14th month"
    assert caught.value.lang == lang


@pytest.mark.parametrize("lang,text,month", [(p[0], p[2], 12) for p in PHRASES]
                         + [(p[0], p[3], 1) for p in PHRASES])
def test_months_12_and_1_keep_their_value(lang, text, month):
    span = extract_timespan(text, lang, ANCHOR).span
    first_of_month = (2026, month, 1)
    assert (span.start.year, span.start.month, span.start.day) == first_of_month
    next_month = (2027, 1, 1) if month == 12 else (2026, month + 1, 1)
    assert (span.end.year, span.end.month, span.end.day) == next_month


@pytest.mark.parametrize("text,day", [
    ("o décimo quarto dia de março", (2026, 3, 14)),
    ("o vigésimo quarto dia de março", (2026, 3, 24)),
    # day 34 of 2026 is 3 February (31 days of January); day 104 is 14 April (90 days to 31 March)
    ("o trigésimo quarto dia de 2026", (2026, 2, 3)),
    ("o centésimo quarto dia de 2026", (2026, 4, 14)),
])
def test_pt_compound_ordinal_ending_in_quarto_is_read_whole(text, day):
    start = extract_timespan(text, "pt", ANCHOR).span.start
    assert (start.year, start.month, start.day) == day
