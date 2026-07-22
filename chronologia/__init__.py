"""chronologia — a general-purpose calendrical and chronological core.

An unbounded, ``datetime``-compatible point type (:class:`AstroDate`), a
half-open interval result type (:class:`DateSpan`), a Julian-Day-Number
calendar registry (:data:`CALENDARS`), and the reckoning layers built on
top of them: eras (year-numbering conventions attached to a calendar),
day cycles, regnal sequences, and Roman-calendar dates.

Everything reduces to the JDN hub, so conversions compose: an
:class:`AstroDate` round-trips through any registered :class:`Calendar`,
and calendar-backed eras (Anno Mundi, French Republican, Bahai) resolve
*exactly* rather than by an epoch-plus-count approximation.
"""
from chronologia.astrodate import (AstroDate, DateSpan, WideDuration,
                                   civil_add, combine_basis, is_leap_year,
                                   resolve_wall_clock)
from chronologia.calendars import (CALENDARS, Calendar, CalendarDate,
                                   CalendarRangeError, TabulatedCalendar,
                                   gregorian_to_jdn, jdn_to_gregorian,
                                   julian_to_jdn, jdn_to_julian,
                                   register_event_provider)
from chronologia.cycles import (DAY_CYCLES, DAY_SUBDIVISIONS, YEAR_CYCLES,
                                DayCycle, DaySubdivision, YearCycle,
                                resolve_cycle_day, year_cycle_label,
                                years_of)
from chronologia.dayparts import (CLDR_VERSION, DAY_PARTS, DayPart,
                                  UnknownDayPartError, daypart_span)
from chronologia.edtf import (EdtfDate, EdtfParseError, format_edtf,
                             parse_edtf)
from chronologia.eras import (ERAS, Era, EraCounting, astro_year_range,
                              resolve_bp, resolve_era, resolve_era_year_span)
from chronologia.axes import (AXES, EARTH_DAY_SECONDS, MARS_SOL_RATIO,
                              MARS_SOL_SECONDS, TimeAxis, astro_from_jd, jd_of)
from chronologia.leapseconds import (GPS_EPOCH, LEAP_SECONDS,
                                     TABLE_VALID_UNTIL, TAI_MINUS_GPS,
                                     TT_MINUS_TAI, gps_to_utc,
                                     is_leap_second_day, table_valid_until,
                                     tai_to_utc, tt_to_utc, utc_tai_offset,
                                     utc_to_gps, utc_to_tai, utc_to_tt)
from chronologia.mars import (DARIAN_EPOCH_MSD, DARIAN_MONTHS, DARIAN_WEEKDAYS,
                              MISSION_ERAS, DarianCalendar, DarianDate,
                              MarsDate, Mission, darian, mission_sol,
                              msd_from_tt, to_mars, tt_from_msd)
from chronologia.localtime import (EOT_ACCURACY, LMTZone, apparent_solar_time,
                                   equation_of_time, local_mean_time)
from chronologia.moon import (EPOCH_NEW_MOON, MEAN_SYNODIC_MONTH_DAYS,
                              MOON_PHASE_ACCURACY, lunation_number, moon_phase,
                              next_phase, previous_phase)
from chronologia.equinoxes import (EQUINOX_ACCURACY, SOLAR_TERM_ACCURACY,
                                   SOLAR_TERM_NAMES, VALID_YEAR_RANGE,
                                   astronomical_season_span, equinox,
                                   solar_term)
from chronologia.luna import (LTC_DRIFT_MICROSECONDS_PER_DAY, LTC_STATUS,
                              LUNAR_DAY_SECONDS, LunarTimeStandardStatus,
                              ltc_offset)
from chronologia.computus import (EASTER_METHODS, FIXED_FEASTS,
                                  MOVABLE_FEAST_OFFSETS, advent_sunday, easter,
                                  fixed_feast, movable_feast)
from chronologia.cosmology import (AGE_OF_UNIVERSE_ERA, COSMIC_PERIODS,
                                   COSMOLOGIES, HUBBLE_TIME_GYR,
                                   UNIVERSE_AGE_GYR,
                                   UNIVERSE_AGE_UNCERTAINTY_GYR, CosmologyParams,
                                   UncertainEra, age_of_universe_gyr,
                                   lookback_gyr, lookback_time, resolve_cosmic)
from chronologia.periods import (ICS_CHART_VERSION, INTCAL20_COARSE, PERIODS,
                                 AmbiguousPeriodError, NamedPeriod, calibrate_c14,
                                 candidates, children, lookup, subdivide)
from chronologia.recurrence import (HolidayRecurrence, Recurrence, every,
                                    last_weekday_of_month,
                                    nth_weekday_of_month, occurrences,
                                    parse_rrule)
from chronologia.regnal import REGNAL_SEQUENCES, RegnalSequence
from chronologia.solar import (SOLAR_ACCURACY, NoSunEvent, SunEvents,
                               sun_events, sunset_day_start)
from chronologia.unequal_hours import (BABYLONIAN_HOURS, CLOCK_CONVENTIONS,
                                       EDO_JAPANESE, ITALIAN_HOURS,
                                       ROMAN_HOURS, UNEQUAL_HOUR_SYSTEMS,
                                       ZMANIM_GRA, ClockConvention,
                                       UnequalHourSystem, convention_time,
                                       temporal_hour_span)
from chronologia.prayer_times import (ASR_METHODS, CONVENTIONS, AsrMethod,
                                      PrayerConvention, PrayerTimes,
                                      prayer_times)
from chronologia.resolution import DateTimeResolution
from chronologia.roman import roman_to_julian
from chronologia.timelines import (TIMELINES, CivilLabel, Discontinuity,
                                   DiscontinuityKind, NeverExisted, Timeline,
                                   TimelineSegment, proleptic)
from chronologia.zone_timelines import (ClockSegment, ClockTimeline,
                                        ZoneDiscontinuity, ZoneNeverExisted,
                                        zone_history_start, zone_timeline)
from chronologia.civil_holidays import (CATEGORIES, IL_INDEPENDENCE_SHIFT,
                                        NL_KINGSDAY_SHIFT,
                                        SATURDAY_SUNDAY_TO_MONDAY,
                                        US_OBSERVED_SHIFT,
                                        SUNDAY_TO_MONDAY, CalendarDateRule,
                                        CivilHoliday, DecreeTableRule,
                                        OneOffRule,
                                        EasterOffsetRule, EquinoxRule,
                                        FixedRule, HolidayCalendar,
                                        HolidayRule, NthWeekdayRule,
                                        ObservedShift, SolarTermRule,
                                        WeekdayOnOrBeforeRule,
                                        holidays_for, is_civil_holiday,
                                        load_calendar, load_translations,
                                        parse_name_cell)
from chronologia.extract import (Candidate, TimeMention, explain,
                                 extract_candidates, extract_duration,
                                 extract_recurrence, extract_timespan,
                                 extract_timespans)
from chronologia.events import Event, extract_event
from chronologia.ical import from_ical, to_ical
from chronologia.serialization import from_json, to_json

from chronologia.version import VERSION_STR as __version__

__all__ = [
    # unbounded datetime-compatible point and half-open interval
    "AstroDate",
    "DateSpan",
    "WideDuration",
    "combine_basis",
    "is_leap_year",
    "resolve_wall_clock",
    "civil_add",
    # JSON serialization (one {"type": ..., ...} envelope convention)
    "to_json",
    "from_json",
    # JDN calendar hub
    "CALENDARS",
    "Calendar",
    "CalendarDate",
    "CalendarRangeError",
    "TabulatedCalendar",
    "gregorian_to_jdn",
    "jdn_to_gregorian",
    "julian_to_jdn",
    "jdn_to_julian",
    "register_event_provider",
    # natural-language extraction (text -> DateSpan)
    "extract_timespan",
    "extract_candidates",
    "Candidate",
    "explain",
    # extraction beyond a single span
    "extract_duration",
    "extract_timespans",
    "extract_recurrence",
    "TimeMention",
    # events (one utterance -> Event) and RFC 5545 iCalendar interop
    "Event",
    "extract_event",
    "to_ical",
    "from_ical",
    # eras
    "ERAS",
    "Era",
    "EraCounting",
    "astro_year_range",
    "resolve_bp",
    "resolve_era",
    "resolve_era_year_span",
    # leap seconds (UTC/TAI/GPS)
    "LEAP_SECONDS",
    "TABLE_VALID_UNTIL",
    "table_valid_until",
    "utc_tai_offset",
    "utc_to_tai",
    "tai_to_utc",
    "utc_to_gps",
    "gps_to_utc",
    "is_leap_second_day",
    "GPS_EPOCH",
    "TAI_MINUS_GPS",
    "TT_MINUS_TAI",
    "utc_to_tt",
    "tt_to_utc",
    # time axes (the generalized reckoning hub: Earth day, Mars sol)
    "TimeAxis",
    "AXES",
    "EARTH_DAY_SECONDS",
    "MARS_SOL_SECONDS",
    "MARS_SOL_RATIO",
    "jd_of",
    "astro_from_jd",
    # Mars: Sol Date, Coordinated Mars Time, Darian calendar, mission eras
    "msd_from_tt",
    "tt_from_msd",
    "MarsDate",
    "to_mars",
    "DarianCalendar",
    "DarianDate",
    "darian",
    "DARIAN_MONTHS",
    "DARIAN_WEEKDAYS",
    "DARIAN_EPOCH_MSD",
    "Mission",
    "MISSION_ERAS",
    "mission_sol",
    # day cycles
    "DAY_CYCLES",
    "DAY_SUBDIVISIONS",
    "DayCycle",
    "DaySubdivision",
    "resolve_cycle_day",
    # year cycles (sexagenary, Chinese zodiac, indiction)
    "YEAR_CYCLES",
    "YearCycle",
    "year_cycle_label",
    "years_of",
    # named-period registry (ICS chart + archaeological periods)
    "NamedPeriod",
    "PERIODS",
    "AmbiguousPeriodError",
    "ICS_CHART_VERSION",
    "INTCAL20_COARSE",
    "lookup",
    "candidates",
    "children",
    "subdivide",
    "calibrate_c14",
    # day-part registry (parts of the civil day, region-tagged)
    "DayPart",
    "DAY_PARTS",
    "UnknownDayPartError",
    "daypart_span",
    "CLDR_VERSION",
    # RFC 5545 recurrence rules (RRULE) over the JDN hub
    "Recurrence",
    "HolidayRecurrence",
    "parse_rrule",
    "occurrences",
    "every",
    "nth_weekday_of_month",
    "last_weekday_of_month",
    # regnal reckoning
    "REGNAL_SEQUENCES",
    "RegnalSequence",
    # roman calendar
    "roman_to_julian",
    # historical local time (mean + apparent solar)
    "LMTZone",
    "local_mean_time",
    "equation_of_time",
    "apparent_solar_time",
    "EOT_ACCURACY",
    # arithmetic solar events (NOAA sunrise/sunset)
    "sun_events",
    "sunset_day_start",
    "SunEvents",
    "NoSunEvent",
    "SOLAR_ACCURACY",
    # moon phases (mean-lunation arithmetic)
    "moon_phase",
    "next_phase",
    "previous_phase",
    "lunation_number",
    "MOON_PHASE_ACCURACY",
    "MEAN_SYNODIC_MONTH_DAYS",
    "EPOCH_NEW_MOON",
    # equinoxes, solstices, astronomical seasons and the 24 solar terms
    "equinox",
    "astronomical_season_span",
    "solar_term",
    "EQUINOX_ACCURACY",
    "SOLAR_TERM_ACCURACY",
    "SOLAR_TERM_NAMES",
    "VALID_YEAR_RANGE",
    # lunar time: natural cycle registered, civil LTC standard withheld
    "LUNAR_DAY_SECONDS",
    "LTC_DRIFT_MICROSECONDS_PER_DAY",
    "LTC_STATUS",
    "LunarTimeStandardStatus",
    "ltc_offset",
    # cosmology: span-valued epochs + parameter-set variants
    "UNIVERSE_AGE_GYR",
    "UNIVERSE_AGE_UNCERTAINTY_GYR",
    "UncertainEra",
    "AGE_OF_UNIVERSE_ERA",
    "resolve_cosmic",
    "CosmologyParams",
    "COSMOLOGIES",
    "lookback_gyr",
    "lookback_time",
    "age_of_universe_gyr",
    "COSMIC_PERIODS",
    "HUBBLE_TIME_GYR",
    # unequal (temporal/seasonal) hours and clock-count conventions
    "UnequalHourSystem",
    "ClockConvention",
    "temporal_hour_span",
    "convention_time",
    "UNEQUAL_HOUR_SYSTEMS",
    "CLOCK_CONVENTIONS",
    "ROMAN_HOURS",
    "ZMANIM_GRA",
    "EDO_JAPANESE",
    "ITALIAN_HOURS",
    "BABYLONIAN_HOURS",
    # islamic prayer times (cited angle-set variants over the solar engine)
    "prayer_times",
    "PrayerTimes",
    "PrayerConvention",
    "AsrMethod",
    "CONVENTIONS",
    "ASR_METHODS",
    # computus: Easter and the movable/fixed liturgical feasts
    "easter",
    "movable_feast",
    "fixed_feast",
    "advent_sunday",
    "EASTER_METHODS",
    "MOVABLE_FEAST_OFFSETS",
    "FIXED_FEASTS",
    # EDTF (Extended Date/Time Format) <-> DateSpan
    "parse_edtf",
    "format_edtf",
    "EdtfDate",
    "EdtfParseError",
    # derived resolution vocabulary
    "DateTimeResolution",
    # timelines & discontinuities
    "Timeline",
    "TimelineSegment",
    "Discontinuity",
    "DiscontinuityKind",
    "CivilLabel",
    "NeverExisted",
    "TIMELINES",
    "proleptic",
    # timezones as timelines (clock-granular view over zoneinfo transitions)
    "zone_timeline",
    "zone_history_start",
    "ClockTimeline",
    "ClockSegment",
    "ZoneDiscontinuity",
    "ZoneNeverExisted",
    # civil holidays — computed public/regional/municipal holiday rules
    "CATEGORIES",
    "FixedRule",
    "NthWeekdayRule",
    "WeekdayOnOrBeforeRule",
    "EasterOffsetRule",
    "CalendarDateRule",
    "DecreeTableRule",
    "OneOffRule",
    "EquinoxRule",
    "SolarTermRule",
    "ObservedShift",
    "US_OBSERVED_SHIFT",
    "SUNDAY_TO_MONDAY",
    "SATURDAY_SUNDAY_TO_MONDAY",
    "IL_INDEPENDENCE_SHIFT",
    "NL_KINGSDAY_SHIFT",
    "HolidayRule",
    "CivilHoliday",
    "HolidayCalendar",
    "holidays_for",
    "is_civil_holiday",
    "load_calendar",
    "load_translations",
    "parse_name_cell",
]
