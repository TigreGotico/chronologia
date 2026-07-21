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
- **`CALENDARS`** — a registry of 17 calendars, each an integer inverse pair
  through the **Julian Day Number** hub: `to_jdn(y, m, d)` and `from_jdn(jdn)`.
  Thirteen are closed-form arithmetic: `julian`, `hebrew`, `islamic_civil`,
  `french_republican`, `bahai`, `coptic`, `ethiopian`, `revised_julian`,
  `armenian`, `egyptian`, `mayan_long_count`, `iso_week`,
  `solar_hijri_arithmetic`. Four
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
  Japanese nengō, New Kingdom Egyptian high/middle/low chronology variants),
  and `roman_to_julian` for `a.d.` Kalends/Nones/Ides reckoning.

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

## Egyptian calendar & New Kingdom regnal chronology

The `egyptian` calendar is the original 365-day "vague year": twelve 30-day
months grouped into three season-thirds — Akhet "Inundation" (months 1-4),
Peret "Emergence" (5-8), Shemu "Harvest" (9-12) — plus five epagomenal days
as month 13, and (unlike Coptic/Ethiopic) **no leap day, ever**. The civil
year drifts one day earlier against the solar year every four years,
completing a full Sothic cycle in 1460 Egyptian years. Epoch: the era of
Nabonassar anchor Ptolemy used to key the *Almagest*'s observation tables —
1 Thoth year 1 = JDN 1448638 = -746-02-26 proleptic Julian.

```python
c.CALENDARS["egyptian"].to_jdn(1, 1, 1)     # 1448638, the epoch
c.CALENDARS["egyptian"].from_jdn(1448638 + 365)  # (2, 1, 1), 365 days later, always
```

`REGNAL_SEQUENCES` includes a small demonstrative New Kingdom (Dynasty
18-19) dataset, Ahmose I through Ramesses II, in **three** parallel
chronology variants — `egyptian_high`, `egyptian_middle` and `egyptian_low`
— reflecting the ±13-25 year disagreement in Egyptological absolute dating.
The dataset is **attested-only**: a ruler is listed in a variant only where
that variant's accession year is directly attested (with an explicit
chronology label) in a cited source, so the three variants have different
ruler subsets and lengths, and documented gaps rather than interpolated
fill-ins — see `chronologia/regnal.py` for the full per-ruler citation
trail. Ramesses II's accession is the one figure directly attested by name
in all three variants: 1304 BC (high), 1290 BC (middle/conventional),
1279 BC (low) — divergence of a quarter-century between the high and low
variants:

```python
c.REGNAL_SEQUENCES["egyptian_high"].year_span("ramesses_ii", 5)
c.REGNAL_SEQUENCES["egyptian_low"].year_span("ramesses_ii", 5)
# same regnal year, ~25 years apart in absolute Gregorian terms
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

## Named periods

`chronologia.periods` names stretches of time. A `NamedPeriod` binds a name
("Jurassic", "Late Bronze Age") to a `DateSpan`, a hierarchy `level`, an
optional `region` (`None` == a global name), a versioned `source`, and a
`parent` key. Two data instances ship in `PERIODS`:

- the **ICS International Chronostratigraphic Chart** (version `2023/09`) — the
  full global scale, every eon/era/period/epoch/age placed on the
  Before-Present axis, published GSSP boundary uncertainties folded *outward*
  into the endpoints, `basis="tabulated"`;
- a small, region-tagged **archaeological set** (British three-age system vs
  Mesopotamian Bronze Age), `basis="reconstructed"`, that exists only to prove
  regional disambiguation. Per-site phasings stay out.

`lookup(name, region=None)` answers an exact global name or a `(name, region)`
pair; a bare, region-ambiguous name raises `AmbiguousPeriodError` and
`candidates(name)` lists the choices — picking a locale default is the
consumer's job. `subdivide(target, part)` cuts any span into conventional
early/mid/late thirds (or first-/second-half halves), but an authority-defined
subdivision wins: the ICS **Late Jurassic** entry, not an arithmetic third.

```python
import chronologia as c

# "during the jurassic" — a chart entry, on the deep-time BP axis
jurassic = c.lookup("jurassic")
(1950 - jurassic.span.start.year) / 1e6    # ~201.6 Ma  (201.4 + 0.2 GSSP unc)
jurassic.span.resolution                   # DateTimeResolution.PERIOD_GEOLOGICAL
jurassic.parent                            # 'mesozoic'
c.lookup("holocene").span.start.year       # -9750  == 1950 - 11_700 yr BP

# early/mid/late — authority-defined subdivision wins over arithmetic thirds
c.subdivide(jurassic, "late") == c.lookup("late jurassic").span   # True

# "late bronze age" is region-ambiguous: Britain vs Mesopotamia
sorted(p.region for p in c.candidates("bronze age"))   # ['GB', 'MESO']
c.lookup("late bronze age", region="GB").span.start.year     # -1149  (1150 BC)
c.lookup("late bronze age", region="MESO").span.start.year   # -1549  (1550 BC)

# Radiocarbon: 14C BP and cal BP are distinct reckonings (coarse IntCal20)
cal = c.calibrate_c14(3000)                # ~3000 14C BP -> a cal-BP span
1950 - cal.start.year                      # ~3300 cal BP (demonstrative, not OxCal)
cal.basis                                  # 'reconstructed'
```

## Leap seconds

`chronologia.leapseconds` converts between the real timescales — UTC, TAI
(International Atomic Time), and GPS time — using the tabulated UTC-TAI
offset history (IERS Bulletin C, mirrored via the IANA/IETF
`leap-seconds.list`). This is unrelated to the `"unix"` era above: POSIX/unix
time ignores leap seconds entirely and always advances 86400 seconds per day.
### Historical local time
Before standard time zones (the international system dates from 1884),
every town kept its own clock set by the sun. `chronologia.localtime`
reconstructs the two pre-zone reckonings against a single UTC reference:
**local mean time** (mean solar time at a meridian, a fixed offset of
4 minutes of time per degree of longitude, east positive) and **apparent
solar time** (what a sundial reads — mean time plus the *equation of
time*). The equation of time uses the closed form cited below, accurate
to within half a minute (`EOT_ACCURACY`), with the explicit
`apparent = mean + EoT` sign convention (a positive value means the
sundial runs *fast*).

```python
from datetime import datetime
import chronologia as c

# cumulative UTC-TAI offset (whole seconds) at an instant
c.utc_tai_offset(datetime(2020, 6, 15))   # 37

# real-timescale conversions (TAI-GPS = 19s constant)
c.utc_to_tai(datetime(2020, 6, 15, 12, 0, 0))
c.utc_to_gps(datetime(2020, 6, 15, 12, 0, 0))

# was a leap second (23:59:60 UTC) inserted on this UTC calendar date?
c.is_leap_second_day(datetime(2016, 12, 31).date())   # True

# the table is confirmed complete only up to this date (predicted/constant
# offset beyond it, per Bulletin C's own ~6-month announcement horizon)
c.table_valid_until()
```

Pre-1972 instants (the fractional "rubber second" era) raise `ValueError` —
out of scope, no cited table backs it.

# Solar noon in Lisbon on 1755-11-01, the day of the great earthquake.
# Lisbon sits ~9.14 deg west, so its mean-time clock trails Greenwich.
lisbon = c.local_mean_time(-9.14)
lisbon.offset            # timedelta(seconds=-2194)  ->  -36m34s
lisbon.tzname()          # 'LMT-00:36:34(lambda=9.140W)'
when = datetime(1755, 11, 1, 12, 0, 0)   # 12:00 UTC
lisbon.from_utc(when)                 # AstroDate(1755, 11, 1, 11, 23, 26)  (LMT)
c.apparent_solar_time(when, -9.14)    # AstroDate(1755, 11, 1, 11, 39, 52, ...) (sundial)
# The equation of time swings ~+16.4 min in early November (sundial fast)
# to ~-14.2 min in mid-February (sundial slow).
c.equation_of_time(datetime(1755, 11, 1))   # timedelta ~ +16m26s

## Timezones
`AstroDate` is naive by default and carries an **optional** `tzinfo`, with
semantics identical to `datetime`: an aware point compares, subtracts and
hashes by the *instant* it names; a naive one by its wall-clock fields;
mixing the two never compares equal and raises `TypeError` on ordering or
subtraction. `utcoffset()` / `tzname()` / `dst()` delegate to the attached
zone; `astimezone(tz)` converts to another zone; `replace(tzinfo=...)`
re-labels the same wall clock without converting.

```python
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import chronologia as c

NY = ZoneInfo("America/New_York")

noon = c.AstroDate(2024, 7, 1, 12, tzinfo=NY)   # aware
noon.utcoffset()                                # timedelta(hours=-4)  (EDT)
noon.astimezone(timezone.utc)                   # 2024-07-01T16:00:00+00:00

# naive vs aware behaves exactly like datetime
c.AstroDate(2024, 1, 1) == c.AstroDate(2024, 1, 1, tzinfo=NY)   # False
```

Two documented deviations / conventions:

- **Naive `astimezone()` raises `ValueError`.** Modern `datetime.astimezone`
  silently assumes the system-local zone for a naive value — a well-known
  footgun. `AstroDate` rejects it: attach a zone with `replace(tzinfo=...)`
  first so the source zone is explicit.
- **Out-of-range zone lookups extrapolate.** Beyond `datetime`'s 1..9999
  window a `zoneinfo` zone has no tabulated data, so offset lookups evaluate
  the zone's *recurring rule* at a **proxy year** `2000 + (year % 400)`. The
  proleptic Gregorian calendar (and every DST rule keyed to month/weekday)
  repeats with a 400-year period, so the proxy shares the real year's leap
  status and weekday pattern. This extrapolates the *current* recurring rule
  across all time; it cannot reconstruct historical offset changes (in-range
  pre-1970 data is used as-is, with `zoneinfo`'s usual reliability caveats).

```python
# The far future still resolves the recurring rule (via the proxy year);
# no real datetime exists out of range, but the point stays comparable.
c.AstroDate(12000, 7, 1, tzinfo=NY).utcoffset()   # timedelta(hours=-4)
```

### Fold and gap
A wall-clock reading can be ambiguous (fall-back repeats an hour) or
non-existent (spring-forward skips one). Rather than a fold bit,
`resolve_wall_clock(y, m, d, h, mi, zone)` returns the outcome as data:

```python
# fall back: 2024-11-03 01:30 happens twice -> the two real instants
early, late = c.resolve_wall_clock(2024, 11, 3, 1, 30, NY)
early.utcoffset(), late.utcoffset()   # -4h (EDT), -5h (EST)
late - early                          # timedelta(hours=1)

# spring forward: 2024-03-10 02:30 never existed -> NeverExisted + why
gone = c.resolve_wall_clock(2024, 3, 10, 2, 30, NY)
gone.discontinuity.kind               # DiscontinuityKind.SKIP

# an unambiguous reading returns a single aware AstroDate
c.resolve_wall_clock(2024, 6, 1, 12, 0, NY)
```

The repeat pair carries each occurrence in a fixed-offset zone (AstroDate
has no fold bit), so the two share one wall reading yet name distinct,
comparable instants. The skip result is a
`NeverExisted` carrying a synthetic `SKIP` `Discontinuity` — a real
"never existed + why" answer, never an exception.

## Civil arithmetic
Time has two kinds of "add a day". **Absolute** arithmetic (`point +
timedelta`) always advances a real duration and is untouched. **Civil**
arithmetic (`civil_add`) walks the calendar the way people mean it:

```python
import chronologia as c

# Months/years clamp the day of month (never spill into the next month):
c.civil_add(c.AstroDate(2024, 1, 31), months=1)   # 2024-02-29 (leap year)
c.civil_add(c.AstroDate(2023, 1, 31), months=1)   # 2023-02-28

# Adding days preserves the wall clock across a DST edge, so the *real*
# elapsed time is 23 or 25 hours, not 24:
start = c.AstroDate(2024, 3, 9, 12, tzinfo=ZoneInfo("America/New_York"))
end = c.civil_add(start, days=1, zone=ZoneInfo("America/New_York"))
end - start                                        # timedelta(hours=23)
# whereas the absolute step is exactly 24h of real time:
(start + timedelta(days=1)) - start                # timedelta(days=1)

# With a timeline, a day step walks civil labels across a reform seam:
c.civil_add(c.AstroDate(1582, 10, 4), days=1,
            timeline=c.TIMELINES["rome_1582"])      # 1582-10-15 (Gregorian)
```

`civil_add` also accepts a `DateSpan`, shifting both endpoints. The two
never silently conflate: absolute duration is `+ timedelta`, civil label
walking is `civil_add`.
## Cited sources

The conversion algorithms are grounded in canonical references, cited inline in
each module's docstring:

- Reingold & Dershowitz, *Calendrical Calculations* (1990 and later editions) —
  the Hebrew, Islamic civil, French Republican, and Bahai arithmetic.
- U.S. Naval Observatory, Julian Date reference — the JDN hub and the
  Gregorian/Julian conversions.
- POSIX.1-2017 §4.16 — the Unix epoch seconds count.
- Radiocarbon 19(3):355–363 — the before-present (1950) reference epoch.
- IERS Bulletin C / IANA-IETF `leap-seconds.list` — the UTC-TAI offset table
  in `chronologia/data/leap_seconds.tab`.
- Honsberg & Bowden, *Solar Time* (PVCDROM / PVEducation) — the equation of
  time closed form and the 4-minutes-per-degree longitude rule for local
  mean and apparent solar time.
- ICS International Chronostratigraphic Chart, version 2023/09 (boundary ages
  via the Macrostrat international timescale, CC-BY 4.0) — the geological
  named periods in `chronologia/data/ics_chart.tab`.
- Reimer et al. 2020, *The IntCal20 Northern Hemisphere radiocarbon age
  calibration curve*, Radiocarbon 62, doi:10.1017/RDC.2020.41 — the coarse
  calibration table in `chronologia/data/intcal20_coarse.tab`.

## Used by

- [ovos-date-parser](https://github.com/OpenVoiceOS/ovos-date-parser)
