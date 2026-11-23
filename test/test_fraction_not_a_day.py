"""A fraction of a month names no day of it.

"third" is also a fraction: Wiktionary, "third", noun sense 2, "One of three
equal parts of a whole" ("He ate a third of the pie").  Only a spelled ordinal
from third to tenth names a fraction, and only when the phrase is not broken by
a comma: "first" and "second" name none, and a day follows "any", "another" or
"the whole" before an ordinal above ten.  The anchor is Saturday 17 October
2026, so the next first of the month is 1 November and the next third is 3
November.
"""
from datetime import datetime

import pytest

from chronologia import AstroDate, extract_timespan

ANCHOR = datetime(2026, 10, 17, 12, 0)


@pytest.mark.parametrize("text", [
    "a full third of the month",
    "a whole fifth of the month",
    "an entire fifth of the month",
    "a solid third of the month",
    "a fair third of the month",
    "a clear third of the month",
    "a complete third of the month",
    "a large third of the month",
    "a mere fifth of the month",
    "an extra fifth of the month",
    "a total third of the month",
    "another third of the month",
    "some third of the month",
    "any third of the month",
    "the first third of the month",
    "the last third of the month",
    "the final third of the month",
    "a full third of march",
    "the middle third of november",
    "the last third of may",
    "the last fifth of may",
    "the final fifth of may is a holiday",
    "some third of may",
    "any third of may",
    "the middle third of may",
])
def test_a_fraction_names_no_day(text):
    assert extract_timespan(text, "en", ANCHOR) is None


@pytest.mark.parametrize("text, day", [
    ("remind me on another first of the month", (2026, 11, 1)),
    ("pay rent on any first of the month", (2026, 11, 1)),
    ("some first of the month", (2026, 11, 1)),
    ("any second of the month", (2026, 11, 2)),
    ("another second of may", (2027, 5, 2)),
    ("the last first of the month", (2026, 11, 1)),
    ("another fifteenth of the month", (2026, 11, 15)),
    ("any fifteenth of the month is fine", (2026, 11, 15)),
    ("any eleventh of the month", (2026, 11, 11)),
    ("a good fifteenth of may", (2027, 5, 15)),
    ("the whole fifth of may was rainy", (2027, 5, 5)),
    ("the whole third of may", (2027, 5, 3)),
    ("the good fifth of may", (2027, 5, 5)),
    ("a full, third of may", (2027, 5, 3)),
    ("a good, fifth of may", (2027, 5, 5)),
    ("another, third of the month", (2026, 11, 3)),
])
def test_a_day_after_a_determiner_stays(text, day):
    r = extract_timespan(text, "en", ANCHOR)
    assert r.span.start == AstroDate(*day)


@pytest.mark.parametrize("text, lang, day, rest", [
    ("the third of the month", "en", (2026, 11, 3), ""),
    ("pay rent on the third of the month", "en", (2026, 11, 3), "pay rent"),
    ("the twenty third of the month", "en", (2026, 10, 23), ""),
    ("book a table third of may", "en", (2027, 5, 3), "book a table"),
    ("see you the third of march", "en", (2027, 3, 3), "see you"),
])
def test_a_day_of_the_month_stays(text, lang, day, rest):
    r = extract_timespan(text, lang, ANCHOR)
    assert (r.span.start, r.remainder) == (AstroDate(*day), rest)


@pytest.mark.parametrize("text, lang, start, rest", [
    ("les 14, 15 mai", "fr", (2027, 5, 15), "les 14"),
    ("il 14, 15 maggio", "it", (2027, 5, 15), "il 14"),
    ("los 14, 15 de mayo", "es", (2027, 5, 15), "los 14"),
    ("a las 9 30 de mayo", "es", (2027, 5, 30, 9), ""),
    ("a les 10 15 de maig", "ca", (2027, 5, 15, 10), ""),
    ("sveglia alle 7 15 maggio", "it", (2027, 5, 15, 7), "sveglia"),
])
def test_a_digit_day_after_an_article_and_a_number_stays(text, lang, start,
                                                         rest):
    r = extract_timespan(text, lang, ANCHOR)
    assert (r.span.start, r.remainder) == (AstroDate(*start), rest)


@pytest.mark.parametrize("text, lang, start, rest", [
    ('los catorce, quince de mayo', 'es', (2027, 5, 15), 'los catorce'),
    ('los catorce y quince de mayo', 'es', (2027, 5, 1, 14, 15), ''),
    ('a las nueve quince de mayo', 'es', (2027, 5, 15, 9, 0), ''),
    ('el lunes a las nueve, quince de mayo', 'es', (2027, 5, 15, 9, 0), ''),
    ('las dos tres de mayo', 'es', (2027, 5, 3, 2, 0), ''),
    ('el uno, dos de mayo', 'es', (2027, 5, 2), 'el uno'),
    ('nació un tres de marzo', 'es', (2027, 3, 3), 'nació un'),
    ('a las once veinte de mayo', 'es', (2027, 5, 20, 11, 0), ''),
    ('llego a las ocho el quince de mayo', 'es', (2027, 5, 15),
     'llego a las ocho'),
    ('the fourteenth, fifteenth of may', 'en', (2027, 5, 15),
     'the fourteenth'),
    ('the third of the month', 'en', (2026, 11, 3), ''),
    ('the first of may', 'en', (2027, 5, 1), ''),
    ('at nine fifteenth of may', 'en', (2027, 5, 15, 9, 0), ''),
    ('the 14th, 15th of may', 'en', (2027, 5, 15), 'the 14th'),
    ('the first, fifteenth of may', 'en', (2027, 5, 15), 'the first'),
    ('the last of may', 'en', (2027, 5, 1), 'the last of'),
    ('os catorze, quinze de maio', 'pt', (2027, 5, 15), 'os catorze'),
    ('às nove, quinze de maio', 'pt', (2027, 5, 15, 9, 0), ''),
    ('a um de maio', 'pt', (2027, 5, 1), ''),
    ('les quatorze, quinze mai', 'fr', (2027, 5, 15), 'les quatorze'),
    ('à neuf heures quinze mai', 'fr', (2027, 5, 1, 9, 15), ''),
    ('le premier, deux mai', 'fr', (2027, 5, 2), 'le premier'),
    ('il quattordici, quindici maggio', 'it', (2027, 5, 15), 'il quattordici'),
    ('alle nove quindici maggio', 'it', (2027, 5, 15, 9, 0), ''),
    ('a les deu quinze de maig', 'ca', (2027, 5, 15, 10, 0), ''),
    ('els catorze, quinze de maig', 'ca', (2027, 5, 15), 'els catorze'),
    ('am vierzehnten, fünfzehnten Mai', 'de', (2027, 5, 15), 'am vierzehnten'),
    ('die zwei dritten Mai', 'de', (2027, 5, 3), 'die zwei'),
    ('de veertiende, vijftiende mei', 'nl', (2027, 5, 15), 'de veertiende'),
    ('om negen vijftien mei', 'nl', (2027, 5, 15, 9, 0), ''),
    ('os catorce, quince de maio', 'gl', (2027, 5, 15), 'os catorce'),
])
def test_a_spelled_number_before_a_day_leaves_it_a_day(text, lang, start,
                                                       rest):
    r = extract_timespan(text, lang, ANCHOR)
    assert (r.span.start, r.remainder) == (AstroDate(*start), rest)


def test_a_spelled_fraction_phrase_with_no_day_stays_none():
    assert extract_timespan("el último tercio del mes", "es", ANCHOR) is None
