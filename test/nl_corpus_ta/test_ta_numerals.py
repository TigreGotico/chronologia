# -*- coding: utf-8 -*-
"""The numeral table, and what it deliberately does not cover.

Tamil compounds are not concatenations.  A compound is built on a distinct
adjectival stem and the join triggers sandhi at the seam, so 11 is பதினொன்று
and not பத்து ஒன்று, and the hundreds are suppletive words in their own right.
The locale ships the surfaces its source spells out and nothing else: a value
whose spelling was not transcribed does not fold, and the corpus pins that
absence so nobody later mistakes it for a bug and closes it by generating the
missing word.
"""
import pytest

from ._corpus import nomatch, start
from chronologia.extract.model import TokenizerModes
from chronologia.extract.numfold_dravidian import fold_ta, read_run
from chronologia.extract.tokenizer import Tokenizer


def folded(text):
    """The token texts the locale's fold leaves behind."""
    return [t.text for t in fold_ta(Tokenizer(TokenizerModes()).tokenize(text))]


@pytest.mark.parametrize("word,value", [
    ("ஒன்று", 1), ("இரண்டு", 2), ("மூன்று", 3), ("நான்கு", 4), ("ஐந்து", 5),
    ("ஆறு", 6), ("ஏழு", 7), ("எட்டு", 8), ("ஒன்பது", 9), ("பத்து", 10),
    ("பதினொன்று", 11), ("பன்னிரண்டு", 12), ("பதின்மூன்று", 13),
    ("பதினைந்து", 15), ("இருபது", 20), ("இருபத்தொன்று", 21), ("முப்பது", 30),
    ("நாற்பது", 40), ("ஐம்பது", 50), ("அறுபது", 60), ("எழுபது", 70),
    ("எண்பது", 80), ("தொண்ணூறு", 90), ("நூறு", 100), ("நூற்றொன்று", 101),
    ("ஆயிரம்", 1000),
])
def test_the_cardinals_read(word, value):
    assert read_run(word) == value


@pytest.mark.parametrize("word,value", [
    ("இருநூறு", 200), ("முந்நூறு", 300), ("நானூறு", 400), ("ஐந்நூறு", 500),
    ("அறுநூறு", 600), ("எழுநூறு", 700), ("எண்ணூறு", 800),
    ("தொள்ளாயிரம்", 900),
])
def test_the_hundreds_are_suppletive_words(word, value):
    """முந்நூறு is not மூன்று joined to நூறு by any rule -- each hundred is
    its own transcribed surface, which is why none is generated."""
    assert read_run(word) == value


@pytest.mark.parametrize("word,value", [
    ("ஒண்ணு", 1), ("ரெண்டு", 2), ("மூணு", 3), ("நாலு", 4), ("அஞ்சு", 5),
    ("இருவத்தொண்ணு", 21),
])
def test_the_colloquial_doublets_read(word, value):
    """A real spoken register, carried by the same source as the citation
    forms; whether it reaches written dates is a question for a native
    speaker, but reading it costs nothing."""
    assert read_run(word) == value


@pytest.mark.parametrize("text,value", [
    ("இரண்டு ஆயிரம் இருபது", 2020),
    ("ஆயிரம் தொள்ளாயிரம் நாற்பது", 1940),
    ("இரண்டு ஆயிரம்", 2000),
])
def test_a_composed_numeral_reads_as_one_number(text, value):
    assert read_run(text) == value


@pytest.mark.parametrize("word", [
    "பதினான்கு", "பதினாறு", "இருபத்திரண்டு", "முப்பத்தைந்து",
])
def test_an_untranscribed_compound_does_not_fold(word):
    """The seam sandhi that would generate these is exactly what the source's
    spelled-out entries show is not mechanical, so the value is left to the
    digits rather than guessed at."""
    assert read_run(word) is None


@pytest.mark.parametrize("text", ["மூன்று", "இருபது", "நூறு", "ஒன்பது"])
def test_a_bare_numeral_is_not_a_date(text):
    """A count with nothing counted names no time.  The four-digit guard is
    what keeps a spelled year from reading out of a bare count."""
    nomatch(text)


def test_a_spelled_year_still_reads_as_a_year():
    assert start("இரண்டு ஆயிரம் இருபது").year == 2020


def test_two_adjacent_numerals_stay_two_numbers():
    """Words of the same magnitude class never compose, so an unconditioned
    run scan cannot silently add them together."""
    assert folded("மூன்று நான்கு") == ["3", "4"]
    assert folded("இரண்டு ஆயிரம் இருபது") == ["2020"]
