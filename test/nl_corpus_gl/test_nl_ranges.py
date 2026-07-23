# -*- coding: utf-8 -*-
"""Ranges.  Dash-framed ranges parse language-agnostically; the word-framed
Romance forms ("de xuño a agosto", "entre ... e ...") parse too -- the "from"
lead ("de"/"desde") and "to"/"between" connectors ship per-locale, so range
framing is not English-only.  Because Galician "a" is a hyper-common preposition
("ás tres", "imos a Vigo"), a bare "A a B" is only trusted as a range when a
"from" lead disambiguates it -- the adversarial cases below pin that down."""
import pytest

from ._corpus import AstroDate, start_end, nomatch


@pytest.mark.parametrize("text,s,e", [
    ("xuño - agosto", (2017, 6, 1), (2017, 9, 1)),
    ("xaneiro - marzo", (2017, 1, 1), (2017, 4, 1)),
    ("5 de xuño - 12 de xuño", (2018, 6, 5), (2018, 6, 13)),
])
def test_dash_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


@pytest.mark.parametrize("text,s,e", [
    ("de xuño a agosto", (2017, 6, 1), (2017, 9, 1)),
    ("de xuño ata agosto", (2017, 6, 1), (2017, 9, 1)),
    ("entre xuño e agosto", (2017, 6, 1), (2017, 9, 1)),
    ("de 5 de xuño a 12 de xuño", (2018, 6, 5), (2018, 6, 13)),
])
def test_word_framed_range(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


# -- adversarial: the "a" trap.  "a" is also the clock preposition ("ás tres"),
# so a bare "A a B" must NEVER fabricate a bounded range without a "from" lead.
def test_a_trap_bare_month_pair_is_single_span():
    # "xuño a agosto" -- no "from" lead, so "a" is untrusted: the normal
    # single-span path runs and yields June alone, NOT a June-September range.
    ss, ee = start_end("xuño a agosto")
    assert ss == AstroDate(2017, 6, 1) and ee == AstroDate(2017, 7, 1)


def test_a_trap_clock_is_single_span():
    # "ás tres" is a clock time, a minute-wide span -- never a range boundary.
    ss, ee = start_end("ás tres")
    assert ss == AstroDate(2017, 6, 28, 3, 0) and ee == AstroDate(2017, 6, 28, 3, 1)


def test_a_trap_non_temporal_place_is_nomatch():
    nomatch("imos a Vigo")


# -- open-ended ranges: "ata" (open start) / "desde" (open end) -------------
from ._corpus import ANCHOR, ad  # noqa: E402


def test_ata_open_start():
    s, e = start_end("ata venres")
    assert s == ad(ANCHOR)
    assert e == AstroDate(2017, 7, 1)


def test_desde_open_end():
    s, e = start_end("desde 2010")
    assert s == AstroDate(2010, 1, 1)
    assert e == ad(ANCHOR)
