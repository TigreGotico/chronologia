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
    ("31 april 2020", "nl", "April 2020 has no 31st", (SPAN, EVENT)),
    ("29 February 4 BC", "en", "February 4 BC has no 29th", (SPAN, EVENT)),
    ("29 de fevereiro de 2017", "pt", "February 2017 has no 29th", (SPAN, EVENT)),
    ("29 de febrero de 2017", "es", "February 2017 has no 29th", (SPAN, EVENT)),
    ("le 30 février", "fr", "February has no 30th", (SPAN, EVENT)),
    ("der 31. April", "de", "April has no 31st", (SPAN, EVENT)),
    ("30 de fevereiro", "pt", "February has no 30th", (SPAN, CANDIDATES, EVENT)),
    ("2017-02-29", "en", "February 2017 has no 29th", (SPAN, CANDIDATES, EVENT)),
    ("31/02/2017", "en", "February 2017 has no 31st", (SPAN, CANDIDATES, EVENT)),
    ("the 31st of this month", "en", "November 2026 has no 31st", (SPAN, CANDIDATES, EVENT)),
    # an ordinal the period never reaches
    ("the 60th day of february", "en", "February has no 60th day",
     (SPAN, CANDIDATES, EVENT)),
    ("the 400th day of the year", "en", "a year has no 400th day",
     (SPAN, CANDIDATES, EVENT)),
    ("the 6th weekend of june", "en", "June has no 6th weekend", (SPAN, EVENT)),
    ("2017-00-00", "en", "2017 has no month 0", (SPAN, CANDIDATES, EVENT)),
    ("2017-13-00", "en", "2017 has no month 13", (SPAN, CANDIDATES, EVENT)),
    ("on 2017-15-00 we met", "en", "2017 has no month 15", (SPAN, CANDIDATES, EVENT)),
    ("de vijfde maandag van februari 2021", "nl", "February 2021 has no 5th Monday",
     (SPAN, EVENT)),
    ("2017-W53", "en", "2017 has no ISO week 53", (SPAN, CANDIDATES, EVENT)),
    ("the fifth friday of february 2026", "en", "February 2026 has no 5th Friday",
     (SPAN, EVENT)),
    ("el sexto lunes de mayo", "es", "May has no 6th Monday",
     (SPAN, EVENT, RECURRENCE)),
    ("every sixth monday of the month", "en", "a month has no 6th Monday",
     (SPAN, EVENT, RECURRENCE)),
    ("the sixtieth monday of the year", "en", "a year has no 60th Monday",
     (SPAN, CANDIDATES, EVENT)),
    # a recurring date the calendar never has
    ("every 31st of April", "en", "April has no 31st",
     (SPAN, CANDIDATES, EVENT, RECURRENCE)),
]

#: text -> the extractors whose default answer is None; the others answer a
#: partial reading, a rule or an error that the option leaves alone
DEFAULT_NONE = {
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
    "el sexto lunes de mayo": (SPAN, EVENT, RECURRENCE),
    "every sixth monday of the month": (SPAN, EVENT, RECURRENCE),
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
    ("the 366th day of the year", "en"),
    ("the fifth monday of may", "en"),
    ("el quinto lunes de mayo", "es"),
    ("o quinto domingo de outubro", "pt"),
    ("the fifth weekend of may", "en"),
    ("29 de fevereiro", "pt"),
    ("o dia 40", "pt"),
    ("the first friday after the 31st", "en"),
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


NOT_A_DATE_TEMPLATES = [
    ("only {} may come on friday", "en"),
    ("{} may attend tomorrow", "en"),
    ("order {} may ship next week", "en"),
    ("{} march on monday", "en"),
    ("the {} march today", "en"),
    ("{} june bugs", "en"),
    ("{} august men", "en"),
    ("flight {} april 3", "en"),
    ("el capítulo {} de abril", "es"),
    ("Raum {} im Mai", "de"),
]
NUMERALS = [32, 33, 40, 45, 50, 60, 64, 99, 100, 150, 200, 500, 1000]
NOT_A_DATE = [(template.format(n), lang) for template, lang in NOT_A_DATE_TEMPLATES
              for n in NUMERALS]


@pytest.mark.parametrize("text,lang", NOT_A_DATE)
def test_a_number_beside_a_month_word_is_no_impossible_date(text, lang):
    for extract in (SPAN, CANDIDATES, EVENT, RECURRENCE):
        call(extract, text, lang, impossible="raise")


@pytest.mark.parametrize("text", ["2017-13-00", "1999-99-00", "2017/13/00",
                                  "2017.13.00", "on 2017-15-00 we met",
                                  "2017-00-00", "0000-00-00"])
@pytest.mark.parametrize("extract", [SPAN, CANDIDATES, EVENT, RECURRENCE],
                         ids=lambda e: e.__name__)
def test_default_mode_answers_a_month_that_does_not_exist_without_error(extract, text):
    call(extract, text, "en")
    assert call(SPAN, text, "en") is None
