# -*- coding: utf-8 -*-
"""Closed ranges written with «по» (uk).

«з ... по ...» names an inclusive period: Словник української мови в 11 томах,
т. 6, s.v. «по», знач. 13, «у сполуч. з прийм. з ... уживається при вказуванні
на кінець дії, стану» -- «З березня по вересень 1917 року», «XXIII з'їзд КПРС
відбувався з 29 березня по 8 квітня 1966 року», a congress that sat on 8 April
too.  So «з 5 по 12 червня» ends at the end of 12 June.

«по» was missing from the vocabulary, so the closed range degraded into the
open one: «з 5 червня» to the anchor instant, with «по 12 червня» left over.

Anchor 2017-06-27 13:04; every edge hand-derived."""
import pytest

from ._corpus import AstroDate, ANCHOR, ad, parse, start_end


@pytest.mark.parametrize("text", [
    "з 5 червня по 12 червня",
    "з 5 по 12 червня",
    "з 5 червня до 12 червня",
])
def test_po_range_ends_after_the_named_day(text):
    ss, ee = start_end(text)
    assert ss == AstroDate(2018, 6, 5)
    assert ee == AstroDate(2018, 6, 13)


@pytest.mark.parametrize("text,s,e", [
    ("з 28 червня по 3 липня", (2017, 6, 28), (2017, 7, 4)),
    ("з 28 грудня по 3 січня", (2017, 12, 28), (2018, 1, 4)),
])
def test_po_range_crosses_month_and_year(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


def test_po_range_consumes_its_framing_words():
    assert parse("з 5 червня по 12 червня").remainder == ""


def test_since_reading_survives():
    s, e = start_end("з 2010")
    assert s == AstroDate(2010, 1, 1) and e == ad(ANCHOR)


@pytest.mark.parametrize("text", ["по", "з по", "з 5 по", "по понеділках"])
def test_po_garbage_never_raises(text):
    parse(text)
