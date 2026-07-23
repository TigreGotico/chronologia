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
assert not is_civil_holiday(santo_antonio, "PT", categories=("public",))  # not statutorily, nationally
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
# The primary name is the official Arabic one; `display_name` renders English.
eid = [h for h in holidays_for("SA", 2024)
       if h.display_name("en") == "Eid al-Fitr"][0]
assert eid.name == "عيد الفطر"
assert eid.date == AstroDate(2024, 4, 10)
assert eid.basis == "tabulated"
```

The table has a range (roughly 1937–2077 CE). Ask for a year past it and the
engine **omits** the Islamic holidays rather than fabricating a wrong date — the
fixed Gregorian national days still resolve:

```python
far = {h.display_name("en") for h in holidays_for("SA", 2100)}
assert far == {"Founding Day", "National Day"}   # Eid dropped, honestly
```

A decree table past its horizon is different: by default the engine *predicts*
the date through a computable rule and marks it `basis="predicted"`. That is
honest, but a caller who never inspects `.basis` silently mixes a fabricated
future date in with facts. Pass `strict_horizon=True` to require
authoritative-only results — past a decree row's own horizon it returns nothing
rather than a predicted date, while computable holidays (fixed dates, weekday
rules) are unaffected:

```python
lenient = {h.name for h in holidays_for("BJ", 2028)}
strict = {h.name for h in holidays_for("BJ", 2028, strict_horizon=True)}
assert "Jour du Ramadan (estimé)" in lenient        # predicted past horizon
assert "Jour du Ramadan (estimé)" not in strict     # refused under strict
assert "Fête du Nouvel An" in strict                # fixed date, always kept
```

## Observed shifts

When a fixed holiday lands on a weekend it is often *observed* on a nearby
weekday. The US federal rule is Saturday → preceding Friday, Sunday → following
Monday. In 2021 Independence Day (4 July) fell on a Sunday:

```python
obs = [h for h in holidays_for("US", 2021) if h.name == "Independence Day"][0]
assert obs.date == AstroDate(2021, 7, 5)   # observed the Monday
```

## Substitute (in-lieu) days

An observed shift *relocates* a holiday; a **substitute** *adds* one, keeping the
nominal day too. The UK grants a substitute weekday when a bank holiday falls on a
weekend, and the Christmas/Boxing pair cascades to two distinct days — resolved
across the whole year so a substitute never lands on another holiday:

```python
gb = {(h.date.month, h.date.day): h.name for h in holidays_for("GB", 2021)}
assert gb[(12, 27)] == "Christmas Day (substitute day)"   # Sat 25 Dec -> Mon 27
assert gb[(12, 28)] == "Boxing Day (substitute day)"      # Sun 26 Dec -> Tue 28
```

Japan's 振替休日 (furikae) is the same mechanism with a Sunday-only trigger:

```python
jp = {(h.date.month, h.date.day): h.name for h in holidays_for("JP", 2024)}
assert jp[(9, 23)] == "秋分の日 (振替休日)"   # Autumnal Equinox: Sun 22 Sep -> Mon 23
```

## Year-gated holidays

A rule can carry a validity range, so a holiday that only became statutory in a
given year is absent before it and present after (US Juneteenth from 2021):

```python
assert "Juneteenth National Independence Day" not in \
    {h.name for h in holidays_for("US", 2020)}
assert "Juneteenth National Independence Day" in \
    {h.name for h in holidays_for("US", 2021)}
```

## Categories

Every holiday carries a documented subset of the schema
`{public, regional, municipal, religious, school}`. A holiday can hold several
at once, and you can filter by them:

```python
religious = holidays_for("PT", 2024, categories=["religious"])
assert all("religious" in h.categories for h in religious)
```

## Internationalisation — a holiday's real name

The golden rule: **a holiday's real name is what its own government calls it.**
Saudi Arabia does not have a holiday called "Eid al-Fitr"; it has one called
عيد الفطر. So the **primary name is the official native name**, and everything
else is layered honestly on top of it.

```python
from chronologia import holidays_for

# China's Spring Festival. Its real name is Chinese; the English name is a
# *co-official* alternate the government also publishes.
cny = [h for h in holidays_for("CN", 2024) if h.name == "春节"][0]
assert cny.name == "春节"                       # official native name (primary)
assert cny.names["en"] == "Spring Festival"     # co-official English name
```

A jurisdiction with several official languages carries **all** of them in
`names`. Canada is bilingual federally; the United Kingdom's bank holidays carry
their Welsh names; India's national days carry Hindi:

```python
canada_day = [h for h in holidays_for("CA", 2024) if h.name == "Canada Day"][0]
assert canada_day.names["fr"] == "Fête du Canada"     # French is official too

xmas = [h for h in holidays_for("GB", 2024) if h.name == "Christmas Day"][0]
assert xmas.names["cy"] == "Dydd Nadolig"             # Welsh, co-official in Wales
```

### Official names vs translations

There are two honestly-distinct kinds of name. **Official names** are citable
facts — a government published them. **Translations** are renderings *we*
authored to help you display a holiday elsewhere; they are marked
`source: translation` and never masquerade as official. `display_name(lang)`
walks a documented fallback chain — **official name → translation → the primary
native name**:

```python
# The government's own word wins where it exists; a translation fills the gap.
assert cny.display_name("en") == "Spring Festival"      # co-official English
assert cny.display_name("pt") == "Ano Novo Chinês"      # a display translation
assert cny.display_name("ja") == "春节"                  # no rendering -> native

# Portugal is single-language official, so display_name renders via translations.
ano_novo = [h for h in holidays_for("PT", 2024) if h.name == "Ano Novo"][0]
assert ano_novo.display_name("de") == "Neujahr"         # translation
assert ano_novo.display_name("pt") == "Ano Novo"        # native (the official)
```

Translations cover the national and regional tiers in English, Portuguese,
Spanish, German and French, for a **deliberately growing** set of jurisdictions:
a jurisdiction earns its full five-language matrix when those renderings are
authored with confidence, rather than fabricating a low-confidence gloss for
every holiday the moment a new country's native-primary file lands. Every
jurisdiction, covered or not, still gets its official native name (and any
co-official names — Switzerland's de/fr/it, Belgium's nl/fr/de, Ireland's
en/ga), and `display_name` always resolves *something* via the fallback chain.
Portugal's ~300 municipal saints'-day feasts are deliberately *not* translated:
"Santo António" is the same proper noun in every language, so `display_name`
falls back to the native name — which is the honest answer, not a gap.

## Data files

Rules live in `chronologia/holiday_data/<country>.tab` — a documented text
format with a mandatory provenance header (official source URL + retrieval
date), one pipe-delimited rule per line:

```
kind | name | args | categories | subdiv | observed | valid
```

The `name` column is normally a single official name. A multi-official
jurisdiction gives `;;`-separated, `lang:`-tagged alternates — the first is the
primary name, the rest populate `names`:

```
calendar_date | zh:春节 ;; en:Spring Festival | chinese 1 1 | public |  |
```

Display translations live separately in `holiday_data/i18n/translations.tab`
(`jurisdiction | name | lang | text`, keyed on the primary native name), so a
rendering can never be mistaken for an official name. The `observed` column
names either a relocating shift (`us`, `sun_mon`, …) or an in-lieu substitute
(`gb_substitute`, `jp_furikae`); the optional `valid` column bounds the years a
rule is in force (`2024-`, `-2015`, `2016-2020`, `2024`).

New jurisdictions are data, not code: add a `.tab` file with its citations and
the engine loads it.
