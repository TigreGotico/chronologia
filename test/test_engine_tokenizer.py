"""Tokenizer stage: mode flags and number/iso detection."""
import pytest

from chronologia.extract import Tokenizer, TokenizerModes


def _texts(tokens):
    return [t.text for t in tokens]


def test_basic_split_and_lowercase():
    toks = Tokenizer(TokenizerModes()).tokenize("Foo BAR baz")
    assert _texts(toks) == ["foo", "bar", "baz"]
    assert [t.index for t in toks] == [0, 1, 2]


def test_number_detection():
    tok = Tokenizer(TokenizerModes()).tokenize("3")[0]
    assert tok.is_number and tok.value == 3 and tok.text == "3"


def test_decimal_number():
    tok = Tokenizer(TokenizerModes()).tokenize("3.5")[0]
    assert tok.is_number and tok.value == 3.5


def test_ordinal_dot_on():
    tok = Tokenizer(TokenizerModes(ordinal_dot=True)).tokenize("5.")[0]
    assert tok.is_number and tok.value == 5 and tok.text == "5" and tok.raw == "5."


def test_ordinal_dot_off_keeps_bare_number():
    tok = Tokenizer(TokenizerModes(ordinal_dot=False)).tokenize("5.")[0]
    assert tok.is_number and tok.value == 5 and tok.raw == "5"


def test_split_contractions_on():
    toks = Tokenizer(TokenizerModes(split_contractions=True)).tokenize("z'day")
    assert _texts(toks) == ["z", "day"]


def test_split_contractions_off():
    toks = Tokenizer(TokenizerModes(split_contractions=False)).tokenize("z'day")
    assert _texts(toks) == ["z'day"]


def test_iso_token_kept_whole():
    toks = Tokenizer(TokenizerModes()).tokenize("2017-06-30")
    assert _texts(toks) == ["2017-06-30"] and not toks[0].is_number


def test_empty_text():
    assert Tokenizer(TokenizerModes()).tokenize("") == ()


def test_garbage_never_raises():
    toks = Tokenizer(TokenizerModes(split_contractions=True, ordinal_dot=True)
                     ).tokenize("!!! ??? --- ...")
    assert toks == ()


def test_iso_week_token_kept_whole_padded_or_not():
    tok = Tokenizer(TokenizerModes())
    assert _texts(tok.tokenize("2026-W01")) == ["2026-w01"]
    assert _texts(tok.tokenize("2026-W1")) == ["2026-w1"]
    assert _texts(tok.tokenize("2026-W1-3")) == ["2026-w1-3"]


# A digit run that continues past a literal's shape is not that literal with a
# spare digit -- it is not that literal at all.  Without the trailing boundary
# guard each of these bound a prefix and stranded the tail, which is how the
# ordinary written year range "1914-1918" came to be read as month 19 of 1914.
@pytest.mark.parametrize("text,expected", [
    ("1914-1918", ["1914", "1918"]),
    ("2026-071", ["2026", "071"]),
    ("2026-07-244", ["2026", "07", "244"]),
    ("12/11/20244", ["12", "11", "20244"]),
    ("15:305", ["15", "305"]),
    ("2026-W123", ["2026", "w", "123"]),
])
def test_digits_past_a_literal_break_it_up(text, expected):
    assert _texts(Tokenizer(TokenizerModes()).tokenize(text)) == expected


@pytest.mark.parametrize("text", ["2017-06-30", "2024/03/06", "2024-03",
                                  "12/11/2024", "15:30", "2026-w01"])
def test_literals_at_their_exact_length_still_bind(text):
    assert _texts(Tokenizer(TokenizerModes()).tokenize(text)) == [text]
