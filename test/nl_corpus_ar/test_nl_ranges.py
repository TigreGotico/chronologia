# -*- coding: utf-8 -*-
"""Ranges.  Dash-framed ranges parse language-agnostically; the word-framed
Arabic form ("من يناير إلى مارس") needs range framings the engine only ships
in English, so it is xfail'd with that reason."""
import pytest

from ._corpus import AstroDate, start_end


@pytest.mark.parametrize("text,s,e", [
    ("يناير - مارس", (2017, 1, 1), (2017, 4, 1)),
    ("يونيو - أغسطس", (2017, 6, 1), (2017, 9, 1)),
    ("15 يناير - 20 يناير", (2018, 1, 15), (2018, 1, 21)),
])
def test_dash_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


@pytest.mark.xfail(reason="engine range framings (from/to) are English-only; "
                          "Arabic 'من X إلى Y' unsupported",
                   strict=True)
def test_word_framed_range():
    ss, ee = start_end("من يناير إلى مارس")
    assert ss == AstroDate(2017, 1, 1) and ee == AstroDate(2017, 4, 1)
