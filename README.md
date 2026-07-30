# chronologia

**A Python library that reads dates written by humans and answers
questions about them — any date, in any calendar, from the age of the
dinosaurs to next Tuesday.**

It does two things that usually need two libraries: it *understands* a
date the way a person wrote it ("the 15th of Ramadan 1446", "next
winter", "66 million years ago") and it *computes* across every system
of reckoning humans have used. One call turns a phrase into the exact
stretch of time it refers to:

```python
from chronologia import extract_timespan
from datetime import datetime

span, _ = extract_timespan("the 15th of Ramadan 1446", "en",
                           datetime(2024, 1, 1))
print(span.start_datetime.date())   # 2025-03-15
```

That is the whole point of a *span*: a phrase names a stretch of time,
not an instant.

When a string contains no date at all, `extract_timespan` returns `None`
(rather than raising), so guard before unpacking on untrusted input:

```python
result = extract_timespan("no date here", "en", datetime(2024, 1, 1))
if result is not None:
    span, _ = result
```

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

Python 3.10+. The calendrical core is pure standard library; the
natural-language layer adds two small helpers — **ovos-number-parser**
(spelled numbers → digits) and **ovos-spec-tools** (loads each language's
vocabulary files).

**Status.** chronologia is in **alpha**: the public API surface named in
`chronologia.__all__` is what you build against, and it is covered by an
extensive test suite, but signatures may still change ahead of a 1.0 that
freezes them. Pin a version if you need stability across upgrades.

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

Under the hood, one trick powers everything: every day that has ever
existed gets a plain number — its **Julian Day Number** — so *any* of the
seventeen built-in calendars can talk to any other by meeting at the
number in the middle. See [docs/getting-started.md](docs/getting-started.md)
for the three ideas the whole library is built from.

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

## Stories the library can tell

Each of these is a full worked guide in [`docs/`](docs/) — here is just
the hook and where to read it.

- **The ten days that never happened.** In October 1582 Pope Gregory
  deleted ten days; Britain lost eleven in 1752, Russia thirteen in 1918
  (which is why the "October" Revolution fell in November), and Sweden
  needed a one-off **February 30th** in 1712. Ask for a deleted day and
  you get a typed `NeverExisted`, not a crash → [docs/timelines.md](docs/timelines.md).
- **Clocks that lie twice a year.** When clocks "fall back", 1:30 AM
  happens twice; when they "spring forward", 2:30 AM never happens at
  all. Resolve a wall-clock time and get the honest answer — both
  instants, or "that time didn't exist" → [docs/timezones.md](docs/timezones.md).
- **The sun, the sundial, and the pre-clock day.** Real sunrise, sunset,
  solar noon and the three twilights (NOAA algorithm, ~1 minute), local
  *mean* time from before timezones, the unequal hours the Roman world
  lived by, Islamic prayer times as named conventions, moon phases and
  the astronomical seasons — plus leap seconds, the reconciliation of
  atomic and astronomical time → [docs/sun-moon-and-seasons.md](docs/sun-moon-and-seasons.md).
- **Deep time, honestly.** "66 million years ago" and "66.043 million"
  are different *claims*, and the span's width says which you made;
  radiocarbon ages calibrate through the published curve →
  [docs/deep-time.md](docs/deep-time.md).
- **Emperors, popes, and consuls.** "Reiwa 7", "the consulship of
  Lentulus and Marcellus", "Year 5 of Ramesses II" in three competing
  scholarly chronologies — plus the full Roman Kalends/Nones/Ides
  grammar in ten living languages → [docs/eras-and-rulers.md](docs/eras-and-rulers.md).
- **Beyond Earth.** Mars Sol Date, the Darian calendar, rover
  mission-sols, a span-valued Big Bang epoch and Sagan's Cosmic Calendar
  → [docs/mars-and-beyond.md](docs/mars-and-beyond.md).

Even a plain word like **"morning"** is a span — and a *convention* a
culture agrees on, not a fact about the sun. English splits afternoon
from evening at 18:00; Spanish runs one *tarde* through to 20:00:

```python
from datetime import date
from chronologia import daypart_span

tuesday = date(2027, 6, 8)
print(daypart_span(tuesday, "afternoon").end.isoformat())            # 2027-06-08T18:00:00
print(daypart_span(tuesday, "tarde", region="es").end.isoformat())  # 2027-06-08T20:00:00
```

## Command line

Installing the package puts a `chronologia` command on your path (or run it
as `python -m chronologia`). Each subcommand prints one friendly line:

```bash
chronologia convert 2024-06-01 --to hebrew        # gregorian 2024-06-01 = hebrew 5784-02-24
chronologia extract "last summer"                 # -> [..., ...) (year)
chronologia holidays US 2024                       # one date + name per line
chronologia easter 2024                            # Easter 2024 (gregorian): 2024-03-31
chronologia when 1984-06?                          # -> [1984-06-01..., 1984-07-01...) [?]
```

The same entry point is callable in-process — handy for scripts and tests —
by handing `main` an argument list (it prints to stdout and returns an exit
code):

```python
from chronologia.__main__ import main

main(["easter", "2024"])                # prints: Easter 2024 (gregorian): 2024-03-31
main(["convert", "2024-06-01", "--to", "coptic"])
main(["when", "1984-06?"])
```

BC / negative years need argparse's `--` separator so the leading `-` is not
read as a flag: `chronologia convert --from julian --to gregorian -- -0043-03-15`.

## Reference

Full guides for everything above live in [`docs/`](docs/), mapped with a
suggested reading order in [**docs/index.md**](docs/index.md). Prefer to learn
by running code? The [`examples/`](examples/) directory is eight self-contained,
self-checking scripts (`python examples/01_extract_basics.py`).

| | |
|---|---|
| **Who is this for?** | [**docs/use-cases.md**](docs/use-cases.md) — worked programs for archivists, historians, archaeologists, faith communities, astronomers, engineers, and voice assistants — start here |
| Reading human dates | [**docs/extraction.md**](docs/extraction.md) — `extract_timespan` turns a phrase into a span; how the per-language vocabulary works and how to add a language |
| 17 calendars | Gregorian, Julian, Hebrew, Islamic (arithmetic + Saudi Umm al-Qura table), Solar Hijri, Chinese (1901–2099), Coptic, Ethiopian, Armenian, ancient Egyptian, Maya Long Count, French Republican, Bahá'í, ISO week, and more — [docs/calendars.md](docs/calendars.md) |
| Timelines | 13 jurisdictions' calendar reforms and dateline hops — Rome, Britain, Sweden, Russia, Greece, Japan, plus the days Samoa, the Philippines and Alaska deleted or re-lived at the International Date Line — [docs/timelines.md](docs/timelines.md) |
| Named periods | the full geological chart (180 entries) plus regional archaeological ages — a British "Late Bronze Age" is not a Mesopotamian one — [docs/deep-time.md](docs/deep-time.md) |
| Eras & counts | BC/CE, Anno Mundi, Hijri years, Holocene, Byzantine, unix time, Julian Day, Before Present; regnal years (Japanese nengō, Roman consuls, Egyptian chronologies) — [docs/eras-and-rulers.md](docs/eras-and-rulers.md) |
| Recurrence | [RFC 5545 RRULE](docs/recurrence.md) — "every third Tuesday", Labor Day, Friday the 13th — parsed and expanded as pure JDN arithmetic into day-wide `DateSpan`s |
| Civil holidays | [public/regional/municipal holidays](docs/civil-holidays.md) as computed rules with observed-shift policies — Portugal at municipal depth (~300 concelhos), US federal, Saudi Arabia |
| Time, sun & sky | [sun, moon & seasons](docs/sun-moon-and-seasons.md) — sunrise/sunset/twilights, unequal hours, prayer times, moon phases, solstices/equinoxes, local mean time, leap seconds, and the French Revolution's 10-hour clock |
| Timezones | [timezones](docs/timezones.md) — reading any `zoneinfo` zone as a timeline with honest fall-back/spring-forward handling |
| Beyond Earth | [Mars and beyond](docs/mars-and-beyond.md) — Mars Sol Date, Coordinated Mars Time, the Darian calendar, and cosmology (a span-valued Big Bang epoch, the Hubble tension, Sagan's Cosmic Calendar) |
| How does it compare? | [**docs/benchmarks.md**](docs/benchmarks.md) — a standing differential benchmark against `dateparser` and `dateutil` on the repo's own hand-derived corpora |

Every algorithm and every number in the data files is transcribed from
a cited published source — citations sit in the module docstrings and
data-file headers. Where sources disagree, both versions ship under
different names. Where sources are silent, the library says so instead
of guessing.

**How this library was built**: see [docs/transparency.md](docs/transparency.md) — an honest account, failures included.

## Related projects

chronologia is part of the OpenVoiceOS family of language-processing libraries.
Where this one *reads and reckons* dates, its neighbours handle the pieces
around them:

- **[ovos-date-parser](https://github.com/OpenVoiceOS/ovos-date-parser)** —
  the voice-facing layer. It builds on chronologia and adds the glue an
  assistant needs: *saying* a date back out loud, session handling, and the
  legacy per-language helpers. If you need to speak a date rather than read
  one, start there.
- **[ovos-number-parser](https://github.com/OpenVoiceOS/ovos-number-parser)** —
  the same idea for numbers: spelled-out numbers, ordinals and fractions to
  digits and back, across many languages. chronologia uses it to read spelled
  numbers inside a date phrase.
- **[ovos-spec-tools](https://github.com/OpenVoiceOS/ovos-spec-tools)** — the
  reference implementation of the OVOS formal specifications (template
  expander, locale loader, dialog renderer, language matcher, linter).
  chronologia loads its per-language vocabulary files through it.

## License

Apache-2.0 © TigreGotico
