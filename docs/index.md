# chronologia documentation

<!-- agent-hint
covers: every documentation page in reading order, with what each gives the reader
source: docs/, examples/
generated: no
verify: diff <(cd docs && ls *.md languages/*.md | grep -v '^index.md$' | sort) <(grep -o '^| \[[^]]*\]([^)]*\.md)' docs/index.md | sed 's/.*](\(.*\))/\1/' | sort)
see: README.md, docs/getting-started.md, docs/languages/index.md
-->

**chronologia** is a Python library that does two jobs. It *reads* a date the way a human wrote it ("the 15th of Ramadan 1446", "next winter", "66 million years ago"). It *computes* across every calendar and system of reckoning that people have used. It works offline, it does not guess, and it says what it cannot know.

**Two ways in. Pick your track:**

- **First time here, and want a quick result**. Go to [getting-started.md](getting-started.md). It gives a first extraction to copy, six common recipes and the three ideas that everything builds on. Then browse [use-cases.md](use-cases.md) for worked programs in your field.
- **Building on the library, and want the full surface**. Start with [design.md](design.md). It covers the JDN hub, the four value types, the scope boundaries, and what the library refuses to do and why. Then read any reference guide below. You import the public API straight from `chronologia`. The end of [getting-started.md](getting-started.md) lists the toolbox.

Three terms recur in every guide. A **span** is a stretch of time with a start and an end, not an instant. Every span carries a one-word **basis** that says how far to trust it: `exact`, `tabulated`, `reconstructed` or `predicted`. The engine converts everything through the **Julian Day Number (JDN)**, a single integer that names each day on an endless number line.

## The guides, grouped

### Orientation
| Guide | What it gives you |
|---|---|
| [use-cases.md](use-cases.md) | Worked programs for archivists, historians, archaeologists, faith communities, astronomers, engineers, and voice assistants. The best first read. |
| [getting-started.md](getting-started.md) | The three primitives, the JDN number line, the `AstroDate` point, and the `DateSpan` interval, taught from zero. |

### Reading dates written by humans
| Guide | What it gives you |
|---|---|
| [extraction.md](extraction.md) | `extract_timespan` turns a phrase into the span it means. Also durations, recurrences, ranked candidates with character offsets, impossible dates, and how the per-language vocabulary works. Shows what a locale declines to read. |
| [adding-a-language.md](adding-a-language.md) | A step-by-step guide to teaching chronologia another language, written so a bilingual non-programmer can follow it. |
| [events.md](events.md) | Pulling a titled event (summary + time) out of a sentence and exporting it as an `.ics` calendar file. |
| [recurrence.md](recurrence.md) | Repeating rules ("every third Tuesday") in the RFC 5545 RRULE grammar, expanded to concrete dates. Shows which rules the library refuses. |
| [edtf.md](edtf.md) | Extended Date/Time Format, cataloguing-style approximate and uncertain dates ("probably the 1890s"). |
| [rulings.md](rulings.md) | The decisions that fix how the library reads a phrase with two possible readings: which occurrence, which hour, which period. Each has examples and sources. |

### Calendars & eras
| Guide | What it gives you |
|---|---|
| [calendars.md](calendars.md) | All 18 built-in calendars in plain language, how to convert in and out, and how far each can be trusted. |
| [eras-and-rulers.md](eras-and-rulers.md) | Year-numbering conventions (Anno Mundi, Hijri, Holocene…), regnal years (Japanese nengō, Roman consuls, Egyptian chronologies), and the full Roman date grammar. |

### Time, sun & sky
| Guide | What it gives you |
|---|---|
| [sun-moon-and-seasons.md](sun-moon-and-seasons.md) | Natural time. Sunrise, sunset and the twilights, unequal hours, prayer times, moon phases, solstices, equinoxes and seasons. Local mean time, the decimal clock, dayparts and leap seconds. |

### Timezones & timelines
| Guide | What it gives you |
|---|---|
| [timezones.md](timezones.md) | The political clock: daylight-saving folds and gaps, wall-clock arithmetic, and reading any `zoneinfo` zone as a timeline of discontinuities. |
| [timelines.md](timelines.md) | Calendar reforms and date-line hops: the ten days deleted in 1582, Sweden's February 30th, the October Revolution, Samoa's lost Friday. |

### Deep time & cosmology
| Guide | What it gives you |
|---|---|
| [deep-time.md](deep-time.md) | Geological and archaeological periods, "Before Present" ages, and radiocarbon calibration, honest to the megayear. |
| [mars-and-beyond.md](mars-and-beyond.md) | Mars Sol Date, the Darian calendar, lunar cycles, a span-valued Big Bang epoch, and Sagan's Cosmic Calendar. |

### Holidays
| Guide | What it gives you |
|---|---|
| [civil-holidays.md](civil-holidays.md) | Public, regional and municipal holidays for 260 jurisdictions, computed from published rules. Outside the range of a decree table, the guide shows the `predicted` basis and the strict mode that omits the date. |

### Reference & meta
| Guide | What it gives you |
|---|---|
| [design.md](design.md) | The developer's tour: the JDN hub, the type system, and, importantly, what the library refuses to do and why. |
| [benchmarks.md](benchmarks.md) | The differential benchmark against `dateparser` and `dateutil` on the natural-language corpora of the repository. Also the cross-view harness that compares two trees. |
| [transparency.md](transparency.md) | The checks that decide whether the library's answers are right, and the provenance tiers of the holiday gold values. |

### Language provenance pages
| Guide | What it gives you |
|---|---|
| [languages/index.md](languages/index.md) | How each language page is organised, and which reader handles the numbers of each of the 61 locales. |
| [languages/sq.md](languages/sq.md) | The sources, the weaker evidence and the refusals of the Albanian (`sq`) locale. |
| [languages/ar.md](languages/ar.md) | The sources, the weaker evidence and the refusals of the Arabic (`ar`) locale. |
| [languages/an.md](languages/an.md) | The sources, the weaker evidence and the refusals of the Aragonese (`an`) locale. |
| [languages/hy.md](languages/hy.md) | The sources, the weaker evidence and the refusals of the Armenian (`hy`) locale. |
| [languages/ast.md](languages/ast.md) | The sources, the weaker evidence and the refusals of the Asturian (`ast`) locale. |
| [languages/az.md](languages/az.md) | The sources, the weaker evidence and the refusals of the Azerbaijani (`az`) locale. |
| [languages/eu.md](languages/eu.md) | The sources, the weaker evidence and the refusals of the Basque (`eu`) locale. |
| [languages/be.md](languages/be.md) | The sources, the weaker evidence and the refusals of the Belarusian (`be`) locale. |
| [languages/bn.md](languages/bn.md) | The sources, the weaker evidence and the refusals of the Bengali (`bn`) locale. |
| [languages/bg.md](languages/bg.md) | The sources, the weaker evidence and the refusals of the Bulgarian (`bg`) locale. |
| [languages/ca.md](languages/ca.md) | The sources, the weaker evidence and the refusals of the Catalan (`ca`) locale. |
| [languages/hr.md](languages/hr.md) | The sources, the weaker evidence and the refusals of the Croatian (`hr`) locale. |
| [languages/cs.md](languages/cs.md) | The sources, the weaker evidence and the refusals of the Czech (`cs`) locale. |
| [languages/da.md](languages/da.md) | The sources, the weaker evidence and the refusals of the Danish (`da`) locale. |
| [languages/nl.md](languages/nl.md) | The sources, the weaker evidence and the refusals of the Dutch (`nl`) locale. |
| [languages/en.md](languages/en.md) | The sources, the weaker evidence and the refusals of the English (`en`) locale. |
| [languages/eo.md](languages/eo.md) | The sources, the weaker evidence and the refusals of the Esperanto (`eo`) locale. |
| [languages/et.md](languages/et.md) | The sources, the weaker evidence and the refusals of the Estonian (`et`) locale. |
| [languages/fil.md](languages/fil.md) | The sources, the weaker evidence and the refusals of the Filipino (`fil`) locale. |
| [languages/fi.md](languages/fi.md) | The sources, the weaker evidence and the refusals of the Finnish (`fi`) locale. |
| [languages/fr.md](languages/fr.md) | The sources, the weaker evidence and the refusals of the French (`fr`) locale. |
| [languages/gl.md](languages/gl.md) | The sources, the weaker evidence and the refusals of the Galician (`gl`) locale. |
| [languages/ka.md](languages/ka.md) | The sources, the weaker evidence and the refusals of the Georgian (`ka`) locale. |
| [languages/de.md](languages/de.md) | The sources, the weaker evidence and the refusals of the German (`de`) locale. |
| [languages/el.md](languages/el.md) | The sources, the weaker evidence and the refusals of the Greek (`el`) locale. |
| [languages/ha.md](languages/ha.md) | The sources, the weaker evidence and the refusals of the Hausa (`ha`) locale. |
| [languages/he.md](languages/he.md) | The sources, the weaker evidence and the refusals of the Hebrew (`he`) locale. |
| [languages/hi.md](languages/hi.md) | The sources, the weaker evidence and the refusals of the Hindi (`hi`) locale. |
| [languages/hu.md](languages/hu.md) | The sources, the weaker evidence and the refusals of the Hungarian (`hu`) locale. |
| [languages/is.md](languages/is.md) | The sources, the weaker evidence and the refusals of the Icelandic (`is`) locale. |
| [languages/id.md](languages/id.md) | The sources, the weaker evidence and the refusals of the Indonesian (`id`) locale. |
| [languages/ga.md](languages/ga.md) | The sources, the weaker evidence and the refusals of the Irish (`ga`) locale. |
| [languages/it.md](languages/it.md) | The sources, the weaker evidence and the refusals of the Italian (`it`) locale. |
| [languages/kab.md](languages/kab.md) | The sources, the weaker evidence and the refusals of the Kabyle (`kab`) locale. |
| [languages/ko.md](languages/ko.md) | The sources, the weaker evidence and the refusals of the Korean (`ko`) locale. |
| [languages/lv.md](languages/lv.md) | The sources, the weaker evidence and the refusals of the Latvian (`lv`) locale. |
| [languages/lt.md](languages/lt.md) | The sources, the weaker evidence and the refusals of the Lithuanian (`lt`) locale. |
| [languages/mk.md](languages/mk.md) | The sources, the weaker evidence and the refusals of the Macedonian (`mk`) locale. |
| [languages/ms.md](languages/ms.md) | The sources, the weaker evidence and the refusals of the Malay (`ms`) locale. |
| [languages/mt.md](languages/mt.md) | The sources, the weaker evidence and the refusals of the Maltese (`mt`) locale. |
| [languages/mwl.md](languages/mwl.md) | The sources, the weaker evidence and the refusals of the Mirandese (`mwl`) locale. |
| [languages/nb.md](languages/nb.md) | The sources, the weaker evidence and the refusals of the Norwegian Bokmål (`nb`) locale. |
| [languages/nn.md](languages/nn.md) | The sources, the weaker evidence and the refusals of the Norwegian Nynorsk (`nn`) locale. |
| [languages/oc.md](languages/oc.md) | The sources, the weaker evidence and the refusals of the Occitan (`oc`) locale. |
| [languages/fa.md](languages/fa.md) | The sources, the weaker evidence and the refusals of the Persian (`fa`) locale. |
| [languages/pl.md](languages/pl.md) | The sources, the weaker evidence and the refusals of the Polish (`pl`) locale. |
| [languages/pt.md](languages/pt.md) | The sources, the weaker evidence and the refusals of the Portuguese (`pt`) locale. |
| [languages/ro.md](languages/ro.md) | The sources, the weaker evidence and the refusals of the Romanian (`ro`) locale. |
| [languages/ru.md](languages/ru.md) | The sources, the weaker evidence and the refusals of the Russian (`ru`) locale. |
| [languages/sr.md](languages/sr.md) | The sources, the weaker evidence and the refusals of the Serbian (`sr`) locale. |
| [languages/sk.md](languages/sk.md) | The sources, the weaker evidence and the refusals of the Slovak (`sk`) locale. |
| [languages/sl.md](languages/sl.md) | The sources, the weaker evidence and the refusals of the Slovenian (`sl`) locale. |
| [languages/es.md](languages/es.md) | The sources, the weaker evidence and the refusals of the Spanish (`es`) locale. |
| [languages/sw.md](languages/sw.md) | The sources, the weaker evidence and the refusals of the Swahili (`sw`) locale. |
| [languages/sv.md](languages/sv.md) | The sources, the weaker evidence and the refusals of the Swedish (`sv`) locale. |
| [languages/ta.md](languages/ta.md) | The sources, the weaker evidence and the refusals of the Tamil (`ta`) locale. |
| [languages/th.md](languages/th.md) | The sources, the weaker evidence and the refusals of the Thai (`th`) locale. |
| [languages/tr.md](languages/tr.md) | The sources, the weaker evidence and the refusals of the Turkish (`tr`) locale. |
| [languages/uk.md](languages/uk.md) | The sources, the weaker evidence and the refusals of the Ukrainian (`uk`) locale. |
| [languages/vi.md](languages/vi.md) | The sources, the weaker evidence and the refusals of the Vietnamese (`vi`) locale. |
| [languages/cy.md](languages/cy.md) | The sources, the weaker evidence and the refusals of the Welsh (`cy`) locale. |
| [languages/fy.md](languages/fy.md) | The sources, the weaker evidence and the refusals of the West Frisian (`fy`) locale. |

## Runnable examples

The [`examples/`](../examples/) directory is a hands-on companion to these guides, eight self-contained scripts, each printing readable output you can follow line by line. Run any of them with `python examples/<name>.py`:

| Script | Teaches |
|---|---|
| `01_extract_basics.py` | Turning a phrase into a span. Anchor and remainder. |
| `02_languages.py` | The same query across eight languages, including right-to-left Arabic and Hebrew. |
| `03_holidays.py` | Holiday queries by jurisdiction, subdivision and category. |
| `04_recurrence_and_events.py` | Recurring rules and exporting an event to iCalendar. |
| `05_durations_and_mentions.py` | Bare durations, and locating every date in a sentence by character offset. |
| `06_calendars_deep_time.py` | Non-Gregorian calendars, dates BC, and deep time. |
| `07_business_days.py` | Composing a working-day policy from the library's holiday facts. |
| `08_confidence.py` | Ranked candidate readings for an ambiguous phrase. |
