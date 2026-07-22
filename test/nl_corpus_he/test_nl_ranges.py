# -*- coding: utf-8 -*-
"""Ranges.  Dash-framed ranges parse language-agnostically; the word-framed
Hebrew form ("מ-ינואר עד מרץ") needs range framings the engine only ships in
English, so it is xfail'd with that reason."""
import pytest

from ._corpus import AstroDate, start_end


@pytest.mark.parametrize("text,s,e", [
    ("ינואר - מרץ", (2017, 1, 1), (2017, 4, 1)),
    ("יוני - אוגוסט", (2017, 6, 1), (2017, 9, 1)),
    ("15 בינואר - 20 בינואר", (2018, 1, 15), (2018, 1, 21)),
])
def test_dash_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


@pytest.mark.xfail(reason="engine range framings (from/to) are English-only; "
                          "Hebrew 'מ-X עד Y' unsupported",
                   strict=True)
def test_word_framed_range():
    ss, ee = start_end("מ-ינואר עד מרץ")
    assert ss == AstroDate(2017, 1, 1) and ee == AstroDate(2017, 4, 1)
