# -*- coding: utf-8 -*-
"""Adversarial: garbage, near-misses, bare markers, the language's own false
friends (bare "mitja"/"quart", a stranded direction marker)."""
import pytest

from ._corpus import parse, nomatch


_NOMATCH = ['', '   ', '\\t\\n', 'banana', 'xyzzy', 'lorem ipsum', '!!!', '...', '???', '@#$%', '-', '5', '42', '1234567890', '3.14', '0', 'fa', 'en', 'les', 'setmana', 'dia', 'any', 'i', 'mitja', 'quart']


@pytest.mark.parametrize("text", _NOMATCH)
def test_no_match(text):
    nomatch(text)


_FUZZ = ['fa muito', 'les les les', 'bc ad bp', '🎉📅🕐', 'SELECT * FROM x', 'juny juny juny', 'en -5 dies']


@pytest.mark.parametrize("text", _FUZZ)
def test_never_raises(text):
    parse(text)


def test_absurdly_long_is_safe():
    assert parse("bla " * 20000) is None
