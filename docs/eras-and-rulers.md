# Eras and rulers

The same year has been numbered many different ways. "2024" to you might be
"5784" to a Jewish calendar, "1445" to an Islamic one, "Reiwa 6" in Japan, or
"the consulship of so-and-so" to an ancient Roman. None of these are wrong —
they are just different ways of *counting* the same procession of years. This
page is about those counting systems: the fixed ones (called **eras**), the
ones tied to who was on the throne (**regnal years**), and the delightfully
strange way Romans named the days of a month.

## Eras: different ways of numbering the same years

An **era** is a rule for turning a year number into a real date. The one you
know best is the common era: year 1 is year 1, and you count up. `resolve_era`
applies any era's rule.

```python
from chronologia import resolve_era

print(resolve_era("common_era", 2024))
# 2024-01-01
```

Some eras count the same years but start their tally somewhere else. The
**Holocene** (or "Human Era") simply adds 10,000, so that the whole span of
human civilisation carries positive numbers — 2024 becomes the year 12024:

```python
print(resolve_era("holocene", 12024))
# 2024-01-01
```

The **Buddhist** era adds 543; the year 2568 BE is our 2025:

```python
print(resolve_era("buddhist", 2568))
# 2025-01-01
```

### Counting backwards: BC

"Before Christ" counts *backwards* toward the year 1. As the
[getting-started guide](getting-started.md) explains, astronomers give 1 BC the
number 0, so "44 BC" is stored as year −43 — but the library will hand it back
to you in ordinary BC counting:

```python
print(resolve_era("before_christ", 44).bc_year)
# 44
```

### Eras tied to a calendar

Some eras are really the year-numbering of another calendar. **Anno Mundi**
("year of the world") is the Hebrew calendar's own count, so the library
resolves it *exactly* through that calendar rather than by rough addition:

```python
print(resolve_era("anno_mundi", 5786))
# 2025-09-23
```

That is the real first day of Hebrew year 5786 — the same Rosh Hashanah the
[calendars guide](calendars.md) computed — because the era is backed by the
actual Hebrew calendar.

The two **Hijri** eras work the same way. The Islamic (lunar) **Hijri** era
counts the years of the Islamic calendar from the Hijra, so "1447 AH" is a real
lunar year, not 1447 read as a Gregorian year:

```python
print(resolve_era("hijri", 1447))
# 2025-06-27
```

The Iranian **Solar Hijri** (Jalali) era counts the same Hijra years on a solar
calendar whose year begins at the vernal-equinox Nowruz:

```python
print(resolve_era("solar_hijri", 1404))
# 2025-03-20
```

### When the year does not start on 1 January

The **Byzantine** Anno Mundi (a Creation era once used across the Orthodox
world) has a twist: its civil year begins on the **1st of September**, not 1
January. So the library reports not just a start date but the whole tiled span
from one September to the next:

```python
from chronologia import resolve_era_year_span

start, end = resolve_era_year_span("byzantine_am", 7535)
print(start.isoformat(), end.isoformat())
# 2026-09-01T00:00:00 2027-09-01T00:00:00
```

### Eras that count something other than years

A few eras count days or seconds instead. **Unix time** counts seconds from the
start of 1970 (this is how nearly every computer tells the time internally),
and **Julian Day** counts days from a starting point deep in 4713 BC (astronomers
use it for exactly the same reason this library does — an unbroken count):

```python
print(resolve_era("unix", 0))
# 1970-01-01 00:00:00+00:00
print(resolve_era("julian_day", 0).isoformat())
# -004713-11-24T00:00:00
```

### Before Present, and why 1950

Radiocarbon scientists count backwards from a fixed "present" — and that
present is frozen at the year **1950**. Why a year in the past? Because
above-ground nuclear testing in the 1950s flooded the atmosphere with extra
carbon-14, corrupting the natural signal, so 1950 was chosen as the last
"clean" reference point. It has stayed the convention ever since.

```python
print(resolve_era("before_present", 5000).isoformat())
# -003050-01-01T00:00:00
```

Five thousand years before 1950 is 3050 BC.

## Regnal years: counting by who was in charge

Before abstract eras, people numbered years by their ruler: "the fifth year of
the king". This library models a succession of reigns as a `RegnalSequence` and
gives you the Gregorian span of any regnal year.

### Japanese eras (nengō)

Japan still does this. Each emperor's reign is an era with its own name, and
years are counted within it. The current era is **Reiwa**, which began in 2019.
"Reiwa 1" runs only from the accession day, so its span is a partial year:

```python
from chronologia import REGNAL_SEQUENCES

reiwa1 = REGNAL_SEQUENCES["nengo"].year_span("reiwa", 1)
print(reiwa1[0].isoformat(), reiwa1[1].isoformat())
# 2019-05-01T00:00:00 2020-01-01T00:00:00

reiwa7 = REGNAL_SEQUENCES["nengo"].year_span("reiwa", 7)
print(reiwa7[0].isoformat(), reiwa7[1].isoformat())
# 2025-01-01T00:00:00 2026-01-01T00:00:00
```

The final year of a *closed* reign is clipped where the next ruler took over —
the long Meiji era's 45th year ended in July 1912 when the emperor died:

```python
meiji45 = REGNAL_SEQUENCES["nengo"].year_span("meiji", 45)
print(meiji45[0].isoformat(), meiji45[1].isoformat())
# 1912-01-01T00:00:00 1912-07-30T00:00:00
```

### Roman consuls

Romans named a year by the two consuls who held office that year. The library
carries a demonstrative set of well-attested consular pairs:

```python
caesar = REGNAL_SEQUENCES["consuls"].year_span("caesar_antonius", 1)
print(caesar[0].isoformat(), caesar[1].isoformat())
# -000043-01-01T00:00:00 -000042-01-01T00:00:00
```

That pair held office in 44 BC — the year of Caesar's assassination.

### Egyptian chronologies, told honestly

Ancient Egyptian dates come with a hard problem: scholars genuinely **do not
agree** on them. The absolute anchor depends on an astronomical observation
whose location is disputed, and the disagreement ripples down the whole
dynasty — as much as **25 years** apart. The honest response is not to pick a
winner. So this library ships *three* parallel chronologies — high, middle and
low — and lets you see all three:

```python
def accession_bc(variant):
    span = REGNAL_SEQUENCES[variant].year_span("ramesses_ii", 1)
    return span[0].bc_year

print(accession_bc("egyptian_high"))     # High chronology
# 1304
print(accession_bc("egyptian_middle"))   # Middle chronology
# 1290
print(accession_bc("egyptian_low"))      # Low chronology
# 1279
```

Ramesses II came to the throne in 1304, 1290, or 1279 BC depending on which
scholarly chronology you follow. The library refuses to choose for you — that
25-year spread *is* the honest answer.

## The Roman calendar: counting backwards from anchor days

Romans did not number the days of a month 1, 2, 3… Instead they counted
*backwards, inclusively*, from three fixed anchor days:

- the **Kalends** — the 1st of the month;
- the **Nones** — the 5th (or 7th in March, May, July, October);
- the **Ides** — the 13th (or 15th in those same four months).

The counting is the strange part. "Three days before the Kalends of April"
(*ante diem III Kalendas Apriles*) counts **inclusively**: the Kalends itself
is day 1, so you count back — 1 April is day 1, 31 March day 2, 30 March day 3.
The answer is 30 March:

```python
from chronologia import roman_to_julian

print(roman_to_julian(-43, 4, "kalends", 3))
# (-43, 3, 30)
```

That inclusive counting is why the arithmetic feels off by one to modern eyes —
you always include the anchor day in the count. A count of 1 is the anchor day
itself (the Ides of March is simply the Ides, count 1):

```python
print(roman_to_julian(-43, 3, "ides", 1))
# (-43, 3, 15)
```

And a count of 2 is the day before — the Romans had a special word for it,
*pridie*:

```python
print(roman_to_julian(-43, 4, "kalends", 2))
# (-43, 3, 31)
```

The result is a **Julian** calendar date (the calendar Rome actually used), in
the Roman date's own labels.

## Movable feasts: why Easter wanders

Most feast days sit on a fixed calendar square — Christmas is always 25
December. Easter is different: it *moves*, and a whole family of feasts moves
with it. The rule is old and deliberately simple: **Easter is the first Sunday
after the first full moon on or after the 21 March equinox.**

The subtle part is that "full moon" here does not mean *look at the sky*. The
Church long ago replaced the real Moon with a **codified arithmetic table** —
a repeating cycle of "ecclesiastical" full-moon dates keyed to the year's place
in a 19-year lunar cycle. So computing Easter (the *computus*) is exact integer
arithmetic on a calendar, not astronomy. Given a year, you get a definite date,
with no error bar:

```python
from chronologia import easter

print(easter(2024).isoformat())
# 2024-03-31T00:00:00
```

Easter can only ever land between **22 March and 25 April** — bounds the rule
guarantees. The earliest possible date last fell in 1818, the latest in 1943:

```python
print(easter(1818).isoformat()[:10], easter(1943).isoformat()[:10])
# 1818-03-22 1943-04-25
```

### Why East and West disagree

The Eastern Orthodox churches mostly still run the *same* rule, but on the
**Julian** calendar with the older Julian lunar table. Two things have drifted
apart — the calendars (now 13 days) and the lunar tables — so Orthodox Easter
usually falls one to five weeks later. `chronologia` gives you both, and lets
you choose how the Orthodox date is expressed:

```python
# Western Easter (Gregorian civil calendar):
print(easter(2024, "gregorian").isoformat()[:10])
# 2024-03-31

# Orthodox Easter, rendered on the civil calendar people actually use:
print(easter(2024, "julian_gregorian_date").isoformat()[:10])
# 2024-05-05

# Orthodox Easter carrying its OWN Julian-calendar label (22 April Julian) --
# a label, not a civil instant, so don't read its weekday as a civil Sunday:
print(easter(2024, "julian").isoformat()[:10])
# 2024-04-22
```

Occasionally the two coincide. 2025 is such a year — both fall on 20 April:

```python
print(easter(2025, "gregorian") == easter(2025, "julian_gregorian_date"))
# True
```

### The feasts that move with Easter

Once Easter is fixed, a chain of feasts follows by counting whole days from it:
Ash Wednesday 46 days before, Good Friday 2 days before, Ascension 39 days
after, Pentecost 49 days after. `movable_feast` returns any of them as a real
civil date:

```python
from chronologia import movable_feast

print(movable_feast("ash_wednesday", 2024).isoformat()[:10])
# 2024-02-14
print(movable_feast("good_friday", 2024).isoformat()[:10])
# 2024-03-29
print(movable_feast("pentecost", 2024).isoformat()[:10])
# 2024-05-19
```

The fixed solar feasts don't move at all, and Advent Sunday is counted back
from the fixed Christmas date (the first Sunday of the four before it):

```python
from chronologia import fixed_feast, advent_sunday

print(fixed_feast("christmas", 2024).isoformat()[:10])
# 2024-12-25
print(advent_sunday(2024).isoformat()[:10])
# 2024-12-01
```

## Reference

| tool | what it does |
|---|---|
| `resolve_era(era, value)` | a year (or day/second) count in an era → a concrete date |
| `resolve_era_year_span(era, value)` | the full start-to-next-start span of a calendar-backed era year |
| `astro_year_range(year, resolution)` | the decade/century/millennium containing any year |
| `resolve_bp(value, unit)` | a Before-Present expression → a `DateSpan` (see [deep-time.md](deep-time.md)) |
| `REGNAL_SEQUENCES[key].year_span(name, n)` | the Gregorian span of regnal year `n` of a ruler |
| `roman_to_julian(year, month, anchor, count)` | a Roman Kalends/Nones/Ides date → a Julian `(year, month, day)` |
| `easter(year, method)` | Easter Sunday as an `AstroDate` (`method`: `gregorian`, `julian`, `julian_gregorian_date`) |
| `movable_feast(name, year, method)` | a feast offset from Easter (Ash Wednesday, Pentecost, …) as a civil date |
| `fixed_feast(name, year)` | a fixed solar feast (Christmas, Epiphany, …) as an `AstroDate` |
| `advent_sunday(year)` | the first Sunday of Advent, counted back from Christmas |

Built-in eras in `ERAS`: `common_era`, `before_christ`, `before_present`,
`unix`, `julian_day`, `holocene`, `anno_mundi`, `french_republican`, `bahai`,
`buddhist`, `byzantine_am`, `olympiad`.

Built-in regnal sequences in `REGNAL_SEQUENCES`: `nengo` (Japanese eras),
`consuls` (Roman consular pairs), and `egyptian_high` / `egyptian_middle` /
`egyptian_low` (the three New Kingdom chronologies).

Roman anchors accepted by `roman_to_julian`: `"kalends"`, `"nones"`, `"ides"`.
The `count` is the inclusive backward ordinal (1 = the anchor day itself,
2 = *pridie*).

Movable feasts in `MOVABLE_FEAST_OFFSETS` (day offset from Easter):
`ash_wednesday` (−46), `palm_sunday` (−7), `good_friday` (−2), `ascension`
(+39), `pentecost` (+49), `trinity_sunday` (+56), `corpus_christi` (+60).
Fixed feasts in `FIXED_FEASTS`: `christmas`, `epiphany`, `assumption`,
`all_saints`.
