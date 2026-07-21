# -*- coding: utf-8 -*-
"""Ranges.  Dash-framed ranges parse language-agnostically; the word-framed
Romance forms ("de junho a agosto", "entre ... e ...") need range framings
the engine only ships in English -- those are xfail'd with that reason."""
import pytest

from ._corpus import AstroDate, start_end, nomatch


@pytest.mark.parametrize("text,s,e", [
    ("junio - agosto", (2017, 6, 1), (2017, 9, 1)),
    ("enero - marzo", (2017, 1, 1), (2017, 4, 1)),
    ("5 de junio - 12 de junio", (2018, 6, 5), (2018, 6, 13)),
])
def test_dash_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


@pytest.mark.xfail(reason="engine range framings (from/to/between/and) are "
                          "English-only; Romance 'de X a Y' unsupported",
                   strict=True)
def test_word_framed_range():
    ss, ee = start_end("de junio a agosto")
    assert ss == AstroDate(2017, 6, 1) and ee == AstroDate(2017, 9, 1)
