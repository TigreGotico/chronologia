# -*- coding: utf-8 -*-
"""Kabyle offsets, relative units and weekdays, from attested sentences.

Every sentence is a Kabyle sentence on Tatoeba (id given), or a phrase built
only from the preposition table of the English Wikipedia "Kabyle grammar"
article (oldid 1383353682).  Gold is calendar arithmetic from the anchor,
Tuesday 2017-06-27 13:04.
"""
from datetime import datetime, timedelta

import pytest
from dateutil.relativedelta import relativedelta

from chronologia import extract_duration, extract_timespan

from ._corpus import ANCHOR, LANG, span

A = ANCHOR
TODAY = datetime(A.year, A.month, A.day)
# Monday of the anchor week.
WEEK0 = TODAY - timedelta(days=A.weekday())


def _day(d):
    return (d.year, d.month, d.day)


@pytest.mark.parametrize("text,delta", [
    # 8691123 -- "We'll be back in three months."
    ("Ad d-nuɣal deg kraḍ n wayyuren.", relativedelta(months=3)),
    # 11266136 -- "The train is leaving in three minutes."
    ("Ad teffeɣ tmacint sya tlata n dqayeq.", relativedelta(minutes=3)),
    # 11663983 "deg sin n wussan" (in two days)
    ("Ad d-nuɣal deg sin n wussan.", relativedelta(days=2)),
])
def test_future_offset(text, delta):
    exp = A + delta
    s = span(text).start
    assert (s.year, s.month, s.day, s.hour, s.minute) == (
        exp.year, exp.month, exp.day, exp.hour, exp.minute)


def test_numeral_without_genitive_is_not_an_offset():
    # The counted noun follows the numeral in the genitive ("sin n
    # yirgazen"); "deg yiwen wass n tegrest" is the narrative "one winter day".
    assert extract_timespan("Deg yiwen wass n tegrest, nekker-d zik.",
                            LANG, A) is None


@pytest.mark.parametrize("text,weeks", [
    ("Ad ruḥeɣ imalas i d-iteddun.", 1),          # 9724592 "I am leaving next week."
    ("Ad ruḥeɣ ddurt i d-iteddun.", 1),           # 8214457 "I'm leaving next week."
    ("Yella-d imalas yezrin.", -1),               # 13715297 "It was last week."
])
def test_relative_week(text, weeks):
    s = span(text)
    exp = WEEK0 + timedelta(weeks=weeks)
    assert (_day(s.start), _day(s.end)) == (_day(exp), _day(exp + timedelta(days=7)))


def test_last_year():
    # 11412451 "Myussanen aseggas yezrin." (they met last year)
    s = span("Myussanen aseggas yezrin.")
    assert (_day(s.start), _day(s.end)) == ((A.year - 1, 1, 1), (A.year, 1, 1))


@pytest.mark.parametrize("text,weekday", [
    ("Neɣcent-iyi-tt Letnayen yezrin.", 0),       # 9170507
    ("Tenɣec-asent-t Lexmis yezrin.", 3),         # 9170490
    ("Yebda wahil lǧemɛa yezrin.", 4),            # 11311983
])
def test_last_weekday(text, weekday):
    back = (A.weekday() - weekday) % 7 or 7
    assert _day(span(text).start) == _day(TODAY - timedelta(days=back))


def test_weekday_range_seg_ar():
    # "seg" = from, "ar" = until (Kabyle grammar, preposition table).
    s = span("seg letnayen ar lexmis")
    mon = WEEK0 + timedelta(weeks=1)
    assert (_day(s.start), _day(s.end)) == (_day(mon), _day(mon + timedelta(days=4)))


@pytest.mark.parametrize("text,seconds", [
    ("Nerǧa ɛecra n tesdatin.", 600),             # 9810719 "We waited ten minutes."
    ("Mazal ɛecra n dqayeq.", 600),               # 12007743 "Ten minutes are left."
    ("Ṭṭseɣ 9 n yisragen.", 9 * 3600),            # 13760239 "I slept nine hours."
])
def test_duration_units(text, seconds):
    r = extract_duration(text, LANG)
    assert r is not None and int(r.duration.total_seconds()) == seconds
