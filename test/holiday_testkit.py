"""Shared national-differential assertions for the per-country holiday suites.

Per-holiday gold DATES are frozen in the per-jurisdiction data files under
``test/holiday_golds/`` (walked, structurally enforced, and provenance-tiered by
test_holiday_golds.py). This module carries only the differential machinery each
country module reuses to compare our national set against the independent
reference package.
"""
from __future__ import annotations

from chronologia import holidays_for


def national_public_dates(jurisdiction: str, year: int):
    """Our jurisdiction-wide (subdiv None) ``public`` holidays as {(month, day)}."""
    return {(h.date.month, h.date.day)
            for h in holidays_for(jurisdiction, year)
            if h.subdiv is None and "public" in h.categories}


def reference_dates(jurisdiction: str, year: int, observed: bool = True):
    """The vacanza/holidays national set as {(month, day)} (differential ref)."""
    import holidays as _pkg
    return {(d.month, d.day)
            for d in _pkg.country_holidays(jurisdiction, years=year,
                                           observed=observed)}


def assert_national_differential(jurisdiction, years, expected_disagreements):
    """Compare our national public set with the reference, year by year.

    ``expected_disagreements`` maps ``year -> {"our_only": {(m,d),...},
    "ref_only": {(m,d),...}}``; every real disagreement must be listed there
    (each carries a primary-source justification in the calling module's
    docstring). An undocumented disagreement fails the test.
    """
    for year in years:
        our = national_public_dates(jurisdiction, year)
        ref = reference_dates(jurisdiction, year)
        want = expected_disagreements.get(year, {})
        assert our - ref == set(want.get("our_only", set())), (
            f"{jurisdiction} {year} undocumented our-only "
            f"{sorted(our - ref)}")
        assert ref - our == set(want.get("ref_only", set())), (
            f"{jurisdiction} {year} undocumented ref-only "
            f"{sorted(ref - our)}")
