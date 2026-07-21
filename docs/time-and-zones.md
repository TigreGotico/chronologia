# Time and zones

The calendars in this library answer "which day?". This page is about the
messier questions *inside* a day: what happens at the two ragged edges of
daylight saving time, why "tomorrow" is sometimes not 24 hours away, why your
phone and a GPS satellite quietly disagree by eighteen seconds, and why a
sundial and a clock rarely agree at all. None of these are bugs. They are
honest facts about time, and the library reports them honestly.

## The clocks that lie twice a year

Twice a year, in places that keep daylight saving time, the clock does
something strange.

**In autumn it "falls back".** At 2 AM the clock jumps back to 1 AM, so the
hour from 1:00 to 2:00 happens *twice*. If you say "1:30 AM that night", you
have named **two different moments**, an hour apart. Picture it:

```
first  1:00 ── 1:30 ── 2:00 ─┐
1 AM                          │  clock jumps back to 1:00
second 1:00 ── 1:30 ── 2:00   ┘
       └── "1:30 AM" lives here twice ──┘
```

**In spring it "springs forward".** At 2 AM the clock jumps to 3 AM, so the
hour from 2:00 to 3:00 *never happens*. "2:30 AM" that night names **no moment
at all.**

Ask the library to resolve a wall-clock reading against a real zone and it
gives you the honest answer for each case. When a time happens twice, you get
both instants:

```python
from zoneinfo import ZoneInfo
from chronologia import resolve_wall_clock

ny = ZoneInfo("America/New_York")
earlier, later = resolve_wall_clock(2024, 11, 3, 1, 30, ny)   # fall-back night
print(earlier.isoformat())
# 2024-11-03T01:30:00-04:00
print(later.isoformat())
# 2024-11-03T01:30:00-05:00
```

Same wall clock, `01:30` both times — but the first is still on summer time
(four hours behind UTC) and the second on winter time (five hours behind), so
they are genuinely an hour apart.

When a time never happens, you get a `NeverExisted` — the same "here is why,
not an error" value the [timelines](timelines.md) guide describes:

```python
gap = resolve_wall_clock(2024, 3, 10, 2, 30, ny)   # spring-forward morning
print(gap.discontinuity.kind.name)
# SKIP
```

And an ordinary, unambiguous time simply comes back as a single dated instant:

```python
noon = resolve_wall_clock(2024, 6, 1, 12, 0, ny)
print(noon.isoformat())
# 2024-06-01T12:00:00-04:00
```

## "This time tomorrow" is not "in 24 hours"

Those ragged edges make an ordinary phrase ambiguous. When you say "this time
tomorrow", do you mean *the same reading on the clock face* (which might be 23
or 25 real hours away), or *exactly 24 hours of real time from now* (which
might land on a different clock reading)? These are two different questions,
and the library makes you choose rather than guessing.

`civil_add` walks the **civil** calendar — same clock reading, next day — and
tells you the true elapsed time. Cross an autumn fall-back and "tomorrow at
00:30" is really **25 hours** away, because a whole extra hour was lived
through:

```python
from datetime import timedelta, timezone
from chronologia import AstroDate, civil_add

start = AstroDate(2024, 11, 3, 0, 30, tzinfo=ny)   # just before fall-back
civil = civil_add(start, days=1, zone=ny)
print(civil.isoformat(), round((civil - start).total_seconds() / 3600, 1))
# 2024-11-04T00:30:00-05:00 25.0
```

The **absolute** question — "in exactly 24 hours" — keeps the real duration
fixed and lets the clock reading fall where it may. Twenty-four real hours
after that same start lands at **23:30**, an hour earlier on the face, because
of the extra hour that was inserted:

```python
absolute = (start.astimezone(timezone.utc) + timedelta(hours=24)).astimezone(ny)
print(absolute.isoformat(), round((absolute - start).total_seconds() / 3600, 1))
# 2024-11-03T23:30:00-05:00 24.0
```

In spring it goes the other way — "this time tomorrow" across a spring-forward
is only **23 hours** away, because an hour was skipped:

```python
spring_start = AstroDate(2024, 3, 10, 0, 30, tzinfo=ny)
spring_civil = civil_add(spring_start, days=1, zone=ny)
print(spring_civil.isoformat(),
      round((spring_civil - spring_start).total_seconds() / 3600, 1))
# 2024-03-11T00:30:00-04:00 23.0
```

## Leap seconds: why GPS and your phone disagree

Here is a small mystery. Ask a GPS receiver and your phone for the time to the
second and, done carefully, they differ by eighteen seconds. Neither is broken.

The Earth's spin is slightly irregular, so **UTC** — the civil time your phone
shows — occasionally inserts a "leap second" (a real 23:59:**60**) to stay in
step with the planet. **TAI** (atomic time) and **GPS time** do not; they just
tick steadily. So the gap between them is not a formula — it is *history*, a
running tally of every leap second ever added, published by an international
body. This library ships that table.

```python
from datetime import date
from chronologia import utc_tai_offset, TAI_MINUS_GPS

print(utc_tai_offset(date(2024, 1, 1)))               # how far TAI leads UTC
# 37
print(utc_tai_offset(date(2024, 1, 1)) - TAI_MINUS_GPS)   # how far GPS leads UTC
# 18
```

There it is: GPS time runs **18 seconds** ahead of the UTC on your phone. You
can convert between the timescales directly:

```python
from datetime import datetime
from chronologia import utc_to_tai

print(utc_to_tai(datetime(2024, 1, 1, 12, 0, 0)))
# 2024-01-01 12:00:37
```

The table knows how far into the future it can be trusted, and which days
actually carried a leap second:

```python
from chronologia import TABLE_VALID_UNTIL, is_leap_second_day

print(is_leap_second_day(date(2016, 12, 31)))   # the last leap second so far
# True
```

**Caveat — scope:** this covers 1972 onward (before that, UTC used a different,
"rubber second" scheme) and stops at the table's expiry date. Beyond that date
the last known offset is returned as a `predicted` value — "no new leap second
has been announced yet", not a promise none will come. Ordinary Unix time
(`time.time()`) ignores leap seconds entirely and is a separate timescale,
deliberately left untouched here.

## Sundials, clocks, and the towns that kept their own time

Before railways forced everyone onto shared time zones, every town set its
clock by the sun: noon was simply when the sun stood highest *there*. A town to
your east saw noon a little earlier; a town to your west, a little later. That
older reckoning is **local mean time**, and it differs from Greenwich time
purely by longitude — four minutes of clock for every degree.

```python
from chronologia import local_mean_time

lisbon = local_mean_time(-9.14)     # Lisbon sits ~9.14° west of Greenwich
print(lisbon.tzname())
# LMT-00:36:34(lambda=9.140W)
```

Lisbon's own sun-clock ran about 36 minutes behind Greenwich — which is exactly
why railway timetables were a nightmare until standard zones arrived.

### Why even the sundial disagrees with the clock

There is one more twist. A **mean** solar clock ticks at a steady rate, but the
*real* sun does not keep steady time: the Earth's tilt and its slightly oval
orbit make the sun run ahead of or behind the average over the year. The
difference is called the **equation of time**, and it swings up to about ±16
minutes. A sundial reads the real sun, so a sundial and a well-set clock
disagree by that much, drifting across the seasons.

```python
from chronologia import equation_of_time

print(round(equation_of_time(date(2024, 11, 3)).total_seconds() / 60, 1))
# 16.3
print(round(equation_of_time(date(2024, 2, 12)).total_seconds() / 60, 1))
# -14.6
```

In early November the sundial runs about 16 minutes *fast*; in mid-February,
about 15 minutes *slow*. Combine longitude and the equation of time and you get
**apparent solar time** — what a sundial at that spot would actually read:

```python
from chronologia import apparent_solar_time

print(apparent_solar_time(datetime(2024, 11, 3, 12, 0, 0), -9.14).isoformat())
# 2024-11-03T11:39:45.748585
```

At Greenwich noon UTC on that November day, a Lisbon sundial reads about 11:40.
(This closed-form equation of time is accurate to within half a minute,
reported as `EOT_ACCURACY`.)

## The French Revolution's decimal clock

For a brief moment the French Revolution tried to decimalise the day itself: 10
hours per day, 100 minutes per hour, 100 seconds per minute. The library
carries this as a `DaySubdivision`, rescaling exactly to ordinary microseconds.
A decimal hour is one-tenth of a day, so "5 decimal hours" is precisely noon:

```python
from chronologia import DAY_SUBDIVISIONS

decimal = DAY_SUBDIVISIONS["french_decimal"]
print(decimal.units_to_us(hours=5))    # microseconds since midnight
# 43200000000
print(86400 * 1000000)                 # microseconds in half a day, for comparison
# 86400000000
```

`43200000000` is exactly half of `86400000000` — 5 decimal hours land dead on
midday.

## Sunrise, sunset, and the twilights

Where local mean time and the equation of time reconstruct the *clock*, the
sun's actual rising and setting need a date, a latitude, and a longitude.
`sun_events` transcribes the NOAA *General Solar Position Calculations*
(NOAA Global Monitoring Division), a closed-form method accurate to within
about a minute for 1901–2099 (`SOLAR_ACCURACY`). All returned instants are
UTC `AstroDate`s, and longitude is east-positive — the same convention as
`local_mean_time`.

```python
from chronologia import sun_events, AstroDate

ev = sun_events(AstroDate(2010, 6, 21), 40.0, -105.0)   # Denver, solstice
print(ev.sunrise.strftime("%Y-%m-%d %H:%M"))    # UTC (Denver is UTC-6)
# 2010-06-21 11:30
print(ev.solar_noon.strftime("%H:%M"))
# 19:01
print(ev.sunset.strftime("%Y-%m-%d %H:%M"))     # sunset falls after UTC midnight
# 2010-06-22 02:31
```

Each day also carries the three standard twilight boundaries — civil, nautical,
and astronomical, at solar depression 6°, 12°, and 18° — as dawn/dusk pairs
around sunrise and sunset:

```python
ev = sun_events(AstroDate(2024, 3, 20), 40.0, 0.0)
order = [ev.astronomical_dawn, ev.nautical_dawn, ev.civil_dawn, ev.sunrise,
         ev.solar_noon, ev.sunset, ev.civil_dusk, ev.nautical_dusk,
         ev.astronomical_dusk]
print([e.strftime("%H:%M") for e in order])
# ['04:33', '05:05', '05:37', '06:04', '12:07', '18:11', '18:38', '19:10', '19:42']
```

### Polar honesty

North of the Arctic Circle the sun may never rise or never set. Rather than
inventing a time, the affected field becomes a typed `NoSunEvent` carrying the
`kind` — the same "never existed" stance the spring-forward gap takes. Every
boundary is judged on its own zenith, so a polar day and a polar night are both
reported truthfully:

```python
from chronologia import NoSunEvent

summer = sun_events(AstroDate(2024, 6, 21), 78.0, 15.0)   # Svalbard, midsummer
print(isinstance(summer.sunrise, NoSunEvent), summer.sunrise.kind)
# True polar_day

winter = sun_events(AstroDate(2024, 12, 21), 78.0, 15.0)  # polar night
print(isinstance(winter.sunrise, NoSunEvent), winter.sunrise.kind)
# True polar_night
```

`solar_noon` is always a real instant — it depends only on longitude and the
equation of time — even when nothing rises or sets.

### Sunset-anchored days

The default civil day starts at midnight, needing no location. But the Hebrew
and Islamic calendars begin each day at the *previous* evening's sunset. When a
location is available, `sunset_day_start` upgrades that convention to a computed
sunset instant:

```python
from chronologia import sunset_day_start

start = sunset_day_start(AstroDate(2024, 6, 1), 31.78, 35.22)  # Jerusalem
print(start.strftime("%Y-%m-%d %H:%M"))    # the 31 May evening sunset that opens 1 June
# 2024-05-31 16:38
```

## Why "the next full moon" has an error bar

Ask an almanac for the next full moon and it gives you one clean-looking
number. That number is a lie of precision. The Moon's orbit is eccentric, so
its actual (true) phase times wander around the arithmetic average by up to
about half a day, in either direction, for no more exciting reason than
gravity.
This library does not run a full lunar ephemeris (that is out of scope — see
the H-series roadmap). Instead it multiplies: a fixed mean lunation length
(29.530589 days, the present-day value) times a lunation count since a cited
epoch (Jean Meeus's Lunation Number 0, the first new moon of 2000, ≈18:14
UTC on 6 January). That arithmetic is exact; the *model* is only
approximately true, so every answer comes back as a span with a stated width,
never a bare instant:

```python
from datetime import datetime
from chronologia import moon_phase, next_phase, previous_phase
# 2024-01-11 11:57 UTC is a real, published new moon (US Naval Observatory).
print(round(moon_phase(datetime(2024, 1, 11, 11, 57)), 3))
# 0.005
full = next_phase(datetime(2024, 7, 1), "full")
print(full.basis)
# predicted
print(full.width)
# 1 day, 4:00:00
```

`0.005` is close to `0.0` (new moon) — a lunation is about 29.5 days, so
`0.005` of one is roughly 3.5 hours, comfortably inside this module's stated
accuracy. `next_phase` always returns a span, never a point: its width is
`2 * MOON_PHASE_ACCURACY` (28 hours), centred on the mean-arithmetic instant.
**The `basis` is honest about direction, not calendar date.** A phase in the
anchor's future is `"predicted"` (a forward model); one in its past is
`"reconstructed"` (modelled from evidence/theory about something that already
happened) — the same reconstructed/predicted split deep-time spans use
elsewhere in this library, just applied at hour granularity instead of
geological granularity:
past_full = previous_phase(datetime(2024, 8, 1), "full")
print(past_full.basis)
# reconstructed
**The accuracy bound is measured, not assumed.** Cross-checked against the
US Naval Observatory's published 2024 phase table, the mean model's largest
new/full-moon miss is about 14 hours — hence `MOON_PHASE_ACCURACY`. Quarter
phases (`"first_quarter"` / `"last_quarter"`) carry a wider, undocumented-bound
error in the same check (up to ~23 hours) because the mean-quarter formula
omits an extra periodic correction that mean new/full moon mostly cancels —
a known asymmetry of the simple model, not a bug.
Every lunation is also numbered, in the older Brown convention almanacs used
1923-1983:
from chronologia import lunation_number
print(lunation_number(datetime(2024, 1, 11, 11, 57)))
# 1250
Ask for a phase name outside the four recognised ones and you get a clear
error rather than a silent nonsense result:
try:
    next_phase(datetime(2024, 1, 1), "waxing_gibbous")
except ValueError as exc:
    print("rejected:", exc)
# rejected: unknown moon phase 'waxing_gibbous'; expected one of ['first_quarter', 'full', 'last_quarter', 'new']
## "Morning" is a convention, and conventions differ

A time zone tells you what a clock reads. It does **not** tell you whether
that reading counts as morning, afternoon, or evening — that is a cultural
boundary, drawn differently from one language to the next, and it is not the
sun's business. English cuts the post-noon day in two, *afternoon* then
*evening*, with the seam at 18:00. Spanish runs a single *tarde* straight
across both, all the way to 20:00. Neither is "right"; they are conventions.

`chronologia` keeps these boundaries as region-tagged data — transcribed from
the Unicode CLDR day-period rules, the machine-readable authority for exactly
this locale variation — and `daypart_span` applies a named part to a real
date, returning the same half-open `DateSpan` every other layer produces:

```python
from datetime import date
from chronologia import daypart_span

tuesday = date(2027, 6, 8)

# English: afternoon ends and evening begins at 18:00.
print(daypart_span(tuesday, "afternoon").start.isoformat(),
      daypart_span(tuesday, "afternoon").end.isoformat())
# 2027-06-08T12:00:00 2027-06-08T18:00:00

# Spanish: one "tarde" covers what English splits into afternoon + evening.
tarde = daypart_span(tuesday, "tarde", region="es")
print(tarde.start.isoformat(), tarde.end.isoformat())
# 2027-06-08T12:00:00 2027-06-08T20:00:00
```

Ask for a part a region does not redefine and you get the global default —
Spanish overrides *tarde*, not *morning*, so `morning` in region `"es"` is the
default morning. Ask for a region-only name with no region and it is honestly
unknown:

```python
from chronologia import UnknownDayPartError

print(daypart_span(tuesday, "morning", region="es")
      == daypart_span(tuesday, "morning"))
# True

try:
    daypart_span(tuesday, "tarde")          # no region: "tarde" is not global
except UnknownDayPartError as exc:
    print("unknown:", "tarde" in str(exc))
# unknown: True
```

Night is the interesting one: **"tuesday night" belongs to Tuesday, yet it
ends on Wednesday.** A part whose clock end is earlier than its start crosses
midnight, and the span anchors to the *named* day and reaches into the next:

```python
night = daypart_span(tuesday, "night")
print(night.start.isoformat(), "->", night.end.isoformat())
# 2027-06-08T21:00:00 -> 2027-06-09T06:00:00
print(night.start.day, night.end.day)
# 8 9
```

Because day-parts are ordinary spans, the interval algebra composes them.
Adjacent parts tile with no gap — `morning` ends exactly where `afternoon`
begins — so their union is one seamless span, and the gap between two
non-adjacent parts is itself a span:

```python
morning = daypart_span(tuesday, "morning")
afternoon = daypart_span(tuesday, "afternoon")
evening = daypart_span(tuesday, "evening")

print(morning.union(afternoon).start.isoformat(),
      morning.union(afternoon).end.isoformat())
# 2027-06-08T06:00:00 2027-06-08T18:00:00

# the stretch morning and evening leave between them is the afternoon:
print(morning.gap(evening) == afternoon)
# True
```

## The hour that stretched in summer

Ask what time it is and you assume the answer ticks at a steady rate — sixty
minutes, every hour, all year. For most of history that was not how anyone told
time. The pre-mechanical world counted a *fixed number of hours between sunrise
and sunset* — twelve, in the Greco-Roman and later European tradition — and
another fixed number through the night. Because the count was fixed but the
daylight was not, the hour itself breathed with the seasons. In high summer,
when the sun is up far longer, each of the twelve daytime hours had to be
*longer* to fit; in deep winter they shrank. At Rome's latitude the swing is
dramatic — a daytime hour ran to about **76 minutes at the June solstice** and
collapsed to roughly **46 minutes at the December solstice** — and the night
hours did the exact opposite. These are **temporal**, **seasonal**, or
**unequal** hours.

`temporal_hour_span` builds them straight on top of `sun_events`: it takes the
daylight span, divides it into the system's hour count, and hands back the
`hour_number`-th slice as a `DateSpan` whose *width is that hour's real length*.

```python
from chronologia import temporal_hour_span, ROMAN_HOURS, AstroDate

rome = (41.9, 12.5)
june = temporal_hour_span(AstroDate(2024, 6, 21), *rome, 1, ROMAN_HOURS)
december = temporal_hour_span(AstroDate(2024, 12, 21), *rome, 1, ROMAN_HOURS)
print(round(june.width.total_seconds() / 60), "min in June")
# 76 min in June
print(round(december.width.total_seconds() / 60), "min in December")
# 46 min in December
```

`hour_number` runs `1..24` for the Roman 12+12 system: hours 1–12 divide
sunrise→sunset, hours 13–24 divide sunset→next sunrise. The daytime hours tile
the daylight exactly — the twelfth ends on sunset with no fencepost gap — and
the width varies with date and latitude, which is the whole point. Ship-in
systems are `ROMAN_HOURS`, `ZMANIM_GRA` (Jewish *sha'ot zmaniyot* by the Vilna
Gaon — the same sunrise→sunset ÷ 12 geometry), and `EDO_JAPANESE` (six day and
six night hours). Every span is `basis="tabulated"`: it inherits the class-B
accuracy of the NOAA solar model, not an ephemeris.

The Magen Avraham reckoning of the *zmanim* is deliberately **not** shipped: it
runs dawn→nightfall at solar depressions of 16.1° and 8.5°, and `sun_events`
exposes only the 6°/12°/18° civil/nautical/astronomical twilights, so no honest
mapping exists yet — better a missing system than a mislabelled one.

### Counting from sunset: Italian and Babylonian hours

A different convention keeps the hour *equal* (a steady sixty minutes) but moves
the **origin** of the count to a solar event. Italian hours (*ore
all'italiana*) numbered 1–24 from sunset, so the clock struck 24 at sunset and
started over; Babylonian hours counted equal hours from sunrise.
`convention_time` returns the instant of a given count. Because the count wraps
modulo 24, the 24th hour lands back on the anchor:

```python
from chronologia import convention_time, sun_events, ITALIAN_HOURS

ev = sun_events(AstroDate(2024, 6, 21), *rome)
print(convention_time(AstroDate(2024, 6, 21), *rome, 24, ITALIAN_HOURS) == ev.sunset)
# True
```

### Polar honesty carries through

An unequal hour needs a sunrise and a sunset to divide; a clock count needs its
anchor event. When the sun never rises or never sets, `sun_events` returns a
typed `NoSunEvent`, and both functions **return it unchanged** — never raising,
never inventing a time:

```python
from chronologia import NoSunEvent

polar = temporal_hour_span(AstroDate(2024, 6, 21), 78.0, 15.0, 1, ROMAN_HOURS)
print(isinstance(polar, NoSunEvent), polar.kind)
# True polar_day
```

## Reference

| tool | what it does |
|---|---|
| `resolve_wall_clock(y, m, d, h, mi, zone)` | resolve a wall time against a DST zone: one instant, a `(earlier, later)` pair (fall-back), or a `NeverExisted` (spring-forward gap) |
| `civil_add(point, *, years, months, days, zone, timeline)` | calendar-aware arithmetic; with a DST `zone` a "day" is the true 23/24/25 hours |
| `utc_tai_offset(instant)` | cumulative seconds TAI leads UTC (1972 onward) |
| `utc_to_tai` / `tai_to_utc` / `utc_to_gps` / `gps_to_utc` | convert between the real timescales |
| `is_leap_second_day(day)` | was a leap second inserted on this UTC date? |
| `TAI_MINUS_GPS`, `GPS_EPOCH`, `LEAP_SECONDS`, `TABLE_VALID_UNTIL` | the constants and the shipped table |
| `local_mean_time(longitude_deg)` | the local-mean-time zone for a meridian (east positive) |
| `equation_of_time(date)` | the sundial-vs-clock offset on a date (`EOT_ACCURACY` bounds it) |
| `apparent_solar_time(instant, longitude_deg)` | what a sundial at that longitude reads |
| `sun_events(date, latitude, longitude)` | sunrise/sunset/solar-noon and the civil/nautical/astronomical twilights, in UTC (`SOLAR_ACCURACY` bounds it) |
| `sunset_day_start(date, latitude, longitude)` | the previous evening's computed sunset that opens a sunset-anchored calendar day |
| `temporal_hour_span(date, lat, lon, hour_number, system)` | the Nth unequal (temporal/seasonal) hour as a `DateSpan` whose width is its true season-varying length; `NoSunEvent` in polar conditions |
| `convention_time(date, lat, lon, hour, convention)` | the instant of an equal-hour clock count re-anchored to a solar event (Italian from sunset, Babylonian from sunrise) |
| `ROMAN_HOURS`, `ZMANIM_GRA`, `EDO_JAPANESE` | shipped proportional-hour systems (`UNEQUAL_HOUR_SYSTEMS`) |
| `ITALIAN_HOURS`, `BABYLONIAN_HOURS` | shipped clock-count conventions (`CLOCK_CONVENTIONS`) |
| `NoSunEvent` | a typed absence (`polar_day`/`polar_night`) returned when the sun never rises or never sets |
| `DAY_SUBDIVISIONS`, `DaySubdivision` | alternative divisions of the day, such as French decimal time |
| `moon_phase(instant)` | mean lunar phase fraction, `0.0`=new..`0.5`=full..→`1.0` |
| `next_phase(instant, phase)` / `previous_phase(instant, phase)` | next/previous `"new"`/`"first_quarter"`/`"full"`/`"last_quarter"` as a `DateSpan`, width `2 * MOON_PHASE_ACCURACY` |
| `lunation_number(instant)` | Brown Lunation Number of the containing lunation |
| `MOON_PHASE_ACCURACY`, `MEAN_SYNODIC_MONTH_DAYS`, `EPOCH_NEW_MOON` | the mean-model constants and their stated/measured accuracy |
| `daypart_span(date_or_span, name, region=None)` | the span a named day-part (morning, tarde, night) occupies on a date; midnight-crossers reach into the next civil day |
| `DAY_PARTS`, `DayPart` | the region-tagged day-part registry (CLDR day-period boundaries) |
| `DateSpan.intersect` / `.union` / `.gap` | half-open interval algebra over spans (overlap, seamless merge, the hole between) |
