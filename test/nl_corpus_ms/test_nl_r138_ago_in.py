# -*- coding: utf-8 -*-
"""Regression for R138: ms 'yang lalu'/'lalu' (ago) and ms/id 'dalam <duration>'
(in <duration>) offsets.

Before the fix, Malay had no 'lalu'/'yang lalu' past marker at all (only
'lepas'), so every 'lalu' phrase silently failed to parse. Neither ms nor id
had a preposed 'dalam' (in) marker, so 'dalam 3 hari' silently failed to
parse in both languages, even though the postposed 'lagi' sibling worked.

Anchor is 2026-07-15 12:00 (Wednesday), from ``_corpus.ANCHOR``.
"""
from datetime import timedelta

import pytest

from ._corpus import ANCHOR, start, nomatch

A = ANCHOR


@pytest.mark.parametrize("text,days", [
    ("3 hari lalu", -3), ("3 hari yang lalu", -3), ("5 hari lalu", -5),
])
def test_ms_yang_lalu_day_offsets(text, days):
    exp = (A + timedelta(days=days)).date()
    assert (start(text).month, start(text).day) == (exp.month, exp.day)


@pytest.mark.parametrize("text,days", [
    ("dalam 3 hari", 3), ("dalam 5 hari", 5),
])
def test_ms_dalam_day_offsets(text, days):
    exp = (A + timedelta(days=days)).date()
    assert (start(text).month, start(text).day) == (exp.month, exp.day)


@pytest.mark.parametrize("text,days", [
    ("3 hari lagi", 3), ("1 hari lagi", 1),
])
def test_ms_lagi_control_unchanged(text, days):
    exp = (A + timedelta(days=days)).date()
    assert (start(text).month, start(text).day) == (exp.month, exp.day)


@pytest.mark.parametrize("text,weeks", [
    ("minggu lalu", -1),
])
def test_ms_minggu_lalu(text, weeks):
    exp = (A + timedelta(weeks=weeks)).date()
    s = start(text)
    assert (s.year, s.month) <= (exp.year, exp.month)
    # minggu lalu resolves to the bare "last week" span; just assert it parses
    # and lands strictly before the anchor.
    assert s.date() < A.date()


def test_ms_minggu_depan_control_unchanged():
    s = start("minggu depan")
    assert s.date() > A.date()


def test_ms_bulan_lalu():
    s = start("bulan lalu")
    assert s.date() < A.date()
    assert s.month == 6


def test_ms_bulan_depan_control_unchanged():
    s = start("bulan depan")
    assert s.month == 8


def test_ms_tahun_lalu():
    s = start("tahun lalu")
    assert s.year == 2025


def test_ms_tahun_depan_control_unchanged():
    s = start("tahun depan")
    assert s.year == 2027
