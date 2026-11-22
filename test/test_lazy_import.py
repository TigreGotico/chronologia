"""The package loads its heavy submodules on first use, not on import."""
import ast
import importlib
from pathlib import Path
import subprocess
import sys

import chronologia

DEV_ALL = frozenset({
    "AGE_OF_UNIVERSE_ERA", "ASR_METHODS", "AXES", "AmbiguousPeriodError",
    "AsrMethod", "AstroDate", "BABYLONIAN_HOURS", "CALENDARS",
    "CATEGORIES", "CLDR_VERSION", "CLOCK_CONVENTIONS", "CONVENTIONS",
    "COSMIC_PERIODS", "COSMOLOGIES", "Calendar", "CalendarDate",
    "CalendarDateRule", "CalendarRangeError", "Candidate", "CivilHoliday",
    "CivilLabel", "ClockConvention", "ClockSegment", "ClockTimeline",
    "CosmologyParams", "DARIAN_EPOCH_MSD", "DARIAN_MONTHS",
    "DARIAN_WEEKDAYS", "DAY_CYCLES", "DAY_PARTS", "DAY_SUBDIVISIONS",
    "DarianCalendar", "DarianDate", "DateSpan", "DateSpanResult",
    "DateTimeResolution", "DayCycle", "DayPart", "DaySubdivision",
    "DecreeTableRule", "Discontinuity", "DiscontinuityKind",
    "DurationResult", "EARTH_DAY_SECONDS", "EASTER_METHODS",
    "EDO_JAPANESE", "EOT_ACCURACY", "EPOCH_NEW_MOON", "EQUINOX_ACCURACY",
    "ERAS", "ERA_ALIASES", "EasterOffsetRule", "EdtfDate",
    "EdtfParseError", "Era", "EraCounting", "Event", "ExcludeRule",
    "FIXED_FEASTS", "FixedRule", "GPS_EPOCH", "HEAT_DEATH_YEAR",
    "HUBBLE_TIME_GYR", "HolidayCalendar", "HolidayRecurrence",
    "HolidayRule", "ICS_CHART_VERSION", "IL_INDEPENDENCE_SHIFT",
    "INTCAL20_COARSE", "ITALIAN_HOURS", "ImpossibleDateError",
    "JurisdictionHolidays", "LEAP_SECONDS", "LMTZone",
    "LTC_DRIFT_MICROSECONDS_PER_DAY", "LTC_STATUS", "LUNAR_DAY_SECONDS",
    "LunarTimeStandardStatus", "MARS_SOL_RATIO", "MARS_SOL_SECONDS",
    "MEAN_SYNODIC_MONTH_DAYS", "MISSION_ERAS", "MOON_PHASE_ACCURACY",
    "MOVABLE_FEAST_OFFSETS", "MarsDate", "Mission", "NL_KINGSDAY_SHIFT",
    "NamedPeriod", "NearestWeekdayRule", "NeverExisted", "NoSunEvent",
    "NthWeekdayRule", "ObservedShift", "OneOffRule", "PERIODS",
    "PrayerConvention", "PrayerTimes", "REGNAL_SEQUENCES", "ROMAN_HOURS",
    "Recurrence", "RecurrenceResult", "RegnalSequence",
    "SATURDAY_SUNDAY_TO_MONDAY", "SOLAR_ACCURACY", "SOLAR_TERM_ACCURACY",
    "SOLAR_TERM_NAMES", "SUNDAY_TO_MONDAY", "SolarEventRule", "SunEvents",
    "TABLE_VALID_UNTIL", "TAI_MINUS_GPS", "TIMELINES", "TT_MINUS_TAI",
    "TabulatedCalendar", "TimeAxis", "TimeMention", "Timeline",
    "TimelineSegment", "UNEQUAL_HOUR_SYSTEMS", "UNIVERSE_AGE_GYR",
    "UNIVERSE_AGE_UNCERTAINTY_GYR", "US_OBSERVED_SHIFT", "UncertainEra",
    "UnequalHourSystem", "UnknownDayPartError", "VALID_YEAR_RANGE",
    "WideDuration", "YEAR_CYCLES", "YearCycle", "ZMANIM_GRA",
    "ZoneDiscontinuity", "ZoneNeverExisted", "advent_sunday",
    "age_of_universe_gyr", "apparent_solar_time", "astro_from_jd",
    "astro_year_range", "astronomical_season_span", "calibrate_c14",
    "candidates", "children", "civil_add", "combine_basis",
    "convention_time", "coverage", "darian", "daypart_span", "easter",
    "equation_of_time", "equinox", "every", "explain",
    "extract_candidates", "extract_duration", "extract_event",
    "extract_recurrence", "extract_timespan", "extract_timespans",
    "fixed_feast", "format_edtf", "from_ical", "from_json", "gps_to_utc",
    "gregorian_to_jdn", "holidays_for", "is_civil_holiday",
    "is_leap_second_day", "is_leap_year", "jd_of", "jdn_to_gregorian",
    "jdn_to_julian", "julian_to_jdn", "last_weekday_of_month",
    "load_calendar", "load_translations", "local_mean_time",
    "lookback_gyr", "lookback_time", "lookup", "ltc_offset",
    "lunation_number", "mission_sol", "moon_phase", "movable_feast",
    "msd_from_tt", "next_phase", "nth_weekday_of_month", "occurrences",
    "parse_edtf", "parse_name_cell", "parse_rrule", "prayer_times",
    "previous_phase", "proleptic", "register_event_provider",
    "resolve_bp", "resolve_cosmic", "resolve_cycle_day", "resolve_era",
    "resolve_era_year_span", "resolve_wall_clock", "roman_to_julian",
    "solar_term", "subdivide", "sun_events", "sunset_day_start",
    "table_valid_until", "tai_to_utc", "temporal_hour_span", "to_ical",
    "to_json", "to_mars", "tt_from_msd", "tt_to_utc", "utc_tai_offset",
    "utc_to_gps", "utc_to_tai", "utc_to_tt", "year_cycle_label",
    "years_of", "zone_history_start", "zone_timeline"
})

HEAVY = ("eras", "civil_holidays", "mars", "luna", "cosmology", "moon", "ical")


def _loaded_after(statement: str) -> set:
    code = (f"import sys; {statement}; "
            f"print(*[m for m in sys.modules if m.startswith('chronologia.')])")
    out = subprocess.run([sys.executable, "-c", code], capture_output=True,
                         text=True, check=True).stdout
    return set(out.split())


def test_import_skips_heavy_modules():
    loaded = _loaded_after("import chronologia")
    for name in HEAVY:
        assert f"chronologia.{name}" not in loaded, name


def test_extractor_import_skips_calendar_extras():
    loaded = _loaded_after("from chronologia.extract import extract_timespan")
    for name in ("eras", "mars", "luna", "cosmology", "moon", "ical"):
        assert f"chronologia.{name}" not in loaded, name


def test_first_access_loads_the_module():
    loaded = _loaded_after("import chronologia; chronologia.ERAS")
    assert "chronologia.eras" in loaded


def test_every_exported_name_is_the_defining_modules_object():
    assert set(chronologia.__all__) == DEV_ALL
    assert set(chronologia._MODULE_OF) == DEV_ALL
    for name, module in chronologia._MODULE_OF.items():
        defined = getattr(importlib.import_module(module), name)
        assert getattr(chronologia, name) is defined, name


def test_dir_lists_every_exported_name():
    assert set(chronologia.__all__) <= set(dir(chronologia))


def test_prayer_times_is_the_function():
    from chronologia.prayer_times import PrayerTimes  # noqa: F401
    assert callable(chronologia.prayer_times)


def test_type_checking_imports_match_the_export_table():
    tree = ast.parse(Path(chronologia.__file__).read_text(encoding="utf-8"))
    block = next(n for n in tree.body if isinstance(n, ast.If)
                 and getattr(n.test, "id", None) == "TYPE_CHECKING")
    imported = {n.module: {a.name for a in n.names}
                for n in block.body if isinstance(n, ast.ImportFrom)}
    assert imported == {m: set(names)
                        for m, names in chronologia._EXPORTS.items()}
