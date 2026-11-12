# -*- coding: utf-8 -*-
"""A weekday beside a day word names the same day, or no day, pt.

An "aposto" is a "Nome ou locução nominal que se junta a outro nome para
melhor o caracterizar" (Priberam s.v. "aposto", 5).  In "amanhã, domingo"
the weekday characterises the day "amanhã" names, so the two name one day
and the weekday does not stay in the remainder.  When the weekday is not
that day's weekday ("amanhã segunda-feira" said on a Saturday), the phrase
names no single day, and the reading is refused.

Anchor Saturday 2026-10-17 12:00.  Gold comes from datetime arithmetic on
the anchor, and the weekday of each day from ``datetime.weekday``.
"""
from datetime import datetime, timedelta

import pytest

from ._corpus import ad, nomatch, parse

SATURDAY = datetime(2026, 10, 17, 12, 0)
DAY = SATURDAY.replace(hour=0)


@pytest.mark.parametrize("text,offset,hour", [
    ("amanhã domingo", 1, 0),
    ("amanhã, domingo", 1, 0),
    ("depois de amanhã segunda-feira", 2, 0),
    ("ontem sexta-feira", -1, 0),
    ("anteontem quinta-feira", -2, 0),
    ("hoje sábado", 0, 0),
    ("domingo amanhã", 1, 0),
    ("amanhã domingo às 10h", 1, 10),
])
def test_day_word_with_its_own_weekday(text, offset, hour):
    expected = DAY + timedelta(days=offset, hours=hour)
    r = parse(text, SATURDAY)
    assert r is not None, f"{text!r} did not parse"
    assert r.span.start == ad(expected)
    assert r.remainder == ""


@pytest.mark.parametrize("text", [
    "amanhã segunda-feira",
    "depois de amanhã sexta-feira",
    "anteontem segunda-feira",
    "ontem domingo",
])
def test_day_word_with_another_weekday_is_refused(text):
    nomatch(text, SATURDAY)


@pytest.mark.parametrize("text,offset,rest", [
    ("amanhã e segunda", 1, "e segunda"),
    ("amanhã ou domingo", 1, "ou domingo"),
])
def test_a_list_is_not_an_apposition(text, offset, rest):
    r = parse(text, SATURDAY)
    assert r.span.start == ad(DAY + timedelta(days=offset))
    assert r.remainder == rest
