# -*- coding: utf-8 -*-
"""Ranges.  Dash-framed ranges parse language-agnostically; the word-framed
Arabic form ("من يناير إلى مارس") parses too -- the "from" lead (من) and the
"to" connector (إلى) ship per-locale (marker_from/marker_to), so range framing
is not English-only.  من / إلى are free words, so they tokenize as their own
tokens; the earlier date is always the span start, never inverted by
right-to-left reading order."""
import pytest

from ._corpus import AstroDate, start_end, nomatch


@pytest.mark.parametrize("text,s,e", [
    ("يناير - مارس", (2017, 1, 1), (2017, 4, 1)),
    ("يونيو - أغسطس", (2017, 6, 1), (2017, 9, 1)),
    ("15 يناير - 20 يناير", (2018, 1, 15), (2018, 1, 21)),
])
def test_dash_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


@pytest.mark.parametrize("text,s,e", [
    ("من يناير إلى مارس", (2017, 1, 1), (2017, 4, 1)),
    ("من يونيو إلى أغسطس", (2017, 6, 1), (2017, 9, 1)),
    ("من 15 يناير إلى 20 يناير", (2018, 1, 15), (2018, 1, 21)),
])
def test_word_framed_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


# -- adversarial: a bare range connector with no valid endpoints must not crash
# and must not fabricate a span.
@pytest.mark.parametrize("text", ["من", "إلى", "بين", "من إلى"])
def test_bare_connector_is_nomatch(text):
    nomatch(text)
