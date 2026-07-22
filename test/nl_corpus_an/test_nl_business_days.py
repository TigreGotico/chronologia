# -*- coding: utf-8 -*-
"""Business days (an): ``en N diyas laborables`` ("in N working days").

A business day is a weekday (Aragonese weekend is Saturday + Sunday) that is
not a public holiday of the ``jurisdiction``.  Anchor Wednesday 2026-12-23.

Holiday-blind (weekend-only), from Wed:
    Thu24(1) Fri25(2) Mon28(3) Tue29(4) Wed30(5) Thu31(6)
Jurisdiction ES (skips Navidad 12-25, Anyo Nuevo 01-01, Reis 01-06):
    Thu24(1) Mon28(2) Tue29(3) Wed30(4) Thu31(5) Mon Jan4(6)"""
from datetime import date, datetime, timedelta
import pytest
from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

ANCHOR = datetime(2026, 12, 23, 9, 0)   # Wednesday


def start(text, jurisdiction=None):
    r = extract_timespan(text, "an", ANCHOR, jurisdiction=jurisdiction)
    assert r is not None, f"{text!r} did not resolve"
    return r[0].start


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


@pytest.mark.parametrize("text,expected", [
    ("en 1 diyas laborables", date(2026, 12, 24)),
    ("en 2 diyas laborables", date(2026, 12, 25)),
    ("en 3 diyas laborables", date(2026, 12, 28)),
    ("en 4 diyas laborables", date(2026, 12, 29)),
    ("en 6 diyas laborables", date(2026, 12, 31)),
])
def test_count_blind(text, expected):
    assert start(text) == _ad(expected)


@pytest.mark.parametrize("text,expected", [
    ("en 1 diyas laborables", date(2026, 12, 24)),
    ("en 2 diyas laborables", date(2026, 12, 28)),   # skips Navidad
    ("en 5 diyas laborables", date(2026, 12, 31)),
    ("en 6 diyas laborables", date(2027, 1, 4)),     # skips Anyo Nuevo + Reis
])
def test_count_es_jurisdiction(text, expected):
    assert start(text, "ES") == _ad(expected)


def test_span_is_one_day_wide():
    r = extract_timespan("en 3 diyas laborables", "an", ANCHOR,
                         jurisdiction="ES")
    assert r[0].width == timedelta(days=1)


@pytest.mark.parametrize("text", ["como siempre", "tot normal"])
def test_negatives(text):
    assert extract_timespan(text, "an", ANCHOR) is None
