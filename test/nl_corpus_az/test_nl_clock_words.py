# -*- coding: utf-8 -*-
"""Spelled-out clock hours in Azerbaijani ("saat <number>").

Gold is independent arithmetic: a bare "saat H" names the next occurrence of
H:00 strictly after the anchor (2017-06-27 13:04).  So H>=14 lands the same
day; H<=13 rolls to the following morning.  The spelled numeral folds via
ovos-number-parser exactly like the digit form, so both must agree.
"""
from datetime import datetime, timedelta
import pytest
from chronologia.astrodate import AstroDate
from ._corpus import start, nomatch

A = datetime(2017, 6, 27, 13, 4)

_WORD = {
    1: "bir", 2: "iki", 3: "üç", 4: "dörd", 5: "beş", 6: "altı",
    7: "yeddi", 8: "səkkiz", 9: "doqquz", 10: "on", 11: "on bir",
    12: "on iki", 13: "on üç", 14: "on dörd", 15: "on beş", 16: "on altı",
    17: "on yeddi", 18: "on səkkiz", 19: "on doqquz", 20: "iyirmi",
    21: "iyirmi bir", 22: "iyirmi iki", 23: "iyirmi üç",
}


def _next_hour(h):
    cand = A.replace(hour=h, minute=0, second=0, microsecond=0)
    if cand <= A:
        cand += timedelta(days=1)
    return cand


@pytest.mark.parametrize("h", list(range(1, 24)))
def test_saat_spelled_hour(h):
    g = _next_hour(h)
    s = start("saat " + _WORD[h], A)
    assert s == AstroDate(g.year, g.month, g.day, h, 0)


@pytest.mark.parametrize("h", list(range(1, 24)))
def test_saat_spelled_matches_digit(h):
    # The spelled form must resolve identically to the digit form.
    assert start("saat " + _WORD[h], A) == start("saat %d" % h, A)


def test_gunorta_is_next_noon():
    # 12:00 has already passed at 13:04, so noon rolls to the next day.
    g = _next_hour(12)
    assert start("günorta", A) == AstroDate(g.year, g.month, g.day, 12, 0)


def test_gece_yarisi_is_next_midnight():
    assert start("gecə yarısı", A) == AstroDate(2017, 6, 28, 0, 0)


def test_locative_hour_suffix_should_parse():
    # 'saat üçdə' = 'at three o'clock' — idiomatic az; currently no-parse.
    assert start("saat üçdə", A).hour == 3
