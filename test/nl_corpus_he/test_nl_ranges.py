# -*- coding: utf-8 -*-
"""Ranges.  Dash-framed ranges parse language-agnostically; the word-framed
Hebrew form ("מ-ינואר עד מרץ") parses too -- the "from" lead (the proclitic מ־)
and the "to" connector (עד) ship per-locale (marker_from/marker_to), so range
framing is not English-only.  The proclitic מ set off by a maqaf/hyphen
tokenizes as its own token (the hyphen is a separator), and עד is a free word;
the earlier date is always the span start, never inverted by right-to-left
reading order."""
import pytest

from ._corpus import AstroDate, start_end, nomatch


@pytest.mark.parametrize("text,s,e", [
    ("ינואר - מרץ", (2017, 1, 1), (2017, 4, 1)),
    ("יוני - אוגוסט", (2017, 6, 1), (2017, 9, 1)),
    ("15 בינואר - 20 בינואר", (2018, 1, 15), (2018, 1, 21)),
])
def test_dash_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


@pytest.mark.parametrize("text,s,e", [
    ("מ-ינואר עד מרץ", (2017, 1, 1), (2017, 4, 1)),
    ("מ-יוני עד אוגוסט", (2017, 6, 1), (2017, 9, 1)),
    ("מ-15 בינואר עד 20 בינואר", (2018, 1, 15), (2018, 1, 21)),
])
def test_word_framed_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


# -- adversarial: a bare range connector with no valid endpoints must not crash
# and must not fabricate a span.
@pytest.mark.parametrize("text", ["מ", "עד", "בין", "מ עד"])
def test_bare_connector_is_nomatch(text):
    nomatch(text)
