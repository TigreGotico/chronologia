# chronologia documentation

Welcome. **chronologia** is a Python library that does two things most projects
need two libraries for: it *reads* a date the way a human wrote it ("the 15th of
Ramadan 1446", "next winter", "66 million years ago"), and it *computes* across
every calendar and system of reckoning humanity has used — offline, without
guessing, and honest about what cannot be known.

This page is a map. You do not have to read the guides in order, but the order
below is the gentlest path from "never seen it" to "building on it". A few terms
recur everywhere and are worth meeting once: a **span** is a stretch of time
(a start and an end), not an instant; every span carries a one-word **basis**
saying how trustworthy it is (`exact`, `tabulated`, `reconstructed`,
`predicted`); and the whole engine converts through the **Julian Day Number
(JDN)** — a single integer naming each day on an endless number line.

## Suggested reading order

### 1. Start here
| Guide | What it gives you |
|---|---|
| [use-cases.md](use-cases.md) | Worked programs for archivists, historians, archaeologists, faith communities, astronomers, engineers, and voice assistants. If you are not sure the library is for you, read this first. |
| [getting-started.md](getting-started.md) | The three ideas the whole library is built from — the JDN number line, the `AstroDate` point, and the `DateSpan` interval — taught from zero. |

### 2. Reading dates written by humans
| Guide | What it gives you |
|---|---|
| [extraction.md](extraction.md) | `extract_timespan` — turn a phrase into the exact span it means; how the per-language vocabulary works, and how to add a language. |
| [events.md](events.md) | Pulling a titled event (summary + time) out of a sentence and exporting it as an `.ics` calendar file. |
| [recurrence.md](recurrence.md) | Repeating rules ("every third Tuesday") via the RFC 5545 RRULE grammar, expanded to concrete dates. |
| [edtf.md](edtf.md) | Extended Date/Time Format — cataloguing-style approximate and uncertain dates ("probably the 1890s"). |

### 3. Calendars and how years are counted
| Guide | What it gives you |
|---|---|
| [calendars.md](calendars.md) | All 17 built-in calendars in plain language, how to convert in and out, and how far each can be trusted. |
| [eras-and-rulers.md](eras-and-rulers.md) | Year-numbering conventions (Anno Mundi, Hijri, Holocene…), regnal years (Japanese nengō, Roman consuls), and full Roman date grammar. |
| [timelines.md](timelines.md) | Calendar reforms and date-line hops: the ten days deleted in 1582, Sweden's February 30th, the October Revolution. |

### 4. Deep time and the sky
| Guide | What it gives you |
|---|---|
| [deep-time.md](deep-time.md) | Geological and archaeological periods, "Before Present" ages, and radiocarbon calibration — honest to the megayear. |
| [mars-and-beyond.md](mars-and-beyond.md) | Mars Sol Date, the Darian calendar, lunar cycles, and a span-valued Big Bang epoch. |

### 5. Time inside a day
| Guide | What it gives you |
|---|---|
| [time-and-zones.md](time-and-zones.md) | Daylight-saving folds and gaps, leap seconds, historical local mean solar time, pre-clock unequal hours. |
| [timezones.md](timezones.md) | How the library reads any `zoneinfo` zone as a timeline of discontinuities. |

### 6. Holidays
| Guide | What it gives you |
|---|---|
| [civil-holidays.md](civil-holidays.md) | Public, regional, and municipal holidays computed from published rules, per jurisdiction, with honest `tabulated` basis and honest omission outside a table's range. |

### 7. Under the hood
| Guide | What it gives you |
|---|---|
| [design.md](design.md) | The developer's tour: the JDN hub, the type system, and — importantly — what the library refuses to do and why. |
| [benchmarks.md](benchmarks.md) | The standing differential benchmark against `dateparser` and `dateutil` on the repo's own natural-language corpora. |
| [transparency.md](transparency.md) | An honest account of how the library was built, failures included. |

## Runnable examples

The [`examples/`](../examples/) directory is a hands-on companion to these
guides — eight self-contained scripts, each printing readable output you can
follow line by line. Run any of them with `python examples/<name>.py`:

| Script | Teaches |
|---|---|
| `01_extract_basics.py` | Turning a phrase into a span; anchor and remainder. |
| `02_languages.py` | The same query across eight languages, including right-to-left Arabic and Hebrew. |
| `03_holidays.py` | Holiday queries by jurisdiction, subdivision, and category. |
| `04_recurrence_and_events.py` | Recurring rules and exporting an event to iCalendar. |
| `05_durations_and_mentions.py` | Bare durations, and locating every date in a sentence by character offset. |
| `06_calendars_deep_time.py` | Non-Gregorian calendars, dates BC, and deep time. |
| `07_business_days.py` | Composing a working-day policy from the library's holiday facts. |
| `08_confidence.py` | Ranked candidate readings for an ambiguous phrase. |
