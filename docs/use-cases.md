# Who is this for?

`chronologia` is a date-reckoning engine. It converts between calendars, holds
years no `datetime` can, and — the part that matters most — hands back **spans**
whose width and **basis** tell you honestly how well anything is really known.
That honesty turns out to be useful to very different people for very different
reasons.

This page walks through seven audiences. Each one gets a story about a real
person with a real problem, a **runnable program** that solves an instance of
it, and a few pointers into the deeper guides. The programs are the showcase:
copy any one of them and it runs.

A note before we start: voice assistants are the **last** section, not the
first. `chronologia` was built to reckon time correctly; being a good backend
for a language parser is one thing that falls out of that, not the reason it
exists.

---

## 1. Digital humanities & archives

Amara catalogues a photographer's estate — nine thousand prints, and almost none
of them dated to the day. Her finding aid is full of the phrases archivists live
with: a print marked "1848?", a batch stamped only "185X", a bundle of letters
one of which is a firmly dated `1856-06-01` and another that a previous curator
pencilled as "circa the 1850s". She cannot write a plain calendar date for most
of these, because she *does not have one* — she has a stretch of time and a
degree of confidence. When a colleague at another institution sends their own
catalogue to merge, the same object turns up written three different ways.

What she needs is not prettier date strings. She needs to **compute** with the
uncertainty: to normalise every catalogue into one shape, and then to answer
questions like "does this circa-dated letter predate that firmly dated one?"
without the software quietly inventing a precision nobody has. The Library of
Congress already standardised how to *write* these dates — the Extended
Date/Time Format (EDTF) — and `chronologia` reads EDTF straight into spans, so
the honest answer to "which came first?" can be *"they overlap — we cannot say"*.

```python
from chronologia import parse_edtf, format_edtf

# A slice of the finding aid, exactly as different catalogues wrote it.
catalogue = ["1848?", "185X", "1856-06-01", "1840/1849"]

for entry in catalogue:
    span = parse_edtf(entry).span
    # Normalise: every entry becomes a start, an end, and an honesty label.
    print(f"{entry:12} {span.start.isoformat()[:10]} .. "
          f"{span.end.isoformat()[:10]}  ({span.basis})")
# 1848?        1848-01-01 .. 1849-01-01  (reconstructed)
# 185X         1850-01-01 .. 1860-01-01  (exact)
# 1856-06-01   1856-06-01 .. 1856-06-02  (exact)
# 1840/1849    1840-01-01 .. 1850-01-01  (exact)

# Now the real question: the "circa 1850s" letter (185X) and a firmly
# dated one (1856-06-01) — which came first?
circa = parse_edtf("185X").span
dated = parse_edtf("1856-06-01").span

if circa.overlaps(dated):
    print("Order unknown: the circa span contains the dated letter.")
elif circa.end <= dated.start:
    print("The circa letter definitely predates the dated one.")
else:
    print("The circa letter definitely postdates the dated one.")
# Order unknown: the circa span contains the dated letter.

# A genuinely earlier entry answers cleanly — no false modesty either:
earlier = parse_edtf("1848").span
assert earlier.end <= dated.start          # definitely before
assert not earlier.overlaps(dated)

# Round-trip back out to share with the other institution:
print(format_edtf(circa))                  # 185X
```

The `overlaps` test is doing the honest work: the "1850s" letter *might* be
older than the 1856 one or might not, and the span-overlap says exactly that
instead of pretending a decade is a day. A firmly earlier entry (`1848`) is
reported as definitely-before, so honesty does not mean uselessness.

**What else you'll want.** The full EDTF surface — decades, seasons, "unknown
digit" masks, uncertain/approximate qualifiers, and years too big for
`datetime` — is in [edtf.md](edtf.md). The span type itself, and what its width
and `basis` mean, is in [getting-started.md](getting-started.md). If your
collection reaches into deep time (`Y170000002`), that Just Works because
`AstroDate` has no year limit.

---

## 2. Historians & genealogists

Ravi is untangling a parish register from the 1730s and keeps hitting the same
trap. An ancestor appears to have been "born 1731 and died 1731" at what the
record implies was a ripe old age — impossible, until you remember that England
before 1752 started its civil year on **25 March**. A January 1731 baptism and a
December 1731 burial were, to the people writing them, nearly a *year* apart, and
many careful scribes wrote such dates *twice* — "1731/2" — to cover both
conventions. Get the calendar wrong and a whole life gets compressed into a
phantom single year.

The traps multiply. His sources date events in the **Julian** ("Old Style")
calendar while a modern gazetteer gives **Gregorian** ("New Style") dates for the
same era, so subtracting them naively is off by days. Some documents number the
year by the reigning monarch — "the 5th year of George II" — not by an absolute
count. And the reforms landed in different years in different countries: Britain
1752, Russia 1918, and Sweden's famously botched transition that produced a real
**30 February 1712**. `chronologia` keeps every one of these straight, because
each calendar meets every other at the day-number underneath.

```python
from chronologia import julian_to_jdn, gregorian_to_jdn, TIMELINES, REGNAL_SEQUENCES

# "How many days between a Julian-dated event and a Gregorian-dated one?"
# An action reported in a Russian (Old Style / Julian) dispatch as 19 Aug 1700,
# and a treaty dated in a Western (New Style / Gregorian) chancery as 10 Sep 1700.
old_style = julian_to_jdn(1700, 8, 19)
new_style = gregorian_to_jdn(1700, 9, 10)
print("days apart:", new_style - old_style)
# days apart: 11

# Done the naive way — subtracting the calendar numbers as if both were the
# same calendar — you would get 22 days and be wrong by the 11-day O.S./N.S. gap.

# Regnal-year sources: "the Nth year of a ruler" -> a real Gregorian span.
# (George II isn't shipped; the machinery is the same — here the Japanese nengo
#  and Roman consuls that ARE shipped stand in for the demonstration.)
meiji1 = REGNAL_SEQUENCES["nengo"].year_span("meiji", 1)
print("Meiji 1 began:", meiji1[0].isoformat()[:10])
# Meiji 1 began: 1868-10-23

consul = REGNAL_SEQUENCES["consuls"].year_span("caesar_antonius", 1)
print("that consulship was:", consul[0].bc_year, "BC")
# that consulship was: 44 BC

# The reforms themselves, as jurisdiction timelines. Russia jumped in 1918,
# so its "25 October 1917" is the world's 7 November:
print("October Revolution:", TIMELINES["russia_1918"].date(1917, 10, 25).isoformat()[:10])
# October Revolution: 1917-11-07

# And Sweden's one-off 30 February 1712 — a day that existed exactly once:
print("Swedish leap day:", TIMELINES["sweden_1700_1712"].date(1712, 2, 30).isoformat()[:10])
# Swedish leap day: 1712-03-11
```

The eleven-day answer is the whole point: the two events were recorded in two
calendars, and the only correct way to measure between them is to send both down
to the day-number line and subtract *there*. The regnal spans and the reform
timelines let you place a source's own dating into the modern frame without
hand-computing any offsets.

**What else you'll want.** Regnal sequences, Roman consular pairs, the three
competing Egyptian chronologies, and the backwards-counting Roman *ante diem*
grammar are in [eras-and-rulers.md](eras-and-rulers.md). Every jurisdiction's
reform — the deleted days, the doubled days, the dateline hops — is in
[timelines.md](timelines.md). The calendars themselves, and how far each is
trustworthy, are in [calendars.md](calendars.md).

---

## 3. Archaeologists & geologists

Nadia runs a dig on a hillfort. Two numbers land on her desk the same week and
they do not speak the same language. The lab reports a charcoal sample at "3500
BP" — a **radiocarbon** age — and her stratigraphy sits against the geological
column with its named ages and their published boundaries. She knows the trap
that catches every first-year: a radiocarbon "3500 BP" is *not* 3500 calendar
years ago, because atmospheric carbon-14 has wobbled over the millennia and the
clock runs uneven. To get a calendar date she must push the measurement through
a calibration curve.

The other half of her problem is naming. Her find is "Bronze Age" — but *whose*
Bronze Age? The British one and the Mesopotamian one are centuries apart, both
real, both correctly called "the Bronze Age". A catalogue that silently picks one
is worse than useless. And when she writes "66 million years" versus "66.043
million years" in a report, those are different **claims** about precision that a
naive number would flatten. `chronologia` keeps calibrated spans, region-tagged
ages, and significant-figure widths all honest.

```python
from chronologia import calibrate_c14, resolve_bp, candidates, lookup, subdivide, AmbiguousPeriodError

# 1. Radiocarbon -> calendar. The answer is a SPAN, marked reconstructed,
#    never a single confident year.
c14 = calibrate_c14(3500)                  # 3500 radiocarbon years BP
print("calibrated:", c14.start.year, "..", c14.end.year, f"({c14.basis})")
# calibrated: -1950 .. -1850 (reconstructed)
# -> roughly 1900 BC, not "3500 years ago" (which would be ~1550 BC).

# 2. Whose Bronze Age? A bare name is ambiguous, so it refuses to guess.
try:
    lookup("bronze age")
except AmbiguousPeriodError:
    for period in candidates("bronze age"):
        print(f"  {period.region}: {period.span.start.year} .. {period.span.end.year}")
    # GB: -2499 .. -799
    # MESO: -3299 .. -1199

british = lookup("bronze age", region="GB")
late_bronze = subdivide(british, "late")   # chart-defined subdivision wins
print("Late British Bronze Age:", late_bronze.start.year, "..", late_bronze.end.year)

# 3. Significant figures: the WIDTH is the precision claim. Pass strings,
#    because "66" and "66.043" carry different meanings the moment you type them.
rough = resolve_bp("66", "Ma")
precise = resolve_bp("66.043", "Ma")
print("rough width (yr): ", round(rough.width.days / 365.25))       # ~1,000,000
print("precise width (yr):", round(precise.width.days / 365.25))    # ~1,000
```

The calibrated span lands the charcoal near 1900 BC and *says* it is
reconstructed; the naive "3500 years ago" would have put it 350 years too young.
The region tags stop the Bronze-Age ambiguity from ever resolving silently. And
the two `resolve_bp` widths — a million years versus a thousand — are the library
reading precision straight off the digits you wrote.

**What else you'll want.** The geological chart (ICS), the archaeological ages,
walking the hierarchy, and the honest caveat that the shipped radiocarbon curve
is a *locating* tool and not a substitute for OxCal are all in
[deep-time.md](deep-time.md). Before-Present numbering (and why "present" is
frozen at 1950) is in [eras-and-rulers.md](eras-and-rulers.md).

---

## 4. Religious & cultural communities

Yusuf coordinates a shared civic calendar for a city with a dozen faith
communities. Every year the same questions arrive, and every year the naive
answers cause offence. When is Easter — and does he mean the Western date or the
Orthodox one, which can fall five weeks later? When does Ramadan begin — and can
he *honestly* print a date, or only a window, given that the religious month
starts on a human moon-sighting nobody can predict? He wants prayer times on the
programme, but "prayer times" is not one thing: different schools use different
sun-depression angles, and printing one as if it were universal is a mistake.

The cultural side is just as particular. The community centre wants the Chinese
zodiac animal and the date of the New Year for its festival; the synagogue plans
around the Hebrew calendar's own arithmetic. None of these are approximations to
be smoothed over — they are exact systems that simply disagree with the civil
calendar and with each other. `chronologia` computes each from its own rules and,
crucially, refuses to fake certainty where the tradition itself withholds it.

```python
from chronologia import easter, prayer_times, CALENDARS, year_cycle_label, AstroDate
from zoneinfo import ZoneInfo

# Easter, both traditions, on the civil calendar people actually use:
print("Western Easter 2027: ", easter(2027, "gregorian").isoformat()[:10])
print("Orthodox Easter 2027:", easter(2027, "julian_gregorian_date").isoformat()[:10])
# Western Easter 2027:  2027-03-28
# Orthodox Easter 2027: 2027-05-02

# Ramadan planning, honestly. Saudi Arabia PUBLISHES a civil table (Umm al-Qura),
# so a civil date is real and computable:
ramadan = CALENDARS["umm_al_qura"].date(1449, 9, 1)   # 1 Ramadan 1449 AH
print("Civil 1 Ramadan 1449:", ramadan.isoformat()[:10])
# Civil 1 Ramadan 1449: 2028-01-28
# The RELIGIOUS start still waits on a moon-sighting — the honest answer there is
# a two-day predicted window, never one confident date. (See calendars.md.)

# Prayer times as a NAMED convention — the angle school is explicit, not hidden:
pt = prayer_times(AstroDate(2028, 1, 28), 21.4225, 39.8262,
                  convention="umm_al_qura_makkah", zone=ZoneInfo("Asia/Riyadh"))
print("Fajr / Maghrib in Makkah:", pt.fajr.strftime("%H:%M"), "/", pt.maghrib.strftime("%H:%M"))

# Chinese zodiac and New Year for the festival:
print("2027 is the year of the", year_cycle_label(AstroDate(2027, 6, 1), "chinese_zodiac"))
print("Chinese New Year 2027:", CALENDARS["chinese"].date(2027, 1, 1).isoformat()[:10])
# 2027 is the year of the goat
# Chinese New Year 2027: 2027-02-06

# Hebrew calendar arithmetic — days from Rosh Hashanah to Passover, computed
# from the calendar's own rules, not looked up:
heb = CALENDARS["hebrew"]
rosh = heb.date(5786, 7, 1)
passover = heb.date(5786, 1, 15)
print("Rosh Hashanah -> Passover:", (passover - rosh).days, "days")
# Rosh Hashanah -> Passover: 191 days
```

Two Easters, a *civil* Ramadan date that is honest about being a published table
while the religious start stays a predicted window, prayer times that wear their
school on their sleeve, and Hebrew arithmetic done from first principles — every
one of these respects that these are exact traditions the civil calendar does not
override.

**What else you'll want.** The computus in full (why East and West drift, the
movable feasts that follow Easter) is in
[eras-and-rulers.md](eras-and-rulers.md). Every calendar's rules and reach —
including exactly where the Islamic and Chinese calendars stop rather than drift
— are in [calendars.md](calendars.md). Prayer conventions, the unequal hours of
the pre-clock world, and sunrise/sunset are in
[time-and-zones.md](time-and-zones.md).

---

## 5. Astronomy educators & enthusiasts

Lena teaches an evening astronomy class and runs a small observing club. Her
students ask for things a planetarium app answers with false confidence: the
exact moment of the spring equinox, tonight's moon phase, when the sun rises at
their latitude. She wants to give them the numbers *and* the error bars, because
the honesty is the lesson — an equinox instant known to a couple of minutes, a
"full moon tonight" that is really a day-wide window, a polar summer where the
sun genuinely never sets and any single "sunrise time" would be a lie.

Her most excited students follow the Mars rovers, and the question "what sol is
it for Perseverance right now?" is a real one with a real answer. And to end a
session she likes Carl Sagan's Cosmic Calendar, squeezing the whole 13.8-billion
year history into one year to show how late humans arrive. `chronologia` gives
her every one of these as an object with its uncertainty attached, so nothing on
her whiteboard pretends to a precision the physics does not have.

```python
from chronologia import (equinox, solar_term, next_phase, sun_events,
                         mission_sol, AstroDate, NoSunEvent, UNIVERSE_AGE_GYR)
from datetime import datetime, timedelta

# The March equinox as a SPAN — its width is the honest error bar:
eq = equinox(2027, "march")
print("equinox 2027:", eq.start.isoformat()[:19], "+/-", int(eq.width.total_seconds() / 2), "s")
# equinox 2027: 2027-03-20T20:23:54 +/- 60 s

# A Chinese solar term (the same solar geometry, named the East-Asian way):
print("start of spring (lichun):", solar_term(2027, "lichun").start.isoformat()[:16])

# "Full moon tonight" is really a day-wide window, and it says so:
full = next_phase(AstroDate(2027, 6, 1), "full")
print("next full moon:", full.start.isoformat()[:16], "width:", full.width, f"({full.basis})")
# next full moon: 2027-06-18T19:28 width: 1 day, 4:00:00 (predicted)

# Sunrise at your latitude — and polar honesty when there is no sunrise at all:
svalbard = sun_events(AstroDate(2027, 6, 21), 78.0, 15.0)
print("Svalbard midsummer sunrise:", type(svalbard.sunrise).__name__,
      getattr(svalbard.sunrise, "kind", ""))
# Svalbard midsummer sunrise: NoSunEvent polar_day
assert isinstance(svalbard.sunrise, NoSunEvent)     # the sun never sets — no lie invented

# "What sol is it for Perseverance?" — mission sol 200, as the Earth day it spanned:
sol = mission_sol("perseverance", 200)
print("Perseverance sol 200 was Earth date:", sol.start.isoformat()[:10])
# Perseverance sol 200 was Earth date: 2021-09-12

# Sagan's Cosmic Calendar: humans arrive in the final minutes of 31 December.
def cosmic_moment(years_ago):
    age = float(UNIVERSE_AGE_GYR) * 1e9
    return (datetime(2001, 1, 1) + timedelta(days=365) * (1 - years_ago / age)).strftime("%b %d %H:%M")

print("modern humans appear:", cosmic_moment(200_000))   # Dec 31 23:5x
```

Each answer carries its honesty: the equinox is a two-minute-wide span, the full
moon a `predicted` day-wide window, the polar sunrise a typed `NoSunEvent` rather
than a fabricated time, and the rover sol a real one-sol-wide stretch of Earth
time. That is exactly the habit of mind an astronomy class should leave with.

**What else you'll want.** Equinoxes, solstices, solar terms, moon phases with
their measured accuracy bounds, and sunrise/sunset with twilight are in
[time-and-zones.md](time-and-zones.md). Mars Sol Date, Coordinated Mars Time, the
Darian calendar, mission-sol counts, and the cosmology (redshift → lookback time,
the Hubble tension, the Cosmic Calendar) are in
[mars-and-beyond.md](mars-and-beyond.md).

---

## 6. Engineers building schedulers & data systems

Priya maintains a scheduling and log-analytics service, and her bugs all rhyme:
they are the ones where time is *nearly* uniform and the "nearly" bites. A daily
job set for 01:30 that fires twice one November night and skips a March one. A
"same wall-clock time tomorrow" that her code computes with `+ timedelta(days=1)`
and gets wrong by an hour twice a year. Log timestamps arriving from GPS-disciplined
hardware in one stream and UTC wall clocks in another, drifting apart by exactly
the leap seconds nobody accounted for. Fiscal reports that must roll up by ISO
week, not calendar month.

None of these are exotic. They are the everyday seams where civil time is not the
smooth number line the arithmetic assumes — and where a library that answers
"that time is ambiguous" or "that time never existed" as a **typed value** saves
her from a silent off-by-one in production. `chronologia` treats folds and gaps,
leap seconds, and week logic as first-class, so the edge case is a return value
she can branch on rather than a corruption she finds in a postmortem.

Recurring schedules are covered too — iCalendar `RRULE` expansion lives in
[the recurrence guide](recurrence.md) (`every("yearly", bymonth=9,
byday="1MO")` is Labor Day). Below, the focus is the part schedulers most
often get wrong: being *correct* at the DST and leap-second seams.

```python
from chronologia import (resolve_wall_clock, civil_add, utc_to_gps, gps_to_utc,
                         utc_tai_offset, CALENDARS, AstroDate, NeverExisted)
from zoneinfo import ZoneInfo

ny = ZoneInfo("America/New_York")

# 1. DST folds and gaps as TYPED answers, not silent bugs.
#    Fall-back night: 01:30 happens twice -> two instants.
fold = resolve_wall_clock(2024, 11, 3, 1, 30, ny)
print("ambiguous 01:30 ->", len(fold), "instants")   # a tuple of two
# ambiguous 01:30 -> 2 instants
#    Spring-forward morning: 02:30 never happens -> NeverExisted.
gap = resolve_wall_clock(2024, 3, 10, 2, 30, ny)
print("nonexistent 02:30 ->", type(gap).__name__)     # NeverExisted

# 2. "Same wall time tomorrow" across a fall-back edge is a 25-hour day.
#    civil_add keeps the wall clock; plain arithmetic silently would not.
start = AstroDate(2024, 11, 2, 1, 30, tzinfo=ny)
tomorrow = civil_add(start, days=1, zone=ny)
print("wall clock preserved:", tomorrow.strftime("%Y-%m-%d %H:%M"))
# wall clock preserved: 2024-11-03 01:30

# 3. Leap-second forensics: reconciling a GPS-stamped log against a UTC one.
#    GPS time does NOT tick leap seconds, so it runs ahead of UTC.
utc_event = AstroDate(2027, 1, 1, 0, 0, 0)
gps_event = utc_to_gps(utc_event)
print("UTC 00:00:00 == GPS", gps_event.strftime("%H:%M:%S"))   # 18 s ahead in 2027
print("current TAI-UTC offset:", utc_tai_offset(utc_event), "s")
assert gps_to_utc(gps_event) == utc_event                       # round-trips exactly

# 4. ISO-week / fiscal logic: which civil date is ISO week 1, Monday of 2027?
iso = CALENDARS["iso_week"]
print("ISO 2027-W01-1:", iso.date(2027, 1, 1).isoformat()[:10])
# ISO 2027-W01-1: 2027-01-04   (not Jan 1 — ISO weeks start the Monday of week 1)
```

The two DST cases return a two-tuple and a `NeverExisted` — values Priya's
scheduler can *test for* instead of a wrong instant it would ship. `civil_add`
keeps 01:30 as 01:30 across the 25-hour day. The GPS/UTC reconciliation is
leap-second exact and round-trips. And ISO week 1 lands on 4 January, not 1
January, because the week calendar knows its own rule.

**What else you'll want.** Timezone folds and gaps, `civil_add` versus raw
`timedelta`, the full leap-second / UTC / TAI / GPS story, and historical local
mean time are all in [time-and-zones.md](time-and-zones.md) and
[timezones.md](timezones.md). Reading any `zoneinfo` zone as a discontinuity
timeline (`zone_timeline`) is in [timelines.md](timelines.md). Span algebra —
`overlaps`, `intersect`, `union`, `gap`, `contains` — is the toolkit under all of
it (see [getting-started.md](getting-started.md)).

---

## 7. NLP & voice assistants — one backend among many

This is the section people expect a date library to lead with, and it comes last
on purpose. Marco builds a voice assistant. When a user says "remind me in June
2027", his natural-language parser has to turn those two words into something the
rest of the system can act on. The tempting move is to snap "June 2027" to a
single instant — midnight on the 1st — and every downstream bug flows from that
lie: the reminder lands on the wrong edge, "is X during June?" gets the wrong
answer, and nobody can see where the precision was invented.

The fix is not in the parser. It is in what the parser is *allowed to return*.
If the reckoning backend speaks in spans, the parser can hand back "the whole of
June 2027" — a stretch with an honest width — and the assistant can decide what
to do with a month-wide answer instead of pretending it got a timestamp.
`chronologia` is that backend. It is what lets a language layer stay honest, and
it is exactly the role it plays for
[ovos-date-parser](https://github.com/OpenVoiceOS/ovos-date-parser), which turns
spoken dates into these spans.

```python
from chronologia import DateSpan, AstroDate

# What a parser SHOULD return for "june 2027" — the whole month, as a span:
june = DateSpan(AstroDate(2027, 6, 1), AstroDate(2027, 7, 1))
print("width:", june.width, "| resolution:", june.resolution.name)
# width: 30 days, 0:00:00 | resolution: MONTH

# Now the assistant can answer honestly. "Is the 15th during 'june 2027'?"
assert june.contains(AstroDate(2027, 6, 15))

# And it can tell a vague utterance from a precise one by the span's WIDTH,
# which a single collapsed instant would have thrown away:
precise = DateSpan(AstroDate(2027, 6, 15, 9, 0), AstroDate(2027, 6, 15, 9, 1))
print("'june 2027' is", june.width // precise.width, "times vaguer than '9am on the 15th'")
```

The span is the whole contribution: "June 2027" stays a month wide, the assistant
can test containment honestly, and the difference between a vague utterance and a
precise one survives as the span's width instead of being flattened to a
timestamp. The language layer lives elsewhere — `chronologia` just makes sure it
never has to lie.

**What else you'll want.** The span type and its `basis` labels are in
[getting-started.md](getting-started.md); the parser that consumes them is
[ovos-date-parser](https://github.com/OpenVoiceOS/ovos-date-parser).

---

## The common thread

Seven audiences, one habit: **typed honesty**. A `DateSpan`'s width says how
precisely a thing is known; its `basis` says whether it was computed, tabulated,
reconstructed, or predicted; and where an answer genuinely does not exist the
library hands back a value that says so — `NeverExisted` for a deleted or
never-happened civil time, `NoSunEvent` for a polar day, an
`AmbiguousPeriodError` for a Bronze Age with no region.

The archivist reaches for that honesty to keep uncertain provenance uncertain.
The historian reaches for it to stop a calendar reform corrupting a lifespan. The
archaeologist to keep a radiocarbon age from masquerading as a calendar year. The
astronomer to teach error bars. The engineer to branch on a fold instead of
shipping a wrong instant. The voice assistant to answer a vague question vaguely.
Different reasons, same engine — one that would rather tell you what is knowable
than guess.
