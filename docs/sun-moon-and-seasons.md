# Sun, moon, and seasons

The calendars in this library answer "which day?". This page is about
*natural* time — the sky the calendar was built to track. Where does the sun
actually rise, and when do its twilights begin and end? What did an "hour" mean
before mechanical clocks, when it stretched and shrank with the seasons? When
is the real solstice, the true full moon, the local noon a sundial reads? And
why do atomic clocks and the turning Earth drift apart, so that every few years
a leap second must reconcile them? None of these are bugs. They are honest
facts about time, and the library reports them honestly.

> **Daylight saving time lives elsewhere.** The twice-a-year clock that "lies" —
> the fall-back hour that happens twice, the spring-forward hour that never
> happens, and wall-clock arithmetic across them — is a *political* fact about
> zones, not a natural one about the sky. It is owned by
> [timezones.md](timezones.md); `resolve_wall_clock` and `civil_add` live there.

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

### Civil days across the date line: `zone=`

`sun_events` (and `daypart_span`, `prayer_times`, `temporal_hour_span`,
`convention_time` alongside it) default to the **solar day**: `date` is read
as a UTC calendar day, exactly as above. `zone=None`, the default everywhere,
keeps that behaviour byte-identical — nothing above this subsection changes.

Pass a `tzinfo` as `zone` and `date` is read instead as that zone's **civil
day** — the wall-clock stretch `[00:00, 24:00)` on that date, in that zone.
Usually the two agree to within minutes. They can disagree by a whole
calendar day at Kiribati's Kiritimati island: its clocks run UTC+14, the
most-ahead zone on Earth, but the island itself sits at 157.4° **west** —
still numerically in the hemisphere the date line is supposed to separate
from UTC+14. Converting the *solar-day* sunrise into that zone lands it a day
late:

```python
from datetime import timezone
from zoneinfo import ZoneInfo
from chronologia import sun_events, AstroDate

kiritimati = ZoneInfo("Pacific/Kiritimati")
d = AstroDate(2024, 6, 21)

solar = sun_events(d, 1.87, -157.4)                       # solar day (UTC)
print(solar.sunrise.replace(tzinfo=timezone.utc)
      .astimezone(kiritimati).strftime("%Y-%m-%d %H:%M"))
# 2024-06-22 06:24  <- a day late for "21 June" in Kiritimati

civil = sun_events(d, 1.87, -157.4, zone=kiritimati)      # civil day
print(civil.sunrise.strftime("%Y-%m-%d %H:%M"))
# 2024-06-21 06:23  <- lands inside the civil day it was asked about
```

Under the hood, `zone=` computes the ordinary solar-day events for
`date - 1`, `date`, and `date + 1`, converts each real event into `zone`, and
keeps — field by field — whichever crossing lands in the requested civil
window. Because a date-line zone can make a civil day contain *two*
occurrences of one kind of event (or none), the convention is: **the earlier
instant wins** when there are two, and the `NoSunEvent`/absence for the solar
day sharing `date`'s own calendar date is returned when there are none (a
persistent polar day/night propagates exactly as before). Every real event
returned this way is an **aware** `AstroDate` in `zone`; a `NoSunEvent` is
returned unconverted, since it names no instant to convert.

`daypart_span(..., zone=...)` gets the same aware endpoints, resolved via
`resolve_wall_clock`: a boundary landing in a DST gap or fold resolves to the
*post-transition* instant (never raises, never picks arbitrarily), so
`DateSpan.width` on the result honestly reports 23 or 25 (or, for a narrower
part, correspondingly thinner/thicker) hours whenever the part's boundaries
straddle a transition. `prayer_times` and the unequal-hour functions
(`temporal_hour_span`, `convention_time`) accept the same `zone=` purely for
*presentation*: the computed instants are identical either way, only the
returned `AstroDate`s become aware wall-clock readings in `zone`.

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

```python
past_full = previous_phase(datetime(2024, 8, 1), "full")
print(past_full.basis)
# reconstructed
```

**The accuracy bound is measured, not assumed.** Cross-checked against the
US Naval Observatory's published 2024 phase table, the mean model's largest
new/full-moon miss is about 14 hours — hence `MOON_PHASE_ACCURACY`. Quarter
phases (`"first_quarter"` / `"last_quarter"`) carry a wider, undocumented-bound
error in the same check (up to ~23 hours) because the mean-quarter formula
omits an extra periodic correction that mean new/full moon mostly cancels —
a known asymmetry of the simple model, not a bug.
Every lunation is also numbered, in the older Brown convention almanacs used
1923-1983:

```python
from chronologia import lunation_number
print(lunation_number(datetime(2024, 1, 11, 11, 57)))
# 1250
```

Ask for a phase name outside the four recognised ones and you get a clear
error rather than a silent nonsense result:

```python
try:
    next_phase(datetime(2024, 1, 1), "waxing_gibbous")
except ValueError as exc:
    print("rejected:", exc)
# rejected: unknown moon phase 'waxing_gibbous'; expected one of ['first_quarter', 'full', 'last_quarter', 'new']
```

## When does summer actually start? Depends whom you ask

Meteorologists, astronomers, and the Sun itself give three different answers.

- **Meteorologists** start summer on the **1st of June** — fixed three-month
  blocks (Jun/Jul/Aug), tidy for climate statistics. That is the
  *meteorological* season, and it is not in this module.
- **Astronomers** start it at the **June solstice** and end it at the
  **September equinox** — each season tied to a real solar event. That is the
  *astronomical* season, and it is `astronomical_season_span`.
- **The Sun itself** reaches those turning points at instants you can compute
  to about a minute, from Jean Meeus's *Astronomical Algorithms* (ch. 27):
  `equinox`.

```python
from chronologia import equinox, astronomical_season_span, solar_term

# The four cardinal instants of 2024, in civil UTC, each a DateSpan whose
# width (2 minutes) IS the stated ~1-minute accuracy.
for which in ("march", "june", "september", "december"):
    sp = equinox(2024, which)
    mid = sp.start + (sp.end - sp.start) / 2
    print(which, mid.strftime("%Y-%m-%d %H:%M"), sp.basis)
# march 2024-03-20 03:06 reconstructed
# june 2024-06-20 20:50 reconstructed
# september 2024-09-22 12:43 reconstructed
# december 2024-12-21 09:20 reconstructed

# Astronomical northern summer: June solstice -> September equinox (~93 days).
summer = astronomical_season_span(2024, "summer")
print("summer runs", (summer.end - summer.start).days, "days")
# summer runs 93 days
```

The label flips with the hemisphere: the **same** March equinox that opens
spring in the north opens **autumn** in the south. Winter (north) and summer
(south) run past New Year's — December solstice of one year to the March
equinox of the next.

```python
north_spring = astronomical_season_span(2024, "spring", "north")
south_autumn = astronomical_season_span(2024, "autumn", "south")
print("same solar events:", north_spring == south_autumn)
# same solar events: True
```

The **basis is `"reconstructed"`** — these are closed-form arithmetic
reconstructions of an astronomical truth from mean orbital theory, the same
honest label the moon phases carry, for the same reason. And like everything
else, bad input is refused, not guessed:

```python
try:
    equinox(2024, "spring")  # not a cardinal-event name
except ValueError as exc:
    print("rejected:", exc)
# rejected: unknown event 'spring'; expected one of ['december', 'june', 'march', 'september']
```

### The 24 solar terms (jieqi)

The same Meeus machinery, run at 15° steps of the Sun's longitude instead of
only the 90° cardinals, gives the 24 Chinese *solar terms* — `lichun` (立春,
"start of spring", ~4 February) through `dongzhi` (冬至, the winter solstice).
Because these use Meeus's *low-accuracy* Sun longitude (ch. 25) rather than the
dedicated cardinal polynomial, they carry a wider bound — `SOLAR_TERM_ACCURACY`
is 30 minutes, honestly larger than the ~1-minute equinoxes.

```python
lichun = solar_term(2024, "lichun")
print("lichun:", lichun.start.strftime("%Y-%m-%d"))
# lichun: 2024-02-04
print("chunfen == March equinox longitude 0")
print(solar_term(2024, "chunfen").start.month)  # 3
```

This is the class-B improvement path for the Chinese-calendar family, but it
**does not upgrade the Chinese calendar itself** (`chronologia.calendars`),
whose tabulated month/leap-month structure stays authoritative — a
mean-longitude term instant is not a substitute for the table's true-longitude
astronomical basis.

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

### Prayer times

Islamic prayer times are the same solar hour-angle machinery with one extra
input: a *convention*. A convention is a named school of calculation, not a
truth — the schools publish different sun-depression angles for Fajr and Isha,
and the library computes what each angle implies. It names the school it used
and never rules on which is right.

```python
from chronologia import prayer_times, AstroDate

pt = prayer_times(AstroDate(2024, 2, 15), 30.0444, 31.2357, "egyptian_gas")
print([getattr(pt, f).strftime("%H:%M")
       for f in ("fajr", "sunrise", "dhuhr", "asr_time", "maghrib", "isha")])
# ['03:08', '04:36', '10:09', '13:18', '15:42', '17:00']   (UTC)
```

Dhuhr is solar noon and Maghrib is sunset, straight from `sun_events`. Fajr and
Isha are the depression-angle crossings — Fajr at the convention's Fajr angle
below the horizon, Isha at its Isha angle — the same shape as the civil /
nautical / astronomical twilights, with the school's angle in place of 6 / 12 /
18°. Asr is the shadow-length crossing: `asr="standard"` (factor 1, the
majority) or `asr="hanafi"` (factor 2), both cited.

Five conventions ship (`mwl`, `isna`, `egyptian_gas`, `umm_al_qura_makkah`,
`karachi`), each carrying the published source it quotes. They differ, and that
difference is the point:

```python
mwl = prayer_times(AstroDate(2024, 2, 15), 30.0444, 31.2357, "mwl")
isna = prayer_times(AstroDate(2024, 2, 15), 30.0444, 31.2357, "isna")
print(isna.fajr > mwl.fajr)   # ISNA's shallower 15° Fajr is later than MWL's 18°
# True
```

Umm al-Qura fixes Isha not by an angle but by a fixed **interval** — 90 minutes
after Maghrib — so both kinds are supported:

```python
from datetime import timedelta
makkah = prayer_times(AstroDate(2024, 2, 15), 21.4225, 39.8262, "umm_al_qura_makkah")
print(makkah.isha == makkah.maghrib + timedelta(minutes=90))
# True
```

**High-latitude honesty.** When the summer night is too short for the sun to
reach the depression angle (a "white night"), Fajr and Isha are simply
undefined — a typed `NoSunEvent`, never a fabricated time:

```python
from chronologia import NoSunEvent
short_night = prayer_times(AstroDate(2024, 6, 21), 60.0, 10.0, "mwl")
print(isinstance(short_night.fajr, NoSunEvent))
# True
```

The various higher-latitude estimation rules (middle-of-the-night, one-seventh,
angle-based) are deliberately **out of scope**: choosing what to substitute when
the arithmetic yields nothing is a jurisprudential decision, not a calculation,
and authorities differ. The convention mechanism is where such a rule would one
day attach as another named school — but the library will not invent one.

## Reference

| tool | what it does |
|---|---|
| `utc_tai_offset(instant)` | cumulative seconds TAI leads UTC (1972 onward) |
| `utc_to_tai` / `tai_to_utc` / `utc_to_gps` / `gps_to_utc` | convert between the real timescales |
| `is_leap_second_day(day)` | was a leap second inserted on this UTC date? |
| `TAI_MINUS_GPS`, `GPS_EPOCH`, `LEAP_SECONDS`, `TABLE_VALID_UNTIL` | the constants and the shipped table |
| `local_mean_time(longitude_deg)` | the local-mean-time zone for a meridian (east positive) |
| `equation_of_time(date)` | the sundial-vs-clock offset on a date (`EOT_ACCURACY` bounds it) |
| `apparent_solar_time(instant, longitude_deg)` | what a sundial at that longitude reads |
| `sun_events(date, latitude, longitude, zone=None)` | sunrise/sunset/solar-noon and the civil/nautical/astronomical twilights (`SOLAR_ACCURACY` bounds it); `zone=None` is the UTC solar day, a `tzinfo` reads `date` as that zone's civil day and returns aware events |
| `sunset_day_start(date, latitude, longitude)` | the previous evening's computed sunset that opens a sunset-anchored calendar day |
| `temporal_hour_span(date, lat, lon, hour_number, system)` | the Nth unequal (temporal/seasonal) hour as a `DateSpan` whose width is its true season-varying length; `NoSunEvent` in polar conditions |
| `convention_time(date, lat, lon, hour, convention)` | the instant of an equal-hour clock count re-anchored to a solar event (Italian from sunset, Babylonian from sunrise) |
| `ROMAN_HOURS`, `ZMANIM_GRA`, `EDO_JAPANESE` | shipped proportional-hour systems (`UNEQUAL_HOUR_SYSTEMS`) |
| `ITALIAN_HOURS`, `BABYLONIAN_HOURS` | shipped clock-count conventions (`CLOCK_CONVENTIONS`) |
| `prayer_times(date, latitude, longitude, convention, asr)` | the five daily Islamic prayer times plus sunrise, in UTC, for a named convention and Asr school |
| `CONVENTIONS`, `PrayerConvention` | the shipped Fajr/Isha schools (`mwl`, `isna`, `egyptian_gas`, `umm_al_qura_makkah`, `karachi`), each with its cited angles or interval |
| `ASR_METHODS`, `AsrMethod` | the two Asr shadow-factor schools (`standard` = 1, `hanafi` = 2), both cited |
| `NoSunEvent` | a typed absence (`polar_day`/`polar_night`) returned when the sun never rises or never sets |
| `DAY_SUBDIVISIONS`, `DaySubdivision` | alternative divisions of the day, such as French decimal time |
| `moon_phase(instant)` | mean lunar phase fraction, `0.0`=new..`0.5`=full..→`1.0` |
| `next_phase(instant, phase)` / `previous_phase(instant, phase)` | next/previous `"new"`/`"first_quarter"`/`"full"`/`"last_quarter"` as a `DateSpan`, width `2 * MOON_PHASE_ACCURACY` |
| `lunation_number(instant)` | Brown Lunation Number of the containing lunation |
| `MOON_PHASE_ACCURACY`, `MEAN_SYNODIC_MONTH_DAYS`, `EPOCH_NEW_MOON` | the mean-model constants and their stated/measured accuracy |
| `equinox(year, which)` | the March/June/September/December equinox or solstice as a `DateSpan` in civil UTC (Meeus ch.27; `EQUINOX_ACCURACY` ~1 min; `basis="reconstructed"`) |
| `astronomical_season_span(year, season, hemisphere)` | the equinox-to-solstice span of a season (the astronomical alternative to the meteorological three-month blocks), north or south |
| `solar_term(year, index_or_name)` | one of the 24 Chinese solar terms (jieqi) via mean-longitude crossing (Meeus ch.25; `SOLAR_TERM_ACCURACY` 30 min) — does not upgrade the tabulated Chinese calendar |
| `SOLAR_TERM_NAMES`, `EQUINOX_ACCURACY`, `SOLAR_TERM_ACCURACY`, `VALID_YEAR_RANGE` | the term names, the two stated bounds, and the 1000..3000 validity window |
| `daypart_span(date_or_span, name, region=None, zone=None)` | the span a named day-part (morning, tarde, night) occupies on a date; midnight-crossers reach into the next civil day; a `tzinfo` `zone` makes the endpoints aware, resolving DST gap/fold to the post-transition instant |
| `DAY_PARTS`, `DayPart` | the region-tagged day-part registry (CLDR day-period boundaries) |
| `DateSpan.intersect` / `.union` / `.gap` | half-open interval algebra over spans (overlap, seamless merge, the hole between) |
