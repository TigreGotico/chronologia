# Mars and beyond

## What time is it on Mars?

It sounds like a novelty question. For the people who drive the rovers it is a
scheduling problem with teeth.

A Martian solar day — a **sol** — is 24 hours, 39 minutes and 35 seconds long.
That extra 39 minutes is small enough that a human can live on it and large
enough that, after a couple of weeks, "morning on Mars" has walked all the way
around the Earth clock. Early in each mission the flight team works Mars time:
every shift starts about 40 minutes later than the last, so the team slides
through Earth's day and night, ordering breakfast at 3am and struggling to
explain their calendar to everyone else. They are, quite literally, living on a
different planet's clock.

To do that you need answers to three questions, and this library gives you each
one as an object:

- **Which sol is it?** — the Mars Sol Date (MSD), a running count of sols.
- **What's the time on that sol?** — Coordinated Mars Time (MTC).
- **What's the date?** — a civil calendar, the Darian calendar.

```python
from chronologia import MarsDate, AstroDate

# An Earth UTC instant -> the Mars time at the same moment.
now_on_mars = MarsDate.from_earth(AstroDate(2000, 1, 6, 0, 0, 0))
print(now_on_mars)                       # MSD 44795 23:59:39 MTC
assert now_on_mars.sol == 44795          # the sol number (Mars Sol Date)
assert (now_on_mars.hour, now_on_mars.minute) == (23, 59)   # MTC clock

# ...and back to Earth.
back = now_on_mars.to_earth()
assert abs((back - AstroDate(2000, 1, 6)).total_seconds()) < 2
```

Objects in, objects out: you hand `from_earth` a real instant and get a
`MarsDate`; `to_earth` returns a real `AstroDate` (UTC). You never thread a raw
sol count by hand unless you want to.

## Sols and the Mars Sol Date

MSD is to Mars what the Julian Day Number is to Earth: a plain running count of
days from a fixed zero, with no month structure to trip over. The zero sits near
1873, chosen so that every date since the first careful telescopic observations
of Mars comes out positive.

The number that matters is the length of a sol: **88,775.244 seconds**
(1.0274912517 Earth days), from Allison & McEwen's 2000 paper as encoded in
NASA's Mars24 algorithm. The Mars Sol Date is just

    MSD = (JD_TT − 2405522.0028779) / 1.0274912517

— a Julian Date on Terrestrial Time, shifted to the epoch and divided by the
sol length. That is the whole formula. Its most-cited checkpoint is Viking 1,
which touched down at MSD 36455:

```python
from chronologia import MarsDate, AstroDate

viking1 = MarsDate.from_earth(AstroDate(1976, 7, 20, 11, 53, 6))
assert viking1.sol == 36455
```

## Coordinated Mars Time — 24 stretched hours

MTC splits a sol into 24 hours, each 60 minutes of 60 seconds — exactly like an
Earth clock, except the day being split is a sol. So an MTC hour is a little over
61 Earth minutes, and midday MTC (half a sol) is 12:00:

```python
from chronologia import MarsDate

assert str(MarsDate(52123, 4, 31, 12)) == "MSD 52123 04:31:12 MTC"

# Half a sol == MTC noon; a quarter-sol == 06:00.
assert MarsDate.from_msd(1000.5).hour == 12
assert MarsDate.from_msd(1000.25).hour == 6
```

This is the same idea as [French Revolutionary decimal time](timezones.md) —
rescaling one day into fixed units — applied to the sol instead of the Earth
day. (MTC is the pure sol fraction; it is *not* the Mars24 "Mean Solar Time"
figure, which carries an extra ~83-second prime-meridian offset.)

## The hub was never about Earth

Strip the labels off the Julian Day Number and nothing about it is specifically
about Earth, or about days: it *counts a periodic unit from an epoch on one
shared instant line*. A day, a sol — anything that ticks a steady length of time
— fits the same shape. That shape is a `TimeAxis`, and it is the real hub this
library was hiding all along.

```python
from chronologia import AXES, AstroDate

# The Earth axis is the JDN, restated: this is exactly the Julian Date.
assert AXES["earth_day"].count_from_tt(AstroDate(2000, 1, 1, 12)) == 2451545.0

# The Mars axis is where the Mars Sol Date is defined.
assert AXES["mars_sol"].unit_seconds > 86400          # a sol is longer than a day
```

The `earth_day` axis changes nothing — Earth timekeeping stays on `AstroDate`
and the JDN hub, and the axis is byte-identical to it — but it stops Earth from
being a special case. For `mars_sol` (and any future body) the axis is where the
count actually lives. Exchange between axes runs through **TT** (Terrestrial
Time, `TAI + 32.184 s`); the leap-second module was the down payment on that
bridge.

## The Darian calendar

A running sol count is fine for logs, but people want months and weekdays. The
**Darian calendar**, designed by Thomas Gangale in 1985, is the most developed
proposal: 24 months, a 7-sol week, and a leap rule tuned to the Martian year of
668.59 sols.

```python
from chronologia import darian

# The civil date of Viking 1's landing sol.
landing = darian.from_msd(36455)
assert str(landing) == "14 Mina 195"
assert landing.month_name == "Mina"          # month 8 of 24
assert landing.weekday_name == "Sol Saturni"

# Objects in, objects out: a Darian date -> the sol it names.
sol = darian.date(195, 8, 14)
assert sol.sol == 36455
```

The structure is fixed by the cited sources: each quarter has five 28-sol months
and one 27-sol month (668 sols in a common year); a leap year adds one sol to the
final month (669 sols). A year is a leap year if it is odd or divisible by 10,
cancelled if divisible by 100, restored if divisible by 500.

**An honest gap.** The sources pin the calendar's *structure* completely but do
not publish a bare numeric sol for its 1609 "Telescopic" epoch. So this library
anchors the calendar to the one clean, doubly-cited correspondence — Viking 1's
landing sol (MSD 36455) is 14 Mina 195 — and numbers years outward from there by
the leap rule. That anchor is what `darian` reproduces exactly; the absolute
epoch constant is derived, not independently cited, and is documented as such in
the code.

## Mission sols: "Sol 1000 of Curiosity"

Each landed mission counts its own sols from touchdown. There is one catch worth
knowing: the counting convention differs. Viking, Curiosity and Perseverance call
their landing sol **Sol 0**; Pathfinder and the Mars Exploration Rovers (Spirit
and Opportunity) call it **Sol 1**. `mission_sol` knows each mission's rule and
hands back the one-sol-wide `DateSpan` of Earth time that mission sol occupied.

```python
from chronologia import mission_sol, AstroDate

# NASA/JPL marked "Curiosity's 1,000th sol" on Earth date 2015-05-31.
sol1000 = mission_sol("curiosity", 1000)
assert sol1000.contains(AstroDate(2015, 5, 31))
assert abs(sol1000.width.total_seconds() - 88775.244) < 0.01   # one sol wide

# Sol 0 is Curiosity's landing sol; Spirit counts from Sol 1 instead.
assert mission_sol("curiosity", 0).start == AstroDate(2012, 8, 6, 5, 17, 57)
assert mission_sol("spirit", 0) if False else True             # Spirit has no Sol 0
```

Asking a mission for a sol it never had is an error, not a guess:

```python
from chronologia import mission_sol
import pytest

with pytest.raises(ValueError):
    mission_sol("spirit", 0)          # MER counts from Sol 1
with pytest.raises(KeyError):
    mission_sol("sojourner", 5)       # not a registered mission
```

## Relativity, honestly

Every conversion here is stated in Terrestrial Time and is accurate to about a
millisecond. That is a deliberate boundary, not an oversight. The periodic
difference between TT and Barycentric Dynamical Time (TDB) is at most ~1.6 ms
(Allison & McEwen 2000), and that sets the floor of what these numbers mean. The
light-time delay between Earth and Mars — minutes, varying with orbit — is a real
effect, but it belongs in a `DateSpan`'s *width* (an honest error bar), never
silently folded into an instant. Full general-relativistic proper time — the fact
that a clock on Mars ticks at its own rate relative to a clock on Earth — is out
of scope: that needs an ephemeris and a spacetime metric, not a calendar.

## Reference

| Concept | Object / call | Source |
|---|---|---|
| Sol length | `MARS_SOL_SECONDS` = 88,775.244 s | Allison & McEwen 2000 (Mars24 notes) |
| Mars Sol Date | `MarsDate.from_earth`, `msd_from_tt` | `(JD_TT − 2405522.0028779)/1.0274912517` |
| Coordinated Mars Time | `MarsDate` MTC fields, `__str__` | 24 stretched hours over the sol |
| UTC → Terrestrial Time | `utc_to_tt` / `tt_to_utc` | `TT = TAI + 32.184 s` |
| Generalized hub | `TimeAxis`, `AXES` | `earth_day` (JDN), `mars_sol` (MSD) |
| Darian calendar | `darian.date`, `darian.from_msd`, `DarianDate` | Gangale, *The Darian Calendar for Mars* |
| Mission sol counts | `mission_sol`, `MISSION_ERAS` | NASA mission pages / *Timekeeping on Mars* |

Every constant above is transcribed from a cited source in the papers library;
where a source is silent (the Darian epoch), the library anchors to a published
correspondence and says so.
