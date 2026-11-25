"""An "until" word is a range word when the span reading of the text that the
rule leaves covers it and has a left bound.

Anchor 2026-11-22, a Sunday.  "june" and "august" name the next ones, so a
rule that ends with August stops at 2027-08-01, and "5 de desembre" is
2026-12-05.
"""
from datetime import datetime

import pytest

from chronologia import extract_recurrence, extract_timespan
from chronologia.extract import nseries

ANCHOR = datetime(2026, 11, 22, 9, 0)
MONDAYS_TO_AUGUST = "FREQ=WEEKLY;UNTIL=20270801T000000;BYDAY=MO"


def recurrence(lang, text):
    got = extract_recurrence(text, lang, ANCHOR)
    return str(got.recurrence), got.remainder


@pytest.mark.parametrize("lang, text", [
    ("de", "jeden Montag von Juni bis August"),
    ("en", "every monday from june until august"),
    ("nl", "elke maandag van juni tot augustus"),
    ("pt", "toda segunda-feira de junho até agosto"),
    ("es", "cada lunes de junio hasta agosto"),
    ("fr", "chaque lundi de juin jusqu'à août"),
    ("it", "ogni lunedì da giugno fino a agosto"),
    ("ca", "cada dilluns de juny fins a agost"),
    ("gl", "cada luns de xuño ata agosto"),
])
def test_a_month_range_leaves_no_left_bound_in_the_remainder(lang, text):
    assert recurrence(lang, text) == (MONDAYS_TO_AUGUST, "")


DAILY = "FREQ=DAILY;UNTIL="
WEEKLY = "FREQ=WEEKLY;UNTIL="


@pytest.mark.parametrize("lang, text, rule", [
    ("ca", "cada dia de dilluns fins al 5 de desembre", DAILY + "20261205T000000"),
    ("ca", "cada dia de dilluns fins al 24 de desembre", DAILY + "20261224T000000"),
    ("ca", "cada dia de dilluns fins al 25 de desembre", DAILY + "20261225T000000"),
    ("ca", "cada dia de dilluns fins al 1 de gener", DAILY + "20270101T000000"),
    ("ca", "cada dia de dilluns fins a 5 de desembre", DAILY + "20261205T000000"),
    ("ca", "cada dia de dilluns fins al dia 5 de desembre", DAILY + "20261205T000000"),
    ("ca", "cada dia de dilluns fins al 5 d'agost", DAILY + "20270805T000000"),
    ("ca", "cada dia de juny fins al 5 de juny", DAILY + "20270605T000000"),
    ("ca", "cada divendres de 3 de juny fins al 5 de juny",
     WEEKLY + "20270605T000000;BYDAY=FR"),
    ("pt", "toda semana de junho até o dia 5 de agosto", WEEKLY + "20270805T000000"),
    ("pt", "toda sexta de junho até o dia 5 de agosto",
     WEEKLY + "20270805T000000;BYDAY=FR"),
    ("pt", "todo dia de junho até o dia 5 de agosto", DAILY + "20270805T000000"),
    ("pt", "todo dia de 3 de junho até dia 5 de junho", DAILY + "20270605T000000"),
    ("pt", "todo dia de 3 de junho até o dia 15 de junho", DAILY + "20270615T000000"),
    ("pt", "todo dia do dia 3 de junho até ao dia 5 de junho", DAILY + "20270605T000000"),
    ("pt", "todo dia de segunda até dia 5 de dezembro", DAILY + "20261205T000000"),
    ("pt", "todo dia de 3 de junho até 5 de junho", DAILY + "20270605T000000"),
    ("en", "every day from june until august 5 times", DAILY + "20270805T000000"),
])
def test_a_date_range_word_grounds_the_date_the_until_bound_reads(lang, text, rule):
    got = recurrence(lang, text)
    assert got[0] == rule
    assert got[1] == ""


@pytest.mark.parametrize("lang, text, rule", [
    ("en", "every week from now until june", "FREQ=WEEKLY;UNTIL=20270601T000000"),
    ("en", "every day from today until friday", "FREQ=DAILY;UNTIL=20261127T000000"),
])
def test_a_left_bound_that_the_span_reads_is_consumed(lang, text, rule):
    assert recurrence(lang, text) == (rule, "")


@pytest.mark.parametrize("lang, text, rule", [
    ("de", "jeden Tag von Montag bis Freitag bis Dezember",
     "FREQ=DAILY;UNTIL=20261201T000000;BYDAY=MO,TU,WE,TH,FR"),
    ("nl", "elke dag van maandag tot vrijdag tot december",
     "FREQ=DAILY;UNTIL=20261201T000000;BYDAY=MO,TU,WE,TH,FR"),
    ("en", "every day from tuesday until friday", "FREQ=DAILY;BYDAY=TU,WE,TH,FR"),
])
def test_the_range_word_of_a_weekday_set_is_not_an_until_bound(lang, text, rule):
    assert recurrence(lang, text) == (rule, "")


@pytest.mark.parametrize("lang, text, rule", [
    ("en", "every friday from monday until friday",
     "FREQ=WEEKLY;UNTIL=20261127T000000;BYDAY=FR"),
    ("en", "every saturday from friday until sunday",
     "FREQ=WEEKLY;UNTIL=20261122T000000;BYDAY=SA"),
    ("en", "every weekday from monday until wednesday",
     "FREQ=WEEKLY;UNTIL=20261125T000000;BYDAY=MO,TU,WE,TH,FR"),
])
def test_a_rule_with_days_keeps_an_until_word_as_its_bound(lang, text, rule):
    assert recurrence(lang, text) == (rule, "")


@pytest.mark.parametrize("lang, text, rule", [
    ("de", "jeden Freitag von Montag bis Freitag", "FREQ=WEEKLY;BYDAY=FR"),
    ("es", "cada viernes de lunes hasta viernes", "FREQ=WEEKLY;BYDAY=FR"),
    ("pt", "toda sexta-feira de segunda-feira até sexta-feira", "FREQ=WEEKLY;BYDAY=FR"),
    ("de", "jeden Werktag von Mo bis Mi", "FREQ=WEEKLY;BYDAY=MO,TU,WE"),
    ("nl", "elke werkdag van ma tot wo", "FREQ=WEEKLY;BYDAY=MO,TU,WE"),
])
def test_an_until_word_that_is_a_to_word_joins_two_weekdays_of_a_rule(lang, text, rule):
    assert recurrence(lang, text) == (rule, "")


@pytest.mark.parametrize("lang, text, rule, remainder", [
    ("pt", "do dia 3 até à última sexta-feira do mês",
     "FREQ=MONTHLY;UNTIL=20261203T000000;BYDAY=-1FR", ""),
    ("pt", "todos os meses do dia 3 até à terceira terça-feira do mês",
     "FREQ=MONTHLY;UNTIL=20261203T000000;BYDAY=3TU", ""),
    ("en", "every day from monday until before christmas",
     "FREQ=DAILY;UNTIL=20261225T000000", "from monday"),
    ("en", "every monday from 9am until 5 december",
     "FREQ=WEEKLY;UNTIL=20261205T000000;BYDAY=MO;BYHOUR=9", "from"),
    ("de", "jeden Tag von 9 Uhr bis 5. Dezember",
     "FREQ=DAILY;UNTIL=20261205T000000;BYHOUR=9", "von"),
])
def test_the_words_of_the_rule_stay_out_of_the_range(lang, text, rule, remainder):
    assert recurrence(lang, text) == (rule, remainder)


@pytest.mark.parametrize("lang, text, start, end", [
    ("en", "from june until before august", datetime(2027, 6, 1), datetime(2027, 9, 1)),
    ("en", "from monday until before christmas", datetime(2026, 11, 23), datetime(2026, 12, 26)),
    ("it", "da giugno fino a prima di agosto", datetime(2027, 6, 1), datetime(2027, 9, 1)),
    ("de", "jeden Werktag von Mo bis Mi", None, None),
])
def test_a_text_that_holds_no_rule_reads_as_before(lang, text, start, end):
    got = extract_timespan(text, lang, ANCHOR)
    if start is None:
        assert got is None
    else:
        assert (got.span.start_datetime, got.span.end_datetime) == (start, end)


def test_a_text_without_an_until_word_runs_no_span_reading(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("read() ran")
    monkeypatch.setattr(nseries, "read", fail)
    assert recurrence("en", "every monday from june to august at 9am")[1] == ""
