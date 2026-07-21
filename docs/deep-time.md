# Deep time

Most of this library is about human dates. This page is about the other 99.9%
of time — the age of the dinosaurs, the ice ages, the Bronze Age — where we
stop counting individual days and start naming vast stretches. The tools here
answer "when was the Jurassic?" and "how old is this campfire charcoal?" with
the same honesty about uncertainty that the rest of the library insists on.

## Named periods: the geological chart

Geologists have agreed on an official map of deep time — a nested chart of
eons, eras, periods, epochs and ages, each with a name and a boundary. It is
maintained by an international body (the ICS, the International Commission on
Stratigraphy) and revised as the science improves. This library ships one
published version of that chart, and lets you look any name up.

```python
from chronologia import lookup

jurassic = lookup("jurassic")
print(jurassic.span.start.year)   # astronomical year of the older edge
# -201598050
print(jurassic.span.end.year)     # astronomical year of the younger edge
# -143098050
print(jurassic.level)
# period
```

Those years — about 201.6 million and 143.1 million years ago — are not
guesses this library made up. They come straight from the chart, and they wear
their basis on their sleeve:

```python
print(jurassic.span.basis)
# tabulated
print(jurassic.source)
# ICS International Chronostratigraphic Chart 2023/09
```

### Why the boundaries have error bars

A geological boundary is never known to the exact year — it is measured, with
an uncertainty of thousands or millions of years. The chart publishes those
uncertainties, and this library folds them *outward* into the span: the older
edge is pushed a little older, the younger edge a little younger, so the span
covers the full published envelope. A wide span is the science being honest
about what it does not precisely know.

## Walking the hierarchy

The chart nests, so you can walk down from a period into its epochs:

```python
from chronologia import children

print([c.name for c in children("jurassic")])
# ['Early Jurassic', 'Middle Jurassic', 'Late Jurassic']
```

## Subdivide: "the Late Jurassic" beats arithmetic

Often you want a rough third of a period — "early", "mid", "late". You can ask
for that on any span, and by default you get an arithmetic slice. But here is
the clever part: when the *chart itself* defines that subdivision, the library
returns the real, official one instead of a mechanical third.

```python
from chronologia import subdivide

late = subdivide(lookup("jurassic"), "late")
print(late.start.year, late.end.year)
# -161498050 -143098050
```

Those are the exact boundaries of the officially-named **Late Jurassic** —
161.5 to 143.1 million years ago — not the last 33% of the Jurassic you would
get by dividing. Looking the name up directly gives the same span:

```python
lj = lookup("late jurassic")
print(lj.span.start.year, lj.span.end.year)
# -161498050 -143098050
```

## Region-tagged archaeology: whose Bronze Age?

Human prehistory has a catch that geology does not: the same name means
*different times in different places*. The British Bronze Age and the
Mesopotamian Bronze Age are both real, both called "the Bronze Age", and
centuries apart — Mesopotamia's began far earlier. A bare name is therefore
genuinely ambiguous, so the library refuses to guess. It lists the candidates
and lets you choose by region:

```python
from chronologia import candidates

for period in candidates("bronze age"):
    print(period.region, period.span.start.year, period.span.end.year)
# GB -2499 -799
# MESO -3299 -1199
```

Ask for a bare "bronze age" with no region and the library raises an error
rather than silently picking one — choosing a locale default is *your* job, not
its:

```python
from chronologia import AmbiguousPeriodError

try:
    lookup("bronze age")
except AmbiguousPeriodError:
    british = lookup("bronze age", region="GB")
    print(british.span.start.year)
    # -2499
```

## resolve_bp: what "66 million years ago" really claims

Deep-time ages are usually written as a number "before present" (BP), where
"present" is fixed at 1950. But here is a subtlety most people miss: **the way
you write the number tells you how precise it is.**

"66 million years ago" and "66.043 million years ago" are *different claims*.
The first is rounded to the nearest million — it could really be anywhere in a
one-million-year band. The second is precise to the nearest thousand years — a
band a thousand times narrower. This is the idea of *significant figures*, and
`resolve_bp` reads it straight off the digits you type:

```python
from chronologia import resolve_bp

rough = resolve_bp("66", "Ma")        # "Ma" = millions of years
print(rough.start.year, rough.end.year)
# -65998050 -64998050

precise = resolve_bp("66.043", "Ma")
print(precise.start.year, precise.end.year)
# -66041050 -66040050
```

Look at the widths. The rough answer spans a *million* years
(−65,998,050 to −64,998,050); the precise one spans just a *thousand*
(−66,041,050 to −66,040,050). Same event — the extinction of the dinosaurs —
but the span's width honestly reflects how precisely each phrasing pins it
down. This is why you should pass the value as a **string**: `"66"` and
`"66.0"` mean different precisions, but the numbers `66` and `66.0` are
identical once Python parses them, so the text is what carries the meaning.

## Radiocarbon: why ¹⁴C years are not calendar years

You have heard of "carbon dating" — measuring the tiny amount of radioactive
carbon-14 left in something once alive to tell how old it is. Here is the part
the TV documentaries skip: **a radiocarbon age is not a calendar age.**

Carbon-14 forms in the atmosphere at a rate that has wobbled over the
millennia, so the radiocarbon "clock" runs unevenly. A lab reports a "3500 BP"
radiocarbon age, but that does *not* mean 3500 calendar years ago. To get a
real calendar date you must run the measurement through a **calibration
curve** — a painstakingly-built table (called IntCal) mapping radiocarbon
years to calendar years. `calibrate_c14` does that conversion:

```python
from chronologia import calibrate_c14

span = calibrate_c14(3500)          # 3500 radiocarbon years BP
print(span.start.year, span.end.year)
# -1950 -1850
print(span.basis)
# reconstructed
```

So a 3500 radiocarbon-year age actually points to roughly 1900 BC in calendar
terms — and the answer is a *span*, marked `reconstructed`, never a single
confident year.

**Honest caveat:** the calibration table shipped here is deliberately coarse —
sampled every hundred years, with a simple nearest-match lookup. It is a
teaching-and-locating tool that puts a radiocarbon age in the right calendar
neighbourhood. It is **not** a substitute for real radiocarbon software (such
as OxCal), which does full statistical calibration. Do not use it for actual
archaeological dating.

## Reference

| tool | what it does |
|---|---|
| `lookup(name)` / `lookup(name, region=...)` | resolve a period name (or key) to its `NamedPeriod` |
| `candidates(name)` | list every entry matching a name, across regions |
| `children(key)` | the entries one level down whose parent is `key` |
| `subdivide(target, part)` | the early/mid/late (or first-/second-half) part; a chart-defined subdivision wins over arithmetic |
| `resolve_bp(value, unit)` | a Before-Present expression as a `DateSpan` whose width is its precision (units `a`, `ka`, `Ma`, `Ga`) |
| `calibrate_c14(bp14c)` | a coarse radiocarbon-to-calendar span, `basis="reconstructed"` |
| `PERIODS` | the full registry, keyed by entry key |
| `ICS_CHART_VERSION` | the version string of the shipped chart |
| `INTCAL20_COARSE` | the coarse calibration samples used by `calibrate_c14` |

A `NamedPeriod` carries: `name`, `span` (a `DateSpan`), `level`
(`eon`/`era`/`period`/`epoch`/`age`, or `period`/`age` for archaeology),
`region` (a tag like `"GB"`, or `None` for a global name), `source`, and
`parent` (the key one level up).

```python
from chronologia import ICS_CHART_VERSION

print(ICS_CHART_VERSION)
# 2023/09
```

Both the deep-time chart and the archaeological set are `tabulated` or
`reconstructed` — never `exact`. Deep time is measured, and the spans say so.
