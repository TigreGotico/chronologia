"""Sweden national differential (source: Lag 1989:253 om allmänna helgdagar).

Per-holiday gold dates live in the shared HOLIDAY_GOLDS registry. Under Swedish law
every Sunday is also an "allmän helgdag", so the reference package lists all ~52
Sundays as bare "Söndag" entries. We ship only the named holidays; the differential
here compares our national public set against the reference with those bare
"Söndag" entries removed — and they agree exactly across 2023-2025 (the named
Sundays Påskdagen and Pingstdagen keep their own names and are matched).
"""
import holidays

from chronologia import AstroDate, holidays_for

_J = "SE"


def _our(year):
    return {(h.date.month, h.date.day) for h in holidays_for(_J, year)
            if h.subdiv is None and "public" in h.categories}


def _ref_named(year):
    """Reference set with the bare weekly-Sunday ("Söndag") entries removed."""
    return {(d.month, d.day)
            for d, n in holidays.country_holidays(_J, years=year).items()
            if n != "Söndag"}


def test_national_differential_named_days_2023_2025():
    for year in (2023, 2024, 2025):
        our, ref = _our(year), _ref_named(year)
        assert our - ref == set(), f"{year} our-only {sorted(our - ref)}"
        assert ref - our == set(), f"{year} ref-only {sorted(ref - our)}"


def test_midsommardagen_and_alla_helgons_are_saturdays():
    got = {h.name: h.date for h in holidays_for(_J, 2024)}
    # Midsummer Day: Saturday in 20-26 June (22 Jun 2024); All Saints: Saturday in
    # 31 Oct-6 Nov (2 Nov 2024).
    assert got["Midsommardagen"] == AstroDate(2024, 6, 22)
    assert got["Alla helgons dag"] == AstroDate(2024, 11, 2)
    assert got["Midsommardagen"].weekday() == 5
    assert got["Alla helgons dag"].weekday() == 5
