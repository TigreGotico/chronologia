# chronologia

**A Python library that answers questions about dates — any date, in any
calendar, from the age of the dinosaurs to next Tuesday.**

Ever wondered…

- what day **"the 15th of Ramadan"** falls on this year?
- why Russia celebrates the **October** Revolution in **November**?
- when exactly **"the Jurassic"** was?
- what happened to the **ten days that vanished** in October 1582?
- whether **February 30th** ever existed? (It did. Once. In Sweden.)

Computers are surprisingly bad at these questions. Python's built-in
`datetime` can't even hold a year before 1 AD. This library answers all
of them — and it never needs the internet, never guesses, and tells you
honestly when history itself doesn't know the answer.

## Install

```bash
pip install chronologia
```

Pure Python. No dependencies. Python 3.10+.

## Your first three lines

When does the Hebrew year 5786 begin?

```python
from chronologia import CALENDARS, jdn_to_gregorian

hebrew = CALENDARS["hebrew"]
print(jdn_to_gregorian(hebrew.to_jdn(5786, 7, 1)))   # (2025, 9, 23)
```

That's September 23rd, 2025 — the real Rosh Hashanah. No lookup
service, no approximation: the library computes it from the same
arithmetic rules the Hebrew calendar itself is defined by.

### How did that work?

One trick powers everything here. Every day that has ever existed gets
a plain number — its **Julian Day Number** — day 1, day 2, day 3…
counting on forever in both directions. Every calendar in the library
knows how to turn its own dates into that number and back again. So
*any* calendar can talk to *any* other calendar by meeting at the
number in the middle. Seventeen calendars are built in — Hebrew,
Islamic, Chinese, Coptic, Ethiopian, Maya, French Revolutionary,
ancient Egyptian, and more (full list at the bottom).

## Dates that don't fit in `datetime`

Python's `datetime` stops at year 1. History doesn't. This library's
`AstroDate` works just like a `datetime` — same methods, same
comparisons, you can mix the two freely — but its year is unlimited:

```python
from chronologia import AstroDate, CALENDARS, jdn_to_gregorian
from datetime import datetime

# The Ides of March, 44 BC — a date in the ROMAN (Julian) calendar,
# so we let the Julian calendar say which day it really was:
ides = AstroDate(*jdn_to_gregorian(CALENDARS["julian"].to_jdn(-43, 3, 15)))
print(ides.weekday())               # 2  — Caesar was assassinated on a Wednesday
print(ides < datetime(2020, 1, 1))  # True — compares freely with datetime
```

Two small things just happened, and both matter. First: historians say
"44 BC", but astronomers give the year 0 to 1 BC so the arithmetic has
no gap — 44 BC is year −43; you only ever notice this before year 1.
Second: ancient dates were written in *their* calendar, not ours — the
Roman "March 15" lands on what our modern calendar, projected backwards,
would call March 13. The library keeps both straight, because that's
exactly the kind of thing humans get silently wrong.

## Nobody means midnight

When someone says **"June 2027"**, they mean the whole month — not one
secret instant at midnight on the 1st. This library takes that
seriously: its answers are **spans** — a start and an end. The width of
a span is honest information. A day is a day wide. A month is a month
wide. "The Jurassic" is fifty-six million years wide:

```python
from chronologia import lookup

jurassic = lookup("jurassic")
print(jurassic.span.start.year)   # -201598050  (about 201.6 million years ago)
print(jurassic.span.end.year)     # -143098050
```

Every span also carries a one-word honesty label, its **basis**: was
this *computed* from an exact rule (`"exact"`), *looked up* in a
published table (`"tabulated"`), *pieced together* by historians
(`"reconstructed"`), or *guessed about a future* nobody has decided yet
(`"predicted"`)? The Jurassic above says `tabulated` — it comes straight
from the official geological chart, uncertainties included.

Even a plain word like **"morning"** is a span, and — this matters — it
is a *convention* a culture agrees on, not a fact about the sun. So the
library keeps day-part boundaries as region-tagged data (from the Unicode
CLDR day-period rules) and hands you the span on a real date. English
splits the afternoon off from the evening at 18:00; Spanish runs one
*tarde* straight through to 20:00:

```python
from datetime import date
from chronologia import daypart_span

tuesday = date(2027, 6, 8)
print(daypart_span(tuesday, "afternoon").end.isoformat())         # 2027-06-08T18:00:00
print(daypart_span(tuesday, "tarde", region="es").end.isoformat())  # 2027-06-08T20:00:00

# "tuesday night" belongs to Tuesday, yet ends on Wednesday morning:
night = daypart_span(tuesday, "night")
print(night.start.isoformat(), "->", night.end.isoformat())
# 2027-06-08T21:00:00 -> 2027-06-09T06:00:00
```

## Stories the library can tell

### The ten days that never happened

In October 1582, Pope Gregory XIII fixed the slowly-drifting calendar
by deleting ten days: in Rome, October 4th was followed directly by
October 15th. Ask this library about one of the deleted days and it
doesn't crash or guess — it tells you *that date never existed there,
and why*:

```python
from chronologia import TIMELINES

rome = TIMELINES["rome_1582"]
print(rome.to_jdn((1582, 10, 9)))
# NeverExisted(label=1582-10-09, discontinuity=SKIP: Oct 4 → Oct 15,
#              citation='Inter gravissimas (1582)')
```

Different countries made the jump in different centuries — Britain in
1752 (eleven days by then), Russia in 1918 (thirteen). That's why the
"October Revolution" of October 25th, 1917 happened on what most of the
world called November 7th:

```python
from chronologia import jdn_to_gregorian
russia = TIMELINES["russia_1918"]
print(jdn_to_gregorian(russia.to_jdn((1917, 10, 25))))   # (1917, 11, 7)
```

And Sweden, after botching a gradual transition, needed a one-off
**February 30th** in 1712 to get back in step. The library knows that
day too — everywhere else, it was March 11th.

### Clocks lie twice a year

When clocks "fall back" in autumn, 1:30 AM happens **twice** that
night; when they "spring forward", 2:30 AM **never happens at all**.
Ask for a wall-clock time in a zone and get the honest answer — both
instants, or "that time didn't exist":

```python
from zoneinfo import ZoneInfo
from chronologia import resolve_wall_clock

ny = ZoneInfo("America/New_York")
resolve_wall_clock(2024, 11, 3, 1, 30, ny)   # → two instants (the fold)
resolve_wall_clock(2024, 3, 10, 2, 30, ny)   # → NeverExisted (the gap)
```

"This time tomorrow" across one of those edges is really a 23- or
25-hour day. `civil_add` keeps the wall clock and tells you the true
duration; plain `+ timedelta` stays exactly 24 hours. You choose which
question you're asking — the library never silently picks for you.

There's more where that came from: leap seconds (the reason precise
systems know UTC and TAI drift apart — 37 seconds so far), and even
local *sun* time for history before timezones existed, when noon in
every town was simply when the sun was overhead.

Give it a date and a place and it computes the actual sunrise, sunset,
solar noon, and the civil/nautical/astronomical twilights (the NOAA
algorithm, accurate to about a minute). And it stays honest at the
poles: north of the Arctic Circle in midsummer the sun never rises or
sets, so instead of inventing a time you get a typed `NoSunEvent`:

```python
from chronologia import sun_events, NoSunEvent, AstroDate

midsummer = sun_events(AstroDate(2024, 6, 21), 78.0, 15.0)  # Svalbard
print(isinstance(midsummer.sunrise, NoSunEvent), midsummer.sunrise.kind)
# True polar_day
```

From those solar events it also builds the **unequal hours** the pre-clock
world lived by — `temporal_hour_span` divides daylight into a fixed count, so a
Roman daytime hour stretches to ~76 minutes at Rome in June and shrinks to ~46
in December — plus the sunset-anchored Italian and sunrise-anchored Babylonian
clock counts (`convention_time`).
On the same machinery it computes Islamic prayer times as *named
conventions* — `mwl`, `isna`, `egyptian_gas`, `umm_al_qura_makkah`,
`karachi` — each a published school with its own Fajr/Isha depression
angles (and a per-call Shafi'i/Hanafi Asr factor); the library computes
what the angles imply and never rules on which school is right, returning
a typed `NoSunEvent` for the white-night latitudes where a depression
angle is never reached.

### Deep time, honestly

"66 million years ago" and "66.043 million years ago" are different
claims — the first is rounded to the nearest million, the second is
precise to the thousand. The library reads precision from how you wrote
the number, and the span's width says exactly what you claimed:

```python
from chronologia import resolve_bp
resolve_bp("66", "Ma")       # a span one million years wide
resolve_bp("66.043", "Ma")   # a span one thousand years wide
```

Radiocarbon dates get the same honesty: a "3500 BP" radiocarbon age is
**not** 3500 calendar years (radiocarbon clocks run uneven);
`calibrate_c14(3500)` converts through the published calibration curve
and answers with a span around 1900 BC, labelled `reconstructed`.

### Emperors, popes, and consuls

"Reiwa 7" (Japan's current era), "the consulship of Lentulus and
Marcellus" (how Romans named their years), "Year 5 of Ramesses II" — in
**three competing scholarly chronologies, 25 years apart**, and the
library gives you all three rather than pretending Egyptologists agree.
Even the full Roman date grammar works: *ante diem III Kalendas
Apriles* is March 30th, counted the way Romans counted — inclusively,
backwards from the Kalends.

## What it will NOT do (on purpose)

Some dates cannot be computed — by anyone — and this library refuses to
pretend otherwise:

- **Moon-sighting months.** The religious Islamic month begins when
  witnesses *see* the new crescent. A future sighting hasn't happened
  yet, so the honest answer is a two-day span labelled `predicted` —
  never fake certainty. (Saudi Arabia's *civil* calendar is published
  as an official table, so it *is* included — as a table, exactly as
  far as the table goes.)
- **The Chinese calendar beyond its tables.** Exact from 1901 to 2099
  via the Hong Kong Observatory's published tables; beyond that the
  true calendar needs astronomy, so the library stops rather than
  drifts.
- **Calendars nobody controlled.** Before Julius Caesar, Roman priests
  added days for political reasons — the "calendar" was whatever they
  decided that year. No software can recover decisions that were never
  rules. Historians' reconstructions are supported *as*
  reconstructions, wearing their uncertainty openly.

One rule covers all of it: **a span's width and basis always tell the
truth about what is knowable.**

## Reference

Full guides for everything above live in [`docs/`](docs/):

| | |
|---|---|
| 17 calendars | Gregorian, Julian, Revised Julian, Hebrew, Islamic (arithmetic + the Saudi Umm al-Qura table), Solar Hijri, Chinese (1901–2099), Coptic, Ethiopian, Armenian, ancient Egyptian, Maya Long Count, French Republican (arithmetic + historical equinox), Bahá'í (arithmetic + true equinox), ISO week |
| Timelines | 10 jurisdictions' calendar reforms — Rome, Britain, Sweden, Russia, Greece, Japan… |
| Named periods | the full geological chart (180 entries) plus regional archaeological ages — a British "Late Bronze Age" is not a Mesopotamian one |
| Eras & counts | BC/CE, Anno Mundi, Hijri years, Holocene, Byzantine, unix time, Julian Day, Before Present |
| Regnal years | Japanese nengō, Roman consuls, Egyptian chronologies |
| Time itself | [timezones](docs/timezones.md) with honest fall-back/spring-forward handling, leap seconds (UTC/TAI/GPS), historical local mean time, the French Revolution's 10-hour clock |
| Moon phases | mean-lunation arithmetic (new/first-quarter/full/last-quarter) as a `DateSpan` with a measured accuracy bound and honest reconstructed/predicted basis |

Every algorithm and every number in the data files is transcribed from
a cited published source — citations sit in the module docstrings and
data-file headers. Where sources disagree, both versions ship under
different names. Where sources are silent, the library says so instead
of guessing.

Used by
[ovos-date-parser](https://github.com/OpenVoiceOS/ovos-date-parser) to
understand dates in spoken language.

## License

Apache-2.0 © TigreGotico
