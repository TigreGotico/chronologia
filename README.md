# chronologia

A general-purpose calendrical and chronological core for Python. It models
*when* something happened, across the whole span of recorded and deep time,
with types that behave like the standard library where they can and reach past
its limits where they must.

`chronologia` is pure Python with **no runtime dependencies** and requires
Python 3.10+.

## What it gives you

- **`AstroDate`** — a frozen point in time with an **unbounded year**
  (astronomical numbering: 1 BC is year 0; proleptic Gregorian). It is
  duck-typed to `datetime`'s public API — `replace()`, `weekday()`,
  `isoweekday()`, `isocalendar()`, `toordinal()`, expanded-year `isoformat()` /
  `fromisoformat()`, a width-safe `strftime` subset, `timedelta` arithmetic,
  and comparison / equality that interoperate with `date` and `datetime`. It
  exists to carry the years C `datetime` refuses (`-003760-09-07T00:00:00` is a
  valid `AstroDate`). Compatibility is protocol-based (subclassing `datetime`
  is impossible — its C-level year bounds are exactly the constraint being
  escaped) and enforced by a test that walks `datetime`'s public API.
- **`DateSpan`** — a frozen **half-open interval** `[start, end)` whose
  endpoints are always `AstroDate`. Width *is* the referential uncertainty:
  "June 2027" is a month-wide span, "44 BC" a year-wide one, a clock time a
  minute-wide one. Half-open so adjacent spans tile with no fenceposts — June
  ends exactly where July begins. `DateTimeResolution` is **derived** from the
  width, never asserted, which removes a whole class of tag-vs-value drift.
- **`CALENDARS`** — a registry of 16 calendars, each an integer inverse pair
  through the **Julian Day Number** hub: `to_jdn(y, m, d)` and `from_jdn(jdn)`.
  Twelve are closed-form arithmetic: `julian`, `hebrew`, `islamic_civil`,
  `french_republican`, `bahai`, `coptic`, `ethiopian`, `revised_julian`,
  `armenian`, `mayan_long_count`, `iso_week`, `solar_hijri_arithmetic`. Four
  are `TabulatedCalendar`s backed by data files in `calendar_data/`:
  `umm_al_qura`, `badi_2015`, `french_republican_equinox`, `chinese` — bounded
  event tables with an out-of-range `CalendarRangeError` fallback contract and
  an optional-ephemeris `register_event_provider` hook for extending past the
  tabulated range. Because everything reduces to JDN, conversions compose
  freely.
- **`ERAS`** — year-numbering conventions attached to a calendar or an epoch:
  `before_christ` / `common_era` / `holocene` number the Gregorian year,
  `anno_mundi` is the Hebrew calendar's own numbering, `unix` and `julian_day`
  are linear counts. Calendar-backed eras resolve **exactly** through the
  calendar's JDN hub — Anno Mundi 5786 begins on 2025-09-23, not an
  epoch-plus-count approximation three months off.
- **Day cycles, regnal sequences, and Roman dates** — `DAY_CYCLES` (week,
  Roman nundinal, Republican décade), `REGNAL_SEQUENCES` (Roman consuls,
  Japanese nengō), and `roman_to_julian` for `a.d.` Kalends/Nones/Ides
  reckoning.

### Scope: arithmetic, tabulated, out of scope

`chronologia` implements **arithmetic** calendars — those whose leap and
month-length rules are closed-form functions of the year, so conversion is a
pure integer computation with no tables to ship — and **tabulated** calendars,
whose civil dates are fixed by observation or a published civil-authority
schedule rather than a closed-form rule. Tabulated calendars load bounded
event tables from `calendar_data/*.tab` files (each carrying its own
provenance header), classify themselves via a `basis` attribute, raise
`CalendarRangeError` outside their tabulated coverage, and accept an optional
ephemeris `register_event_provider` callback for callers who want to extend
coverage past the shipped table. Calendars requiring live astronomical
ephemerides by default are **out of scope** — this is a reckoning core, not an
astronomy engine.

## Quickstart

```python
from datetime import timedelta
import chronologia as c

# An unbounded date, well before datetime's year-1 floor
a = c.AstroDate(-3760, 9, 7)
a.isoformat()          # '-003760-09-07T00:00:00'
a.weekday()            # 0
(a + timedelta(days=1)).isoformat()  # '-003760-09-08T00:00:00'

# Round-trip any date through the JDN hub into another calendar
jdn = c.gregorian_to_jdn(2025, 9, 23)
c.CALENDARS["hebrew"].from_jdn(jdn)   # (5786, 7, 1)  -> 1 Tishri 5786

# Eras resolve to concrete dates; calendar-backed ones are exact
c.resolve_era("anno_mundi", 5786)     # datetime.date(2025, 9, 23)

# A half-open span derives its own resolution from its width
span = c.DateSpan(c.AstroDate(2027, 6, 1), c.AstroDate(2027, 7, 1))
span.resolution        # DateTimeResolution.MONTH

# Roman calendar: the Ides of March, 44 (a.d. count is inclusive, 1 == the day)
c.roman_to_julian(44, 3, "ides", 1)   # (44, 3, 15)
c.roman_to_julian(44, 3, "ides", 2)   # (44, 3, 14)  -> pridie
```

## Cited sources

The conversion algorithms are grounded in canonical references, cited inline in
each module's docstring:

- Reingold & Dershowitz, *Calendrical Calculations* (1990 and later editions) —
  the Hebrew, Islamic civil, French Republican, and Bahai arithmetic.
- U.S. Naval Observatory, Julian Date reference — the JDN hub and the
  Gregorian/Julian conversions.
- POSIX.1-2017 §4.16 — the Unix epoch seconds count.
- Radiocarbon 19(3):355–363 — the before-present (1950) reference epoch.

## Used by

- [ovos-date-parser](https://github.com/OpenVoiceOS/ovos-date-parser)
