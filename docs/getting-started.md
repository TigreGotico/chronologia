# Getting started

This page teaches you the three ideas the whole library is built from. You
do not need to know anything about calendars, and you barely need to know
Python. If you can run one line of code and read a printed answer, you can
follow along.

## Install

```bash
pip install chronologia
```

That is everything. The calendrical core is pure standard library; the
natural-language layer adds two small helpers (ovos-number-parser and
ovos-spec-tools), installed automatically with the line above. It never
talks to the internet. You need Python 3.10 or newer.

## The one big idea: give every day a number

Calendars disagree about what to *call* a day. Today might be "the 21st of
July" to you, "the 5th of Muharram" to someone else, and "day 2 of the week"
to a third person. That is a naming problem, and naming problems are hard.

So this library sidesteps it. Imagine laying every day that has ever existed
in a single straight line and writing a plain counting number under each one:

```
   … -2    -1     0     1     2     3     4    …
────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼────►
   day   day   day   day   day  today  day
  before                          ↑
                          just a big number
```

That number is called the **Julian Day Number**, or **JDN** for short. (The
name is historical; think of it simply as "the day's index on the number
line.") It keeps counting forward forever, and it keeps counting *backward*
forever too, straight through the age of the pyramids and the dinosaurs
without ever hitting a wall.

Here is the trick that makes the whole library work: **every calendar knows
how to turn its own dates into a JDN, and back again.** So to translate a
date from one calendar to another, you never compare the two calendars
directly — you send the date down to its number on the line, then ask the
other calendar what *it* calls that number. The number in the middle is the
common language.

Let's do it. When does the Hebrew year 5786 begin?

```python
from chronologia import CALENDARS

hebrew = CALENDARS["hebrew"]
print(hebrew.date(5786, 7, 1))   # 1 Tishri, the new year
# 2025-09-23T00:00:00
```

`date` pushed the Hebrew date down to its spot on the number line and asked
our everyday (Gregorian) calendar what day sits there, handing back an
`AstroDate` — a real date object, no integers to thread. The answer, the
23rd of September 2025, is the real Rosh Hashanah, computed from the Hebrew
calendar's own rules, not looked up anywhere.

The number in the middle is still there under the object — every JDN is just
an integer, so you can look at one directly:

```python
from chronologia import gregorian_to_jdn

print(gregorian_to_jdn(2000, 1, 1))
# 2451545
```

The first day of the year 2000 is day number 2,451,545 on the line. Nothing
magic — just its position.

## AstroDate: a date without the year limit

Python already has a way to hold a date: the built-in `datetime`. It is good,
but it has one hard limit — its year must be between 1 and 9999. Ask it about
44 BC or the year 12000 and it simply refuses.

`AstroDate` is this library's answer. **Think of it as a `datetime` whose year
can be any whole number at all** — deep into the past, far into the future. It
has all the same parts (year, month, day, hour, minute, and so on) and all the
same abilities (compare two dates, ask what weekday a date is, add a week to
it), and you can freely mix it with a real `datetime`:

```python
from chronologia import AstroDate
from datetime import datetime

caesar = AstroDate(-43, 3, 15)      # a day in 44 BC (we explain the -43 next)
print(caesar.isoformat())
# -000043-03-15T00:00:00
print(caesar < datetime(2020, 1, 1))
# True
```

### Why 44 BC is written as year −43

Historians count the years before the common era as "1 BC, 2 BC, 3 BC…" —
and, by an old convention, they put *no year zero* between 1 BC and AD 1.
That missing zero makes arithmetic go wrong: how many years from 1 BC to
AD 1? You would want to say "two", but the plain subtraction gives one.

Astronomers fixed this by giving that gap a real year 0. So they count:

```
  … 3 BC   2 BC   1 BC    AD 1   AD 2   AD 3 …   ← what historians say
  …  -2     -1     0       1      2      3  …    ← what AstroDate uses
```

1 BC becomes year 0, 2 BC becomes −1, and in general **X BC becomes the year
`1 − X`**. So 44 BC is `1 − 44 = −43`. This is called *astronomical year
numbering*, and it is the reason the arithmetic in this library never needs a
"skip the missing year" special case. You only ever meet the difference for
dates before AD 1. `AstroDate` will even convert back for you:

```python
print(AstroDate(-43, 1, 1).bc_year)
# 44
```

## DateSpan: a stretch of time

Here is a quiet truth about how people talk about time. When someone says
**"June 2027"**, they do not mean one secret instant at midnight on the 1st.
They mean *the whole month* — any moment from the start of June to the start
of July.

So this library's answers are not single instants; they are **stretches**. A
`DateSpan` is exactly that: a start and an end, holding everything in between.
And the *width* of the stretch is real, useful information — it tells you how
precise the answer is.

```python
from chronologia import DateSpan, AstroDate

june = DateSpan(AstroDate(2027, 6, 1), AstroDate(2027, 7, 1))
print(june.width)
# 30 days, 0:00:00
print(june.resolution.name)
# MONTH
```

A single day is a day wide. A month is a month wide. "The Jurassic" is
fifty-six million years wide. The width is the honesty: a wide span is the
library admitting it only knows the answer roughly.

## Basis: where an answer came from

Alongside its width, every span carries a one-word honesty label called its
**basis**. It answers a simple human question: *how do we know this?*

Think of it like the difference between four kinds of statement about time:

| basis | everyday analogy | what it means |
|---|---|---|
| `exact` | "the meeting is at 3 o'clock" | computed from a firm rule; no doubt |
| `tabulated` | "the tide table says high tide is 4:12" | read from an official published table |
| `reconstructed` | "historians think the battle was around 480 BC" | pieced together from evidence about the past |
| `predicted` | "the eclipse should be visible next April" | a forward guess about something not yet settled |

An `exact` answer is trustworthy to the second. A `reconstructed` one wears
its uncertainty openly. When the library combines two spans, the result takes
the *least* certain of their bases — a chain is only as strong as its weakest
link:

```python
from chronologia import combine_basis

print(combine_basis("exact", "tabulated"))
# tabulated
```

## Where to go next

You now know the three ideas — the **JDN** number line, the unbounded
**AstroDate**, the **DateSpan** stretch with its **basis** — that everything
else is built on. The other guides go deeper, gently:

- **[calendars.md](calendars.md)** — all 17 calendars, how to convert, and
  how far each one can be trusted.
- **[timelines.md](timelines.md)** — the days that vanished, the day that
  happened twice, and February 30th.
- **[deep-time.md](deep-time.md)** — geological periods, archaeology, and
  radiocarbon dating.
- **[sun-moon-and-seasons.md](sun-moon-and-seasons.md)** — sunrise, twilights,
  moon phases, seasons, unequal hours, leap seconds, and sundials.
- **[timezones.md](timezones.md)** — daylight-saving folds and gaps, and reading
  any `zoneinfo` zone as a timeline.
- **[eras-and-rulers.md](eras-and-rulers.md)** — BC/AD, emperors, consuls, and
  the Roman way of counting days.
- **[design.md](design.md)** — the developer's tour of how it all fits
  together.

## Reference: the public toolbox

Everything below can be imported straight from `chronologia`. It is grouped by
topic so you can find the tool for the job.

```python
# The number line and the unbounded date/stretch types
from chronologia import (
    AstroDate, DateSpan, WideDuration,
    combine_basis, is_leap_year, resolve_wall_clock, civil_add,
)

# The calendar hub: 17 calendars plus direct Gregorian/Julian conversion
from chronologia import (
    CALENDARS, Calendar, CalendarDate, TabulatedCalendar, CalendarRangeError,
    gregorian_to_jdn, jdn_to_gregorian,
    julian_to_jdn, jdn_to_julian,
    register_event_provider,
)

# Eras: ways of numbering years (BC/AD, Anno Mundi, Before Present, …)
from chronologia import (
    ERAS, Era, EraCounting,
    astro_year_range, resolve_bp, resolve_era, resolve_era_year_span,
)

# Leap seconds: the real UTC / TAI / GPS timescales
from chronologia import (
    LEAP_SECONDS, TABLE_VALID_UNTIL, table_valid_until,
    utc_tai_offset, utc_to_tai, tai_to_utc,
    utc_to_gps, gps_to_utc, is_leap_second_day,
    GPS_EPOCH, TAI_MINUS_GPS,
)

# Day cycles (the week and its cousins) and day subdivisions (decimal time)
from chronologia import (
    DAY_CYCLES, DAY_SUBDIVISIONS, DayCycle, DaySubdivision, resolve_cycle_day,
)

# Named periods: the geological chart and archaeological ages
from chronologia import (
    PERIODS, NamedPeriod, AmbiguousPeriodError,
    ICS_CHART_VERSION, INTCAL20_COARSE,
    lookup, candidates, children, subdivide, calibrate_c14,
)

# Regnal reckoning (emperors, consuls) and the Roman calendar
from chronologia import REGNAL_SEQUENCES, RegnalSequence, roman_to_julian

# Historical local time: mean solar time and the sundial's equation of time
from chronologia import (
    LMTZone, local_mean_time, equation_of_time, apparent_solar_time,
    EOT_ACCURACY,
)

# Timelines: a jurisdiction's calendar reforms and their discontinuities
from chronologia import (
    TIMELINES, Timeline, TimelineSegment,
    Discontinuity, DiscontinuityKind, CivilLabel, NeverExisted, proleptic,
)

# The granularity vocabulary a DateSpan reports
from chronologia import DateTimeResolution
```
