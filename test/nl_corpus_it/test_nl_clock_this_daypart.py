"""A clock before "di questo pomeriggio", "di questa sera" or "di stasera"
falls in that part of today.

"stasera" is the fused form of "questa sera", so "le dieci di stasera" is
22:00 today.  The gold is clock arithmetic: the spoken hour plus 12 on the
anchor day, Tuesday 2017-06-27.
"""
from datetime import datetime

import pytest

from ._corpus import ANCHOR, ad, parse, span


@pytest.mark.parametrize("text,hour,minute", [
    ("alle due di questo pomeriggio", 14, 0),
    ("per le tre di questo pomeriggio", 15, 0),
    ("per le dieci di questa sera", 22, 0),
    ("alle nove e mezza di questa sera", 21, 30),
    ("per le dieci di stasera", 22, 0),
    ("per le sette di stasera", 19, 0),
])
def test_clock_before_this_daypart(text, hour, minute):
    assert span(text).start == ad(ANCHOR.replace(hour=hour, minute=minute))


@pytest.mark.parametrize("text,hour", [
    ("ci vediamo stasera", 18),
    ("Stasera passo da mia sorella.", 18),
    ("Stamattina ho incontrato Lucia al mercato.", 6),
])
def test_fused_daypart_alone(text, hour):
    """CLDR 47 it bands: mattina from 06:00, sera from 18:00."""
    assert span(text).start == ad(ANCHOR.replace(hour=hour, minute=0))


def test_clock_after_stasera():
    assert span("stasera alle 10").start == ad(ANCHOR.replace(hour=22, minute=0))
    assert parse("stasera alle 10")[1].strip() == ""
    oct17 = datetime(2026, 10, 17, 12, 0)
    got = span("stasera dieci meno un quarto", oct17).start
    assert got == ad(oct17.replace(hour=21, minute=45))


@pytest.mark.xfail(strict=True, reason="chronologia#1560: 'da' in a noun phrase opens a range")
def test_da_in_noun_phrase_is_no_range_start():
    got = span("il campo da tennis per stasera alle nove")
    assert (got.start, got.end) == (ad(ANCHOR.replace(hour=21, minute=0)),
                                    ad(ANCHOR.replace(hour=21, minute=1)))
