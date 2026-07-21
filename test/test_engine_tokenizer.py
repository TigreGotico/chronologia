"""Tokenizer stage: mode flags and number/iso detection."""
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
