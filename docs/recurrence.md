# Recurrence rules (RFC 5545 RRULE)

<!-- agent-hint
covers: RFC 5545 RRULE parsing and expansion into day-wide spans, and the rules the library refuses
source: chronologia/recurrence.py, chronologia/extract/impossible.py
generated: no
verify: .venv/bin/python -c 'exec("import ast,io,re,sys,contextlib as c\np=sys.argv[1];t=open(p).read();ns={};n=bad=0\nfor b in re.findall(r\"\\x60\\x60\\x60python\\n(.*?)\\x60\\x60\\x60\",t,re.S):\n    if \"# doctest: skip\" in b: continue\n    L=b.split(\"\\n\")\n    for s in ast.parse(b).body:\n        o=io.StringIO()\n        with c.redirect_stdout(o): exec(compile(ast.Module([s],[]),p,\"exec\"),ns)\n        n+=isinstance(s,ast.Assert)\n        m=re.match(r\"^\\s*print\\(.*\\)\\s+# (.+)$\",L[s.end_lineno-1]) if isinstance(s,ast.Expr) and s.lineno==s.end_lineno else None\n        if m: n+=1; bad|=m[1].strip()!=o.getvalue().strip()\nsys.exit(bad or n==0)\n")' docs/recurrence.md
see: docs/events.md, docs/civil-holidays.md
-->

"Every third Tuesday." "The last Monday of May." "Friday the 13th." These are *recurrence rules*, a compact grammar for an unbounded set of dates. The calendar world already standardised that grammar in [RFC 5545 §3.3.10](https://www.rfc-editor.org/rfc/rfc5545#section-3.3.10) (the iCalendar `RRULE`). So chronologia speaks it directly, and evaluates it as pure Julian-Day-Number arithmetic over `AstroDate` / `DateSpan`.

Expansion is integer math on the JDN hub. A yearly rule runs the same in the year 2025, the year −500 and the year 50000. There is no `datetime` window and nothing overflows.

## The golden rule: every third Tuesday

```python
from chronologia import parse_rrule, occurrences, every, AstroDate

# "The third Tuesday of every month", the classic standing-meeting rule.
third_tuesday = parse_rrule("FREQ=MONTHLY;BYDAY=TU;BYSETPOS=3")

for span in occurrences(third_tuesday, AstroDate(2025, 1, 1), count=4):
    print(span.start.date())
```

`BYDAY=TU` expands each month to its Tuesdays. `BYSETPOS=3` then keeps the third one. Every occurrence comes back as a **day-wide `DateSpan`**, a whole calendar day, `[start, start+1 day)`, so it drops straight into the rest of chronologia (`span.start`, `span.contains(...)`, `span.overlaps(...)`).

## Building rules pythonically

You do not have to write RRULE strings by hand. `every(freq, **by)` is the friendly constructor, and there are conveniences for the common "nth weekday" shapes:

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

Every rule round-trips through `to_string()` / `parse_rrule`, so the pythonic form and the RFC string are interchangeable.

## The Jan-31 lesson: invalid dates are omitted, never clamped

This is the trap that catches every naive "add one month" implementation. Take a monthly recurrence that starts on 31 January. A naive library might return 3 March (31 January + 31 days) or clamp to 28 February. RFC 5545 does neither. **A generated date that does not exist is dropped** (§3.3.10, "Recurrence rules may generate recurrence instances with an invalid date ... Such ... instances MUST be ignored").

```python
month_end = parse_rrule("FREQ=MONTHLY;COUNT=4")
# Jan 31, Mar 31, May 31, Jul 31  (February and April have no 31st)
print([s.start.date() for s in occurrences(month_end, AstroDate(2023, 1, 31))])  # [datetime.date(2023, 1, 31), datetime.date(2023, 3, 31), datetime.date(2023, 5, 31), datetime.date(2023, 7, 31)]
```

February is skipped, not fudged. The same rule keeps leap day honest, a yearly recurrence anchored on 29 February only fires in leap years:

```python
leap = parse_rrule("FREQ=YEARLY;COUNT=3")
# 2024-02-29, 2028-02-29, 2032-02-29
print([s.start.date() for s in occurrences(leap, AstroDate(2024, 2, 29))])  # [datetime.date(2024, 2, 29), datetime.date(2028, 2, 29), datetime.date(2032, 2, 29)]
```

If you want "the last day of the month" *whatever* its length, name that instead, `BYMONTHDAY=-1` counts back from the end:

```python
last_day = parse_rrule("FREQ=MONTHLY;COUNT=4;BYMONTHDAY=-1")
# Jan 31, Feb 28, Mar 31, Apr 30
print([s.start.date() for s in occurrences(last_day, AstroDate(2023, 1, 1))])  # [datetime.date(2023, 1, 31), datetime.date(2023, 2, 28), datetime.date(2023, 3, 31), datetime.date(2023, 4, 30)]
```

## A rule that can never occur

A rule that names a date no year has is an error. `FREQ=YEARLY;BYMONTH=2;BYMONTHDAY=30` asks for 30 February, so `parse_rrule` and `every` raise `ValueError` at construction. They do not return a rule that scans for ever.

```python
try:
    parse_rrule("FREQ=YEARLY;BYMONTH=2;BYMONTHDAY=30")
except ValueError as exc:
    print(exc)  # BYMONTH=(2,) with BYMONTHDAY=(30,) can never occur (e.g. 30 February); the rule matches no date
```

A spoken phrase takes the same road. `extract_recurrence("every 30th of february", "en")` returns `None`. With `impossible="raise"` it raises `ImpossibleDateError`, a `ValueError`, whose `reason` is "February has no 30th". [Impossible dates and out-of-range ordinals](extraction.md#impossible-dates-and-out-of-range-ordinals) lists every refusal.

```python
from chronologia import ImpossibleDateError, extract_recurrence

print(extract_recurrence("every 30th of february", "en"))  # None
try:
    extract_recurrence("every 30th of february", "en", impossible="raise")
except ImpossibleDateError as err:
    print(err.reason)  # February has no 30th
```

## Bounded by design

An RRULE can describe an infinite set ("every Monday, forever"). `occurrences` refuses to enumerate one blindly. If neither the rule (`COUNT`/`UNTIL`) nor your call (`count=`/`until=`) bounds it, `occurrences` raises instead of looping.

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

The start date anchors the rule. It fixes the interval phase and fills in any detail the rule leaves unsaid. But chronologia includes it in the result set **only if it actually matches the rule**. This is the strict reading of RFC 5545. It differs from `python-dateutil`, which always prepends the start date even when it does not satisfy the rule. Start a Monday rule on a Wednesday and you get only Mondays:

```python
mondays = parse_rrule("FREQ=WEEKLY;BYDAY=MO;COUNT=2")
wednesday = AstroDate(2025, 6, 11)          # a Wednesday
# 2025-06-16, 2025-06-23  (the seed Wednesday is NOT emitted)
print([s.start.date() for s in occurrences(mondays, wednesday)])  # [datetime.date(2025, 6, 16), datetime.date(2025, 6, 23)]
```

## What this engine covers, and what it doesn't

Supported rule parts (date-level recurrence): `FREQ` = `DAILY` / `WEEKLY` / `MONTHLY` / `YEARLY`, `INTERVAL`, `COUNT`, `UNTIL`, `BYMONTH`, `BYWEEKNO` (ISO weeks, honouring `WKST`), `BYYEARDAY`, `BYMONTHDAY` (including negatives), `BYDAY` (including ordinals such as `1MO` / `-1FR`), `BYSETPOS`, and `WKST`.

On top of that date skeleton the engine accepts a **time-of-day pin**, `BYHOUR` and `BYMINUTE`. So a civil rule spoken with a clock ("daily at 9") keeps its hour. When a clock is pinned each matched day expands to that time (a one-hour span, or a one-minute span when the minute is pinned too):

```python
rule = parse_rrule("FREQ=DAILY;BYHOUR=9")
first = next(iter(occurrences(rule, AstroDate(2026, 1, 1), count=1)))
print(first.start.hour)   # 9
```

Deliberately **out of scope**: the sub-day *frequencies*, `FREQ=HOURLY` / `MINUTELY` / `SECONDLY` and `BYSECOND`. A within-day *frequency* has no meaning for a civil calendar rule, so parsing one raises rather than dropping it silently:
```python
try:
    parse_rrule("FREQ=HOURLY;COUNT=3")
except ValueError as exc:
    print("sub-day rejected:", "out of scope" in str(exc))
```

## Movable feasts: `HolidayRecurrence`

Some holidays recur every year but have *no* RFC 5545 rule. Easter is a *computus*. The Islamic feasts are a lunar-calendar lookup. `HolidayRecurrence` holds these. It expands to real dates through the holiday engine, and `to_string()` refuses to invent a rule.

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

"Every holiday in Portugal" is not one date's recurrence. It is a whole calendar of holidays, queried again for each year from `chronologia.civil_holidays`. `JurisdictionHolidays` holds it on the same terms as `HolidayRecurrence`. It gives real dates through `occurrences()`, and `to_string()` gives no invented `RRULE`.

`categories` defaults to `("public",)`, "holiday" plainly means the public holidays unless asked for more (e.g. `("public", "bank")`).

```python
from chronologia.recurrence import JurisdictionHolidays

pt = JurisdictionHolidays("PT")
dates = list(pt.occurrences(AstroDate(2026, 1, 1), count=14))
# every 2026 Portuguese public holiday
print([d.start.month for d in dates])  # [1, 2, 4, 4, 4, 5, 6, 6, 8, 10, 11, 12, 12, 12]

try:
    pt.to_string()
except ValueError as exc:
    print("no RRULE:", "jurisdiction holiday set" in str(exc))
```

`extract_recurrence` reads the "every [public] holiday in <jurisdiction>" frame (and its per-locale equivalents, e.g. Portuguese "todos os feriados em Portugal" / "cada feriado de Portugal") straight into this object. An unrecognised jurisdiction name simply does not match, never a guess.

---
[← Events and iCalendar](events.md) · [Home](index.md) · [EDTF →](edtf.md)
