# -*- coding: utf-8 -*-
"""The singular year word names one year, the plural names a decade.

Galician frames a decade with the plural "os anos 80"; the singular
"o ano 1980" names the single year 1980.  Golds are computed here by independent arithmetic: a year N spans
1 January of N to 1 January of N+1 and a decade opening on N spans ten
years to 1 January of N+10.  Every positive case asserts an empty
remainder, since a wrong reading with nothing left over gives the caller
no signal.
"""
from datetime import datetime

import pytest

from ._corpus import ad, parse


def resolved(text):
    r = parse(text)
    assert r is not None, f"{text!r} did not parse"
    span, remainder = r[0], r[1]
    assert remainder == "", f"{text!r} left remainder {remainder!r}"
    return span.start, span.end


def year(n):
    return ad(datetime(n, 1, 1)), ad(datetime(n + 1, 1, 1))


def decade(n):
    return ad(datetime(n, 1, 1)), ad(datetime(n + 10, 1, 1))


@pytest.mark.parametrize("n", [1914, 1980, 2000])
def test_singular_year_word_is_one_year(n):
    assert resolved(f"o ano {n}") == year(n)


@pytest.mark.parametrize("n", [1920, 1980, 2000])
def test_plural_year_word_is_a_decade(n):
    assert resolved(f"os anos {n}") == decade(n)


def test_plural_year_word_off_the_ten_is_one_year():
    assert resolved("os anos 1914") == year(1914)


# -- controls: surfaces that must keep working --------------------------


def test_bare_tens_decade():
    assert resolved("os anos 80") == decade(1980)


def test_spelled_tens_decade():
    assert resolved("os anos noventa") == decade(1990)


def test_early_part_of_a_decade():
    assert resolved("a principios dos anos 80") == (ad(datetime(1980, 1, 1)),
                                                    ad(datetime(1983, 1, 1)))


def test_late_part_of_a_spelled_decade():
    assert resolved("a finais dos anos noventa") == (ad(datetime(1997, 1, 1)),
                                                     ad(datetime(2000, 1, 1)))


def test_bare_year():
    assert resolved("1980") == year(1980)


def test_dated_day():
    assert resolved("15 de marzo de 2026") == (ad(datetime(2026, 3, 15)),
                                               ad(datetime(2026, 3, 16)))


def test_year_range():
    assert resolved("entre 2010 e 2020") == (ad(datetime(2010, 1, 1)),
                                             ad(datetime(2021, 1, 1)))


def test_decade_bc_unchanged():
    s, e = resolved("os anos 80 ac")
    assert (s.year, e.year) == (-88, -78)
