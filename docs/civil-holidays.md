# Civil holidays

The golden question this module answers is not "what are the holidays this
year?" but **"is Monday a holiday where *you* live?"** — and in most of the
world the honest answer depends on your *municipality*, not your country.

A civil holiday is a **rule**, not a date. "New Year's Day" is *1 January every
year*; "US Labor Day" is *the first Monday of September*; "Corpo de Deus" is
*the 60th day after Easter*; "Eid al-Fitr" is *1 Shawwal on the Umm al-Qura
table*. `chronologia` stores the rule and computes the date, reusing the same
JDN machinery as the rest of the library — so a holiday for the year 1789 falls
out of the same arithmetic as one for 2024.

```python
from chronologia import holidays_for, is_civil_holiday, AstroDate

# Portugal's national public holidays for 2024.
national = [h for h in holidays_for("PT", 2024)
            if h.subdiv is None and "public" in h.categories]
names = {h.name for h in national}
assert "Sexta-feira Santa" in names      # Good Friday, Easter - 2
assert "Corpo de Deus" in names          # Corpus Christi, Easter + 60
```

## The municipal story

Portugal is the flagship. Beyond the 13 national days, nearly every one of the
~300 *concelhos* (municipalities) has its own **feriado municipal**. Lisbon
stops for Santo António on 13 June; Porto for São João on 24 June. Ask the
country and you miss both; ask the municipality and the real answer appears.

```python
# Is 13 June 2024 a holiday? It depends where you live.
santo_antonio = AstroDate(2024, 6, 13)
assert not is_civil_holiday(santo_antonio, "PT")                 # not nationally
assert is_civil_holiday(santo_antonio, "PT", subdiv="PT-LSB")    # yes, in Lisbon

# Porto's São João a fortnight later.
sao_joao = AstroDate(2024, 6, 24)
assert is_civil_holiday(sao_joao, "PT", subdiv="PT-PRT")
```

Subdivisions are additive: `holidays_for("PT", 2024, subdiv="PT-LSB")` returns
the national days **plus** Lisbon's municipal ones. Municipal rules can be
movable too — Castelo de Vide keeps *Nossa Senhora da Luz* on Easter Monday:

```python
cv = holidays_for("PT", 2024, subdiv="PT-CVD")
easter_monday = [h for h in cv if h.subdiv == "PT-CVD"]
assert AstroDate(2024, 4, 1) in {h.date for h in easter_monday}
```

## Rule kinds

Each kind of rule is its own frozen class; a holiday names one and adds its
civil metadata.

| kind | means | example |
|---|---|---|
| `FixedRule(month, day)` | same Gregorian date every year | New Year's Day |
| `NthWeekdayRule(month, n, weekday, post_offset)` | the n-th (−1 = last) weekday of a month, optionally offset | US Labor Day = 1st Monday of September |
| `EasterOffsetRule(offset, method)` | whole-day offset from computed Easter | Corpo de Deus = Easter + 60 |
| `CalendarDateRule(calendar_key, month, day)` | a fixed date in *another* calendar | Eid al-Fitr = 1 Shawwal (Umm al-Qura) |
| `DecreeTableRule(dates)` | explicit per-year dates, no rule | China's 调休 shift days |

```python
from chronologia import (FixedRule, NthWeekdayRule, EasterOffsetRule,
                         CalendarDateRule)

labor_day = NthWeekdayRule(9, 1, 0)                # 1st Monday of September
assert labor_day.observances(2024)[0][0] == AstroDate(2024, 9, 2)

corpus = EasterOffsetRule(60)
assert corpus.observances(2024)[0][0] == AstroDate(2024, 5, 30)
```

## Rules vs decrees — the honest kind

Some holidays genuinely have no computable rule: they are announced by decree
each year (China's shift days, one-off royal events). Pretending they follow a
formula would be a lie, so `DecreeTableRule` stores the explicit dates and marks
them `tabulated`. The engine is honest about *how* it knows each date.

## Basis honesty and calendar ranges

`CalendarDateRule` resolves through another calendar. Saudi Arabia's Eid dates
come from the **Umm al-Qura** table, so they carry `basis="tabulated"` — a
published-table date, not an astronomical recomputation:

```python
eid = [h for h in holidays_for("SA", 2024) if h.name == "Eid al-Fitr"][0]
assert eid.date == AstroDate(2024, 4, 10)
assert eid.basis == "tabulated"
```

The table has a range (roughly 1937–2077 CE). Ask for a year past it and the
engine **omits** the Islamic holidays rather than fabricating a wrong date — the
fixed Gregorian national days still resolve:

```python
far = {h.name for h in holidays_for("SA", 2100)}
assert far == {"Founding Day", "National Day"}   # Eid dropped, honestly
```

## Observed shifts

When a fixed holiday lands on a weekend it is often *observed* on a nearby
weekday. The US federal rule is Saturday → preceding Friday, Sunday → following
Monday. In 2021 Independence Day (4 July) fell on a Sunday:

```python
obs = [h for h in holidays_for("US", 2021) if h.name == "Independence Day"][0]
assert obs.date == AstroDate(2021, 7, 5)   # observed the Monday
```

## Categories

Every holiday carries a documented subset of the schema
`{public, regional, municipal, religious, school}`. A holiday can hold several
at once, and you can filter by them:

```python
religious = holidays_for("PT", 2024, categories=["religious"])
assert all("religious" in h.categories for h in religious)
```

## Data files

Rules live in `chronologia/holiday_data/<country>.tab` — a documented text
format with a mandatory provenance header (official source URL + retrieval
date), one pipe-delimited rule per line:

```
kind | name | args | categories | subdiv | observed
```

New jurisdictions are data, not code: add a `.tab` file with its citations and
the engine loads it.
