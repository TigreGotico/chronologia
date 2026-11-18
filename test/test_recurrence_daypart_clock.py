# -*- coding: utf-8 -*-
"""A part of the day before a clock names a rule when it recurs.

The plural of a part of the day is an adverb for a regular time of day
(Wiktionary s.v. "mornings"), and "every morning" is a rule by its determiner.
So "mornings at 8" and "every morning at 8" are ``FREQ=DAILY;BYHOUR=8``, and a
"weekday" before the part of the day limits the rule to Monday to Friday (RFC
5545 section 3.3.10: BYHOUR is an hour of the day).  The part of the day
supplies the half of the day of a bare hour, as for a single time.  A single
part of the day ("morning at 8") is one time, not a rule.

Every expected rule is written by hand from RFC 5545.
"""
import pytest

from chronologia import extract_recurrence

WEEKDAYS = "FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR"

CASES = [
    ("every weekday morning at 8", "en", WEEKDAYS + ";BYHOUR=8"),
    ("weekday mornings at 8", "en", WEEKDAYS + ";BYHOUR=8"),
    ("mornings at 8", "en", "FREQ=DAILY;BYHOUR=8"),
    ("every morning at 8", "en", "FREQ=DAILY;BYHOUR=8"),
    ("todas as manhãs às 8", "pt", "FREQ=DAILY;BYHOUR=8"),
    ("nas manhãs às 8", "pt", "FREQ=DAILY;BYHOUR=8"),
    ("every morning at 9:30", "en", "FREQ=DAILY;BYHOUR=9;BYMINUTE=30"),
    ("every evening at 8", "en", "FREQ=DAILY;BYHOUR=20"),
    ("every weekday evening at 8", "en", WEEKDAYS + ";BYHOUR=20"),
    ("every morning at 8 for 2 weeks", "en", "FREQ=DAILY;COUNT=14;BYHOUR=8"),
]


@pytest.mark.parametrize("text,lang,rule", CASES)
def test_a_recurring_part_of_the_day_with_a_clock(text, lang, rule):
    found = extract_recurrence(text, lang)
    assert found is not None
    assert found.recurrence.to_string() == rule
    assert found.remainder == ""


@pytest.mark.parametrize("text,lang", [
    ("morning at 8", "en"),
    ("every morning", "en"),
    ("every morning at 9pm", "en"),
    ("three mornings at 8", "en"),
])
def test_no_rule_without_a_recurring_part_of_the_day_and_a_fitting_clock(
        text, lang):
    assert extract_recurrence(text, lang) is None
