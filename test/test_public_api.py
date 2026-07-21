"""Public surface + cross-module smoke integrations for chronologia."""
from datetime import date

import chronologia


EXPECTED_EXPORTS = {
    "AstroDate", "DateSpan", "is_leap_year",
    "CALENDARS", "Calendar", "gregorian_to_jdn", "jdn_to_gregorian",
    "julian_to_jdn", "jdn_to_julian",
    "ERAS", "Era", "EraCounting", "astro_year_range",
    "resolve_era", "resolve_era_year_span",
    "DAY_CYCLES", "DAY_SUBDIVISIONS", "DayCycle", "DaySubdivision",
    "resolve_cycle_day",
    "REGNAL_SEQUENCES", "RegnalSequence",
    "roman_to_julian",
    "DateTimeResolution",
}


def test_all_exports_present():
    assert EXPECTED_EXPORTS <= set(chronologia.__all__)
    for name in EXPECTED_EXPORTS:
        assert hasattr(chronologia, name), name


def test_registries_are_populated():
    assert chronologia.CALENDARS
    assert chronologia.ERAS
    assert chronologia.DAY_CYCLES
    assert chronologia.REGNAL_SEQUENCES


def test_astrodate_calendar_jdn_round_trip():
    # AstroDate <-> Gregorian calendar through the JDN hub
    a = chronologia.AstroDate(2025, 9, 23)
    jdn = chronologia.gregorian_to_jdn(a.year, a.month, a.day)
    assert chronologia.jdn_to_gregorian(jdn) == (2025, 9, 23)

    # every registered calendar is an integer inverse pair through JDN
    for cal in chronologia.CALENDARS.values():
        y, m, d = cal.from_jdn(jdn)
        assert cal.to_jdn(y, m, d) == jdn


def test_resolve_era_anno_mundi_exact():
    # AM 5786 begins at 1 Tishri 5786, resolved exactly through the
    # Hebrew calendar's own JDN hub -> 2025-09-23 Gregorian.
    assert chronologia.resolve_era("anno_mundi", 5786) == date(2025, 9, 23)


def test_datespan_resolution_is_derived():
    span = chronologia.DateSpan(
        chronologia.AstroDate(2027, 6, 1),
        chronologia.AstroDate(2027, 7, 1),
    )
    assert span.resolution is chronologia.DateTimeResolution.MONTH
