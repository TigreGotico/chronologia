"""An "until" word is a range word when it joins the left and the right bound
of the span reading of the text that the rule leaves.

Anchor 2026-11-22, a Sunday.  "june" and "august" name the next ones, so a
rule that ends with August stops at 2027-08-01, and "5 de desembre" is
2026-12-05.
"""
from datetime import datetime

import pytest

from chronologia import extract_recurrence, extract_timespan
from chronologia.extract import nseries

ANCHOR = datetime(2026, 11, 22, 9, 0)
MONDAYS_TO_AUGUST = "FREQ=WEEKLY;UNTIL=20270901T000000;BYDAY=MO"


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
    ("ca", "cada dia de dilluns fins al 5 de desembre", DAILY + "20261206T000000"),
    ("ca", "cada dia de dilluns fins al 24 de desembre", DAILY + "20261225T000000"),
    ("ca", "cada dia de dilluns fins al 25 de desembre", DAILY + "20261226T000000"),
    ("ca", "cada dia de dilluns fins al 1 de gener", DAILY + "20270102T000000"),
    ("ca", "cada dia de dilluns fins a 5 de desembre", DAILY + "20261206T000000"),
    ("ca", "cada dia de dilluns fins al dia 5 de desembre", DAILY + "20261206T000000"),
    ("ca", "cada dia de dilluns fins al 5 d'agost", DAILY + "20270806T000000"),
    ("ca", "cada dia de juny fins al 5 de juny", DAILY + "20270606T000000"),
    ("ca", "cada divendres de 3 de juny fins al 5 de juny",
     WEEKLY + "20270606T000000;BYDAY=FR"),
    ("pt", "toda semana de junho até o dia 5 de agosto", WEEKLY + "20270806T000000"),
    ("pt", "toda sexta de junho até o dia 5 de agosto",
     WEEKLY + "20270806T000000;BYDAY=FR"),
    ("pt", "todo dia de junho até o dia 5 de agosto", DAILY + "20270806T000000"),
    ("pt", "todo dia de 3 de junho até dia 5 de junho", DAILY + "20270606T000000"),
    ("pt", "todo dia de 3 de junho até o dia 15 de junho", DAILY + "20270616T000000"),
    ("pt", "todo dia do dia 3 de junho até ao dia 5 de junho", DAILY + "20270606T000000"),
    ("pt", "todo dia de segunda até dia 5 de dezembro", DAILY + "20261206T000000"),
    ("pt", "todo dia de 3 de junho até 5 de junho", DAILY + "20270606T000000"),
])
def test_a_date_range_word_ends_the_rule_with_its_right_bound(lang, text, rule):
    got = recurrence(lang, text)
    assert got[0] == rule
    assert got[1] == ""


@pytest.mark.parametrize("lang, text, rule", [
    ("en", "every week from now until june", "FREQ=WEEKLY;UNTIL=20270701T000000"),
    ("en", "every day from today until friday", "FREQ=DAILY;UNTIL=20261128T000000"),
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


# A rule with days of its own reads two weekdays joined by an until word that
# is no "to" word as a date range, not as a weekday set: UNTIL is the end of
# the right weekday.
@pytest.mark.parametrize("lang, text, rule", [
    ("en", "every friday from monday until friday",
     "FREQ=WEEKLY;UNTIL=20261128T000000;BYDAY=FR"),
    ("en", "every saturday from friday until sunday",
     "FREQ=WEEKLY;UNTIL=20261130T000000;BYDAY=SA"),
    ("en", "every weekday from monday until wednesday",
     "FREQ=WEEKLY;UNTIL=20261126T000000;BYDAY=MO,TU,WE,TH,FR"),
])
def test_a_rule_with_days_reads_two_weekdays_as_a_date_range(lang, text, rule):
    assert recurrence(lang, text) == (rule, "")


@pytest.mark.parametrize("lang, text, rule", [
    ("de", "jeden Freitag von Montag bis Freitag", "FREQ=WEEKLY;BYDAY=FR"),
    ("es", "cada viernes de lunes hasta viernes", "FREQ=WEEKLY;BYDAY=FR"),
    ("pt", "toda sexta-feira de segunda-feira até sexta-feira", "FREQ=WEEKLY;BYDAY=FR"),
    ("en", "every friday from mon until fri", "FREQ=WEEKLY;BYDAY=FR"),
    ("de", "jeden Werktag von Mo bis Mi", "FREQ=WEEKLY;BYDAY=MO,TU,WE"),
    ("nl", "elke werkdag van ma tot wo", "FREQ=WEEKLY;BYDAY=MO,TU,WE"),
])
def test_two_weekdays_that_no_date_reads_join_as_a_set_in_a_rule(lang, text, rule):
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


# The range reads a duration after it as part of its right bound, as a plain
# until bound does, so UNTIL is the end of August and no COUNT is set.
@pytest.mark.parametrize("lang, text, rule", [
    ("en", "every day from june until august for 5 weeks", DAILY + "20270901T000000"),
    ("en", "every monday from june until august for 3 months",
     WEEKLY + "20270901T000000;BYDAY=MO"),
    ("en", "every day from 3 june until 5 august for 5 weeks", DAILY + "20270806T000000"),
    ("pt", "todo dia de junho até agosto por 5 semanas", DAILY + "20270901T000000"),
    ("pt", "toda segunda de junho até agosto por 5 semanas",
     WEEKLY + "20270901T000000;BYDAY=MO"),
    ("es", "cada día de junio hasta agosto durante 5 semanas", DAILY + "20270901T000000"),
    ("de", "jeden Tag von Juni bis August für 5 Wochen", DAILY + "20270901T000000"),
    ("fr", "chaque jour de juin jusqu’à août pendant 5 semaines", DAILY + "20270901T000000"),
    ("nl", "elke dag van juni tot augustus gedurende 5 weken", DAILY + "20270901T000000"),
    ("nl", "elke maandag van juni tot augustus voor 5 weken",
     WEEKLY + "20270901T000000;BYDAY=MO"),
    ("ca", "cada dia de juny fins a agost durant 5 setmanes", DAILY + "20270901T000000"),
    ("gl", "cada día de xuño ata agosto durante 5 semanas", DAILY + "20270901T000000"),
])
def test_a_duration_after_a_range_sets_no_count(lang, text, rule):
    assert recurrence(lang, text) == (rule, "")


# UNTIL wins over a duration read before it: RFC 5545 allows one of the two.
@pytest.mark.parametrize("lang, text, rule", [
    ("en", "daily for 5 weeks from june until august", DAILY + "20270901T000000"),
    ("en", "every day for 5 weeks until june", DAILY + "20270601T000000"),
])
def test_an_until_bound_wins_over_a_duration_before_it(lang, text, rule):
    assert recurrence(lang, text) == (rule, "for 5 weeks")


# In "between A and B until C" the until word follows the right bound "B", so
# it is the rule's bound: UNTIL is the start of December 2026.
@pytest.mark.parametrize("lang, text, rule, remainder", [
    ("en", "every monday between june and august until december",
     WEEKLY + "20261201T000000;BYDAY=MO", "between june and august"),
    ("en", "every day between monday and friday until december",
     DAILY + "20261201T000000", "between monday and friday"),
    ("en", "every day between 3 june and 5 august until december",
     DAILY + "20261201T000000", "between 3 june and 5 august"),
    ("pt", "toda segunda entre junho e agosto até dezembro",
     WEEKLY + "20261201T000000;BYDAY=MO", "entre junho e agosto"),
    ("es", "cada lunes entre junio y agosto hasta diciembre",
     WEEKLY + "20261201T000000;BYDAY=MO", "entre junio y agosto"),
    ("de", "jeden Montag zwischen Juni und August bis Dezember",
     WEEKLY + "20261201T000000;BYDAY=MO", "zwischen Juni und August"),
    ("fr", "chaque lundi entre juin et août jusqu’à décembre",
     WEEKLY + "20261201T000000;BYDAY=MO", "entre juin et août"),
    ("it", "ogni lunedì tra giugno e agosto fino a dicembre",
     WEEKLY + "20261201T000000;BYDAY=MO", "tra giugno e agosto"),
    ("nl", "elke maandag tussen juni en augustus tot december",
     WEEKLY + "20261201T000000;BYDAY=MO", "tussen juni en augustus"),
    ("ca", "cada dilluns entre juny i agost fins a desembre",
     WEEKLY + "20261201T000000;BYDAY=MO", "entre juny i agost"),
    ("gl", "cada luns entre xuño e agosto ata decembro",
     WEEKLY + "20261201T000000;BYDAY=MO", "entre xuño e agosto"),
])
def test_an_until_word_after_a_between_range_is_the_rule_bound(lang, text, rule,
                                                               remainder):
    assert recurrence(lang, text) == (rule, remainder)


@pytest.mark.parametrize("lang, text, rule, remainder", [
    # "before christmas" is no left bound: UNTIL is 2026-12-25
    ("en", "every monday before christmas until december",
     WEEKLY + "20261225T000000;BYDAY=MO", ""),
    # a word between the rule and the range lead
    ("de", "jeden Monat Meeting von Montag bis Freitag",
     "FREQ=MONTHLY;BYDAY=MO,TU,WE,TH,FR", "Meeting"),
    ("de", "jeden Montag Meeting von Juni bis August", MONDAYS_TO_AUGUST, "Meeting"),
    # an until word that starts a longer "to" word of the locale
    ("nl", "elke dag van maandag tot en met vrijdag",
     "FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR", ""),
])
def test_the_range_starts_at_its_left_bound(lang, text, rule, remainder):
    assert recurrence(lang, text) == (rule, remainder)


@pytest.mark.parametrize("text, rule", [
    ("every friday until june", WEEKLY + "20270601T000000;BYDAY=FR"),
    ("every friday at 9 until june", WEEKLY + "20270601T000000;BYDAY=FR;BYHOUR=9"),
])
def test_an_until_word_after_the_rule_alone_runs_no_span_reading(monkeypatch, text,
                                                                 rule):
    def fail(*args, **kwargs):
        raise AssertionError("read() ran")
    monkeypatch.setattr(nseries, "read", fail)
    assert recurrence("en", text) == (rule, "")


# "until august" from 2026-11-22 is 2027-08-01; the clock sets the hour.  A
# right bound with a clock keeps the value of a plain until bound.
@pytest.mark.parametrize("lang, text, until", [
    ("es", "cada lunes desde junio hasta agosto a las 9", "2027-08-01T09:00:00"),
    ("es", "todos los lunes de junio hasta agosto a las 9", "2027-08-01T09:00:00"),
    ("es", "cada lunes desde junio hasta agosto a la una", "2027-08-01T01:00:00"),
    ("es", "cada lunes desde junio hasta agosto a mediodía", "2027-08-01T12:00:00"),
    ("fr", "chaque lundi de juin jusqu'à août à 9h", "2027-08-01T09:00:00"),
    ("fr", "tous les jours du 3 juin jusqu'au 5 août à 8h", "2027-08-05T08:00:00"),
    ("fr", "tous les jours de juin jusqu'en août à 8 heures", "2027-08-01T08:00:00"),
    ("ca", "cada dilluns de juny fins a agost a les 9", "2027-08-01T09:00:00"),
    ("ca", "cada dilluns de juny fins a agost al migdia", "2027-08-01T12:00:00"),
    ("it", "ogni lunedì da giugno fino a agosto a mezzogiorno",
     "2027-08-01T12:00:00"),
    ("pt", "todos os dias de junho até agosto ao meio-dia", "2027-08-01T12:00:00"),
    ("en", "every monday from june until august at 9", "2027-08-01T09:00:00"),
])
def test_a_clock_after_a_month_range_is_not_its_right_bound(lang, text, until):
    got = extract_recurrence(text, lang, ANCHOR)
    assert (got.recurrence.until.isoformat(), got.remainder) == (until, "")
