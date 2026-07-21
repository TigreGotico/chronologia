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
from chronologia.calendars import (CALENDARS, Calendar, CalendarRangeError,
                                   TabulatedCalendar, gregorian_to_jdn,
                                   jdn_to_gregorian, julian_to_jdn,
                                   jdn_to_julian, register_event_provider)
from chronologia.cycles import (DAY_CYCLES, DAY_SUBDIVISIONS, DayCycle,
                                DaySubdivision, resolve_cycle_day)
from chronologia.dayparts import (CLDR_VERSION, DAY_PARTS, DayPart,
                                  UnknownDayPartError, daypart_span)
from chronologia.eras import (ERAS, Era, EraCounting, astro_year_range,
                              resolve_bp, resolve_era, resolve_era_year_span)
from chronologia.leapseconds import (GPS_EPOCH, LEAP_SECONDS,
                                     TABLE_VALID_UNTIL, TAI_MINUS_GPS,
                                     gps_to_utc, is_leap_second_day,
                                     table_valid_until, tai_to_utc,
                                     utc_tai_offset, utc_to_gps, utc_to_tai)
from chronologia.localtime import (EOT_ACCURACY, LMTZone, apparent_solar_time,
                                   equation_of_time, local_mean_time)
from chronologia.moon import (EPOCH_NEW_MOON, MEAN_SYNODIC_MONTH_DAYS,
                              MOON_PHASE_ACCURACY, lunation_number, moon_phase,
                              next_phase, previous_phase)
from chronologia.periods import (ICS_CHART_VERSION, INTCAL20_COARSE, PERIODS,
                                 AmbiguousPeriodError, NamedPeriod, calibrate_c14,
                                 candidates, children, lookup, subdivide)
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

__version__ = "0.1.0a1"

__all__ = [
    # unbounded datetime-compatible point and half-open interval
    "AstroDate",
    "DateSpan",
    "WideDuration",
    "combine_basis",
    "is_leap_year",
    "resolve_wall_clock",
    "civil_add",
    # JDN calendar hub
    "CALENDARS",
    "Calendar",
    "CalendarRangeError",
    "TabulatedCalendar",
    "gregorian_to_jdn",
    "jdn_to_gregorian",
    "julian_to_jdn",
    "jdn_to_julian",
    "register_event_provider",
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
    # day cycles
    "DAY_CYCLES",
    "DAY_SUBDIVISIONS",
    "DayCycle",
    "DaySubdivision",
    "resolve_cycle_day",
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
]
