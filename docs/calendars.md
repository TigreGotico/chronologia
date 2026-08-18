# Calendars

A calendar is just an agreement about how to name days. Humanity has invented
dozens of these agreements, and this library speaks eighteen of them. This
page introduces each one in plain language, shows you how to translate dates
in and out of it, and — most importantly — tells you honestly how far each one
can be trusted.

## How a conversion works

Every calendar here meets every other calendar at the number line described in
[getting-started.md](getting-started.md): each day has a **Julian Day Number**
(JDN), and every calendar knows how to cross that number line. You never touch
the number yourself, though — a calendar takes a date and hands back a real
date object:

```python
from chronologia import CALENDARS

hebrew = CALENDARS["hebrew"]
print(hebrew.date(5786, 7, 1))            # a Hebrew date -> an AstroDate
# 2025-09-23T00:00:00
print(hebrew.from_astro(hebrew.date(5786, 7, 1)))   # and back again
# hebrew 5786-07-01
```

`date(year, month, day)` gives the everyday-calendar instant (an `AstroDate`)
of that calendar's date; `from_astro` takes any `AstroDate`, `date` or
`datetime` and tells you what *this* calendar calls it, as a `CalendarDate`
(its `str` is deliberately numeric — `hebrew 5786-07-01` — because naming the
months is a language job, not a calendar job). That is the pattern for the
whole page: objects in, objects out. (The Julian Day Number still does the
work underneath; see [design.md](design.md) if you want to watch it.)

## Two families: rule-based and table-based

The calendars split into two kinds, and the difference matters for how much
you can trust them.

**Arithmetic (rule-based) calendars** are defined by a formula. "Every fourth
year is a leap year" is a rule; a computer can follow it forward or backward
forever with no lookups. These calendars are *exact* as far as their own rules
go, in any century you like.

**Table-based calendars** cannot be reduced to a formula, because their months
begin on something you have to *observe* — the sighting of a new moon, an
astronomical new moon plus a solar term, an equinox. Authorities publish these
as official **tables**, and this library ships a copy of the table. A
table-based calendar is exact *inside* the years the table covers, and simply
stops at the edges rather than guessing.

Every registry calendar lives in one dictionary, `CALENDARS`, keyed by a short
name.

---

## Arithmetic calendars

### Julian

The calendar Julius Caesar introduced in 46 BC and most of Europe used until
the 1580s. It has a leap year every four years with no exceptions, which is
why it slowly drifted against the seasons — the very drift the Gregorian
reform later corrected.

```python
from chronologia import CALENDARS

julian = CALENDARS["julian"]
print(julian.date(-43, 3, 15))   # the Ides of March, 44 BC
# -000043-03-13T00:00:00
```

The Roman "15 March" lands on the 13th of *our* modern calendar, projected
backwards — the two calendars had drifted two days apart by then. **Caveat:**
this is the *proleptic* Julian calendar (the rules run cleanly in both
directions); it does not model the irregular leap years Roman priests actually
kept before Caesar's reform settled down.
Source: Fliegel & Van Flandern (1968), *Communications of the ACM* 11(10):657.

### Revised Julian

A twentieth-century refinement adopted by several Orthodox churches in 1923.
It keeps the Julian calendar's shape but uses a cleverer leap-century rule, so
it tracks the seasons even more closely than the Gregorian calendar does.

```python
print(CALENDARS["revised_julian"].date(2800, 3, 1))
# 2800-02-29T00:00:00
```

The Revised Julian and Gregorian calendars agree from 1600 to 2800 and first
disagree on 1 March 2800: the Gregorian calendar makes 2800 a leap year, the
Revised Julian one does not, so its "1 March 2800" is our 29 February 2800.
Source: the Milanković 900-year rule (a century year is leap only when
`year % 900` is 200 or 600).

### Hebrew

The Jewish calendar: a lunisolar calendar whose months follow the moon while
occasional leap *months* keep it in step with the sun. Remarkably, its rules
are fully arithmetic, so dates far outside any table can be computed exactly.

```python
from chronologia import AstroDate

hebrew = CALENDARS["hebrew"]
print(hebrew.date(5786, 7, 1))   # 1 Tishri = Rosh Hashanah
# 2025-09-23T00:00:00
print(hebrew.from_astro(AstroDate(2025, 9, 23)))
# hebrew 5786-07-01
```

**A numbering note:** month 7 is Tishri, the civil new year. This library uses
the *ecclesiastical* numbering (Nisan = 1 … Tishri = 7) because the source
arithmetic is built on it. Source: Dershowitz & Reingold, *Calendrical
Calculations*, SP&E 20(9):899–928 (1990).

### Islamic (tabular / civil)

The arithmetic form of the Islamic (Hijri) calendar — twelve lunar months in a
fixed 30-year leap cycle. It powers most everyday date software.

```python
islamic = CALENDARS["islamic_civil"]
print(islamic.date(1446, 9, 15))   # 15 Ramadan 1446
# 2025-03-15T00:00:00
```

**Caveat:** the *religious* Islamic month begins when witnesses actually see
the new crescent moon, which no formula can predict. The tabular calendar can
therefore differ from the observed one by **±1 day**. For the official Saudi
civil table, see `umm_al_qura` below. Source: Dershowitz & Reingold (1990).

### Solar Hijri (arithmetic)

The Iranian and Afghan solar calendar, whose year begins at the spring
equinox — the festival of Nowruz. This entry is the arithmetic 33-year-cycle
approximation of it.

```python
print(CALENDARS["solar_hijri_arithmetic"].date(1403, 1, 1))
# 2024-03-20T00:00:00
```

**Caveat — validity window:** the *legal* Iranian calendar sets Nowruz by the
observed equinox, which is not a fixed rule. This arithmetic version tracks it
across the modern era but is known to drift by ±1 day in scattered years; near
a critical year, consult an astronomical source. Source: the 8-leap-years-per-33
tabulation associated with Ahmad Birashk, verified against documented Nowruz
dates for AP 1370–1408.

### Coptic

The calendar of the Coptic Orthodox Church of Egypt: twelve 30-day months plus
a short thirteenth month of 5 or 6 days. It descends directly from the ancient
Egyptian year, fixed to a leap rule so its new year stays put.

```python
print(CALENDARS["coptic"].date(1741, 1, 1))   # 1 Thoout
# 2024-09-11T00:00:00
```

Source: Dershowitz & Reingold, *Calendrical Calculations*, chapter 4; epoch
1 Thoout AM 1 = 29 August 284 (Julian).

### Ethiopian

The calendar of Ethiopia and the Ethiopian Orthodox Church. It shares the
Coptic calendar's exact structure but numbers its years 276 higher, which is
why Ethiopia's millennium celebration fell in our 2007.

```python
print(CALENDARS["ethiopian"].date(2017, 1, 1))   # 1 Maskaram
# 2024-09-11T00:00:00
```

Notice this is the *same* Gregorian day as Coptic 1741 above — the two
calendars are the same clock with different year numbers. Source: Dershowitz &
Reingold; epoch 1 Maskaram EE 1 = 29 August AD 8 (Julian).

### Berber (Amazigh)

The Amazigh agricultural calendar in modern use across the Berber-speaking
world (Algeria, Morocco, and the Kabyle and Riffian diaspora): structurally
the Julian calendar — same twelve months and leap rule — with the months
named in Berber and the year counted from a different era. 1 Yennayer
(Berber new year) always falls on 1 January Julian, which is 14 January
Gregorian throughout the 1900–2099 window.

```python
print(CALENDARS["berber"].date(2976, 1, 1))   # 1 Yennayer 2976
# 2026-01-14T00:00:00
```

**Era note:** the +950 offset (Berber year 2976 = 2026 CE) was fixed in 1968
by the Académie Berbère to commemorate the accession of Shoshenq I, the
Berber pharaoh of Egypt's 22nd dynasty (conventionally dated 950 BC) — a
documented 20th-century symbolic choice, not an ancient reckoning.

**Caveat — civil holidays are separate from the arithmetic:** Algeria's
Yennayer public holiday is fixed by decree at 12 January Gregorian (2017),
and Morocco's at 13 January Gregorian (2023) — both legislated civil dates
that diverge from this calendar's own 14 January new year and are not
derived from it. Those dates live in the civil-holidays data
([civil-holidays.md](civil-holidays.md)), never in this conversion. The
year-end placement of the calendar's leap day (whether it falls in February,
as here, or is appended after the last month) is attested by only a single
source and is left as an open, unresolved convention rather than hard-coded.

Source: the Julian JDN algorithm above, shifted by the documented +950 era;
epoch and era history from the Académie Berbère's 1968 adoption and the
Algerian (2017) and Moroccan (2023) holiday decrees.

### Armenian

The traditional Armenian calendar: twelve 30-day months plus five extra days,
and — unusually — *no leap year at all*. Every year is exactly 365 days, so its
new year slips one day earlier against the seasons every four years.

```python
print(CALENDARS["armenian"].date(1, 1, 1))   # 1 Navasard AE 1
# 0552-07-13T00:00:00
```

**Caveat:** because it never intercalates, this "vague year" wanders steadily
against the sun; a date's season depends entirely on how many years have
passed. Source: Dershowitz & Reingold, *Calendrical Calculations* (Armenian
calendar); epoch 11 July 552 (Julian).

### Egyptian (civil)

The original 365-day "wandering year" of ancient Egypt — the ancestor of the
Coptic, Ethiopian and Armenian calendars. Three four-month seasons of harvest,
flood and growth, plus five feast days, and no leap day ever.

```python
print(CALENDARS["egyptian"].date(1, 1, 1))   # 1 Thoth, year 1 of Nabonassar
# -000746-02-18T00:00:00
```

**Caveat:** the same wandering-year caution as the Armenian calendar — with no
intercalation the calendar drifts a full year against the sun every 1,460
years (the "Sothic cycle"). Source: Dershowitz & Reingold (Egyptian calendar);
epoch anchored to the era of Nabonassar, 26 February 747 BC (Julian).

### French Republican (arithmetic)

The calendar of the French Revolution: twelve poetically-named 30-day months
plus five or six festival days, meant to sweep away the old order. This entry
uses the tidy arithmetic ("Romme") leap rule.

```python
print(CALENDARS["french_republican"].date(1, 1, 1))   # 1 Vendémiaire An I
# 1792-09-22T00:00:00
```

**Caveat:** the calendar as actually used set its leap years by the *observed*
autumnal equinox at Paris, which is not arithmetic. For that historical
version see `french_republican_equinox` below. Source: the Romme arithmetic
variant; epoch 22 September 1792.

### Bahá'í (arithmetic)

The Badíʿ calendar of the Bahá'í Faith: nineteen months of nineteen days, with
a handful of intercalary days tucked in before the last month. This entry uses
the pre-2015 form, where the new year (Naw-Rúz) was locked to 21 March.

```python
print(CALENDARS["bahai"].date(1, 1, 1))   # 1 Bahá, BE 1
# 1844-03-21T00:00:00
```

**Caveat:** since 2015 the calendar sets Naw-Rúz by the true vernal equinox at
Tehran, which is not arithmetic. For that, see `badi_2015` below. Source: the
arithmetic Badíʿ rules; epoch 21 March 1844.

### Maya Long Count

Not a year/month/day calendar at all, but a straight count of days written in
five positions — the system that famously "ended" on 21 December 2012 (it
simply rolled over, like a car's odometer). Because it is pure counting, the
standalone functions take all five positions.

The registry entry `CALENDARS["mayan_long_count"]` offers a three-field view
for uniformity with the other calendars: everything at or above the *tun* is
collapsed into the first field, so 13.0.0.0.0 (the close of the 13th baktun)
becomes tun-count `5200`:

```python
from chronologia import AstroDate

print(AstroDate.from_calendar("mayan_long_count", 5200, 0, 0))
# 2012-12-21T00:00:00 — the famous "end" of the Maya calendar
print(AstroDate(2012, 12, 21).to_calendar("mayan_long_count"))
# mayan_long_count 5200-00-00
```

The full five-position notation (`baktun.katun.tun.uinal.kin`) is available
through standalone functions for those who want it:

```python
# doctest: skip
from chronologia.calendars import mayan_long_count_to_jdn, mayan_long_count_from_jdn
mayan_long_count_to_jdn(13, 0, 0, 0, 0)     # -> the JDN of 13.0.0.0.0
mayan_long_count_from_jdn(2456283)          # -> (13, 0, 0, 0, 0)
```

Source: the Goodman–Martínez–Thompson correlation (GMT = 584283).

### ISO week date

The international standard for numbering weeks — "2020-W01-3" means the third
day of the first ISO week of 2020. It is a reckoning *of* the Gregorian
calendar, not a separate era, and businesses use it for scheduling.

```python
print(CALENDARS["iso_week"].date(2020, 1, 3))   # 2020, week 1, Wednesday
# 2020-01-01T00:00:00
```

**A subtlety worth knowing:** an ISO week can belong to a different year than
its calendar days. Week 1 is the week containing the first Thursday of January,
so early-January days sometimes fall in the *previous* ISO year. Source: ISO
8601.

---

## Table-based calendars

These read from a shipped published table. Each one is exact only inside its
`coverage` range, and raises a `CalendarRangeError` outside it — often naming a
`fallback` arithmetic calendar you can drop back to.

### Umm al-Qura (Saudi civil Hijri)

The official civil calendar of Saudi Arabia. Its months are fixed by a
published astronomical criterion and issued as an official table, so unlike the
tabular Islamic calendar it *is* the authoritative civil date — as far as the
table reaches.

```python
umm = CALENDARS["umm_al_qura"]
print(umm.date(1446, 9, 1))   # 1 Ramadan 1446
# 2025-03-01T00:00:00
```

**Caveat — range with fallback:** the table covers AH 1356–1500. Outside it,
the calendar raises an error that points you at the arithmetic calendar to use
instead:

```python
from chronologia import CalendarRangeError

try:
    umm.date(1200, 1, 1)            # before the table begins
except CalendarRangeError as error:
    print(error.fallback)
    # islamic_civil
```

Source: the official Umm al-Qura civil calendar table (coverage: AH 1356-01 ..
AH 1500-12).

### Chinese

The traditional Chinese lunisolar calendar, whose months follow the new moon
and whose leap months keep the year aligned to the sun. Its month-starts come
from astronomy, not a formula, so this library ships the Hong Kong Observatory
tables.

```python
chinese = CALENDARS["chinese"]
print(chinese.date(2025, 1, 1))   # Chinese New Year 2025
# 2025-01-29T00:00:00
```

A leap month is addressed by adding 100 to the ordinary month number, so 2025's
leap sixth month is month 106:

```python
print(chinese.date(2025, 106, 1))   # start of leap month 6
# 2025-07-25T00:00:00
```

**Caveat — table range:** exact for lunar years **1901 to 2099** only. There
is no arithmetic fallback (the true calendar needs astronomy), so out-of-range
access raises with no fallback rather than drifting. Source: Hong Kong
Observatory published conversion tables.

### Bahá'í (true equinox)

The post-2015 Badíʿ calendar, whose new year follows the observed vernal
equinox at Tehran — the astronomical companion to the arithmetic `bahai` entry.

```python
badi = CALENDARS["badi_2015"]
print(badi.date(180, 1, 1))   # 1 Bahá, BE 180
# 2023-03-21T00:00:00
```

**Caveat — table range:** covers BE 172–220. Source: the published equinox
table for the Badíʿ calendar.

### French Republican (equinox)

The French Revolutionary calendar as it was *actually kept*, with leap years
fixed by the observed autumnal equinox at Paris — the historical companion to
the arithmetic `french_republican` entry.

```python
freq = CALENDARS["french_republican_equinox"]
print(freq.date(1, 1, 1))   # 1 Vendémiaire An I
# 1792-09-22T00:00:00
```

**Caveat — table range:** covers An I to An XIII, the years the calendar was in
official use. Source: the published equinox table for the Republican calendar.

## Year cycles: which recent years were dragon years?

`chronologia.cycles` also registers **year cycles** — repeating labelled
sequences of *years*, the year-axis counterpart of the day cycles above
(`DAY_CYCLES`). Three are shipped: the 60-term Chinese **sexagenary** cycle
(stem-branch, e.g. `jia-zi`), the 12-term **Chinese zodiac** (`rat` .. `pig`),
and the 15-year Roman/Byzantine **indiction**.

```python
from chronologia import year_cycle_label, years_of, AstroDate

print(year_cycle_label(AstroDate(2024, 6, 1), "chinese_zodiac"))
# dragon

print([start.year for start, _ in years_of("chinese_zodiac", "dragon", 1990, 2025)])
# [2000, 2012, 2024]
```

**The mod-12-is-wrong-at-January lesson.** The zodiac and sexagenary labels
apply to the *Chinese lunisolar year*, not the Gregorian year, so a naive
`gregorian_year % 12` breaks every January/February until Chinese New Year
catches up:

```python
print(year_cycle_label(AstroDate(2024, 1, 15), "chinese_zodiac"))   # before CNY 2024-02-10
# rabbit
print(year_cycle_label(AstroDate(2024, 2, 10), "chinese_zodiac"))   # Chinese New Year 2024
# dragon
```

`year_cycle_label` resolves through `CALENDARS["chinese"]` itself (see
"Chinese" above), so it inherits that table's exact coverage — lunar years
1901–2099 — and raises `CalendarRangeError` outside it, same as any other
Chinese-calendar lookup.

**The indiction's own year-start edge.** The 15-year indiction is keyed to the
plain Gregorian year, but its own year begins 1 September (the
Constantinopolitan convention — see "When the year does not start on 1
January" in *Eras and rulers*), so August and October of the *same* Gregorian
year carry different indiction numbers:

```python
print(year_cycle_label(AstroDate(2024, 8, 15), "indiction"))   # before 1 Sept
# 2
print(year_cycle_label(AstroDate(2024, 10, 15), "indiction"))  # after 1 Sept
# 3
```

Sources: Wikipedia, "Sexagenary cycle" (1984 = jiazi, the stem x branch
pairing) and "Indiction" (Constantinopolitan 1-September year start; formula
corroborated against a second independent worked example at
skypoint.com/members/waltzmn/MSDating.html); both retrieved 2026-07-21 — see
`chronologia/cycles.py` for the full citations.

---

## Reference: all 18 calendars

`basis` is `exact` for the arithmetic calendars (no error bar) and `tabulated`
for the table-based ones. `months` is the highest month number a calendar can
name (leap-month and intercalary calendars use the larger count).

| key | months | epoch (JDN) | coverage | basis |
|---|---|---|---|---|
| `julian` | 12 | 1721424 | any year (proleptic) | exact |
| `revised_julian` | 12 | 1721426 | any year (proleptic) | exact |
| `hebrew` | 13 | 347998 | any year (proleptic) | exact |
| `islamic_civil` | 12 | 1948440 | any year (±1 day vs sighting) | exact |
| `solar_hijri_arithmetic` | 12 | 1948320 | modern era (±1 day) | exact |
| `coptic` | 13 | 1825030 | any year (proleptic) | exact |
| `ethiopian` | 13 | 1724221 | any year (proleptic) | exact |
| `berber` | 12 | 1374436 | any year (proleptic) | exact |
| `armenian` | 13 | 1922868 | any year (proleptic) | exact |
| `egyptian` | 13 | 1448638 | any year (proleptic) | exact |
| `french_republican` | 13 | 2375840 | any year (proleptic) | exact |
| `bahai` | 19 | 2394647 | any year (proleptic) | exact |
| `mayan_long_count` | 18 | 584283 | any day (proleptic) | exact |
| `iso_week` | 53 | 1721426 | any year (proleptic) | exact |
| `umm_al_qura` | 12 | 2428607 | AH 1356–1500 | tabulated |
| `chinese` | 12 | 2415435 | lunar years 1901–2099 | tabulated |
| `badi_2015` | 19 | 2457103 | BE 172–220 | tabulated |
| `french_republican_equinox` | 13 | 2375840 | An I–XIII | tabulated |

The Gregorian calendar itself is not a registry entry — it is the reference
everything converts against, via `gregorian_to_jdn` and `jdn_to_gregorian`.
