"""An "until" word is a range word when the span reading of the text covers it.

Anchor 2026-11-22, a Sunday.  "june" and "august" name the next ones, so a
rule that ends with August stops at 2027-08-01 and a range from monday to
wednesday reads 2026-11-23 up to 2026-11-26.
"""
from datetime import datetime

import pytest

from chronologia import extract_recurrence, extract_timespan
from chronologia.extract import nseries
from chronologia.extract.reading import read

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


@pytest.mark.parametrize("lang, text, rule", [
    ("en", "every week from now until june", "FREQ=WEEKLY;UNTIL=20270601T000000"),
    ("en", "every day from today until friday", "FREQ=DAILY;UNTIL=20261127T000000"),
    ("en", "every day from june until august 5 times",
     "FREQ=DAILY;UNTIL=20270805T000000"),
])
def test_a_range_word_reads_the_bounds_the_span_reading_names(lang, text, rule):
    assert recurrence(lang, text) == (rule, "")


@pytest.mark.parametrize("lang, text, rule", [
    ("de", "jeden Tag von Montag bis Freitag bis Dezember",
     "FREQ=DAILY;UNTIL=20261201T000000;BYDAY=MO,TU,WE,TH,FR"),
    ("nl", "elke dag van maandag tot vrijdag tot december",
     "FREQ=DAILY;UNTIL=20261201T000000;BYDAY=MO,TU,WE,TH,FR"),
    ("en", "every weekday from monday until wednesday",
     "FREQ=WEEKLY;BYDAY=MO,TU,WE"),
])
def test_the_range_word_of_a_weekday_set_is_not_an_until_bound(lang, text, rule):
    assert recurrence(lang, text) == (rule, "")


@pytest.mark.parametrize("lang, text, end, remainder", [
    ("de", "jeden Werktag von Mo bis Mi", datetime(2026, 11, 26), "jeden Werktag"),
    ("nl", "elke werkdag van ma tot wo", datetime(2026, 11, 26), "elke werkdag"),
    ("de", "jeden Tag von Mo bis Fr", datetime(2026, 11, 28), "jeden Tag"),
    ("de", "jeden Freitag von Montag bis Freitag", datetime(2026, 11, 28), "jeden Freitag"),
])
def test_a_particle_before_a_bare_weekday_leads_the_range(lang, text, end, remainder):
    got = extract_timespan(text, lang, ANCHOR)
    assert got.span.start_datetime == datetime(2026, 11, 23)
    assert got.span.end_datetime == end
    assert got.remainder == remainder


@pytest.mark.parametrize("lang, text", [
    ("de", "jeden Freitag von Montag bis Freitag"),
    ("nl", "elke vrijdag van maandag tot vrijdag"),
    ("es", "cada viernes de lunes hasta viernes"),
    ("pt", "toda sexta-feira de segunda-feira até sexta-feira"),
])
def test_a_rule_weekday_inside_a_weekday_range_keeps_its_set(lang, text):
    assert recurrence(lang, text) == ("FREQ=WEEKLY;BYDAY=FR", "")


@pytest.mark.parametrize("lang, text, rule", [
    ("pt", "do dia 3 até à última sexta-feira do mês",
     "FREQ=MONTHLY;UNTIL=20261203T000000;BYDAY=-1FR"),
    ("pt", "todos os meses do dia 3 até à terceira terça-feira do mês",
     "FREQ=MONTHLY;UNTIL=20261203T000000;BYDAY=3TU"),
])
def test_a_rule_that_holds_the_right_bound_keeps_the_until_bound(lang, text, rule):
    assert recurrence(lang, text) == (rule, "")


@pytest.mark.parametrize("lang, text, rule, remainder", [
    ("en", "every monday from 9am until 5 december",
     "FREQ=WEEKLY;UNTIL=20261205T000000;BYDAY=MO;BYHOUR=9", "from"),
    ("de", "jeden Tag von 9 Uhr bis 5. Dezember",
     "FREQ=DAILY;UNTIL=20261205T000000;BYHOUR=9", "von"),
])
def test_the_clock_of_the_rule_holds_the_left_bound(lang, text, rule, remainder):
    assert recurrence(lang, text) == (rule, remainder)


def test_a_particle_before_a_weekday_and_an_hour_is_no_range():
    got = extract_timespan("una hora antes del lunes a las 9", "es", ANCHOR)
    assert got.span.start_datetime == datetime(2026, 11, 23, 8, 0)


def test_until_before_a_holiday_is_no_closed_range():
    spans = [r for r in read("from monday until before christmas", "en", ANCHOR)
             if r.kind == "span"]
    assert spans == []


def test_a_text_without_an_until_word_runs_no_span_reading(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("read() ran")
    monkeypatch.setattr(nseries, "read", fail)
    assert recurrence("en", "every monday from june to august at 9am")[1] == ""
