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
     (SPAN, CANDIDATES, EVENT, RECURRENCE)),
    ("every 263rd weekday of the year", "en", "a year has no 263rd business day",
     (SPAN, EVENT, RECURRENCE)),
    ("the 25th weekday of the month", "en", "a month has no 25th business day",
     (SPAN, EVENT, RECURRENCE)),
    ("the 25th weekday of every month", "en", "a month has no 25th business day",
     (SPAN, EVENT, RECURRENCE)),
    ("the 25th weekday of a month", "en", "a month has no 25th business day",
     (SPAN, EVENT, RECURRENCE)),
    ("the 263rd weekday of the year", "en", "a year has no 263rd business day",
     (SPAN, EVENT, RECURRENCE)),
    ("the 0th weekday of the month", "en", "a month has no 0th business day",
     (SPAN, EVENT, RECURRENCE)),
    ("the 0th weekday of the year", "en", "a year has no 0th business day",
     (SPAN, EVENT, RECURRENCE)),
    # a recurring date the calendar never has
    ("every 24th weekday of the month", "en", "a month has no 24th business day",
     (SPAN, EVENT, RECURRENCE)),
    ("jeden 24. Werktag des Monats", "de", "a month has no 24th business day",
     (RECURRENCE,)),
    ("every 31st of April", "en", "April has no 31st",
     (SPAN, CANDIDATES, EVENT, RECURRENCE)),
    ("annually on the 30th of february", "en", "February has no 30th",
     (EVENT, RECURRENCE)),
    ("annually on the 31st of february", "en", "February has no 31st",
     (EVENT, RECURRENCE)),
    ("yearly on the 31st of april", "en", "April has no 31st",
     (EVENT, RECURRENCE)),
    ("annually at 9 on the 31st of february", "en", "February has no 31st",
     (EVENT, RECURRENCE)),
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
    "the sixtieth monday of the year": (SPAN, EVENT, RECURRENCE),
    "every 263rd weekday of the year": (SPAN, RECURRENCE),
    "every 24th weekday of the month": (SPAN,),
    "the 25th weekday of the month": (SPAN, EVENT, RECURRENCE),
    "the 25th weekday of every month": (SPAN, EVENT, RECURRENCE),
    "the 25th weekday of a month": (SPAN, EVENT, RECURRENCE),
    "the 263rd weekday of the year": (SPAN, EVENT, RECURRENCE),
    "the 0th weekday of the month": (SPAN, EVENT, RECURRENCE),
    "the 0th weekday of the year": (SPAN, EVENT, RECURRENCE),
    "every 31st of April": (SPAN, EVENT, RECURRENCE),
    "annually on the 30th of february": (EVENT, RECURRENCE),
    "annually on the 31st of february": (EVENT, RECURRENCE),
    "yearly on the 31st of april": (EVENT, RECURRENCE),
    "annually at 9 on the 31st of february": (EVENT, RECURRENCE),
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
    ("every 23rd weekday of the month", "en"),
    ("every 262nd weekday of the year", "en"),
    ("the 23rd weekday of the month", "en"),
    ("the 262nd weekday of the year", "en"),
    ("I worked 25 weekdays of the month", "en"),
    ("25 weekdays of the month", "en"),
    ("the first 25 weekdays of the month", "en"),
    ("the 25.5 weekday of the month", "en"),
    ("the 300.7 weekday of the year", "en"),
    ("ik werkte 25 werkdagen van de maand", "nl"),
    ("25 werkdagen van de maand", "nl"),
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


@pytest.mark.parametrize("text", ["15/13", "31/13", "dia 15/13"])
@pytest.mark.parametrize("extract", [SPAN, CANDIDATES, EVENT, RECURRENCE],
                         ids=lambda e: e.__name__)
def test_default_mode_answers_a_day_over_a_month_that_does_not_exist_without_error(
        extract, text):
    call(extract, text, "pt")
    assert call(SPAN, text, "pt") is None


@pytest.mark.parametrize("text,lang", [
    ("I worked 5 weekdays of the month", "en"),
    ("5 weekdays of the month", "en"),
    ("the first 5 weekdays of the month", "en"),
    ("the 2.5 weekday of the month", "en"),
    ("ik werkte 5 werkdagen van de maand", "nl"),
])
def test_a_count_of_weekdays_or_a_fraction_is_no_ordinal_rule(text, lang):
    assert call(RECURRENCE, text, lang) is None


@pytest.mark.parametrize("text,position", [
    ("bis zum Ablauf des dritten Werktags des Monats", 3),
    ("am Ende des 5. Werktags des Monats", 5),
    ("zum Ablauf des 3. Werktags des Monats", 3),
])
def test_a_genitive_german_weekday_ordinal_is_still_read(text, position):
    """"Werktags" is the genitive singular of "Werktag", not a plural count."""
    rule = call(RECURRENCE, text, "de")
    assert rule is not None and rule.recurrence.bysetpos == (position,)
    assert call(EVENT, text, "de").recurrence.bysetpos == (position,)


#: A rule that never occurs leaves no candidate: the bare weekday or month the
#: phrase spends on the impossible date is no reading of it.
NEVER_OCCURS = [
    ("the 25th weekday of the month", "en", "a month has no 25th business day"),
    ("the sixth monday of may", "en", "May has no 6th Monday"),
    ("every sixth monday of the month", "en", "a month has no 6th Monday"),
    ("el sexto lunes de mayo", "es", "May has no 6th Monday"),
    ("the sixtieth monday of the year", "en", "a year has no 60th Monday"),
    ("every weekday from saturday to sunday", "en",
     "the range from Saturday to Sunday holds no day the rule allows"),
]


@pytest.mark.parametrize("text,lang,reason", NEVER_OCCURS)
def test_a_rule_that_never_occurs_leaves_no_candidate(text, lang, reason):
    assert call(CANDIDATES, text, lang) == []
    assert call(CANDIDATES, text, lang, impossible="none") == []


@pytest.mark.parametrize("text,lang,reason", NEVER_OCCURS)
def test_a_rule_that_never_occurs_raises_from_candidates(text, lang, reason):
    with pytest.raises(ImpossibleDateError) as caught:
        call(CANDIDATES, text, lang, impossible="raise")
    assert caught.value.reason == reason
    assert caught.value.text == text
    assert caught.value.lang == lang


#: text, the day its valid date starts on, a day a reading of the refused words would start on.
#: ANCHOR is Thursday 2026-11-19: the next "friday" is 2026-11-20, the next "3 june" is
#: 2027-06-03 and a bare "monday" is 2026-11-23.
VALID_BESIDE_NEVER = [
    ("the sixth monday of may, or else on 3 june", datetime(2027, 6, 3), datetime(2026, 11, 23)),
    ("meet on friday or the sixth monday of may", datetime(2026, 11, 20), datetime(2026, 11, 23)),
]


@pytest.mark.parametrize("text,valid,spent", VALID_BESIDE_NEVER)
def test_a_valid_date_beside_a_never_occurring_rule_stays_a_candidate(text, valid, spent):
    for mode in ("none", "raise"):
        found = call(CANDIDATES, text, "en", impossible=mode)
        starts = [c.span.start_datetime for c in found]
        assert starts[0] == valid
        assert spent not in starts
        assert found[0].span == call(SPAN, text, "en").span


#: yearly dates that no year has: the rule builder refuses them, the one-off reading stays
YEARLY_NEVER = ["annually on the 30th of february", "annually on the 31st of february",
                "yearly on the 31st of april"]


@pytest.mark.parametrize("text", YEARLY_NEVER)
def test_a_yearly_adverb_date_no_year_has_does_not_crash_candidates(text):
    default = call(CANDIDATES, text, "en")
    assert default == call(CANDIDATES, text, "en", impossible="raise")
