# -*- coding: utf-8 -*-
"""A number that counts the next noun is no clock hour.

"a las 3 vecinas" (three neighbours) and "look at 5 houses" read a time of day
at 03:00 and 05:00 and took the place of the date beside them.  A bare hour
behind a clock preposition that also introduces a counted group
(``marker_at_counts``) and directly before a noun of
``marker_counted_noun`` stays a candidate at a low confidence, below the
date-only reading, and it is not the parse winner.  Any other word after the
hour, a verb included, leaves the clock as it is.

Anchor: Friday 2026-09-25 12:00, so "tomorrow" is Saturday 2026-09-26.  Every
expected value is the calendar day or the spoken hour, written by hand.
"""
from dataclasses import replace
from datetime import datetime

import pytest

from chronologia import extract_candidates, extract_timespan
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
    ("ás 2 rapazas mañá", "gl", "ás 2 rapazas"),
    ("dillo alle due ragazze domani", "it", "dillo alle due ragazze"),
    ("demain à 8 personnes", "fr", "à 8 personnes"),
    ("morgen om 3 mensen", "nl", "om 3 mensen"),
    ("morgen um 3 Euro", "de", "um 3 Euro"),
]

COUNTS_ALONE = [
    ("a las 5 personas", "es"),
    ("wave at 5 people", "en"),
    ("a les 3 noies", "ca"),
    ("ás 2 rapazas", "gl"),
    ("om 5 euro", "nl"),
    ("om 8 mensen", "nl"),
    ("um 8 Leute", "de"),
    ("alle 5 persone", "it"),
    ("à 8 personnes", "fr"),
    ("às 8 pessoas", "pt"),
]

# text, language, expected instant: a word after the hour that is no counted
# noun leaves the clock, whatever its class.  A lone hour takes the next
# twelve-hour reading after the anchor (ruling 17), a named day keeps it.
CLOCKS = [
    ("wake me at 7 again", "en", datetime(2026, 9, 25, 19)),
    ("see you at 8 then", "en", datetime(2026, 9, 25, 20)),
    ("at 8 we leave", "en", datetime(2026, 9, 25, 20)),
    ("at 8 i will call", "en", datetime(2026, 9, 25, 20)),
    ("pick me up at 8 sharp", "en", datetime(2026, 9, 25, 20)),
    ("be at 6 home", "en", datetime(2026, 9, 25, 18)),
    ("a las 8 llegamos", "es", datetime(2026, 9, 25, 20)),
    ("a las 8 empieza la película", "es", datetime(2026, 9, 25, 20)),
    ("a las 8 nos vemos", "es", datetime(2026, 9, 25, 20)),
    ("a las 8 te llamo", "es", datetime(2026, 9, 25, 20)),
    ("quedamos a las 8 entonces", "es", datetime(2026, 9, 25, 20)),
    ("mañana a las 8 por favor", "es", datetime(2026, 9, 26, 8)),
    ("um 8 gehe ich", "de", datetime(2026, 9, 25, 20)),
    ("um 8 beginnt das Treffen", "de", datetime(2026, 9, 25, 20)),
    ("ich rufe dich um 8 an", "de", datetime(2026, 9, 25, 20)),
    ("om 8 ben ik thuis", "nl", datetime(2026, 9, 25, 20)),
    ("om 8 ga ik", "nl", datetime(2026, 9, 25, 20)),
    ("ik haal je om 8 af", "nl", datetime(2026, 9, 25, 20)),
    ("ik kom morgen om 8 thuis", "nl", datetime(2026, 9, 26, 8)),
    ("alle 8 arriva Marco", "it", datetime(2026, 9, 25, 20)),
    ("à 8 je pars", "fr", datetime(2026, 9, 25, 20)),
    ("às 8 chega o comboio", "pt", datetime(2026, 9, 25, 20)),
    ("a les 8 arriba el tren", "ca", datetime(2026, 9, 25, 20)),
    ("ás 8 chega o tren", "gl", datetime(2026, 9, 25, 20)),
    ("a les 8 llegamos", "ast", datetime(2026, 9, 25, 20)),
    ("hacia las 8 llegamos", "es", datetime(2026, 9, 25, 20)),
    ("a las 8 mañana", "es", datetime(2026, 9, 26, 8)),
    ("son las 5 personas", "es", datetime(2026, 9, 25, 17)),
    ("at 8, people are waiting", "en", datetime(2026, 9, 25, 20)),
    ("a las 8. Personas mayores primero", "es", datetime(2026, 9, 25, 20)),
    ("nos vemos a las 8. Personas no", "es", datetime(2026, 9, 25, 20)),
    ("às 8. Pessoas mais velhas primeiro", "pt", datetime(2026, 9, 25, 20)),
    ("um 8. Leute warten", "de", datetime(2026, 9, 25, 20)),
    ("à 8 personne ne répond", "fr", datetime(2026, 9, 25, 20)),
    ("à 8 personne ne vient", "fr", datetime(2026, 9, 25, 20)),
    ("at 8 monday", "en", datetime(2026, 9, 28, 8)),
    ("let's meet next tuesday evening at 9 downtown", "en",
     datetime(2026, 9, 29, 21)),
]


@pytest.mark.parametrize("text,lang,remainder", COUNTS_WITH_DATE)
def test_count_leaves_the_date_alone(text, lang, remainder):
    found = extract_timespan(text, lang, ANCHOR)
    assert found.span.start.datetime() == TOMORROW
    assert found.span.end.datetime() == datetime(2026, 9, 27)
    assert found.remainder == remainder


@pytest.mark.parametrize("text,lang", COUNTS_ALONE)
def test_count_alone_is_no_time(text, lang):
    assert extract_timespan(text, lang, ANCHOR) is None


@pytest.mark.parametrize("text,lang,expected", CLOCKS)
def test_a_word_that_is_no_counted_noun_leaves_the_clock(text, lang, expected):
    assert extract_timespan(text, lang, ANCHOR).span.start.datetime() == expected


@pytest.mark.parametrize("text,lang,hour", [
    ("recuérdame llamar a las 3 vecinas mañana", "es", 15),
    ("look at 5 houses tomorrow", "en", 17),
    ("llama a las 4 vecinas mañana", "es", 16),
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


@pytest.mark.parametrize("text,lang", [
    ("no gracias, mañana", "es"),
    ("no o mañana", "es"),
    ("nicht oder morgen", "de"),
    ("pas ou demain", "fr"),
])
def test_clock_vocabulary_does_not_join_the_exclusion_words(text, lang):
    found = extract_timespan(text, lang, ANCHOR)
    assert found.span.start.datetime() == TOMORROW


def test_a_language_without_counting_prepositions_keeps_the_clock():
    found = extract_timespan("je la sesa vespere", "eo", ANCHOR)
    assert found.span.start.datetime() == datetime(2026, 9, 25, 18)
    assert "vespere" in found.remainder
