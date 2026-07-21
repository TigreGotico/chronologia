# Civil holidays

*Is Monday a holiday in Scotland?*

That question has two halves, and chronologia answers only one of them itself.
"Is this the first Monday of August?" is **arithmetic** — a recurrence rule
anyone can reproduce forever. "Does Scotland close its offices that Monday?"
is a **decree** — a fact that exists because a government said so, that England
does *not* share, and that can change by the next gazette. chronologia owns the
rules. For the decrees it borrows a database.

```python
import datetime
from chronologia import is_holiday

monday = datetime.date(2026, 8, 3)          # a Monday
scotland = is_holiday(monday, "GB", subdiv="SCT", language="en_US")
england = is_holiday(monday, "GB", subdiv="ENG", language="en_US")

print(scotland.name)   # Summer Bank Holiday Monday
print(england)         # None — same Monday, no holiday south of the border
```

## Rules vs decrees — the division of labour

chronologia's core is rules. Easter is a computus; Christmas is a fixed
December date; Eid, Rosh Hashanah and the Spring Festival are calendar
conversions off the shared Julian-Day hub. None of that needs a database — it
needs a formula, and the formula never goes stale.

Civil observances are the other half: *which* of those anchors a particular
state actually closes for, plus the parts that are pure proclamation — founding
days, in-lieu "bridge" days, subdivision quirks. That half is data, it changes
every few years, and keeping it current is a full-time project. The
[`vacanza/holidays`](https://github.com/vacanza/holidays) package is that
project.

So `chronologia.holiday_bridge` is the **tzdb pattern** applied to holidays,
exactly as [`zone_timelines`](timezones.md) delegates the offset database to
`zoneinfo` while owning the typed timeline. chronologia keeps the rules; the
bridge borrows the decrees and hands them back as chronologia's own types.

## An optional extra — the core stays dependency-free

The `holidays` database is **not** a runtime dependency of chronologia. It is
an opt-in extra:

```
pip install chronologia[holidays]
```

Importing the bridge never pulls the database in — the import is lazy, inside
each function. If the extra is missing, you get an actionable error naming the
install, not a bare `ModuleNotFoundError`.

## Objects out, not strings

`civil_holidays(country, year, ...)` returns a tuple of frozen `Holiday`
objects. Each carries a day-wide `DateSpan`, the country, any subdivision, the
categories that claim it, and a `basis` — the honesty signal described below.

```python
from chronologia import civil_holidays

for h in civil_holidays("US", 2026):
    if h.name in ("New Year's Day", "Independence Day"):
        print(h.name, h.date, h.span.width, h.basis)
# New Year's Day 2026-01-01 1 day, 0:00:00 tabulated
# Independence Day 2026-07-04 1 day, 0:00:00 tabulated
```

Subdivisions fold in their state- or province-specific observances, and
categories tag each holiday with exactly the requested categories that apply to
it:

```python
ca = civil_holidays("US", 2026, subdiv="CA")
print(any("Chavez" in h.name for h in ca))   # True — Cesar Chavez Day is CA-only
```

## The honesty layer: estimated becomes *predicted*

A lunar observance far in the future cannot be *known* — the day a country will
observe Eid depends on a moon sighting or a future decree. `holidays` computes
those forward dates from an arithmetic model and **flags them as estimates** by
wrapping the holiday name with a locale-specific marker (`"(estimated)"` in
English). The bridge reads that flag, strips the marker back off the name, and
maps it onto chronologia's `basis` axis:

* an estimated future date → `basis="predicted"` — a forward model, not a fact;
* a confirmed past date, or an officially published forward calendar →
  `basis="tabulated"`.

```python
egypt = civil_holidays("EG", 2033, language="en_US")
eid = [h for h in egypt if "Eid al-Fitr" in h.name][0]
print(eid.name, eid.basis)      # Eid al-Fitr predicted  (marker stripped, honesty kept)
```

Saudi Arabia is the instructive counter-example: it publishes the official
Umm al-Qura calendar years ahead, so it does *not* mark future Eid as
estimated — and the bridge reports those dates as `tabulated`, not `predicted`.

```python
saudi = civil_holidays("SA", 2033, language="en_US")
eid = [h for h in saudi if "Eid al-Fitr" in h.name][0]
print(eid.basis)                # tabulated — an official published calendar
```

Detection reads the database object's *own* translated marker templates, so it
holds in every locale rather than matching a hard-coded English string.

## Multi-day feasts and in-lieu days

`holidays` emits every observed day as its own dated entry: a four-day Eid is
four entries, and an in-lieu substitute day is a *separate* entry from the
holiday it compensates. The bridge passes these through one-to-one, so
iterating the result shows exactly the days that are off.

```python
saudi_2026 = civil_holidays("SA", 2026, language="en_US")
eid_days = [h.date for h in saudi_2026 if h.name == "Eid al-Fitr Holiday"]
print(len(eid_days) >= 2)       # True — a multi-day feast, one Holiday per day
```
