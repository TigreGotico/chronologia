"""``impossible="raise"`` tells a date the calendar rejects from a phrase that is no date.

Every reason text is written by hand from the calendar: 2017 is no leap year,
February 2026 has 28 days (four of each weekday), November 2026 has 30 days
and five Mondays, 2017 has 52 ISO weeks.
"""
from datetime import datetime

import pytest

from chronologia import ImpossibleDateError, extract_event
from chronologia.extract import (extract_candidates, extract_recurrence,
                                 extract_timespan)

ANCHOR = datetime(2026, 11, 19, 10, 0)

SPAN, CANDIDATES, EVENT, RECURRENCE = (
    extract_timespan, extract_candidates, extract_event, extract_recurrence)


def call(extract, text, lang, **kwargs):
    if extract is extract_event:
        return extract(text, lang, ANCHOR, **kwargs)
    return extract(text, lang, anchor=ANCHOR, **kwargs)


#: text, language, reason, the extractors that raise it
IMPOSSIBLE = [
    # a day the month never has
    ("the 32nd of February", "en", "no month has a 32nd", (SPAN, CANDIDATES, EVENT)),
    ("32 aprile", "it", "no month has a 32nd", (SPAN, CANDIDATES, EVENT)),
    ("29 de fevereiro de 2017", "pt", "February 2017 has no 29th", (SPAN, CANDIDATES, EVENT)),
    ("29 de febrero de 2017", "es", "February 2017 has no 29th", (SPAN, CANDIDATES, EVENT)),
    ("le 30 février", "fr", "February has no 30th", (SPAN, CANDIDATES, EVENT)),
    ("der 31. April", "de", "April has no 31st", (SPAN, CANDIDATES, EVENT)),
    ("30 de fevereiro", "pt", "February has no 30th", (SPAN, CANDIDATES, EVENT)),
    ("2017-02-29", "en", "February 2017 has no 29th", (SPAN, CANDIDATES, EVENT)),
    ("31/02/2017", "en", "February 2017 has no 31st", (SPAN, CANDIDATES, EVENT)),
    ("the 31st of this month", "en", "November 2026 has no 31st", (SPAN, CANDIDATES, EVENT)),
    ("the first friday after the 31st", "en", "November 2026 has no 31st",
     (SPAN, CANDIDATES, EVENT)),
    # an ordinal the period never reaches
    ("the 60th day of february", "en", "February 2026 has no 60th day",
     (SPAN, CANDIDATES, EVENT)),
    ("2017-W53", "en", "2017 has no ISO week 53", (SPAN, CANDIDATES, EVENT)),
    ("the fifth friday of february 2026", "en", "February 2026 has no 5th Friday",
     (SPAN, CANDIDATES)),
    ("the fifth monday of may", "en", "May 2026 has no 5th Monday", (SPAN, CANDIDATES)),
    ("el sexto lunes de mayo", "es", "May has no 6th Monday",
     (SPAN, CANDIDATES, EVENT, RECURRENCE)),
    ("the sixtieth monday of the year", "en", "2026 has no 60th Monday",
     (SPAN, CANDIDATES)),
    ("the sixtieth monday of the year", "en", "a year has no 60th Monday",
     (EVENT, RECURRENCE)),
    # a recurring date the calendar never has
    ("every 31st of April", "en", "April has no 31st",
     (SPAN, CANDIDATES, EVENT, RECURRENCE)),
]

#: text -> the extractors whose default answer is None; the others answer a
#: partial reading, a rule or an error that the option leaves alone
DEFAULT_NONE = {
    "the 32nd of February": (SPAN, EVENT),
    "32 aprile": (SPAN, EVENT),
    "29 de fevereiro de 2017": (SPAN, EVENT),
    "29 de febrero de 2017": (SPAN, EVENT),
    "le 30 février": (SPAN, EVENT),
    "der 31. April": (SPAN, EVENT),
    "30 de fevereiro": (SPAN, EVENT),
    "2017-02-29": (SPAN, EVENT),
    "31/02/2017": (SPAN, EVENT),
    "the 31st of this month": (SPAN, EVENT),
    "the 60th day of february": (SPAN, EVENT),
    "2017-W53": (SPAN, EVENT),
    "the fifth friday of february 2026": (SPAN,),
    "el sexto lunes de mayo": (SPAN,),
    "the sixtieth monday of the year": (SPAN,),
    "every 31st of April": (SPAN, EVENT, RECURRENCE),
}

CASES = [(text, lang, reason, extract)
         for text, lang, reason, raising in IMPOSSIBLE for extract in raising]


@pytest.mark.parametrize("text,lang,reason,extract", CASES,
                         ids=[f"{c[3].__name__}-{c[0]}" for c in CASES])
def test_impossible_date_raises_with_its_reason(text, lang, reason, extract):
    with pytest.raises(ImpossibleDateError) as caught:
        call(extract, text, lang, impossible="raise")
    assert caught.value.reason == reason
    assert caught.value.text == text
    assert caught.value.lang == lang


DEFAULT = [(text, extract) for text, extractors in DEFAULT_NONE.items()
           for extract in extractors]


@pytest.mark.parametrize("text,extract", DEFAULT,
                         ids=[f"{e.__name__}-{t}" for t, e in DEFAULT])
def test_default_mode_answers_none(text, extract):
    lang = next(c[1] for c in CASES if c[0] == text)
    assert call(extract, text, lang) is None
    assert call(extract, text, lang, impossible="none") is None


VALID_OR_NOT_A_DATE = [
    ("the 29th of february 2028", "en"),
    ("29 de fevereiro de 2028", "pt"),
    ("5 de junio", "es"),
    ("le 30 janvier", "fr"),
    ("der 31. Oktober", "de"),
    ("the fifth Monday of November 2026", "en"),
    ("el quinto lunes de agosto de 2026", "es"),
    ("every 31st of October", "en"),
    ("every friday", "en"),
    ("tomorrow", "en"),
    ("2028-02-29", "en"),
    ("2026-W53", "en"),
    ("the 366th day of the year 2020", "en"),
    ("week 53 of 2020", "en"),
    ("100 years ago", "en"),
    ("tomorrow 100 people", "en"),
    ("a finales de los años noventa", "es"),
    ("20h60", "es"),
    ("hello world", "en"),
    ("the 5th of the cohort", "en"),
    ("", "en"),
]


@pytest.mark.parametrize("text,lang", VALID_OR_NOT_A_DATE)
@pytest.mark.parametrize("extract", [SPAN, CANDIDATES, EVENT, RECURRENCE],
                         ids=lambda e: e.__name__)
def test_valid_dates_and_non_dates_answer_the_same_in_both_modes(extract, text, lang):
    assert call(extract, text, lang, impossible="raise") == call(extract, text, lang)


@pytest.mark.parametrize("extract", [SPAN, CANDIDATES, EVENT, RECURRENCE],
                         ids=lambda e: e.__name__)
def test_unknown_mode_names_the_allowed_values(extract):
    with pytest.raises(ValueError, match="'none', 'raise'") as caught:
        call(extract, "tomorrow", "en", impossible="strict")
    assert not isinstance(caught.value, ImpossibleDateError)


def test_the_error_is_a_value_error_with_the_phrase_in_its_message():
    with pytest.raises(ValueError, match="February 2017 has no 29th") as caught:
        extract_timespan("29 February 2017", "en", impossible="raise")
    assert isinstance(caught.value, ImpossibleDateError)
    assert extract_timespan("29 February 2017", "en") is None
