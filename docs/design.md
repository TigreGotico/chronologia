# Design: the developer's tour

This is the one page written for someone who wants to build *on* the library
rather than just use it. It explains how the pieces fit, why the boundaries are
drawn where they are, and — most importantly — what the library will never do
and why. Even here, the rule is plain words first, precision second.

## The one architectural idea: everything meets at the JDN

The whole system is a hub-and-spoke. The hub is the **Julian Day Number** — a
single integer naming each day on an infinite line. Every calendar, timeline,
era and regnal sequence is a *spoke*: it knows only how to convert its own
labels to a JDN and back. Nothing converts directly to anything else.

```
   Hebrew ──┐                 ┌── Islamic
   Coptic ──┤                 ├── Chinese
   Mayan  ──┼──►  JDN (int)  ◄─┼── Julian
   Eras   ──┤    the one hub   ├── Timelines
   Regnal ──┘                 └── Gregorian
```

This buys three things. Conversions **compose** for free (Hebrew → JDN →
Chinese needs no Hebrew↔Chinese code). Duration math is **always safe**, because
it happens on the integer line where there are no gaps or reforms. And each
spoke is **independently testable** against its own cited source, since it only
has to get its own JDN round-trip right.

## The type system

Four value types carry all temporal information. All are frozen (immutable) and
compare by value.

### AstroDate — an unbounded point

`AstroDate` is a `datetime` whose year can be any integer. It cannot subclass
`datetime` (the year bounds are exactly what it escapes), so it duck-types the
whole `datetime` public API instead — `weekday`, `isoformat`, `replace`,
`timedelta` arithmetic, and comparisons that interoperate with real `date` and
`datetime` values. It uses **astronomical year numbering** (1 BC is year 0) and
is proleptic Gregorian for its own field math. It carries *no* uncertainty tag:
a point is a point. Width lives in the next type.

### DateSpan — a half-open stretch, and the error bar

`DateSpan` is a half-open interval `[start, end)` of two `AstroDate` values, and
it is the primitive result of the whole system. The insight is that **width is
the uncertainty**. "3 pm" is a one-minute span; "June" is a month-wide span;
"the Jurassic" is a 56-million-year span. Points, imprecise references,
durations, seasons and eras all unify under this one type, and a derived
`DateTimeResolution` is *computed* from the width, never separately asserted —
which removes an entire class of tag-vs-value bugs.

### basis — a small lattice of trust

Alongside width, every span carries a **basis**: how its endpoints were
established. There are four values, ordered by increasing doubt:

```
exact  <  tabulated  <  { reconstructed , predicted }
```

`exact` is a firm arithmetic rule; `tabulated` is a published table that may
differ from observation; `reconstructed` is modelled from past evidence;
`predicted` is a forward model. The top two are *peers* — one faces the past,
one the future, and neither is more certain than the other. Combining bases
takes the worst (least certain) of the inputs:

```python
from chronologia import combine_basis

print(combine_basis("exact", "tabulated"))
# tabulated
print(combine_basis("reconstructed", "predicted"))
# reconstructed
```

`exact` is the identity element, so `combine_basis("exact", x)` is just `x`.
When the two differing peers meet, the result is a stable canonical
representative (`reconstructed`) — documented, not meaningful.

### WideDuration — a width that overflows timedelta

`timedelta` caps at about ±2.74 million years, but a geological span is tens of
millions. So `DateSpan.width` returns a plain `timedelta` whenever the interval
fits — byte-identical to `end - start` — and a `WideDuration` only when it would
otherwise overflow:

```python
from datetime import timedelta
from chronologia import lookup

width = lookup("jurassic").span.width
print(type(width).__name__, width.years)
# WideDuration 58500000
print(width > timedelta(days=999))
# True
```

`WideDuration` is orderable and equality-comparable against both other
`WideDuration` values and ordinary `timedelta`, so a geological width and a
human-scale width compare cleanly.

## The scope boundary: exact, tabulated, or out

The registry draws a deliberate three-way line, and understanding it explains
almost every "why isn't X included?" question.

- **Arithmetic → shipped as `exact`.** If a calendar reduces to a deterministic
  rule (the Hebrew molad, the Coptic leap cycle), it is computed exactly in any
  century, forward or backward.
- **Observational-but-published → shipped as `tabulated`, bounded.** If a
  calendar's month-starts require observation (crescent sighting, new moon plus
  solar term, an equinox) but an authority *publishes* an official table, that
  table is shipped. It is exact inside its range and raises a
  `CalendarRangeError` outside it — often naming a `fallback` rule-based
  calendar to degrade to.

```python
from chronologia import CALENDARS, CalendarRangeError

try:
    CALENDARS["umm_al_qura"].to_jdn(1200, 1, 1)   # before the table starts
except CalendarRangeError as error:
    print(error.fallback)
    # islamic_civil
```

- **Neither rule nor citable table → left out, on purpose.** The Burmese and
  Javanese lunisolar calendars are documented as *considered and excluded*: no
  single downloaded canonical source pins both their rule and datable gold
  values, so shipping them would mean inventing the gap. Inventing is worse than
  omitting.

The guiding rule for every entry: an algorithm or table is transcribed from a
downloaded, cited canonical source — never from another conversion library.
Where sources disagree, both versions ship under different keys (the arithmetic
`bahai` and the equinox `badi_2015`). Where sources are silent, the library
says so.

## The timeline model

Calendars are pure proleptic bijections — they never jump. Civil *label
mappings* jump, because popes and parliaments decreed it. A `Timeline` keeps
these separate: it is an ordered list of `TimelineSegment`s (which calendar was
in force over each stretch of JDN) plus a tuple of one-time `Discontinuity`
events, each of a `DiscontinuityKind`: `SKIP`, `REPEAT`, `INSERT`, `RELABEL`
(see [timelines.md](timelines.md)). A non-existent label returns a typed
`NeverExisted` rather than raising, and the default timeline
(`proleptic(key)`) has zero discontinuities, so opting in is explicit. The
boundary rule mirrors the scope boundary above: predictable from the calendar's
own law → it belongs to the calendar; it took a human decree → it belongs to a
timeline.

## The data-file format: facts only

Every shipped table is a plain text file with a `#`-comment header carrying its
provenance and metadata, then whitespace- or tab-separated data rows. The
header is machine-read for a handful of `# name: value` keys and human-read for
everything else. A calendar table looks like this:

```
# tabulated-calendar v1
# key: umm_al_qura
# basis: tabulated
# fallback: islamic_civil
# month_count: 12
# source: official KACST Umm al-Qura table as published by R. H. van Gent …
# retrieved: 2026-07-21
# coverage: AH 1356-01 .. AH 1500-12 (last row 1501 1 is the terminal sentinel)
# columns: year month leap jdn_start
1356 1 0 2428607
1356 2 0 2428636
1356 3 0 2428665
```

The design principle is that the data file holds **only transcribed facts and
their citation** — no logic, no interpolation. The last row of a calendar table
is a *terminal sentinel* (the start of the month after the last real one) so the
final month's length is known without extrapolation. The leap-second and
geological-chart files follow the same shape: a cited header, then rows.

## The representability story: what can never be supported

This is the most important design decision in the library, and it is a decision
about *honesty*. Three kinds of thing are structurally unsupportable, and the
library refuses to fake any of them.

1. **The computed sky.** A calendar whose future months depend on an
   astronomical computation the library does not carry (the Chinese calendar
   beyond 2099) stops at its table rather than drift. There is a documented
   opt-in — `register_event_provider` — for an application that *has* an
   ephemeris, but the core ships none.

2. **The observed sky.** A month that begins only when a human *sees* the new
   crescent cannot be known in advance. The honest answer for a future
   religious Islamic month is a two-day span labelled `predicted`, never a fake
   exact date. (The published Saudi civil table is included precisely because it
   *is* published — as a table, as far as it goes.)

3. **Human decisions that were never rules.** Before Julius Caesar, Roman
   priests inserted days for political reasons. No software can recover a
   decision that was never a rule. Such reconstructions are supported *as*
   reconstructions, wearing their basis openly, never as computed fact.

One sentence covers all three, and it is the invariant the whole library
upholds: **a span's width and basis always tell the truth about what is
knowable.** Everything else — the JDN hub, the type system, the scope
boundaries — exists to keep that promise.

## Reference: the six registries

| registry | holds | keyed by |
|---|---|---|
| `CALENDARS` | arithmetic and tabulated calendars | short calendar name |
| `ERAS` | year-numbering conventions | era name |
| `REGNAL_SEQUENCES` | successions of reigns | sequence name |
| `DAY_CYCLES` | the week and its cousins | cycle name |
| `DAY_SUBDIVISIONS` | alternative divisions of the day | subdivision name |
| `TIMELINES` | jurisdictions' calendar reforms | jurisdiction key |

Named periods live in a seventh registry, `PERIODS` (see
[deep-time.md](deep-time.md)). Every entry in every registry converts through
the same JDN hub, and every shipped number traces to a cited source.
