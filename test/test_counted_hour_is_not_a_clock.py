# -*- coding: utf-8 -*-
"""A number after a clock preposition that counts the next word is no hour.

"a las 3 vecinas" (three neighbours) and "look at 5 houses" read a time of day
at 03:00 and 05:00 and took the place of the date beside them.  A bare hour
followed by an ordinary word stays a candidate at a low confidence, below the
date-only reading, and it is not the parse winner.  A word of the date
grammar, a courtesy phrase or a punctuation break after the hour keeps the
clock.

Anchor: Friday 2026-09-25 12:00, so "tomorrow" is Saturday 2026-09-26.  Every
expected value is the calendar day or the spoken hour, written by hand.
"""
from dataclasses import replace
from datetime import datetime

import pytest

from chronologia import extract_candidates, extract_timespan, extract_timespans
from chronologia.extract.confidence import confidence
from chronologia.extract.timespan import _timespan_engine

ANCHOR = datetime(2026, 9, 25, 12, 0)
TOMORROW = datetime(2026, 9, 26)

# text, language, remainder of the date-only reading
COUNTS_WITH_DATE = [
    ("recuérdame llamar a las 3 vecinas mañana", "es",
     "recuérdame llamar a las 3 vecinas"),
    ("look at 5 houses tomorrow", "en", "look at 5 houses"),
    ("wave at 5 people tomorrow", "en", "wave at 5 people"),
    ("llama a las 4 vecinas mañana", "es", "llama a las 4 vecinas"),
    ("amanhã liga às 3 vizinhas", "pt", "liga às 3 vizinhas"),
    ("digues-ho a les 3 noies demà", "ca", "digues-ho a les 3 noies"),
    ("dillo alle due ragazze domani", "it", "dillo alle due ragazze"),
    ("demain à 8 personnes", "fr", "à 8 personnes"),
    ("morgen om 3 mensen", "nl", "om 3 mensen"),
    ("morgen um 3 Euro", "de", "um 3 Euro"),
]

COUNTS_ALONE = [
    ("a las 5 personas", "es"),
    ("wave at 5 people", "en"),
    ("ás 2 rapazas", "gl"),
    ("a les 3 noies", "ca"),
    ("om 5 euro", "nl"),
    ("om 8 en 9 kinderen", "nl"),
    ("om 8 of 9 mensen", "nl"),
]

# text, language, expected instant
CLOCKS = [
    ("mañana a las 8 por favor", "es", datetime(2026, 9, 26, 8)),
    ("a las 8 gracias", "es", datetime(2026, 9, 26, 8)),
    ("ás 8 por favor", "gl", datetime(2026, 9, 26, 8)),
    ("demà a les 8 si us plau", "ca", datetime(2026, 9, 26, 8)),
    ("a les 8 gracies", "ast", datetime(2026, 9, 26, 8)),
    ("às oito por favor", "pt", datetime(2026, 9, 26, 8)),
    ("alle otto per favore", "it", datetime(2026, 9, 26, 8)),
    ("wake me at 8 please", "en", datetime(2026, 9, 26, 8)),
    ("tomorrow at 8 please", "en", datetime(2026, 9, 26, 8)),
    ("at 8, wave at the people", "en", datetime(2026, 9, 26, 8)),
    ("a las 8 mañana", "es", datetime(2026, 9, 26, 8)),
    ("at 8 tomorrow", "en", datetime(2026, 9, 26, 8)),
    ("at 8 monday", "en", datetime(2026, 9, 28, 8)),
    ("hacia las 8 llegamos", "es", datetime(2026, 9, 26, 8)),
    ("a las 8 horas", "es", datetime(2026, 9, 26, 8)),
    ("um 8 bitte", "de", datetime(2026, 9, 26, 8)),
    ("let's meet next tuesday evening at 9 downtown", "en",
     datetime(2026, 9, 29, 21)),
]


def start(found):
    return found.span.start.datetime()


@pytest.mark.parametrize("text,lang,remainder", COUNTS_WITH_DATE)
def test_count_leaves_the_date_alone(text, lang, remainder):
    found = extract_timespan(text, lang, ANCHOR)
    assert start(found) == TOMORROW
    assert found.span.end.datetime() == datetime(2026, 9, 27)
    assert found.remainder == remainder


@pytest.mark.parametrize("text,lang", COUNTS_ALONE)
def test_count_alone_is_no_time(text, lang):
    assert extract_timespan(text, lang, ANCHOR) is None


@pytest.mark.parametrize("text,lang,expected", CLOCKS)
def test_hour_before_a_courtesy_or_date_word_is_a_clock(text, lang, expected):
    assert start(extract_timespan(text, lang, ANCHOR)) == expected


@pytest.mark.parametrize("text,lang,hour", [
    ("recuérdame llamar a las 3 vecinas mañana", "es", 3),
    ("look at 5 houses tomorrow", "en", 5),
    ("a las 8 te llamo", "es", 8),
])
def test_doubtful_clock_stays_a_candidate_below_the_date(text, lang, hour):
    candidates = extract_candidates(text, lang, ANCHOR)
    clocks = [c for c in candidates if c.construction == "clock_time"
              and c.span.start.datetime().hour == hour]
    dates = [c for c in candidates if c.construction != "clock_time"]
    assert clocks
    assert candidates[0] is not clocks[0] or not dates
    assert all(clock.confidence < date.confidence
               for clock in clocks for date in dates)
    assert max(c.confidence for c in clocks) < 0.5


def test_doubt_halves_the_confidence():
    engine = _timespan_engine("en")
    tokens = engine.tokenize("look at 5 houses")
    clock = next(c.match for c in engine.matcher._candidates(tokens)
                 if c.match.construction == "clock_time")
    assert clock.doubt
    resolution = engine.resolver.resolve(clock, ANCHOR, None)
    plain = confidence(replace(clock, doubt=False), resolution, 2, engine.spec)
    assert confidence(clock, resolution, 2, engine.spec) == round(plain / 2, 4)


def test_or_joins_two_readings_of_a_bare_hour():
    anchor = datetime(2017, 6, 27, 13, 4)
    found = extract_timespans("meet friday at 3 or monday at noon", "en",
                              anchor)
    assert [m.text for m in found] == ["friday at 3", "monday at noon"]
    assert found[0].span.start.datetime() == datetime(2017, 6, 30, 3)


def test_a_language_without_counting_prepositions_keeps_the_clock():
    found = extract_timespan("je la sesa vespere", "eo", ANCHOR)
    assert found.span.start.datetime() == datetime(2026, 9, 26, 6)
    assert "vespere" in found.remainder
