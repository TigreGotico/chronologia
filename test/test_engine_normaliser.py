"""Normaliser stage: lemma map + suffix strip, pure Token->Token."""
from engine_helpers import load_zz

from chronologia.extract import TemporalNormaliser, Token


def _norm(text, is_number=False, value=None):
    n = TemporalNormaliser(load_zz())
    return n.normalise_token(Token(text=text, raw=text, index=0,
                                   is_number=is_number, value=value))


def test_irregular_lemma():
    assert _norm("zwochen").text == "zweek"


def test_suffix_strip_aren():
    assert _norm("zfriaren").text == "zfri"


def test_suffix_strip_en():
    assert _norm("zdayen").text == "zday"


def test_lemma_wins_over_suffix():
    # zwochen ends with "en" too; the exact lemma map must win outright
    assert _norm("zwochen").text == "zweek"


def test_numbers_untouched():
    tok = _norm("3", is_number=True, value=3)
    assert tok.text == "3" and tok.value == 3


def test_raw_preserved():
    n = TemporalNormaliser(load_zz())
    out = n.normalise_token(Token("zfriaren", "zFriAren", 2, False, None))
    assert out.raw == "zFriAren" and out.index == 2 and out.text == "zfri"


def test_unknown_token_passes_through():
    assert _norm("zmon").text == "zmon"
