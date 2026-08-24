# Timezones

This is the page you reached for the moment you thought, *"fine, but how does
it handle timezones?"* — the first hard question anyone who has been burned by
dates asks. The short answer is that `chronologia` treats a timezone as a
**political fact**, quarantines it away from everything that computes, and lets
it in only at a handful of clearly marked doors. This page walks through why,
where those doors are, how to wire the library up to the real world's zone
data, and how it compares to the other tools you might reach for.

Its companion, [Sun, moon, and seasons](sun-moon-and-seasons.md), tells the
natural-time story — sunrise, twilights, moon phases, sundials, local mean time,
and leap seconds. This one drills into the political zones themselves.

## Why everyone hates timezones

Timezones are hated because the word "time" quietly means **three different
things at once**, and a zone is the tangled rule that ties them together:

1. **An instant** — a physical moment, the same for everyone in the universe.
   The Voyager probe and you share instants; you do not share clocks.
2. **A wall-clock label** — what a clock on the wall *reads*: "1:30 AM,
   the 3rd of November". A label is a human name for a moment, and by itself it
   is ambiguous, because…
3. **A political rule** — the law that maps between the two. Some parliament
   decided that on such-and-such a night the clocks jump. That decision is not
   physics, not arithmetic; it is a *decree*, and it can change next year.

Confusion is what happens when code treats one of these as another. Here is the
whole problem in a single night. In New York, autumn 2024, the clock "falls
back": at 2 AM it jumps to 1 AM, so the wall reads **1:30 AM twice**, an hour
apart in real instants:

```python
from zoneinfo import ZoneInfo
from chronologia import resolve_wall_clock

ny = ZoneInfo("America/New_York")
earlier, later = resolve_wall_clock(2024, 11, 3, 1, 30, ny)
print(earlier.isoformat())   # 2024-11-03T01:30:00-04:00  (still summer time)
print(later.isoformat())     # 2024-11-03T01:30:00-05:00  (now winter time)
print((later - earlier).total_seconds() / 3600)   # 1.0 — a real hour apart
```

The *label* "1:30 AM" names two *instants*, because the *political rule* said
so. Any function that took "1:30 AM that night" and handed back one instant
would be guessing which one you meant — and half the time guessing wrong. A
library that hates you less does not guess. It hands you both and lets you
choose. That refusal to guess is the whole design, and the rest of this page is
what it looks like in practice.

## The quarantine principle

The core idea is a public-health metaphor. Zones are an *infection* — a source
of ambiguity and political churn — so everything that computes is kept in
**quarantine**, unable to catch it. Nothing in the computing core knows a
timezone exists:

- **The sun** takes a latitude and a longitude and answers in **UTC**. It has
  never heard of "Eastern Time"; the Earth turns the same in every jurisdiction.
- **The calendars** speak only **Julian Day Numbers** — a plain count of days.
  A day is a day whether or not a parliament is meddling with clocks.
- **Spans** measure **real elapsed time**. Their width is physics, not law.
- **The moon** is one **global instant** — a full moon happens for the whole
  planet at once; only the local clock reading of it differs.

Because the core is clean, a timezone can enter at **exactly four seams**, and
nowhere else. Naming them is the fastest way to hold the whole model in your
head.

**Seam 1 — wall-clock label → instant.** You have a clock reading and want the
real moment. This is the only place fold and gap ambiguity can arise, so it is
the only place they are *answered*, with a type, never a guess: one instant, a
`(earlier, later)` pair, or a `NeverExisted`.

```python
# unambiguous → one instant; gap → a typed "never existed + why"
noon = resolve_wall_clock(2024, 6, 1, 12, 0, ny)
print(noon.isoformat())                       # 2024-06-01T12:00:00-04:00

gap = resolve_wall_clock(2024, 3, 10, 2, 30, ny)   # spring-forward morning
print(type(gap).__name__, gap.discontinuity.kind.name)   # NeverExisted SKIP
```

**Seam 2 — instant → wall-clock rendering.** You have a real moment and want to
show it on a local clock. That is `astimezone`, and it can never be ambiguous —
one instant has exactly one reading per zone.

```python
from datetime import timezone
from chronologia import AstroDate

instant = AstroDate(2024, 6, 1, 16, 0, tzinfo=timezone.utc)   # 16:00 UTC
print(instant.astimezone(ny).isoformat())     # 2024-06-01T12:00:00-04:00
```

**Seam 3 — wall-preserving arithmetic.** "Same time tomorrow" is a statement
about the *label*, not the instant, so it belongs to `civil_add` with a zone.
Across a fall-back night, keeping the wall reading means living a real 25-hour
day — and the library tells you the true duration rather than pretending it was
24 hours:

```python
from chronologia import civil_add

start = AstroDate(2024, 11, 3, 0, 30, tzinfo=ny)   # just before fall-back
tomorrow = civil_add(start, days=1, zone=ny)
print(tomorrow.isoformat())                            # 2024-11-04T00:30:00-05:00
print((tomorrow - start).total_seconds() / 3600)       # 25.0 — a real extra hour
```

**Seam 4 — the civil-day anchor for solar queries.** The sun answers in UTC,
but "sunrise *on the 21st of June*" needs someone to say which civil day the
21st *is* — and that labelling is a zone's job. `sun_events` therefore takes the
civil date you care about (plus the physical latitude and longitude); the date
is the anchor, and you choose it deliberately. More on the subtlety of this seam
in [the solar/day-part connection](#the-solarday-part-connection) below.

```python
from chronologia import sun_events
ev = sun_events(AstroDate(2024, 6, 21), 40.0, -105.0)   # Denver, in UTC
print(ev.sunrise.strftime("%H:%M"))    # 11:30 — a UTC instant, zone-free
```

Four doors, each labelled, each with a typed answer. If a piece of code is not
standing at one of these four doors, it does not touch a timezone at all.

## Integration guide: chronologia + zoneinfo

Now the practical part: how to actually use this with the real world's zone
data.

### ZoneInfo objects plug straight in

`chronologia` invents no zone type of its own. An `AstroDate`'s `tzinfo` is the
ordinary `datetime` slot, so a standard-library `zoneinfo.ZoneInfo` drops in
directly and does all the real work:

```python
from zoneinfo import ZoneInfo
from chronologia import AstroDate

tokyo = ZoneInfo("Asia/Tokyo")
d = AstroDate(2024, 6, 1, 12, 0, tzinfo=tokyo)
print(d.utcoffset())   # 9:00:00
print(d.tzname())      # JST
```

Anything that satisfies the `tzinfo` protocol works the same way — `zoneinfo`,
`dateutil.tz`, a fixed `datetime.timezone`, or the library's own
[`LMTZone`](#pre-zone-history-lmtzone) for history before zones existed.

### Getting the zone database: `pip install tzdata`

`ZoneInfo` needs the IANA time-zone database ("tzdb"). On Linux and macOS it is
usually already on disk (`/usr/share/zoneinfo`); on Windows, and in slim
containers, it is not, and `ZoneInfo("Asia/Tokyo")` raises
`ZoneInfoNotFoundError`. The fix is a pip package that ships the same data:

```bash
pip install tzdata
```

`zoneinfo` finds it automatically. `chronologia` does **not** depend on it —
you install it only if your system lacks the OS copy, and you keep control of
which one you get.

### Why chronologia vendors no zone data — the Morocco story

That "you keep control" is a deliberate refusal, and it is worth understanding.
Zone rules change *constantly*, by decree, often with only weeks' notice. The
flow of a change is:

> a government issues a decree → **IANA** edits the tzdb → your OS (or the
> `tzdata` package) ships the update → your program picks it up.

`chronologia` sits at the *end* of that chain and vendors **nothing**, so a
zone change never requires a new release of this library — you just update
`tzdata`.

Morocco is the standing example. It observes permanent daylight saving time but
*suspends* it during Ramadan, whose dates move ~11 days earlier each year on
the Gregorian calendar. So Morocco changes its clocks **twice a year, on dates
that are not known until the government announces them**, sometimes at very
short notice. Any library that froze a copy of the world's zone rules into its
own source would be wrong about Morocco within months. By owning no zone data,
`chronologia` is wrong about Morocco *never* — it defers to whatever `tzdb` your
system currently trusts. The same discipline that makes the library refuse to
guess about a fall-back hour makes it refuse to guess about a decree it cannot
see.

### Turning user input into an instant: `resolve_wall_clock`

When a human types "1:30 AM", you have a *label*, not an instant — Seam 1. Never
assume; resolve:

```python
from chronologia import resolve_wall_clock, NeverExisted

result = resolve_wall_clock(2024, 11, 3, 1, 30, ny)
if isinstance(result, tuple):
    earlier, later = result
    print("ambiguous:", earlier.isoformat(), "or", later.isoformat())
elif isinstance(result, NeverExisted):
    print("that time was skipped:", result.discontinuity.kind.name)
else:
    print("unique:", result.isoformat())
# ambiguous: 2024-11-03T01:30:00-04:00 or 2024-11-03T01:30:00-05:00
```

Three branches, because there are genuinely three cases. Handling all three is
the difference between code that works in October and code that works in
November too.

### Displaying an instant, and "same time tomorrow"

To *show* a moment locally, use `astimezone` (Seam 2). To move by calendar days
while keeping the clock reading, use `civil_add` with a zone (Seam 3). The two
answer different questions and never quietly stand in for one another:

```python
from datetime import timedelta

start = AstroDate(2024, 11, 3, 0, 30, tzinfo=ny)

civil = civil_add(start, days=1, zone=ny)          # same clock reading, next day
absolute = start + timedelta(hours=24)             # exactly 24 real hours later
print(civil.isoformat())      # 2024-11-04T00:30:00-05:00  (25 real hours away)
print(absolute.isoformat())   # 2024-11-03T23:30:00-04:00  (24 real hours, earlier clock)
```

### The footgun: why a naive `astimezone` raises

Modern `datetime` has a trap that this library deliberately declines to inherit.
A **naive** `datetime` (no `tzinfo`) that you convert with `.astimezone()`
silently *assumes it is in the machine's local zone* — turning the system
timezone into a hidden global variable that the same code reads differently on a
laptop in Lisbon and a server in Denver:

```python
from datetime import datetime, timezone

naive = datetime(2024, 6, 1, 12, 0)          # no tzinfo
aware = naive.astimezone(timezone.utc)        # does NOT raise — silently guesses local
print(aware.tzinfo)                           # UTC
# ...but which instant it named depends on the machine that ran it.
```

`AstroDate` refuses to play. A naive `AstroDate` has no zone to convert *from*,
and inventing one from the environment is exactly the silent guess the library
exists to prevent, so it raises instead:

```python
try:
    AstroDate(2024, 6, 1, 12, 0).astimezone(timezone.utc)
except ValueError as exc:
    print("refused:", "naive" in str(exc))    # refused: True
```

The fix is to say what you mean — attach the zone the reading was *in* with
`replace(tzinfo=...)` (a re-label, not a conversion), then convert:

```python
reading = AstroDate(2024, 6, 1, 12, 0).replace(tzinfo=ny)   # "this was New York noon"
print(reading.astimezone(timezone.utc).isoformat())         # 2024-06-01T16:00:00+00:00
```

### Pre-zone history: `LMTZone` and local mean time

Timezones are a *railway-age invention* — before them, every town set noon to
its own sun. For dates before standard zones (Britain adopted railway time in
1847; the international zone system dates from 1884), there is no `ZoneInfo`
entry to use, and asking for one would be an anachronism. The library offers
**local mean time** instead: a fixed offset that is pure longitude, four minutes
of clock per degree.

```python
from chronologia import local_mean_time

lisbon = local_mean_time(-9.14)      # ~9.14° west of Greenwich (east-positive)
print(lisbon.tzname())               # LMT-00:36:34(lambda=9.140W)
print(lisbon.offset)                 # -1 day, 23:23:26  (about 36 min behind GMT)
```

This is not a guess dressed as a fact — it is the honest reckoning that actually
governed local clocks then. It also aligns with tzdb's own policy: the IANA
database explicitly states that its **pre-1970 data is not reliable** and is
provided only on a best-effort basis, because zone rules that far back are
poorly documented and often disputed. For deep history, longitude-based local
mean time is the honest floor, not a synthesised political zone the sources
cannot actually support.

### Far-future years: the mod-400 convention

`ZoneInfo` rules are defined for the years `datetime` can hold (1–9999). Ask an
`AstroDate` in the year 5,000,000 for its offset and there is no rule to read.
Rather than fail, the library evaluates the zone at a **proxy year**,
`2000 + (year mod 400)` — the Gregorian calendar (leap days and weekdays)
repeats on a 400-year cycle, so the proxy shares the real year's calendar shape,
and the *current* zone rule is projected onto it:

```python
far = AstroDate(5_000_000, 6, 1, 12, 0, tzinfo=ny)
print(far.utcoffset())    # -1 day, 20:00:00 — today's US DST rule, projected forward
```

Read this for exactly what it is: a **convention**, not a prediction. Nobody
knows whether the United States will keep daylight saving in the year five
million; the mod-400 answer freezes *today's* rule and extends it, so you get a
stable, reproducible label rather than an error. Where you need the true civil
rule of a far year, there is none to be had — the honest limit of the
convention is that it reports the present, not the future.

## How this compares to other libraries

A fair question: Python already has several date libraries. What does this one
do differently? The honest comparison runs along three axes:

- **Honesty semantics** — when a wall time is ambiguous or impossible, does the
  library force you to confront it (typed fold/gap answers), and does it carry
  span width and an evidentiary *basis*?
- **Range** — how far can dates go? Unbounded years, 18 calendars, deep time?
- **Scope** — does it model *civil* time only, or also everything before and
  around it (solar events, historical local time, calendar reforms, geology)?

Every other library here does civil time genuinely well. The difference is
almost never *quality* on the ground they cover — it is how much ground that is.

| Library | Ambiguous/skipped wall time | Year range | Calendars | Scope beyond civil time |
|---|---|---|---|---|
| **stdlib** `datetime`+`zoneinfo` | a single `fold` bit (0/1); the two readings compare **equal** | 1–9999 | proleptic Gregorian only | none |
| **pytz** | `localize()` / `normalize()` dance, easy to get wrong | 1–9999 | Gregorian | none |
| **dateutil** | `tz.resolve_imaginary`, `datetime_ambiguous` helpers | 1–9999 | Gregorian | recurrence rules, parsing |
| **pendulum** | raises on skipped, picks post-transition on ambiguous | 1–9999 | Gregorian | nice human durations/periods |
| **arrow** | follows stdlib fold | 1–9999 | Gregorian | humanization, parsing |
| **whenever** | **typed** `disambiguate=` (raise/earlier/later/compatible) | 1–9999 | Gregorian | DST-safe arithmetic |
| **chronologia** | **typed** answer: one / `(earlier, later)` / `NeverExisted` | **unbounded** | **18** | sun, moon, LMT, reforms, deep time |

### stdlib `datetime` + `zoneinfo` — verified live

The standard library is correct and complete for its range; two of its choices
are worth seeing directly. First, its answer to a fall-back ambiguity is a
single **`fold` bit** — and, famously, the two folded instants compare *equal*
even though their offsets differ:

```python
from datetime import datetime
from zoneinfo import ZoneInfo

zone = ZoneInfo("America/New_York")
first = datetime(2024, 11, 3, 1, 30, fold=0, tzinfo=zone)
second = datetime(2024, 11, 3, 1, 30, fold=1, tzinfo=zone)
print(first.utcoffset(), second.utcoffset())   # -1 day, 20:00:00 / -1 day, 19:00:00
print(first == second)                          # True  — different instants, still "equal"
```

Those offsets are UTC−4 and UTC−5 — genuinely different moments — yet `==` says
`True`. The fold bit works, but it hides the ambiguity behind a flag you have to
know to check. `chronologia` instead *returns two distinct, comparable
instants*, so the ambiguity is in your hands, not in a bit you might forget.

Second, the naive-`astimezone` footgun, [shown above](#the-footgun-why-a-naive-astimezone-raises):
stdlib assumes the machine's local zone; `AstroDate` raises. (Both snippets in
this section run against the live standard library.)

The stdlib's other boundary is simply range: `datetime` cannot hold a year
below 1 or above 9999, so no reform-era Julian date, no geological span, no
`44 BC` at all — which is where an unbounded `AstroDate` starts.

### pytz — the `localize` trap

`pytz` (the pre-`zoneinfo` workhorse) is fast and correct *if used exactly
right*, and a decade of Stack Overflow answers got it wrong. You must not pass a
`pytz` zone to the `datetime` constructor's `tzinfo`; doing so attaches the
zone's **Local Mean Time** offset (a quirky historical value like `-7:53`)
instead of a modern one. The correct spell is `zone.localize(naive_dt)` to
attach a zone, and `zone.normalize(dt)` after arithmetic to fix up a crossed DST
transition — two extra steps that are easy to forget and fail silently when you
do. `zoneinfo` (Python 3.9+) exists precisely to retire this trap, and
`chronologia` builds on `zoneinfo`, never on `pytz`.

```python
# doctest: skip
import pytz                                       # pytz 2024.1
eastern = pytz.timezone("US/Eastern")
wrong = datetime(2024, 6, 1, 12, 0, tzinfo=eastern)   # attaches LMT −4:56, a bug
right = eastern.localize(datetime(2024, 6, 1, 12, 0)) # the only correct way
```

### dateutil, pendulum, arrow

- **`dateutil.tz`** reads the same OS `tzdb` and adds excellent parsing and
  recurrence rules (`rrule`). For ambiguity it offers helper predicates
  (`tz.datetime_ambiguous`, `tz.resolve_imaginary`) rather than a type that
  makes you handle every case; it is point-based and Gregorian, years 1–9999.
- **`pendulum`** has the nicest ergonomics of the bunch — fluent `add()`/
  `subtract()`, real `Period`/`Duration` objects, DST-aware arithmetic. On
  ambiguity it raises for skipped times and picks the post-transition instant
  for repeated ones (`dst_rule`). Still point-based, Gregorian, 1–9999; no
  spans-with-basis, no deep time.
- **`arrow`** is about human-friendliness — `humanize()`, easy parsing/
  formatting — and follows the stdlib `fold` model underneath. Same range and
  scope limits.

```python
# doctest: skip
import pendulum                                   # pendulum 3.0
dt = pendulum.datetime(2024, 11, 3, 0, 30, tz="America/New_York")
print(dt.add(days=1).diff(dt).in_hours())         # 25 — DST-aware, like civil_add

import arrow                                       # arrow 1.3
print(arrow.get(2024, 6, 1, 12, 0).to("America/New_York"))
```

None of these are wrong; they are *smaller in scope on purpose*. They model the
civil clock beautifully. `chronologia` models the civil clock **and** the sun
that predates it, the calendars that reformed under it, and the deep time around
it — and pays for that reach by being less specialised at, say, natural-language
duration formatting.

### whenever — closest in spirit

`whenever` (Rust-backed, correctness-first, released 2024–2025) is the nearest
relative on the dimension this library cares most about: it makes ambiguity a
**typed decision** you cannot skip. Its `disambiguate=` parameter takes
`"raise"`, `"earlier"`, `"later"`, or `"compatible"`, and its arithmetic is
DST-safe by construction — the same instinct behind `resolve_wall_clock` and
`civil_add`. It is an excellent library and, on fold/gap handling, the one we
most resemble.

```python
# doctest: skip
from whenever import ZonedDateTime                 # whenever 0.6
# ambiguity is a required, typed choice — no silent default:
ZonedDateTime(2024, 11, 3, 1, 30, tz="America/New_York", disambiguate="earlier")
```

Where the two part ways is range and scope. `whenever` is civil time, done
rigorously, within years 1–9999 on the Gregorian calendar. `chronologia`
carries the same honesty *outward* — to unbounded years, seventeen calendars,
spans with an evidentiary basis, sunrise and moon phase, calendar reforms, and
geological deep time. If your problem is "civil timestamps, correctly," reach
for `whenever` without hesitation. If it is "any date, in any calendar, from the
dinosaurs to next Tuesday," that is the ground this library was built for.

## The solar/day-part connection

Zones and the sun meet cleanly *because* of the quarantine. Sun events, prayer
times, and unequal hours are all **computed as instants** (in UTC, from
latitude and longitude) and only **rendered locally** at Seam 2. That separation
dissolves two puzzles that otherwise look like bugs.

**The "prayer times jumped an hour" illusion.** People sometimes report that
sunrise or a prayer time "moved an hour overnight" in spring. It did not — the
*sun* did nothing unusual. What moved was the *clock*, because a DST transition
changed the offset between UTC and the wall reading. The underlying UTC instant
drifts by only its natural minute-a-day; the whole hour is an artefact of
rendering it against a clock that jumped. Compute in UTC, render locally, and
the illusion is explained rather than mysterious:

```python
from chronologia import sun_events, AstroDate
from zoneinfo import ZoneInfo

madrid = ZoneInfo("Europe/Madrid")
before = sun_events(AstroDate(2024, 3, 30), 40.4, -3.7).sunrise   # day before DST
after = sun_events(AstroDate(2024, 3, 31), 40.4, -3.7).sunrise    # DST begins
print(before.strftime("%H:%M"), after.strftime("%H:%M"))          # UTC: 06:02 / 06:00
# the UTC instants are ~2 min apart; only the LOCAL clock reading leaps an hour.
```

**The civil-day vs solar-day anchor.** This is Seam 4's subtlety. The sun's day
is anchored to a *physical meridian* (your longitude); the clock's day is
anchored to a *political zone*. Usually they roughly agree. Where a country has
chosen a zone far from its actual longitude, they diverge:

- **Kiribati** shifted the Line Islands to UTC+14 so the whole nation shares one
  calendar day — the clock's day and the sun's day are ~13–14 hours out of step.
- **Western China** runs on Beijing time (UTC+8) despite spanning what would
  naturally be five zones, so in Kashgar the sun peaks near 3 PM on the clock.

The library keeps the two inputs separate, exactly as the quarantine
demands: the **true latitude and longitude** feed the sun (which does not
care about politics), and the **political zone** decides which civil day
you are asking about. By default, `sun_events(date, lat, lon)` anchors on
the *solar* day and answers in UTC. When you mean a *civil* day — "sunrise
on their 21st of June" — say so explicitly:

```python
from zoneinfo import ZoneInfo
from datetime import date
from chronologia import sun_events

kiritimati = ZoneInfo("Pacific/Kiritimati")   # UTC+14, longitude ~157° WEST
ev = sun_events(date(2024, 6, 21), 1.87, -157.4, zone=kiritimati)
print(ev.sunrise.isoformat()[:22])
# 2024-06-21T06:23:56.73
```

Without `zone=`, the same question answered by solar-day anchoring lands a
full calendar day away — the classic off-by-one-day bug of solar libraries,
which here is a *named, tested convention* instead of an accident. The knob
does not secretly reconcile physics and politics; it states, in the call,
which of the two days you meant.

## Timezones ARE timelines

Everything above treats a zone as an *infection* to quarantine. There is a
second, complementary truth worth seeing plainly: a timezone **is** the same
mechanism as a calendar reform — a jurisdiction's history of civil
label-mappings, where a parliament decrees that a wall-clock label shall jump.
`chronologia` already has a vocabulary for exactly that — the
[Timelines](timelines.md) layer, with its `SKIP` (a label that never existed)
and `REPEAT` (one label, two moments). A daylight-saving change is a **`SKIP`**
(spring-forward: 2:30 AM never happened) or a **`REPEAT`** (fall-back: 1:30 AM
happened twice). The golden rule of this page, stated once:

> **A timezone is the Timeline mechanism at clock granularity.**

### The golden rule's parable: the country that deleted a Friday

At the end of 2011, **Samoa deleted a day**. To move from the American side of
the International Date Line to the Asian side — so its clocks matched Australia
and New Zealand, its main trading partners — the country jumped from UTC−11 to
UTC+13, and in doing so **Friday, 30 December 2011 simply never happened**.
Thursday the 29th was followed directly by Saturday the 31st. No baby was born
that Friday; no wage was paid; the day is a hole in the civil record. That is a
`SKIP`, the very same kind of event as the ten days Pope Gregory deleted in
1582 — a *decree* removing labels no clock ever bore:

```python
from chronologia import TIMELINES, NeverExisted

samoa = TIMELINES["samoa_2011"]
gone = samoa.date(2011, 12, 30)               # ask for the deleted Friday
print(type(gone).__name__)                    # NeverExisted
print(gone.discontinuity.kind.name)           # SKIP
# the days on either side are now neighbours — one day apart, not two:
print((samoa.date(2011, 12, 31) - samoa.date(2011, 12, 29)).days)   # 1
```

Samoa, the Philippines (which deleted 31 December 1844), and Alaska (whose 1867
transfer *repeated* a Friday while switching Julian→Gregorian — the one seam
that carries a `REPEAT` and a `SKIP` at once) live in `TIMELINES` as day-level
entries, because a whole civil day was added or removed.

### Events versus rules — why it is an adapter, not a copy

Here is the distinction that keeps the two layers honest, and it is the whole
reason `chronologia` vendors no zone data (the [Morocco
story](#why-chronologia-vendors-no-zone-data--the-morocco-story) above):

- **`tzdb` stores *rules*** — *intensional*, recurring law: "spring forward on
  the second Sunday of March, every year, until repealed." One sentence covers
  infinitely many future transitions.
- **A `Timeline` stores *events*** — *extensional*, one-time facts: "on this
  JDN, Samoa skipped a Friday." Each is written out, once.

So the library does **not** re-encode any zone rule (that would be copying
`tzdb`, and going stale the moment Morocco moves its clocks). Instead
`zone_timeline` is an **adapter**: give it a zone and a finite window, and it
*materializes* the rule into events — walking the window, finding the actual
UTC transitions `zoneinfo` reports, and emitting one discontinuity apiece in the
Timeline vocabulary:

```python
from datetime import datetime, timezone
from chronologia import zone_timeline

utc = timezone.utc
ny_view = zone_timeline("America/New_York",
                        datetime(2024, 1, 1, tzinfo=utc),
                        datetime(2025, 1, 1, tzinfo=utc))
for d in ny_view.discontinuities:
    print(d.kind.name, d.instant.date(), "|", d.citation)
# SKIP   2024-03-10 | UTC-5 -> UTC-4 (America/New_York)
# REPEAT 2024-11-03 | UTC-4 -> UTC-5 (America/New_York)
```

The offset *decreases* on fall-back (UTC−4 → UTC−5) so the November event is a
`REPEAT`; it *increases* on spring-forward so March is a `SKIP`. The view is
clock-granular — its `to_instant` gives back the same typed honesty as Seam 1
(one instant, an `(earlier, later)` fold pair, or a "never existed"):

```python
gap = ny_view.to_instant(datetime(2024, 3, 10, 2, 30))    # spring-forward morning
print(type(gap).__name__)                                  # ZoneNeverExisted

fold = ny_view.to_instant(datetime(2024, 11, 3, 1, 30))   # fall-back night
print((fold[1] - fold[0]).total_seconds() / 3600)          # 1.0 — an hour apart
```

Because it is a materialized view over *whatever `zoneinfo` currently trusts*, a
`zone_timeline` is never wrong about Morocco either — re-materialize it and you
get today's `tzdb`, not a frozen copy.

### The first door a zone ever opened: `zone_history_start`

Every `tzdb` zone begins in **Local Mean Time** — raw longitude, odd-minute
offsets — and has exactly one first transition to a rounded standard offset, the
moment the jurisdiction adopted standard time. `zone_history_start` surfaces it.
The classic case is London adopting **GMT on 1 December 1847** (railway time):

```python
from chronologia import zone_history_start

instant, lmt, standard = zone_history_start("Europe/London")
print(instant.date())                     # 1847-12-01
print(lmt.total_seconds())                # -75.0  — LMT ~1m15s west of Greenwich
print(standard.total_seconds())           # 0.0    — GMT
```

Read these values as a *faithful surfacing of `tzdb`*, cited to it — not an
independent historical claim. IANA warns that its pre-1970 data is not reliable,
so `zone_history_start` reports what `zoneinfo` actually returns and no more; for
deep history the honest floor remains longitude-based
[`local_mean_time`](#pre-zone-history-lmtzone).

## Reference

### Timezone-related public API

| tool | seam | what it does |
|---|---|---|
| `sun_events(date, lat, lon, zone=...)` | 4 | with `zone`, the date is that zone's civil day and events return aware |
| `resolve_wall_clock(y, m, d, h, mi, zone)` | 1 | wall label → instant: one `AstroDate`, an `(earlier, later)` pair (fall-back fold), or a `NeverExisted` (spring-forward gap) |
| `AstroDate.astimezone(tz)` | 2 | instant → wall reading in `tz`; **raises** on a naive `AstroDate` (no assumed local zone) |
| `AstroDate.replace(tzinfo=...)` | — | re-*label* a reading with a zone (does not convert the instant) |
| `AstroDate(..., tzinfo=zone)` | — | attach any `tzinfo` (a `zoneinfo.ZoneInfo`, `LMTZone`, or fixed `timezone`) |
| `AstroDate.utcoffset()` / `.tzname()` / `.dst()` | — | the `tzinfo` protocol, evaluated at a mod-400 proxy year when out of `datetime` range |
| `civil_add(point, *, days, zone=...)` | 3 | wall-preserving day arithmetic; with a DST `zone` a "day" is the true 23/24/25 hours |
| `sun_events(date, lat, lon)` | 4 | solar events for a civil date at a physical location, returned as UTC instants |
| `local_mean_time(longitude_deg)` | — | an `LMTZone` fixed-offset zone for pre-1884 history (four minutes per degree, east-positive) |
| `zone_timeline(tz, start, end)` | — | materialize a zone's transitions in `[start, end)` as a clock-granular `ClockTimeline` (fall-back → `REPEAT`, spring-forward → `SKIP`) |
| `zone_history_start(tz)` | — | the zone's first transition out of Local Mean Time: `(instant, lmt_offset, first_standard_offset)`, as `zoneinfo` reports it |
| `LMTZone` | — | the mean-solar-time zone type; duck-types `tzinfo` for labelling |
| `NeverExisted` | 1 | the typed "this wall time was skipped, and why" result |

### The four seams

1. **wall label → instant** — `resolve_wall_clock` (the only place fold/gap
   ambiguity is answered).
2. **instant → wall rendering** — `astimezone` (never ambiguous).
3. **wall-preserving arithmetic** — `civil_add(..., zone=...)` (the true
   23/24/25-hour day).
4. **civil-day anchor for solar queries** — the `date` you pass to `sun_events`
   labels which civil day the UTC solar instant belongs to.

### Conventions

- **Naive rejection.** A naive `AstroDate` never assumes the system-local zone;
  `astimezone` raises rather than reading a hidden global. Attach a zone with
  `replace(tzinfo=...)` first.
- **Mod-400 extrapolation.** Out-of-range years evaluate their zone at
  `2000 + (year mod 400)`, projecting *today's* rule forward as a stable
  convention — reproducible, but not a prediction of future law.
- **LMT fallback.** Before standard zones existed, the library offers
  longitude-based local mean time rather than an anachronistic `ZoneInfo`,
  matching tzdb's own policy that pre-1970 zone data is not reliable.
- **No vendored zone data.** `chronologia` ships no copy of the IANA database;
  it defers to your system's `zoneinfo` / `tzdata`, so a decree (Morocco,
  anywhere) reaches you through `tzdb` without a library release.
</content>
