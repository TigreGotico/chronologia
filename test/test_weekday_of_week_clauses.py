# -*- coding: utf-8 -*-
"""A weekday and a relative week in different clauses are two mentions.

"friday, next week is busy" names Friday and, separately, next week; it does
not name the Friday of next week.  Gold days come from the Monday 2026-10-19
anchor by hand: the coming Friday is 2026-10-23 and next week is the seven
days from Monday 2026-10-26.
"""
from datetime import date, datetime

import pytest

from chronologia import extract_timespan, extract_timespans

ANCHOR = datetime(2026, 10, 19, 10, 0)
FRIDAY = (date(2026, 10, 23), 1)
NEXT_WEEK = (date(2026, 10, 26), 7)

CASES = [
    ("en", "I'll call you on friday, next week is busy", [FRIDAY, NEXT_WEEK]),
    ("en", "the report is due friday, next week we review it", [FRIDAY, NEXT_WEEK]),
    ("en", "friday. next week we start", [FRIDAY, NEXT_WEEK]),
    ("en", "friday; next week we start", [FRIDAY, NEXT_WEEK]),
    ("en", "on friday? next week works too", [FRIDAY, NEXT_WEEK]),
    ("en", "Friday: next week planning", [FRIDAY, NEXT_WEEK]),
    ("en", "we are off next week, friday we are back", [NEXT_WEEK, FRIDAY]),
    ("en", "next week, friday is a holiday", [NEXT_WEEK, FRIDAY]),
    ("es", "nos vemos el viernes, la semana que viene empieza el curso",
     [FRIDAY, NEXT_WEEK]),
    ("pt", "vemo-nos na sexta, a próxima semana começa o curso",
     [FRIDAY, NEXT_WEEK]),
    ("de", "wir sehen uns Freitag, nächste Woche beginnt der Kurs",
     [FRIDAY, NEXT_WEEK]),
    ("en", "friday\u2026 next week we start", [FRIDAY, NEXT_WEEK]),
    ("el", "Παρασκευή· την επόμενη εβδομάδα ξεκινάμε", [FRIDAY, NEXT_WEEK]),
    ("en", "see you friday, the following week we start", [FRIDAY, NEXT_WEEK]),
]

# Arabic weeks start on Saturday: next week is 2026-10-24 .. 2026-10-31.
AR_NEXT_WEEK = (date(2026, 10, 24), 7)
AR_CASES = [
    "الجمعة\u060c الأسبوع القادم نبدأ",
    "نلتقي الجمعة\u061f الأسبوع القادم مشغول",
]
AR_MULTIWORD = [
    "الأسبوع القادم, يوم الجمعة عطلة",
    "الأسبوع القادم\u060c يوم الجمعة عطلة",
]


@pytest.mark.parametrize("lang,text,want", CASES)
def test_clause_break_keeps_two_mentions(lang, text, want):
    got = [(m.span.start_datetime.date(), (m.span.end - m.span.start).days)
           for m in extract_timespans(text, lang, ANCHOR)]
    assert got == want


def test_single_span_does_not_fuse_across_a_comma():
    result = extract_timespan("friday, next week is busy", "en", ANCHOR)
    assert result.span.start_datetime.date() == date(2026, 10, 23)
    assert "next week" in result.remainder


@pytest.mark.parametrize("text", ["friday of next week", "friday next week",
                                  "next week friday"])
def test_without_punctuation_the_days_still_join(text):
    result = extract_timespan(text, "en", ANCHOR)
    assert result.span.start_datetime.date() == date(2026, 10, 30)
    assert result.remainder == ""


@pytest.mark.parametrize("text", AR_CASES)
def test_arabic_punctuation_keeps_two_mentions(text):
    got = [(m.span.start_datetime.date(), (m.span.end - m.span.start).days)
           for m in extract_timespans(text, "ar", ANCHOR)]
    assert got == [FRIDAY, AR_NEXT_WEEK]


@pytest.mark.parametrize("text", AR_MULTIWORD)
def test_break_before_a_multiword_token_is_kept(text):
    got = [(m.span.start_datetime.date(), (m.span.end - m.span.start).days)
           for m in extract_timespans(text, "ar", ANCHOR)]
    assert AR_NEXT_WEEK in got
    assert FRIDAY in got
    assert all(day != date(2026, 10, 30) for day, _ in got)
