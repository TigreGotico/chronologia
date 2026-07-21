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
from chronologia import AstroDate
from datetime import datetime

caesar = AstroDate(-43, 3, 15)        # the Ides of March, 44 BC
print(caesar.weekday())               # 2  — it was a Wednesday
print(caesar < datetime(2020, 1, 1))  # True — compares with datetime
```

Why −43 and not −44? Historians say "44 BC", but astronomers give the
year 0 to 1 BC so the arithmetic has no gap — so 44 BC is year −43.
You only ever notice this before year 1.

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
| Time itself | timezones with honest fall-back/spring-forward handling, leap seconds (UTC/TAI/GPS), historical local mean time, the French Revolution's 10-hour clock |

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
