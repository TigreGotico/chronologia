# -*- coding: utf-8 -*-
"""A plural part of the day names the band like the singular does.

"weekday mornings at 8" is eight in the morning, so a lone hour behind it keeps
the spoken hour instead of taking the next twelve-hour reading (ruling 17).
Each plural is a Wiktionary noun form of its singular (en also an adverb), and
the vocabulary files cite it.

Anchor: Friday 2026-09-25 12:00.  Each expected value is the spoken hour in the
named band, on the first day after the anchor that has it, written by hand.
"""
from datetime import datetime

import pytest

from chronologia import extract_timespan

ANCHOR = datetime(2026, 9, 25, 12, 0)

CASES = [
    ("remind me to go to work weekday mornings at 8", "en",
     datetime(2026, 9, 26, 8)),
    ("mornings at 8", "en", datetime(2026, 9, 26, 8)),
    ("nas manhãs de dia útil às 8", "pt", datetime(2026, 9, 26, 8)),
    ("nas manhãs às 8", "pt", datetime(2026, 9, 26, 8)),
    ("nas manhas às 8", "pt", datetime(2026, 9, 26, 8)),
    ("nas madrugadas às 3", "pt", datetime(2026, 9, 26, 3)),
]


@pytest.mark.parametrize("text,lang,expected", CASES)
def test_plural_part_of_day_keeps_the_spoken_hour(text, lang, expected):
    assert extract_timespan(text, lang, ANCHOR).span.start.datetime() == expected


@pytest.mark.parametrize("plural,singular,lang", [
    ("afternoons at 3", "afternoon at 3", "en"),
    ("evenings at 8", "evening at 8", "en"),
    ("nights at 9", "night at 9", "en"),
    ("nas noites às 9", "na noite às 9", "pt"),
])
def test_a_plural_part_of_day_reads_like_the_singular(plural, singular, lang):
    assert (extract_timespan(plural, lang, ANCHOR).span.start.datetime()
            == extract_timespan(singular, lang, ANCHOR).span.start.datetime())


@pytest.mark.parametrize("text,lang,expected", [
    ("at 8", "en", datetime(2026, 9, 25, 20)),
    ("às 8", "pt", datetime(2026, 9, 25, 20)),
])
def test_a_lone_hour_with_no_part_of_the_day_takes_the_next_reading(
        text, lang, expected):
    assert extract_timespan(text, lang, ANCHOR).span.start.datetime() == expected
