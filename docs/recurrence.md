# Recurrence rules (RFC 5545 RRULE)

"Every third Tuesday." "The last Monday of May." "Friday the 13th." These are
*recurrence rules* — a compact grammar for an unbounded set of dates. The
calendar world already standardised that grammar in
[RFC 5545 §3.3.10](https://www.rfc-editor.org/rfc/rfc5545#section-3.3.10) (the
iCalendar `RRULE`), so chronologia speaks it directly, and evaluates it as pure
Julian-Day-Number arithmetic over `AstroDate` / `DateSpan`.

Because expansion is just integer math on the JDN hub, a yearly rule runs the
same in the year 2025, the year −500, or the year 50000. There is no
`datetime` window and nothing overflows.

## The golden rule: every third Tuesday

```python
from chronologia import parse_rrule, occurrences, every, AstroDate

# "The third Tuesday of every month" — the classic standing-meeting rule.
third_tuesday = parse_rrule("FREQ=MONTHLY;BYDAY=TU;BYSETPOS=3")

for span in occurrences(third_tuesday, AstroDate(2025, 1, 1), count=4):
    print(span.start.date())
```

`BYDAY=TU` expands each month to its Tuesdays; `BYSETPOS=3` then keeps the
third one. Every occurrence comes back as a **day-wide `DateSpan`** — a whole
calendar day, `[start, start+1 day)` — so it drops straight into the rest of
chronologia (`span.start`, `span.contains(...)`, `span.overlaps(...)`).

## Building rules pythonically

You do not have to write RRULE strings by hand. `every(freq, **by)` is the
friendly constructor, and there are conveniences for the common "nth weekday"
shapes:

```python
from chronologia import nth_weekday_of_month, last_weekday_of_month

labor_day = every("yearly", bymonth=9, byday="1MO")          # 1st Mon of Sep
thanksgiving = nth_weekday_of_month(4, "TH", month=11)        # 4th Thu of Nov
spring_bank = last_weekday_of_month("MO", month=5)           # last Mon of May

print(labor_day.to_string())
for name, rule in [("Labor Day", labor_day),
                   ("Thanksgiving", thanksgiving),
                   ("UK spring bank", spring_bank)]:
    days = [s.start.date() for s in occurrences(rule, AstroDate(2025, 1, 1),
                                                count=1)]
    print(name, days[0])
```

Every rule round-trips through `to_string()` / `parse_rrule`, so the pythonic
form and the RFC string are interchangeable.

## The Jan-31 lesson: invalid dates are omitted, never clamped

This is the trap that catches every naive "add one month" implementation. Ask
for a monthly recurrence starting on 31 January and a reasonable-looking
library might hand you 3 March (31 January + 31 days) or silently clamp to
28 February. RFC 5545 does neither: **a generated date that does not exist is
simply dropped** (§3.3.10, "Recurrence rules may generate recurrence instances
with an invalid date ... Such ... instances MUST be ignored").

```python
month_end = parse_rrule("FREQ=MONTHLY;COUNT=4")
print([s.start.date() for s in occurrences(month_end, AstroDate(2023, 1, 31))])
# -> Jan 31, Mar 31, May 31, Jul 31  (February and April have no 31st)
```

February is skipped, not fudged. The same rule keeps leap day honest — a
yearly recurrence anchored on 29 February only fires in leap years:

```python
leap = parse_rrule("FREQ=YEARLY;COUNT=3")
print([s.start.date() for s in occurrences(leap, AstroDate(2024, 2, 29))])
# -> 2024-02-29, 2028-02-29, 2032-02-29
```

If you want "the last day of the month" *whatever* its length, name that
instead — `BYMONTHDAY=-1` counts back from the end:

```python
last_day = parse_rrule("FREQ=MONTHLY;COUNT=4;BYMONTHDAY=-1")
print([s.start.date() for s in occurrences(last_day, AstroDate(2023, 1, 1))])
# -> Jan 31, Feb 28, Mar 31, Apr 30
```

## Bounded by design

An RRULE can describe a genuinely infinite set ("every Monday, forever").
`occurrences` refuses to enumerate one blindly: if neither the rule
(`COUNT`/`UNTIL`) nor your call (`count=`/`until=`) bounds it, it raises rather
than looping forever.

```python
forever = parse_rrule("FREQ=WEEKLY;BYDAY=MO")
try:
    list(occurrences(forever, AstroDate(2025, 1, 1)))
except ValueError as exc:
    print("refused:", "unbounded" in str(exc))

# Bound it with a count or an until and it runs:
print(len(list(occurrences(forever, AstroDate(2025, 1, 1), count=5))))
```

## DTSTART is strict here (a deliberate dateutil difference)

The start date anchors the rule — it fixes the interval phase and fills in any
detail the rule leaves unsaid — but chronologia includes it in the result set
**only if it actually matches the rule**. This is the strict reading of
RFC 5545, and it differs from `python-dateutil`, which always prepends the
start date even when it does not satisfy the rule. Start a Monday rule on a
Wednesday and you get only Mondays:

```python
mondays = parse_rrule("FREQ=WEEKLY;BYDAY=MO;COUNT=2")
wednesday = AstroDate(2025, 6, 11)          # a Wednesday
print([s.start.date() for s in occurrences(mondays, wednesday)])
# -> 2025-06-16, 2025-06-23  (the seed Wednesday is NOT emitted)
```

## What this engine covers, and what it doesn't

Supported rule parts (date-level recurrence): `FREQ` = `DAILY` / `WEEKLY` /
`MONTHLY` / `YEARLY`, `INTERVAL`, `COUNT`, `UNTIL`, `BYMONTH`, `BYWEEKNO` (ISO
weeks, honouring `WKST`), `BYYEARDAY`, `BYMONTHDAY` (including negatives),
`BYDAY` (including ordinals such as `1MO` / `-1FR`), `BYSETPOS`, and `WKST`.

On top of that date skeleton the engine accepts a **time-of-day pin** —
`BYHOUR` and `BYMINUTE` — so a civil rule spoken with a clock ("daily at 9")
keeps its hour. When a clock is pinned each matched day expands to that time (a
one-hour span, or a one-minute span when the minute is pinned too):

```python
rule = parse_rrule("FREQ=DAILY;BYHOUR=9")
first = next(iter(occurrences(rule, AstroDate(2026, 1, 1), count=1)))
print(first.start.hour)   # 9
```

Deliberately **out of scope**: the sub-day *frequencies* — `FREQ=HOURLY` /
`MINUTELY` / `SECONDLY` and `BYSECOND`. A within-day *frequency* has no meaning
for a civil calendar rule, so parsing one raises rather than dropping it
silently:
```python
try:
    parse_rrule("FREQ=HOURLY;COUNT=3")
except ValueError as exc:
    print("sub-day rejected:", "out of scope" in str(exc))
```

## Movable feasts: `HolidayRecurrence`

Some holidays recur every year yet have *no* RFC 5545 rule — Easter is a
*computus*, the Islamic feasts a lunar-calendar lookup. `HolidayRecurrence` is
the honest home for those: it expands to real dates through the holiday engine,
but `to_string()` refuses to fabricate a rule.

```python
from chronologia.recurrence import HolidayRecurrence

easter = HolidayRecurrence("easter")
dates = list(easter.occurrences(AstroDate(2026, 1, 1), count=2))
print([d.start.year for d in dates])   # [2026, 2027]

try:
    easter.to_string()
except ValueError as exc:
    print("no RRULE:", "movable feast" in str(exc))
```

## Jurisdiction holiday sets: `JurisdictionHolidays`

"Every holiday in Portugal" is not one date's recurrence — it is a whole
calendar's worth of holidays, re-queried per year from
`chronologia.civil_holidays`. `JurisdictionHolidays` is the honest home for
that, on the same terms as `HolidayRecurrence`: real dates through
`occurrences()`, no fabricated `RRULE` from `to_string()`.

`categories` defaults to `("public",)` — "holiday" plainly means the public
holidays unless asked for more (e.g. `("public", "bank")`).

```python
from chronologia.recurrence import JurisdictionHolidays

pt = JurisdictionHolidays("PT")
dates = list(pt.occurrences(AstroDate(2026, 1, 1), count=14))
print([d.start.month for d in dates])   # every 2026 Portuguese public holiday

try:
    pt.to_string()
except ValueError as exc:
    print("no RRULE:", "jurisdiction holiday set" in str(exc))
```

`extract_recurrence` reads the "every [public] holiday in <jurisdiction>"
frame (and its per-locale equivalents, e.g. Portuguese "todos os feriados em
Portugal" / "cada feriado de Portugal") straight into this object; an
unrecognised jurisdiction name simply does not match — never a guess.
