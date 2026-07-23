# -*- coding: utf-8 -*-
"""Ranges.  Dash-framed ranges parse language-agnostically; the word-framed
Romance forms ("de juny a agost", "entre ... i ...") parse too -- the "from"
lead ("de"/"des de") and "to"/"between" connectors ship per-locale, so range
framing is not English-only.  Because Catalan "a" is a hyper-common preposition
("a les tres", "anem a Barcelona"), a bare "A a B" is only trusted as a range
when a "from" lead disambiguates it -- the adversarial cases below pin that down."""
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


@pytest.mark.parametrize("text,s,e", [
    ("de juny a agost", (2017, 6, 1), (2017, 9, 1)),
    ("de juny fins a agost", (2017, 6, 1), (2017, 9, 1)),
    ("entre juny i agost", (2017, 6, 1), (2017, 9, 1)),
    ("de 5 de juny a 12 de juny", (2018, 6, 5), (2018, 6, 13)),
])
def test_word_framed_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


# -- adversarial: the "a" trap.  "a" is also the clock preposition ("a les 3"),
# so a bare "<month> a <time>" / "a les tres" must NEVER become a bounded range;
# without a "from" lead the "a"-connector is untrusted and the normal single-span
# path runs (a minute-wide clock span), while a non-temporal endpoint is nomatch.
def test_a_trap_bare_month_plus_time_is_single_span():
    # "juny a les tres" folds month+clock into ONE minute-wide span, not a range
    ss, ee = start_end("juny a les tres")
    assert ss == AstroDate(2017, 6, 1, 3, 0) and ee == AstroDate(2017, 6, 1, 3, 1)


def test_a_trap_non_temporal_place_is_nomatch():
    nomatch("anem a Barcelona")


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
