# -*- coding: utf-8 -*-
"""Business days (mwl): ``an N dies laborales`` ("in N working days").

A business day is a weekday (weekend is Saturday + Sunday) that is not a public
holiday of the ``jurisdiction``.  Anchor Wednesday 2026-12-23.

Holiday-blind (weekend-only), from Wed:
    Thu24(1) Fri25(2) Mon28(3) Tue29(4) Wed30(5) Thu31(6)
Jurisdiction PT (skips Natal 12-25, Ano Novo 01-01):
    Thu24(1) Mon28(2) Tue29(3) Wed30(4) Thu31(5) Mon Jan4(6)"""
from datetime import date, datetime, timedelta
import pytest
from chronologia import extract_timespan
from chronologia.astrodate import AstroDate

ANCHOR = datetime(2026, 12, 23, 9, 0)   # Wednesday


def start(text, jurisdiction=None):
    r = extract_timespan(text, "mwl", ANCHOR, jurisdiction=jurisdiction)
    assert r is not None, f"{text!r} did not resolve"
    return r[0].start


def _ad(d):
    return AstroDate(d.year, d.month, d.day)


@pytest.mark.parametrize("text,expected", [
    ("an 1 dies laborales", date(2026, 12, 24)),
    ("an 2 dies laborales", date(2026, 12, 25)),
    ("an 3 dies laborales", date(2026, 12, 28)),
    ("an 4 dies laborales", date(2026, 12, 29)),
    ("an 6 dies laborales", date(2026, 12, 31)),
])
def test_count_blind(text, expected):
    assert start(text) == _ad(expected)


@pytest.mark.parametrize("text,expected", [
    ("an 1 dies laborales", date(2026, 12, 24)),
    ("an 2 dies laborales", date(2026, 12, 28)),   # skips Natal
    ("an 6 dies laborales", date(2027, 1, 4)),     # skips Ano Novo
])
def test_count_pt_jurisdiction(text, expected):
    assert start(text, "PT") == _ad(expected)


def test_span_is_one_day_wide():
    r = extract_timespan("an 3 dies laborales", "mwl", ANCHOR,
                         jurisdiction="PT")
    assert r[0].width == timedelta(days=1)


@pytest.mark.parametrize("text", ["cumo siempre", "todo normal"])
def test_negatives(text):
    assert extract_timespan(text, "mwl", ANCHOR) is None
