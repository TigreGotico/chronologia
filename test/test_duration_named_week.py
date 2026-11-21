"""extract_duration reads "last week" and "next week" as a named calendar week.

Class 2b of the OVOS date rulings reads a named week as the calendar unit,
not as a length.  English "last week" is no length; the phrases below are the
same words in other locales.  Each row comes from the date.entity file or the
golden utterances of ovos-skill-date-time.  A week with an article and no
modifier ("la semana", "a week") stays a length of 7 days.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_duration

ANCHOR = datetime(2017, 6, 27, 13, 4)


@pytest.mark.parametrize("text,lang", [
    ("la semana pasada", "es"),
    ("la semana que viene", "es"),
    ("la semana próxima", "es"),
    ("a semana pasada", "gl"),
    ("a semana passada", "pt"),
    ("a semana que vem", "pt"),
    ("la semaine dernière", "fr"),
    ("la semaine prochaine", "fr"),
    ("la settimana scorsa", "it"),
    ("la setmana passada", "ca"),
    ("ezen a héten", "hu"),
    ("last week", "en"),
])
def test_named_week_is_no_length(text, lang):
    assert extract_duration(text, lang, anchor=ANCHOR) is None


@pytest.mark.parametrize("text,lang", [
    ("la semana", "es"),
    ("una semana", "es"),
    ("a semana", "gl"),
    ("a week", "en"),
    ("a héten", "hu"),
])
def test_article_week_stays_a_length(text, lang):
    found = extract_duration(text, lang, anchor=ANCHOR)
    assert found.duration == timedelta(days=7)
    assert found.remainder == ""
