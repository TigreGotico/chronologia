# -*- coding: utf-8 -*-
"""A bare hour after "for" is a clock only behind an alarm or reminder noun.

"an alarm for 7" and "a reminder for 9" name a time of day, and the hour takes
the next of its two twelve-hour readings (ruling 17).  "a table for 4", "wait
for 10" and "for 10 minutes" name no time, and "alarm for 10 minutes" is a
length.  The nouns are listed per locale in ``marker_alarm_at.voc``.

Every expected instant is worked out by hand from the anchor, Tuesday
2026-11-17 08:00: 10 comes at 10:00, 9 at 09:00, and 7 has passed so it is the
evening reading, 19:00.
"""
from datetime import datetime

import pytest

from chronologia import extract_recurrence, extract_timespan

ANCHOR = datetime(2026, 11, 17, 8, 0)

# text, language, expected instant
CLOCKS = [
    ("create an alarm for 10 daily", "en", datetime(2026, 11, 17, 10, 0)),
    ("set an alarm for 7", "en", datetime(2026, 11, 17, 19, 0)),
    ("reminder for 9", "en", datetime(2026, 11, 17, 9, 0)),
    ("set two alarms for 7", "en", datetime(2026, 11, 17, 19, 0)),
    ("wake-up call for 6", "en", datetime(2026, 11, 17, 18, 0)),
    ("wakeup call for 6", "en", datetime(2026, 11, 17, 18, 0)),
    ("alarm for 10 pm", "en", datetime(2026, 11, 17, 22, 0)),
    ("alarme para 10 todos os dias", "pt", datetime(2026, 11, 17, 10, 0)),
    ("despertador para 7", "pt", datetime(2026, 11, 17, 19, 0)),
    ("alarma para 10 todos los días", "es", datetime(2026, 11, 17, 10, 0)),
    ("despertador para 7", "es", datetime(2026, 11, 17, 19, 0)),
    ("réveil pour 7", "fr", datetime(2026, 11, 17, 19, 0)),
    ("Wecker für 9", "de", datetime(2026, 11, 17, 9, 0)),
    ("sveglia per 7", "it", datetime(2026, 11, 17, 19, 0)),
    ("wekker voor 7", "nl", datetime(2026, 11, 17, 19, 0)),
    ("despertador per 7", "ca", datetime(2026, 11, 17, 19, 0)),
    ("espertador para 7", "gl", datetime(2026, 11, 17, 19, 0)),
]

NO_CLOCK = [
    ("a table for 4", "en"),
    ("wait for 10", "en"),
    ("for 10 minutes", "en"),
    ("alarm for 10 minutes", "en"),
    ("alarm for 2 hours", "en"),
    ("uma mesa para 4", "pt"),
    ("espera para 10", "pt"),
    ("alarme para 10 minutos", "pt"),
    ("mesa para 4", "es"),
    ("alarma para 10 minutos", "es"),
    ("table pour 4", "fr"),
    ("Tisch für 4", "de"),
    ("tavolo per 4", "it"),
    ("tafel voor 4", "nl"),
    ("taula per 4", "ca"),
    ("mesa para 4", "gl"),
]


@pytest.mark.parametrize("text,lang,expected", CLOCKS)
def test_an_alarm_noun_makes_the_bare_hour_a_clock(text, lang, expected):
    found = extract_timespan(text, lang, ANCHOR)
    assert found.span.start.datetime() == expected
    assert found.span.end.datetime() == datetime(
        expected.year, expected.month, expected.day, expected.hour,
        expected.minute + 1)


@pytest.mark.parametrize("text,lang", NO_CLOCK)
def test_any_other_for_number_is_no_clock(text, lang):
    assert extract_timespan(text, lang, ANCHOR) is None


@pytest.mark.parametrize("text,lang,rule", [
    ("create an alarm for 10 daily", "en", "FREQ=DAILY;BYHOUR=10"),
    ("alarme para 10 todos os dias", "pt", "FREQ=DAILY;BYHOUR=10"),
    ("alarma para 10 todos los días", "es", "FREQ=DAILY;BYHOUR=10"),
])
def test_the_alarm_hour_pins_the_daily_recurrence(text, lang, rule):
    found = extract_recurrence(text, lang, anchor=ANCHOR)
    assert found[0].to_string() == rule
