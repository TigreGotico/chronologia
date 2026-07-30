"""Era year-start not on 1 January: the Byzantine Anno Mundi reckoning.

The Byzantine (Creation) era numbers the Gregorian calendar but begins its
civil year on 1 September (Wikipedia, "Byzantine calendar": epoch 1 Sep
5509 BC; AD 2026 -> AM 7535 after 1 September).  ``resolve_era_year_span``
returns the half-open [start, next-start) span, so era years tile with no
gap across the September boundary.
"""
import pytest

from chronologia.astrodate import AstroDate
from chronologia.eras import (ERAS, resolve_era, resolve_era_year_span)


def test_byzantine_am_7535_spans_september_to_september():
    start, end = resolve_era_year_span("byzantine_am", 7535)
    assert start == AstroDate(2026, 9, 1)
    assert end == AstroDate(2027, 9, 1)


def test_byzantine_am_year_start_is_september():
    assert ERAS["byzantine_am"].year_start == (9, 1)


def test_byzantine_am_start_matches_resolve_era_point():
    # resolve_era returns the era-year *start*; the span's start agrees
    start, _ = resolve_era_year_span("byzantine_am", 7535)
    assert resolve_era("byzantine_am", 7535) == start.date()


def test_byzantine_am_years_tile():
    _, end_a = resolve_era_year_span("byzantine_am", 7535)
    start_b, _ = resolve_era_year_span("byzantine_am", 7536)
    assert end_a == start_b                              # no gap, no overlap


def test_anno_mundi_span_still_tishri():
    # the pre-existing Hebrew Anno Mundi keeps its Tishri (month 7) year start
    start, end = resolve_era_year_span("anno_mundi", 5786)
    assert start == AstroDate(2025, 9, 23)              # 1 Tishri 5786
    assert (end - start).days in (353, 354, 355, 383, 384, 385)


def test_span_requires_calendar_backed_era():
    with pytest.raises(ValueError):
        resolve_era_year_span("before_christ", 44)
