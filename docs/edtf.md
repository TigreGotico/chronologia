# EDTF: how archives write dates they're not sure about

When a museum catalogues a photograph as "probably the 1890s", or a manuscript
as "June 1637, approximately", it cannot write a plain calendar date — it does
not *have* one. It has a **stretch of time**, and some notion of how confident
it is. The Library of Congress standardised exactly this: the **Extended
Date/Time Format** (EDTF), the "uncertain and imprecise dates" profile of
ISO 8601-2. It is the lingua franca of archives, libraries and digital
collections for dates nobody is fully sure of.

That is precisely what a `DateSpan` already is in this library — a half-open
stretch of time whose *width is the uncertainty*. So EDTF maps onto the engine
almost one-to-one. `parse_edtf` turns an EDTF string into a span; `format_edtf`
turns a span back into the tightest EDTF string.

> Reference: Library of Congress, *Extended Date/Time Format (EDTF)
> Specification*, <https://www.loc.gov/standards/datetime/> (spec dated
> 2019-02-04). Every example below is drawn from that document.

## The everyday cases (Level 0)

A full date is a one-day span. A less precise string is a wider span — "1985"
is the whole year, "1985-04" the whole month. The width *is* the precision.

```python
from chronologia import parse_edtf

day = parse_edtf("1985-04-12").span
print(day.start, day.end)         # a single day
# 1985-04-12T00:00:00 1985-04-13T00:00:00

month = parse_edtf("1985-04").span
print(month.start, month.end)     # the whole of April
# 1985-04-01T00:00:00 1985-05-01T00:00:00

year = parse_edtf("1985").span
print(year.resolution)            # the engine derives the precision
# DateTimeResolution.YEAR
```

An interval is written `start/end`, and its span runs from the start of the
first to the *end* of the last:

```python
span = parse_edtf("2004-06/2006-08").span
print(span.start, span.end)       # June 2004 through the end of August 2006
# 2004-06-01T00:00:00 2006-09-01T00:00:00
```

Times work too, with an optional UTC or offset suffix, and come back as a
one-second span carrying the zone:

```python
t = parse_edtf("1985-04-12T23:20:30-04").span.start
print(t.utcoffset())
# -1 day, 20:00:00
```

## Saying you're not sure (Level 1 qualifiers)

EDTF has three qualifier characters: `?` *uncertain* ("possibly, not
definitely"), `~` *approximate* ("roughly"), and `%` for both. These speak
about the **claim**, not about how the dates were computed, so parsing keeps
them as flags on the returned `EdtfDate` and marks the span's `basis` as
`reconstructed`:

```python
ed = parse_edtf("1984?")
print(ed.uncertain, ed.approximate)
# True False
print(ed.span.basis)
# reconstructed
```

Compare that with *imprecision*, which is carried by the width alone — a decade
span has perfectly exact endpoints, so its basis stays `exact`. Uncertainty
about the claim and imprecision about the extent are two different things, and
the library keeps them separate.

## The unsure digits (Level 1 `X`)

The masterstroke of EDTF: put an `X` where a digit is unknown. `156X` is "the
1560s" — a decade. `20XX` is a whole century. An unknown month (`2004-XX`) is
simply the whole year.

```python
decade = parse_edtf("156X").span
print(decade.start.year, decade.end.year)
# 1560 1570
print(decade.basis)               # exact endpoints; the width is the doubt
# exact
```

## Seasons and quarters

`2001-21` is Spring 2001. EDTF deliberately leaves the season boundaries
undefined, so this library adopts the **Northern-Hemisphere meteorological**
seasons — three-month blocks starting in March, June, September and December.
Level 2 adds quarters and semesters (`2001-34` is the second quarter).

```python
spring = parse_edtf("2001-21").span
print(spring.start, spring.end)   # March, April, May
# 2001-03-01T00:00:00 2001-06-01T00:00:00
```

## Open-ended and unknown ends

An ongoing or unknown interval end is written `..` (open) or left empty
(unknown). A span cannot bound infinity, so the result keeps the *bounded*
side and flags the open end:

```python
ed = parse_edtf("1985-04-12/..")
print(ed.open_end, ed.span.start)
# True 1985-04-12T00:00:00
```

## The deep-time flagship: `Y170000002`

Here is where this library earns its keep. `datetime` cannot represent a year
outside 1..9999, but archives and scientists genuinely need larger numbers. For
years beyond four digits EDTF uses a `Y` prefix — and because this engine's
point type (`AstroDate`) has an **unbounded** year, that Just Works:

```python
ed = parse_edtf("Y170000002")     # the year one hundred seventy million...
print(ed.span.start.year)
# 170000002
print(ed.span.start.in_datetime_range)   # far outside datetime's window
# False
```

Level 2 goes further still. An *exponential* year `Y-17E7` means
-17 x 10^7, and *significant digits* express estimation — `1950S2` is "some
year in the 1900s, estimated to be 1950":

```python
print(parse_edtf("Y-17E7").span.start.year)
# -170000000
est = parse_edtf("1950S2").span
print(est.start.year, est.end.year)
# 1900 2000
```

## Writing EDTF back out

`format_edtf` emits the tightest EDTF string a span allows: a year-wide span
becomes `1985`, a decade becomes `156X`, an arbitrary interval becomes
`start/end`.

```python
from chronologia import format_edtf, AstroDate, DateSpan

print(format_edtf(DateSpan(AstroDate(1560, 1, 1), AstroDate(1570, 1, 1))))
# 156X
print(format_edtf(parse_edtf("2001-21").span))   # a season -> its interval
# 2001-03/2001-05
```

Formatting is honest about being lossy: it emits what the *span* knows, so an
exponential year returns as plain `Y170000000` and a per-component qualifier
scope collapses to one trailing character. What is guaranteed is a round trip on
the **span** — parse, format, parse again, and you land on the same stretch of
time:

```python
original = parse_edtf("Y170000002")
assert parse_edtf(format_edtf(original)).span == original.span
```

## What raises, and why

Malformed input never fails silently — it raises `EdtfParseError` (a
`ValueError`):

```python
from chronologia import EdtfParseError

for junk in ("", "1985-13", "1985-4", "not-a-date"):
    try:
        parse_edtf(junk)
    except EdtfParseError as exc:
        print("rejected:", junk)
# rejected: 
# rejected: 1985-13
# rejected: 1985-4
# rejected: not-a-date
```

A few *valid* EDTF strings denote a genuinely non-contiguous set of instants
that no single span can hold — `156X-12-25` means "December 25th of some year in
the 1560s" (ten separate days), and the set forms `[1667,1668]` / `{1960,1961}`
select or collect scattered dates. These raise `NotImplementedError` rather than
pretend a single span could represent them.

## Coverage at a glance

| Level | Feature | Support |
|-------|---------|---------|
| 0 | date (day / month / year precision) | full |
| 0 | date + time, `Z` / `±hh` / `±hh:mm` shift | full |
| 0 | interval `start/end` | full |
| 1 | qualifiers `?` `~` `%` (date-level) | full |
| 1 | qualifiers per-component (L2 placement) | recognised, collapsed to date-level flags |
| 1 | unspecified `X` digits (year / month / day) | full for contiguous (trailing) cases |
| 1 | negative years, `Y`-prefix big years | full (unbounded via `AstroDate`) |
| 1 | seasons 21-24 | full (NH meteorological convention) |
| 1 | open / unknown interval ends | full (bounded side + flag) |
| 2 | exponential years `Y…E…` | full |
| 2 | significant digits `…S…` | full |
| 2 | Northern/Southern seasons 25-32, quarters/quadrimesters/semesters 33-41 | full |
| 2 | unspecified digit anywhere (contiguous) | full |
| 2 | non-contiguous `X` (e.g. `1XXX-12`), set `[…]` `{…}` | raises `NotImplementedError` |
```
