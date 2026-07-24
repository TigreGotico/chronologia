# -*- coding: utf-8 -*-
"""Closed ranges written with «по» (ru).

«с ... по ...» is the standard Russian inclusive date range, and «по» with the
accusative names the limit *including* the day it names: Ожегов, Шведова,
Толковый словарь русского языка, s.v. «по», II.1 «Вплоть до (какого-н. места
или времени)» -- «Прочитать с первой по десятую главу», «Отпуск по
воскресенье»; Большой толковый словарь русского языка (С. А. Кузнецов, ред.),
s.v. «по», II.2 «при указании временного предела действия» -- «Проездной
действителен по март месяц», «Оплата с января по апрель».  So «с 5 по 12
июня» ends at the end of 12 June, not at its start.

«по» used to be missing from the vocabulary altogether, which made the closed
range degrade into the OPEN one: «с 5 июня» to the anchor instant, a strictly
wider span than was said, with «по 12 июня» left in the remainder.

Anchor 2017-06-27 13:04; every edge hand-derived."""
import pytest

from ._corpus import AstroDate, ANCHOR, ad, parse, start_end, nomatch


@pytest.mark.parametrize("text", [
    "с 5 июня по 12 июня",
    "с 5 по 12 июня",
    "с 5 июня до 12 июня",
])
def test_po_range_ends_after_the_named_day(text):
    ss, ee = start_end(text)
    assert ss == AstroDate(2018, 6, 5)
    assert ee == AstroDate(2018, 6, 13)


@pytest.mark.parametrize("text,s,e", [
    ("с 28 июня по 3 июля", (2017, 6, 28), (2017, 7, 4)),
    ("с 28 декабря по 3 января", (2017, 12, 28), (2018, 1, 4)),
    # the straddle repair: the left endpoint is pulled back a year so the
    # pair reads as the nearest calendar year rather than inverting
    ("с 1 января по 31 декабря", (2017, 1, 1), (2018, 1, 1)),
])
def test_po_range_crosses_month_and_year(text, s, e):
    ss, ee = start_end(text)
    assert ss == AstroDate(*s) and ee == AstroDate(*e)


def test_po_range_consumes_its_framing_words():
    assert parse("с 5 июня по 12 июня").remainder == ""


# -- adversarial ------------------------------------------------------------

def test_leading_po_alone_is_not_a_closed_range():
    # nothing to the left of the marker, so no closed range can be built and
    # «до 2020» stays the open reading it always was
    s, e = start_end("до 2020")
    assert s == ad(ANCHOR) and e == AstroDate(2021, 1, 1)


def test_since_reading_survives():
    s, e = start_end("с 2010")
    assert s == AstroDate(2010, 1, 1) and e == ad(ANCHOR)


@pytest.mark.parametrize("text", ["по", "с по", "с 5 по", "по понедельникам"])
def test_po_garbage_never_raises(text):
    parse(text)
