# -*- coding: utf-8 -*-
"""The singular year word names one year, the plural names a decade.

Aragonese frames a decade with the plural "os anyos 80"; the
singular "anyo 1980" names the single year 1980.  Golds are computed here by independent arithmetic: a year N spans
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
    assert resolved(f"o anyo {n}") == year(n)


@pytest.mark.parametrize("n", [1920, 1980, 2000])
def test_plural_year_word_is_a_decade(n):
    assert resolved(f"os anyos {n}") == decade(n)


def test_plural_year_word_off_the_ten_is_one_year():
    assert resolved("os anyos 1914") == year(1914)


# -- controls: surfaces that must keep working --------------------------


def test_bare_tens_decade():
    assert resolved("os anyos 80") == decade(1980)


def test_spelled_tens_decade():
    assert resolved("os anyos noranta") == decade(1990)


def test_castilianised_singular_is_one_year():
    assert resolved("año 1980") == year(1980)


def test_bare_year():
    assert resolved("1980") == year(1980)


def test_dated_day():
    assert resolved("15 de marzo de 2026") == (ad(datetime(2026, 3, 15)),
                                               ad(datetime(2026, 3, 16)))
