# -*- coding: utf-8 -*-
"""Ranges.  Dash-framed ranges parse language-agnostically; the word-framed
Romance forms ("de junho a agosto", "entre ... e ...") need range framings
the engine only ships in English -- those are xfail'd with that reason."""
import pytest

from ._corpus import AstroDate, start_end, nomatch


@pytest.mark.parametrize("text,s,e", [
    ("juny - agost", (2017, 6, 1), (2017, 9, 1)),
    ("gener - març", (2017, 1, 1), (2017, 4, 1)),
    ("5 de juny - 12 de juny", (2018, 6, 5), (2018, 6, 13)),
])
def test_dash_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


@pytest.mark.xfail(reason="engine range framings (from/to/between/and) are "
                          "English-only; Romance 'de X a Y' unsupported",
                   strict=True)
def test_word_framed_range():
    ss, ee = start_end("de juny a agost")
    assert ss == AstroDate(2017, 6, 1) and ee == AstroDate(2017, 9, 1)


# -- open-ended ranges: "fins" (open start) / "des de" (open end) -----------
from ._corpus import ANCHOR, ad  # noqa: E402


def test_fins_open_start():
    s, e = start_end("fins divendres")
    assert s == ad(ANCHOR)
    assert e == AstroDate(2017, 7, 1)


def test_desde_open_end():
    s, e = start_end("des de 2010")
    assert s == AstroDate(2010, 1, 1)
    assert e == ad(ANCHOR)
