"""extract_duration refuses an ordinal as a count.

An ordinal is "a word that expresses the relative position of an item in a
sequence" (Wiktionary, "ordinal number", sense 1).  "The second week" names
which week; it is not two weeks long.  The library already reads these
phrases as positions: every non-English phrase below comes from that
locale's own corpus, where extract_timespan resolves it to one week or one
day ("die zweite woche" is calendar week 2 in
test/nl_corpus_de/test_nl_indefinite_article_is_not_a_week_number.py).
"""
from datetime import timedelta

import pytest

from chronologia import extract_duration


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
])
def test_a_count_is_still_a_length(text, lang, length, remainder):
    got = extract_duration(text, lang)
    assert got is not None
    assert got.duration == length
    assert got.remainder == remainder
