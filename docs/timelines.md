# Timelines

Calendars, as the other guides describe them, are tidy machines: feed one a
date, get back a day on the number line, forever, in both directions. But real
history is not tidy. Popes, parliaments, tsars and emperors have all, at one
time or another, stood up and decreed that *tomorrow shall be called something
the calendar would never have produced on its own.* A **timeline** is how this
library remembers those decrees for one country or jurisdiction.

## Why the calendar drifted, and what Gregory did

Start with the problem that caused most of the drama. The Julian calendar adds
a leap day every four years without fail. That is very slightly too often — the
real solar year is about eleven minutes shorter than the Julian calendar
assumes. Eleven minutes sounds like nothing, but over centuries it piles up:
by the 1500s the calendar had slipped ten full days behind the sun, and the
spring equinox — which the date of Easter depends on — was arriving on the
"wrong" date.

In 1582 Pope Gregory XIII fixed it in one stroke. He deleted ten days: in Rome,
Thursday the 4th of October was followed directly by Friday the **15th** of
October. The 5th through the 14th simply never happened. He also tightened the
leap-year rule so the drift would not return — that tightened rule is the
**Gregorian** calendar we use today.

Different countries took the leap in different centuries, and by then the gap
had grown. So the deleted days differ: ten in 1582, eleven by Britain's turn in
1752, thirteen by Russia's in 1918.

## The two rules that never change

Two things stay true no matter how wild the history gets, and they are what
keep this library honest:

1. **The number line never jumps.** The JDN count is a pure tally of days; it
   has no reforms and no gaps. All the drama lives in the *names* civil
   authorities assigned to days, never in the days themselves.
2. **Duration math is always safe.** Because you measure elapsed time on the
   number line, "how many days between these two dates" is never confused by a
   reform, even one that straddles it.

By default, a calendar has *no* reforms — a plain, straight-through mapping
called a **proleptic** timeline. You opt into a country's real history by
naming its timeline in `TIMELINES`.

```python
from chronologia import proleptic, AstroDate

# With no reforms, a timeline is just the bare calendar — hand it a real
# instant and it hands back the civil label a local would have written:
oct10 = AstroDate.from_calendar("julian", 1582, 10, 10)
print(proleptic("julian").from_astro(oct10))
# CivilLabel(year=1582, month=10, day=10)
```

## The four kinds of discontinuity

Every reform is one of exactly four shapes. Meet each one through a real
example.

### SKIP — days that never existed

This is Gregory's deletion: a block of labels that no day ever bore. Ask a
timeline about one of those labels and it does **not** crash. It hands back a
typed `NeverExisted` value that says *this date never existed here, and here is
the decree that explains why.*

```python
from chronologia import TIMELINES

rome = TIMELINES["rome_1582"]
answer = rome.date(1582, 10, 9)           # one of the deleted days
print(answer.discontinuity.kind.name)
# SKIP
print(answer.discontinuity.citation)
# Inter gravissimas (1582); gregorian_adoption_reference.html
```

`NeverExisted` is the library "telling you why, not failing" — it is a real
answer to a real question, carrying the historical citation, never an
exception you have to catch.

### REPEAT — one label, two days

Sometimes a reform runs the *other* way and a label happens **twice**. The
cleanest everyday version of this is the autumn clock change: when the clocks
"fall back", 1:30 AM comes around a second time, so "1:30 AM" that night names
two different instants an hour apart. (Time zones handle this case; see
[timezones.md](timezones.md), where `resolve_wall_clock` returns the
pair of instants for exactly this reason.) The same shape appears in calendar
history — for instance when a territory changes which side of the
International Date Line it sits on, and lives one calendar date over again.

### INSERT — a day no calendar would generate

Sweden spent twelve years bungling its switch to the Gregorian calendar. It
began a gradual transition, abandoned it, and to climb back onto the Julian
calendar it needed a one-off extra day in 1712: a **February 30th** — a date
that has existed exactly once in human history.

```python
sweden = TIMELINES["sweden_1700_1712"]
print(sweden.date(1712, 2, 30))            # a real day, as an AstroDate
# 1712-03-11T00:00:00
```

Everywhere else on Earth, that day was the 11th of March 1712. The timeline
stamps the "30 February" label onto that one JDN because no calendar in force
would ever have produced it.

### RELABEL — the year starts on a new day

The subtlest kind. For centuries, England began its civil *year* not on 1
January but on the 25th of March (Lady Day). So a date like "24 February 1731"
in an English document is what we would call early **1732** — the year number
had not yet ticked over. To avoid confusion, people wrote such dates with
*both* years, like "1731/32", a practice called **dual dating**.

When Britain finally reformed in 1752, it moved the year-start to 1 January
*and* deleted eleven days. The timeline models the year-start change so that
old English labels come out with their original year number:

```python
britain = TIMELINES["britain_1752"]

# The English civil label for the day we would call 24 Feb 1732:
feb24 = AstroDate.from_calendar("julian", 1752, 2, 24)
print(britain.from_astro(feb24))
# CivilLabel(year=1752, month=2, day=24)
```

And the deleted-days SKIP still applies to the same timeline:

```python
answer = britain.date(1752, 9, 5)         # inside the 11 deleted days
print(answer.discontinuity.kind.name)
# SKIP
```

## The ten timelines

Each entry in `TIMELINES` is one jurisdiction's history. Here is every one,
with the story it tells and a line you can run.

### rome_1582 (and its aliases) — the original ten-day deletion

Rome, October 1582: the 5th to the 14th deleted. Spain, Portugal, the Italian
principalities and Poland–Lithuania switched on the very same day, so they are
aliases of this timeline (`spain_1582`, `portugal_1582`, `italy_1582`,
`poland_1582`).

```python
rome = TIMELINES["rome_1582"]
print(rome.date(1582, 10, 9).discontinuity.after_label.as_tuple())
# (1582, 10, 15)
```

### britain_1752 — deletion *and* new year's day

Britain, September 1752: eleven days deleted, and the civil year moved from 25
March to 1 January (see the RELABEL example above).

```python
print(TIMELINES["britain_1752"].date(1752, 9, 5).discontinuity.kind.name)
# SKIP
```

### russia_1918 — thirteen days, and the "October" Revolution

By 1918 the gap was thirteen days. This is why Russia's October Revolution of
25 October 1917 fell on what the rest of the world called 7 November:

```python
russia = TIMELINES["russia_1918"]
print(russia.date(1917, 10, 25))
# 1917-11-07T00:00:00
```

### greece_1923 — one of the last European switches

Greece's civil switch in 1923: the day after 15 February (Julian) was 1 March
(Gregorian), deleting the 16th to the 28th.

```python
print(TIMELINES["greece_1923"].date(1923, 2, 20).discontinuity.kind.name)
# SKIP
```

### sweden_1700_1712 — the February 30th mess

Sweden's botched transition and its unique 30 February 1712 (see the INSERT
example above), followed by its actual Gregorian adoption in 1753.

```python
print(TIMELINES["sweden_1700_1712"].date(1712, 2, 30))
# 1712-03-11T00:00:00
```

### japan_1873 — from a lunisolar calendar to the Gregorian one

Japan switched at the start of 1873 (Meiji 6), abandoning its traditional
lunisolar calendar. The post-switch side works fully; the pre-1873 lunisolar
side is not yet a supported calendar, so a date before the switch is reported
as simply outside the modelled span:

```python
print(TIMELINES["japan_1873"].date(1873, 1, 1))
# 1873-01-01T00:00:00
```

Ask that same timeline about a *pre-1873* date and it reports, honestly, that
the date is outside the part of history it can currently model — the older
lunisolar calendar is not yet wired in — rather than inventing an answer.

## Reference: the timeline registry

| key | jurisdiction | reform kinds modelled |
|---|---|---|
| `rome_1582` | Papal States (Rome) | SKIP (10 days, Oct 1582) |
| `spain_1582` | Spain | alias of `rome_1582` |
| `portugal_1582` | Portugal | alias of `rome_1582` |
| `italy_1582` | Italian principalities | alias of `rome_1582` |
| `poland_1582` | Poland–Lithuania | alias of `rome_1582` |
| `britain_1752` | Britain | RELABEL (year-start) + SKIP (11 days) |
| `russia_1918` | Russia | SKIP (13 days, Feb 1918) |
| `greece_1923` | Greece | SKIP (13 days, Feb 1923) |
| `sweden_1700_1712` | Sweden | INSERT (30 Feb 1712) + SKIP (1753) |
| `japan_1873` | Japan | RELABEL (lunisolar → Gregorian) |

Two calls do all the work on any timeline, objects in and objects out:

- `timeline.date(year, month, day)` → the astronomical instant(s) a civil label
  names: a single `AstroDate`, an `(earlier, later)` tuple of `AstroDate`s for a
  REPEAT, or a `NeverExisted` for a label inside a SKIP window.
- `timeline.from_astro(moment)` → the civil `CivilLabel(year, month, day)` a
  person in that jurisdiction would have written for that `AstroDate`/`date`/
  `datetime`.

Underneath, the low-level `timeline.to_jdn((year, month, day))` and
`timeline.from_jdn(jdn)` speak raw Julian Day Numbers directly; the two calls
above are the object-returning facade over them.

And the four `DiscontinuityKind` values — `SKIP`, `REPEAT`, `INSERT`,
`RELABEL` — are exactly the four shapes above. The distinction the library
draws: if a calendar's own law predicts the change, it belongs to the
*calendar*; if it took a pope, a parliament, a tsar or an emperor, it belongs
to a *timeline*.
