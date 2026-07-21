"""Shared assertions for the per-country civil-holiday gold suites.

Kept separate from :mod:`holiday_golds` (pure data registry) so the country
modules share exactly one implementation of "does this gold resolve?" and "does
our national set agree with the reference package?".
"""
from __future__ import annotations

from datetime import timedelta

from chronologia import AstroDate, holidays_for
from chronologia.computus import easter

from holiday_golds import Gold


def assert_gold(gold: Gold) -> None:
    """A holiday named ``gold.name`` under its subdiv resolves to the gold date.

    For movable golds (``easter_offset`` set) the expected date is re-derived
    independently in-test as ``easter(year, method) + offset`` and cross-checked
    against the stated ``(month, day)`` — never read back from the rule engine.
    """
    expected = AstroDate(gold.year, gold.month, gold.day)
    if gold.easter_offset is not None:
        recomputed = easter(gold.year, gold.easter_method) + timedelta(
            days=gold.easter_offset)
        assert recomputed == expected, (
            f"{gold.name}: source phrase easter{gold.easter_offset:+d} = "
            f"{recomputed.date()}, gold says {expected.date()}")
    hs = holidays_for(gold.jurisdiction, gold.year, subdiv=gold.subdiv)
    matches = [h for h in hs if h.name == gold.name
               and h.subdiv == gold.subdiv]
    assert matches, (
        f"no holiday named {gold.name!r} (subdiv={gold.subdiv}) in "
        f"{gold.jurisdiction} {gold.year}")
    assert expected in {h.date for h in matches}, (
        f"{gold.jurisdiction}/{gold.subdiv} {gold.name} {gold.year}: "
        f"expected {expected.date()}, got {[m.date.date() for m in matches]}")


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
