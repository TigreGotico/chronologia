"""Georgian counts in base twenty, and the fold has to read it that way.

Between the score multiples -- ოცი 20, ორმოცი 40, სამოცი 60, ოთხმოცი 80 -- a
number is the score plus და ("and") plus a remainder drawn from the 1..19
series, all written as ONE word: ოცდაათი is "twenty-and-ten" == 30.  A
tens/ones reading of the kind the Germanic folds use produces a confident
wrong answer on every value from 21 to 99, so the gold below is spelled out
independently from the Wiktionary numeral entries and the boundaries of the
base (19/20/21, 39/40/41, 59/60, 79/80, 99/100) are all crossed.
"""
from datetime import timedelta

import pytest

from chronologia.extract.numfold_georgian import read_run, surface

from ._corpus import ANCHOR, ad, start

#: value -> the surface, taken from the en.wiktionary.org entry for each word
#: (its "Georgian numbers" navigation box states the value) rather than from
#: anything the library composes.
SPELLED = {
    0: "ნული", 1: "ერთი", 2: "ორი", 3: "სამი", 4: "ოთხი", 5: "ხუთი",
    6: "ექვსი", 7: "შვიდი", 8: "რვა", 9: "ცხრა", 10: "ათი",
    11: "თერთმეტი", 12: "თორმეტი", 13: "ცამეტი", 14: "თოთხმეტი",
    15: "თხუთმეტი", 16: "თექვსმეტი", 17: "ჩვიდმეტი", 18: "თვრამეტი",
    19: "ცხრამეტი",
    20: "ოცი", 21: "ოცდაერთი", 25: "ოცდახუთი", 29: "ოცდაცხრა",
    30: "ოცდაათი", 38: "ოცდათვრამეტი",
    40: "ორმოცი", 41: "ორმოცდაერთი", 47: "ორმოცდაშვიდი", 50: "ორმოცდაათი",
    59: "ორმოცდაცხრამეტი",
    60: "სამოცი", 79: "სამოცდაცხრამეტი",
    80: "ოთხმოცი", 90: "ოთხმოცდაათი", 99: "ოთხმოცდაცხრამეტი",
    100: "ასი", 200: "ორასი", 300: "სამასი", 400: "ოთხასი", 500: "ხუთასი",
    600: "ექვსასი", 700: "შვიდასი", 800: "რვაასი", 900: "ცხრაასი",
    1000: "ათასი",
}


@pytest.mark.parametrize("value,word", sorted(SPELLED.items()))
def test_surface_matches_the_attested_word(value, word):
    assert surface(value) == word


@pytest.mark.parametrize("value,word", sorted(SPELLED.items()))
def test_word_reads_back_to_its_value(value, word):
    assert read_run(word) == value


@pytest.mark.parametrize("value,words", [
    (250, "ორას ორმოცდაათი"),
    (415, "ოთხას თხუთმეტი"),
    (2000, "ორი ათასი"),
    (2010, "ორი ათას ათი"),
    (10000, "ათი ათასი"),
])
def test_compound_runs(value, words):
    """A hundred or ათასი with a remainder loses its final -ი and the
    remainder follows as a separate word -- and a vigesimal expression nests
    inside a hundreds one untouched ("two-hundred twenty-and-thirty")."""
    assert surface(value) == words
    assert read_run(words) == value


@pytest.mark.parametrize("n", [19, 20, 21, 30, 39, 40, 41, 59, 60, 79, 80,
                               90, 99])
def test_score_boundaries_are_not_tens_and_ones(n):
    """Every value in the base-20 range names its SCORE, so no surface here
    may be built from a "tens" word the language does not have."""
    word = surface(n)
    assert read_run(word) == n
    if n >= 20 and n % 20:
        score = (n // 20) * 20
        assert word.startswith(surface(score)[:-1] + "და")


def _days_ago(n):
    return ad(ANCHOR - timedelta(days=n))


@pytest.mark.parametrize("n", [1, 5, 19, 20, 21, 30, 47, 59, 60, 99])
def test_spelled_count_drives_a_real_offset(n):
    """The fold has to reach the resolver: a spelled vigesimal count in an
    "N days ago" phrase must move the anchor by exactly N days."""
    assert start(f"{surface(n)} დღის წინ") == _days_ago(n)


@pytest.mark.parametrize("n,wrong", [(30, 20), (50, 40), (99, 19), (21, 1)])
def test_score_compound_is_not_its_remainder_alone(n, wrong):
    """Reading ოცდაათი as its remainder (or as its bare score) is the exact
    failure a non-vigesimal fold makes; both readings must be absent."""
    assert start(f"{surface(n)} დღის წინ") == _days_ago(n)
    assert start(f"{surface(n)} დღის წინ") != _days_ago(wrong)


@pytest.mark.parametrize("n", [8, 9, 29, 90])
def test_vowel_final_and_score_words_round_trip(n):
    assert read_run(surface(n)) == n
