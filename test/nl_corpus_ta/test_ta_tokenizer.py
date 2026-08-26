# -*- coding: utf-8 -*-
"""The Tamil script reaches the matcher as whole words.

Tamil is an abugida: a syllable is a base consonant carrying combining vowel
signs, and the virama that cancels the inherent vowel is a combining mark too.
Those marks are Unicode categories Mn and Mc, which the regex letter class
``\\w`` does not match, so a letter class built from ``\\w`` alone cuts every
Tamil word at its first vowel sign -- ஒன்பதரை arrives as the two fragments
"ஒன" and "பதர", and not one of them is a word.  The tokenizer's letter class
carries the Tamil block's mark subranges for exactly this reason, and this file
is the pin: if they are ever dropped, the whole locale stops matching and these
cases say so directly instead of leaving a hundred parse failures to explain.
"""
import pytest

from chronologia.extract.model import TokenizerModes
from chronologia.extract.tokenizer import Tokenizer

TOKENIZE = Tokenizer(TokenizerModes()).tokenize


@pytest.mark.parametrize("word", [
    "ஒன்பதரை",        # virama + vowel sign AI
    "திங்கள்",          # vowel sign I + virama
    "ஞாயிற்றுக்கிழமை",   # vowel signs AA, U, I, AI and two viramas
    "செவ்வாய்",         # vowel sign E, prefixed in visual order
    "மணிக்கு",          # vowel signs I and U across a virama
    "நாட்களில்",        # the locative, one token
    "பிற்பகல்",         # a day-period word
    "தொள்ளாயிரம்",      # the suppletive nine hundred
    "அந்தி",           # the first half of a two-word band name
    "விநாடிகளுக்கு",     # the dative plural of the second
])
def test_a_tamil_word_is_one_token(word):
    assert [t.text for t in TOKENIZE(word)] == [word]


def test_a_phrase_cuts_only_at_its_spaces():
    text = "காலை ஒன்பதரை மணி"
    assert [t.text for t in TOKENIZE(text)] == ["காலை", "ஒன்பதரை", "மணி"]


@pytest.mark.parametrize("text,value", [
    ("௧௫", 15), ("௨௦௨௬", 2026), ("௩௦", 30),
])
def test_the_tamil_digits_read_as_numbers_unaided(text, value):
    """௦-௯ are ordinary Unicode decimal digits, so the numeric rule already
    reads them and the locale ships no digit pass of its own."""
    tokens = TOKENIZE(text)
    assert len(tokens) == 1
    assert tokens[0].is_number and tokens[0].value == value


@pytest.mark.parametrize("word,expected", [
    # the marks added for Tamil are Tamil-block codepoints and cannot appear
    # in another script, so the class stays inert everywhere else.
    ("tomorrow", ["tomorrow"]),
    ("übermorgen", ["übermorgen"]),
    ("понедельник", ["понедельник"]),
    ("मंगलवार", ["मंगलवार"]),
    ("วันจันทร์", ["วันจันทร์"]),
])
def test_the_other_scripts_tokenize_unchanged(word, expected):
    assert [t.text for t in TOKENIZE(word)] == expected
