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
                                   combine_basis, is_leap_year)
from chronologia.calendars import (CALENDARS, Calendar, CalendarRangeError,
                                   TabulatedCalendar, gregorian_to_jdn,
                                   jdn_to_gregorian, julian_to_jdn,
                                   jdn_to_julian, register_event_provider)
from chronologia.cycles import (DAY_CYCLES, DAY_SUBDIVISIONS, DayCycle,
                                DaySubdivision, resolve_cycle_day)
from chronologia.eras import (ERAS, Era, EraCounting, astro_year_range,
                              resolve_bp, resolve_era, resolve_era_year_span)
                              resolve_era, resolve_era_year_span)
from chronologia.leapseconds import (GPS_EPOCH, LEAP_SECONDS,
                                     TABLE_VALID_UNTIL, TAI_MINUS_GPS,
                                     gps_to_utc, is_leap_second_day,
                                     table_valid_until, tai_to_utc,
                                     utc_tai_offset, utc_to_gps, utc_to_tai)
from chronologia.regnal import REGNAL_SEQUENCES, RegnalSequence
from chronologia.resolution import DateTimeResolution
from chronologia.roman import roman_to_julian
from chronologia.timelines import (TIMELINES, CivilLabel, Discontinuity,
                                   DiscontinuityKind, NeverExisted, Timeline,
                                   TimelineSegment, proleptic)

__version__ = "0.1.0a1"

__all__ = [
    # unbounded datetime-compatible point and half-open interval
    "AstroDate",
    "DateSpan",
    "WideDuration",
    "combine_basis",
    "is_leap_year",
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
    # regnal reckoning
    "REGNAL_SEQUENCES",
    "RegnalSequence",
    # roman calendar
    "roman_to_julian",
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
]
