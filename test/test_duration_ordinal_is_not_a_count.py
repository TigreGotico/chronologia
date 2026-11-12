"""extract_duration refuses an ordinal as a count.

An ordinal is "a word that expresses the relative position of an item in a
sequence" (Wiktionary, "ordinal number", sense 1).  "The second week" names
which week; it is not two weeks long.  The library already reads these
phrases as positions: the non-English phrases in the first block come from
that locale's own corpus, where extract_timespan resolves them to one week
or one day ("die zweite woche" is calendar week 2 in
test/nl_corpus_de/test_nl_indefinite_article_is_not_a_week_number.py).
The second block holds one phrase for each ordinal fold that no corpus
phrase reaches, with the dictionary entry that makes its word an ordinal.
"""
from datetime import datetime, timedelta

import pytest

from chronologia import extract_duration, extract_timespan


@pytest.mark.parametrize("text,lang", [
    ("the second minute", "en"),
    ("a second minute of the game", "en"),
    ("the second week of march", "en"),
    ("a second week of march", "en"),
    ("the 2nd week", "en"),
    ("the twenty-second day", "en"),
    ("the first hour", "en"),
    ("la segunda semana de marzo", "es"),
    ("el segundo día de marzo", "es"),
    ("la deuxième semaine de mars", "fr"),
    ("le premier jour de juillet", "fr"),
    ("la seconda settimana di marzo", "it"),
    ("la segona setmana de març", "ca"),
    ("a segunda semana de marzo", "gl"),
    ("la segunda selmana de marzu", "ast"),
    ("a segunda semana de março", "pt"),
    ("die zweite woche", "de"),
    ("die 2. woche", "de"),
    ("den 2. uge i marts", "da"),
    ("втората седмица на април", "bg"),
    ("la prima settimana di aprile", "it"),
    ("as nonas semanas de março", "pt"),
    ("a doua săptămână din martie", "ro"),
    ("trečioji savaitė", "lt"),
    ("þriðja vika", "is"),
    ("तीसरा सप्ताह", "hi"),
    ("an t-aonú lá is tríocha", "ga"),
    ("tríochadú lá is aon", "ga"),
    ("la cuarta semana de marzo", "es"),
    ("le vingt et unième jour de janvier", "fr"),
    # en.wiktionary: lt "antras" "second"; is "tuttugasti" "twentieth",
    # "fyrstur" "first"; pt "décimo" "(ordinal) tenth"; nl "2e" "abbreviation
    # of tweede (second)"; fr "1er" "abbreviation of premier (first)", "21e"
    # "abbreviation of vingt-et-unième", "onzième" "(ordinal) eleventh".
    ("antra savaitė", "lt"),
    ("dvidešimt antroji savaitė", "lt"),
    ("tuttugasta og fyrsta vika", "is"),
    ("o décimo dia", "pt"),
    ("de 2e week", "nl"),
    ("le 1er jour", "fr"),
    ("la 21e semaine", "fr"),
    ("le onzième jour", "fr"),
])
def test_an_ordinal_is_not_a_length(text, lang):
    assert extract_duration(text, lang) is None


@pytest.mark.parametrize("text,lang,length,remainder", [
    ("a couple of days", "en", timedelta(days=2), ""),
    ("two weeks", "en", timedelta(weeks=2), ""),
    ("the first two weeks", "en", timedelta(weeks=2), "the first"),
    ("one second", "en", timedelta(seconds=1), ""),
    ("dos semanas después de pascua", "es", timedelta(weeks=2),
     "después de pascua"),
    ("deux semaines après pâques", "fr", timedelta(weeks=2), "après pâques"),
    ("täglich für zwei wochen", "de", timedelta(weeks=2), "täglich"),
    ("en uge før jul", "da", timedelta(weeks=1), "før jul"),
    ("una setmana abans del 5 d'abril", "ca", timedelta(weeks=1),
     "abans del 5 d'abril"),
    ("tre giorni prima del 5 aprile", "it", timedelta(days=3),
     "prima del 5 aprile"),
    ("dvi savaitės", "lt", timedelta(weeks=2), ""),
    ("tvær vikur", "is", timedelta(weeks=2), ""),
    ("पाँच हफ़्ते", "hi", timedelta(weeks=5), ""),
    ("trí lá", "ga", timedelta(days=3), ""),
    ("două minute", "ro", timedelta(minutes=2), ""),
    ("doua minute", "ro", timedelta(minutes=2), ""),
    ("două ore și jumătate", "ro", timedelta(hours=2, minutes=30), ""),
])
def test_a_count_is_still_a_length(text, lang, length, remainder):
    got = extract_duration(text, lang)
    assert got is not None
    assert got.duration == length
    assert got.remainder == remainder


def test_a_cardinal_two_after_a_clock_is_still_a_length():
    # Romanian "două" is the cardinal two (en.wiktionary "două", Numeral,
    # "two"); the ordinal is "a doua".  Sunday 2026-09-27: Monday at 9 for
    # two hours is 09:00 to 11:00 on 2026-09-28.
    got = extract_timespan("luni la ora 9 timp de două ore", "ro",
                           datetime(2026, 9, 27, 13, 4))
    assert got is not None
    assert (got.span.start.day, got.span.start.hour) == (28, 9)
    assert (got.span.end.day, got.span.end.hour, got.span.end.minute) == (28, 11, 0)
    assert got.remainder == ""
