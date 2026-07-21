# -*- coding: utf-8 -*-
"""Adversarial: garbage, near-misses, bare markers, the language's own false
friends (bare "meia"/"quarto", a stranded direction marker)."""
import pytest

from ._corpus import parse, nomatch


_NOMATCH = ['', '   ', '\\t\\n', 'banana', 'xyzzy', 'lorem ipsum', '!!!', '...', '???', '@#$%', '-', '5', '42', '1234567890', '3.14', '0', 'há', 'em', 'às', 'semana', 'dia', 'ano', 'e', 'meia', 'quarto']


@pytest.mark.parametrize("text", _NOMATCH)
def test_no_match(text):
    nomatch(text)


_FUZZ = ['há muito', 'às às às', 'bc ad bp', '🎉📅🕐', 'SELECT * FROM x', 'junho junho junho', 'em -5 dias']


@pytest.mark.parametrize("text", _FUZZ)
def test_never_raises(text):
    parse(text)


def test_absurdly_long_is_safe():
    assert parse("bla " * 20000) is None
