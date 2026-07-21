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
  A span also carries a **`basis`** (`exact` / `tabulated` / `reconstructed` /
  `predicted`) recording how its endpoints were established; `combine_basis()`
  is the worst-of rule for propagating it. Widths beyond `timedelta`'s
  ~2.7-million-year ceiling are reported as a **`WideDuration`** so a
  geological span never overflows (see **Deep time** below).
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

## Timelines & discontinuities

Calendars are pure proleptic bijections — the astronomical timeline (JDN) never
jumps. What jumps is *civil* labelling, when a pope, parliament, tsar or emperor
decrees that "tomorrow" shall be called something the calendar in force would
never have generated. A `Timeline` records, for one jurisdiction, which calendar
was in force over each stretch of days and what its reforms did to the labels.
Duration math is unaffected (always JDN-space); a non-existent label is a typed
answer, not an exception.
## Deep time

`chronologia` reaches past the geological ceiling of `datetime` — and past the
~2.7-million-year ceiling of `timedelta`. A span millions of years wide still
constructs, compares, and classifies without overflow, and scaled
Before-Present expressions carry their own precision.

- **`WideDuration`** — `DateSpan.width` returns a plain `timedelta` for any
  span that fits one (byte-identical to `end - start`) and a `WideDuration`
  (whole mean-Gregorian-years plus a sub-year `remainder`) only when a
  `timedelta` would raise `OverflowError`. Both are orderable against each
  other and against `timedelta`.
- **Geological resolution tiers** — above `MILLENNIUM`, width derives one of
  `EPOCH_GEOLOGICAL` (≳10 kyr), `PERIOD_GEOLOGICAL` (≳10 Myr),
  `ERA_GEOLOGICAL` (≳100 Myr) or `EON` (≳500 Myr). Thresholds sit near the
  order of magnitude of the like-named ICS divisions (a period is ~10⁷–10⁸ yr,
  the Jurassic ~56 Myr), not any single revisable boundary.
- **`resolve_bp(value, unit)`** — scaled Before-Present units `a` / `ka` /
  `Ma` / `Ga` (10⁰/10³/10⁶/10⁹ years before AD 1950). The returned span's
  **width is the precision of the expression**, read off the last significant
  digit — so pass `value` as a **string** when precision matters (`"66"` and
  `"66.0"` denote different precisions the floats cannot tell apart).

```python
import chronologia as c

# The October Revolution: 25 October 1917 was the label in force in Russia
# (Julian), the same instant proleptic Gregorian calls 7 November 1917.
russia = c.TIMELINES["russia_1918"]
jdn = c.julian_to_jdn(1917, 10, 25)
russia.from_jdn(jdn)                     # CivilLabel(year=1917, month=10, day=25)
russia.to_jdn((1917, 10, 25)) == jdn     # True
c.jdn_to_gregorian(jdn)                  # (1917, 11, 7)
c.proleptic("gregorian").from_jdn(jdn)   # CivilLabel(year=1917, month=11, day=7)

# 1–13 February 1918 never existed (the switch skipped them):
res = russia.to_jdn((1918, 2, 9))
isinstance(res, c.NeverExisted)          # True
res.discontinuity.kind                   # DiscontinuityKind.SKIP

# The default proleptic timeline is zero behaviour change — it matches the
# bare calendar. Registered jurisdictions: rome_1582 (+ es/pt/it/pl group),
# britain_1752, russia_1918, greece_1923, sweden_1700_1712, japan_1873.
# A Jurassic-scale span: constructs, compares and classifies with no overflow
jurassic = c.DateSpan(c.AstroDate(-201_400_000, 1, 1),
                      c.AstroDate(-143_100_000, 1, 1))
w = jurassic.width                 # WideDuration(years=58_300_000, ...)
w.years                            # 58300000
jurassic.resolution                # DateTimeResolution.PERIOD_GEOLOGICAL
jurassic.contains(c.AstroDate(-180_000_000, 1, 1))   # True

# Scaled Before-Present: precision comes from the significant figures
kpg = c.resolve_bp("66", "Ma")     # the K-Pg boundary, to Ma precision
kpg.start.year                     # -65998050  == 1950 - 66_000_000
kpg.width.total_seconds() / (365.2425 * 86400)   # ~1_000_000  (1 Ma wide)
kpg.basis                          # 'reconstructed'
c.resolve_bp("66.043", "Ma").width # 1 ka wide  (last digit is the .001 Ma place)

# Worst-of basis lattice: exact < tabulated < {reconstructed, predicted}
c.combine_basis("exact", "tabulated")            # 'tabulated'
c.combine_basis("reconstructed", "predicted")    # 'reconstructed' (peer tie-break)
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
