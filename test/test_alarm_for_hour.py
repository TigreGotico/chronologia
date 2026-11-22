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
    ("espertador para 7", "gl", datetime(2026, 11, 17, 19, 0)),
    ("alarm for seven thirty", "en", datetime(2026, 11, 17, 19, 30)),
    ("alarm for 7 thirty", "en", datetime(2026, 11, 17, 19, 30)),
    ("alarm for 7 30", "en", datetime(2026, 11, 17, 19, 30)),
    ("alarm for 7 30 am", "en", datetime(2026, 11, 18, 7, 30)),
    ("alarme para 7 e meia", "pt", datetime(2026, 11, 17, 19, 30)),
    ("alarma para 7 y media", "es", datetime(2026, 11, 17, 19, 30)),
    ("sveglia per 7 e mezza", "it", datetime(2026, 11, 17, 19, 30)),
    ("alarm for 20 to 8", "en", datetime(2026, 11, 17, 19, 40)),
    ("set an alarm for 5 to 7", "en", datetime(2026, 11, 17, 18, 55)),
    ("alarm for 10 to 7", "en", datetime(2026, 11, 17, 18, 50)),
    ("alarm for 10 to 11", "en", datetime(2026, 11, 17, 10, 50)),
    ("reminder for 10 to 11", "en", datetime(2026, 11, 17, 10, 50)),
    ("alarm for 7 till 8", "en", datetime(2026, 11, 17, 19, 53)),
    ("alarms for 7 and 8 pm", "en", datetime(2026, 11, 17, 20, 0)),
    ("alarm for 7 or 8 pm", "en", datetime(2026, 11, 17, 20, 0)),
    ("alarme para 7 às 8 da noite", "pt", datetime(2026, 11, 17, 20, 0)),
    ("alarma para 7 a 8 de la noche", "es", datetime(2026, 11, 17, 20, 0)),
    ("alarm for 7 and 8 in the morning", "en", datetime(2026, 11, 17, 8, 0)),
    ("set an alarm for 6 or 7 pm tomorrow", "en",
     datetime(2026, 11, 18, 19, 0)),
    ("reminder for 10 to noon", "en", datetime(2026, 11, 17, 11, 50)),
    ("reminder for 7 to midnight", "en", datetime(2026, 11, 17, 23, 53)),
    ("set an alarm for 7 tomorrow morning", "en",
     datetime(2026, 11, 18, 7, 0)),
    ("alarm for 7 tomorrow morning", "en", datetime(2026, 11, 18, 7, 0)),
    ("alarm for 7 on friday morning", "en", datetime(2026, 11, 20, 7, 0)),
    ("alarm for 9 on monday morning", "en", datetime(2026, 11, 23, 9, 0)),
    ("reminder for 9 tomorrow morning", "en", datetime(2026, 11, 18, 9, 0)),
    ("wake-up call for 6 tomorrow morning", "en",
     datetime(2026, 11, 18, 6, 0)),
    ("set a reminder for 8 tomorrow morning to call bob", "en",
     datetime(2026, 11, 18, 8, 0)),
    ("alarme para 7 amanhã de manhã", "pt", datetime(2026, 11, 18, 7, 0)),
    ("alarme para 6 amanhã de manhã", "pt", datetime(2026, 11, 18, 6, 0)),
    ("alarme para 7 na segunda de manhã", "pt", datetime(2026, 11, 23, 7, 0)),
    ("despertador para 6 el lunes por la mañana", "es",
     datetime(2026, 11, 23, 6, 0)),
    ("réveil pour 7 demain matin", "fr", datetime(2026, 11, 18, 7, 0)),
    ("réveil pour 6 demain matin", "fr", datetime(2026, 11, 18, 6, 0)),
    ("alarme pour 7 lundi matin", "fr", datetime(2026, 11, 23, 7, 0)),
    ("sveglia per 7 domani mattina", "it", datetime(2026, 11, 18, 7, 0)),
    ("sveglia per 7 lunedì mattina", "it", datetime(2026, 11, 23, 7, 0)),
    ("wekker voor 7 morgenochtend", "nl", datetime(2026, 11, 18, 7, 0)),
    ("wekker voor 7 maandagochtend", "nl", datetime(2026, 11, 23, 7, 0)),
    ("wekker voor 7 morgen in de ochtend", "nl",
     datetime(2026, 11, 18, 7, 0)),
    ("alarm for 7 and call mum in the evening", "en",
     datetime(2026, 11, 18, 7, 0)),
    ("reminder for 9 about the party tonight", "en",
     datetime(2026, 11, 17, 9, 0)),
    ("alarm for 7 then a meeting at 3 pm", "en", datetime(2026, 11, 18, 7, 0)),
    ("alarm for 7 and dinner at 8 pm", "en", datetime(2026, 11, 18, 7, 0)),
    ("alarm for 7 and remind me at 8 pm", "en", datetime(2026, 11, 18, 7, 0)),
    ("alarm for 7, dinner at 8 pm", "en", datetime(2026, 11, 18, 7, 0)),
    ("alarm for 7. Meeting at 3 pm", "en", datetime(2026, 11, 18, 7, 0)),
    ("alarm for 7. Tonight I sleep", "en", datetime(2026, 11, 18, 7, 0)),
    ("alarm for 7. Or 8 pm", "en", datetime(2026, 11, 18, 7, 0)),
    ("alarm for 7 and 8 then I go for a run in the morning", "en",
     datetime(2026, 11, 18, 7, 0)),
    ("alarm for 7 and 8. In the morning I run", "en",
     datetime(2026, 11, 18, 7, 0)),
    ("alarm for 7 and 8 tomorrow morning", "en",
     datetime(2026, 11, 18, 7, 0)),
    ("alarme para 7 ou 8 amanhã de manhã", "pt",
     datetime(2026, 11, 18, 7, 0)),
    ("réveil pour 7 ou 8 demain matin", "fr", datetime(2026, 11, 18, 7, 0)),
    ("sveglia per 7 o 8 domani mattina", "it", datetime(2026, 11, 18, 7, 0)),
    ("alarma para 7 o 8 mañana por la mañana", "es",
     datetime(2026, 11, 18, 7, 0)),
    ("reminder for 9 about 2 pm meeting", "en",
     datetime(2026, 11, 17, 9, 0)),
    ("alarm for 5 for 8 am flight", "en", datetime(2026, 11, 18, 5, 0)),
    ("alarma para 7 o 8 de la mañana", "es", datetime(2026, 11, 17, 8, 0)),
    ("alarm for 7 and 8 on monday evening", "en",
     datetime(2026, 11, 18, 7, 0)),
    ("alarm for 7 then 9 am meeting", "en", datetime(2026, 11, 18, 7, 0)),
    ("reminder for 9 then 3 pm meeting", "en", datetime(2026, 11, 17, 9, 0)),
    ("wekker voor 7 of 8 uur 's avonds", "nl", datetime(2026, 11, 17, 20, 0)),
]

NO_CLOCK = [
    ("a table for 4", "en"),
    ("wait for 10", "en"),
    ("for 10 minutes", "en"),
    ("alarm for 10 minutes", "en"),
    ("alarm for 2 hours", "en"),
    ("alarm for 7 30 minutes", "en"),
    ("alarm for 1 30 hours", "en"),
    ("alarm for 2 hrs", "en"),
    ("alarm for 2 hr", "en"),
    ("alarm for 10 more minutes", "en"),
    ("snooze the alarm for 10 more minutes", "en"),
    ("alarm for 10 extra minutes", "en"),
    ("alarm for 10 to 15 minutes", "en"),
    ("alarm for 10 through 15 min", "en"),
    ("alarme para 10 min", "pt"),
    ("alarma para 10 min", "es"),
    ("uma mesa para 4", "pt"),
    ("espera para 10", "pt"),
    ("alarme para 10 minutos", "pt"),
    ("mesa para 4", "es"),
    ("alarma para 10 minutos", "es"),
    ("table pour 4", "fr"),
    ("Tisch für 4", "de"),
    ("tavolo per 4", "it"),
    ("tafel voor 4", "nl"),
    ("mesa para 4", "gl"),
]


# text, language, first instant, end (one minute past the last instant read)
RANGES = [
    ("set a reminder for 3 to 5 pm", "en",
     datetime(2026, 11, 17, 15, 0), datetime(2026, 11, 17, 17, 1)),
    ("reminder for 2 to 4 pm", "en",
     datetime(2026, 11, 17, 14, 0), datetime(2026, 11, 17, 16, 1)),
    ("reminder for 1 to 3 pm tomorrow", "en",
     datetime(2026, 11, 18, 13, 0), datetime(2026, 11, 18, 15, 1)),
    ("reminder for 10 am to noon", "en",
     datetime(2026, 11, 17, 10, 0), datetime(2026, 11, 17, 12, 1)),
    ("set a reminder for 9 am to 10 am", "en",
     datetime(2026, 11, 17, 9, 0), datetime(2026, 11, 17, 10, 1)),
    ("reminder for 3 pm to 5 pm", "en",
     datetime(2026, 11, 17, 15, 0), datetime(2026, 11, 17, 17, 1)),
    ("reminder for tuesday to thursday", "en",
     datetime(2026, 11, 17), datetime(2026, 11, 20)),
    ("set a reminder for next monday to friday", "en",
     datetime(2026, 11, 23), datetime(2026, 11, 28)),
    ("alarma para las 7 hasta las 8", "es",
     datetime(2026, 11, 18, 7, 0), datetime(2026, 11, 18, 8, 1)),
]


@pytest.mark.parametrize("text,lang,start,end", RANGES)
def test_an_explicit_range_after_an_alarm_noun_stays_a_range(text, lang,
                                                             start, end):
    found = extract_timespan(text, lang, ANCHOR)
    assert found.span.start.datetime() == start
    assert found.span.end.datetime() == end


@pytest.mark.parametrize("text,lang,expected", CLOCKS)
def test_an_alarm_noun_makes_the_bare_hour_a_clock(text, lang, expected):
    found = extract_timespan(text, lang, ANCHOR)
    assert found.span.start.datetime() == expected
    assert found.span.end.datetime() == datetime(
        expected.year, expected.month, expected.day, expected.hour,
        expected.minute + 1)


@pytest.mark.parametrize("text,lang", [
    ("wecker für 7 oder 8 uhr abends", "de"),
    ("wecker für 7 bzw. 8 uhr abends", "de"),
    ("wecker für 7 beziehungsweise 8 uhr abends", "de"),
    ("espertador para 7 ou 8 da tarde", "gl"),
    ("sveglia per 7 oppure 8 di sera", "it"),
])
def test_each_locale_joiner_shares_the_later_meridiem(text, lang):
    found = extract_timespan(text, lang, ANCHOR)
    assert found.span.start.datetime() == datetime(2026, 11, 17, 20, 0)
    assert found.span.end.datetime() == datetime(2026, 11, 17, 20, 1)


@pytest.mark.xfail(
    strict=True, reason="https://github.com/TigreGotico/chronologia/issues/1058")
def test_nl_joiner_shares_the_later_meridiem_without_uur():
    found = extract_timespan("wekker voor 7 of 8 's avonds", "nl", ANCHOR)
    assert found is not None
    assert found.span.start.datetime() == datetime(2026, 11, 17, 20, 0)


@pytest.mark.parametrize("text,remainder", [
    ("alarm for 7 pm tomorrow evening", "evening"),
    ("alarm for 7 pm and a call in the evening",
     "and a call in the evening"),
    ("alarm for 7 pm and 8 am", "and 8 am"),
])
def test_a_meridiem_hour_keeps_the_alarm_noun_in_the_reading(text, remainder):
    assert extract_timespan(text, "en", ANCHOR).remainder == remainder


@pytest.mark.xfail(
    strict=True, reason="https://github.com/TigreGotico/chronologia/issues/1058")
def test_alarm_for_seven_tonight_reads_seven_in_the_evening():
    found = extract_timespan("alarm for 7 tonight", "en", ANCHOR)
    assert found.span.start.datetime() == datetime(2026, 11, 17, 19, 0)


@pytest.mark.parametrize("text,lang", NO_CLOCK)
def test_any_other_for_number_is_no_clock(text, lang):
    assert extract_timespan(text, lang, ANCHOR) is None


@pytest.mark.parametrize("text,lang", [
    ("réveil pour 7 et demie", "fr"),
])
def test_minutes_the_order_cannot_read_leave_no_clock(text, lang):
    assert extract_timespan(text, lang, ANCHOR) is None


@pytest.mark.parametrize("text,lang,rule", [
    ("create an alarm for 10 daily", "en", "FREQ=DAILY;BYHOUR=10"),
    ("alarme para 10 todos os dias", "pt", "FREQ=DAILY;BYHOUR=10"),
    ("alarma para 10 todos los días", "es", "FREQ=DAILY;BYHOUR=10"),
])
def test_the_alarm_hour_pins_the_daily_recurrence(text, lang, rule):
    found = extract_recurrence(text, lang, anchor=ANCHOR)
    assert found[0].to_string() == rule
