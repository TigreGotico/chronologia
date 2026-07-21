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
| `DAY_SUBDIVISIONS`, `DaySubdivision` | alternative divisions of the day, such as French decimal time |
