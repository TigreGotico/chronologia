# chronologia

<!-- agent-hint
covers: what chronologia does, how to install it, a first extraction and where each topic is documented
source: pyproject.toml, chronologia/__init__.py:__all__, chronologia/__main__.py, chronologia/extract/numlayer.py:NUMTAG_LANGS
generated: no
verify: diff <(sed -n '/^\x60\x60\x60python/,/^\x60\x60\x60$/p' README.md | sed '/^\x60\x60\x60/d;/^main(/d' | .venv/bin/python -) <(sed -n 's/^print(.*)  *# //p' README.md)
see: docs/index.md, docs/getting-started.md, AGENTS.md, CONTRIBUTING.md
-->

**chronologia is a Python library that reads dates as people write them and computes across every calendar, from the dinosaurs to next Tuesday**. It turns a phrase into the exact stretch of time it names. Examples are "the 15th of Ramadan 1446", "next winter" and "66 million years ago". It works offline, it never guesses, and it says so when history does not know the answer.

Try it: [chronologia demo Space](https://huggingface.co/spaces/TigreGotico/chronologia), which runs in the browser.

## Quick start

```bash
pip install chronologia
```

You need Python 3.11 or newer. The calendar code uses only the standard library. The reading of phrases needs two small helpers that `pip` installs with the package. **numtag** reads the numbers of 40 of the 61 languages. The table in [docs/languages/index.md](docs/languages/index.md) lists them and names the reader of each other language. **ovos-spec-tools** loads the vocabulary of each language. The `test` extra adds the test and benchmark tools.

One call turns a phrase into a span of time:

```python
from chronologia import extract_timespan
from datetime import datetime

span, _ = extract_timespan("the 15th of Ramadan 1446", "en",
                           datetime(2024, 1, 1))
print(span.start_datetime.date())   # 2025-03-15
```

A phrase names a stretch of time, not an instant. The third argument is the anchor: the moment that counts as the present for relative phrases. `extract_timespan` returns `None` when the text holds no date. Guard before you unpack text you do not control:

```python
result = extract_timespan("no date here", "en", datetime(2024, 1, 1))
if result is not None:
    span, _ = result
```

The public names are in `chronologia.__all__`. The library is in alpha. Signatures can change before a 1.0 release, so pin a version if you need stability. Read [docs/getting-started.md](docs/getting-started.md) for the three ideas that the library builds on. The index in [docs/index.md](docs/index.md) lists every guide in reading order.

## Spans, not instants

When someone says "June 2027", they mean the whole month, not one instant at midnight on the 1st. Every answer is a **span** with a start and an end. A day is a day wide and a month is a month wide. "The Jurassic" is fifty-eight and a half million years wide, and it starts about 201.6 million years ago:

```python
from chronologia import lookup

jurassic = lookup("jurassic")
print(jurassic.span.start.year)   # -201598050
print(jurassic.span.end.year)     # -143098050
```

Every span also carries a one-word label for its **basis**. The basis says how the library knows the span:

- `"exact"`: computed from an exact rule.
- `"tabulated"`: looked up in a published table. The Jurassic above is `tabulated`, because it comes from the official geological chart with its uncertainties.
- `"reconstructed"`: pieced together by historians.
- `"predicted"`: a guess about a future that nobody has decided yet.

One idea powers the rest. Every day that has ever existed gets a plain number, its **Julian Day Number**. Any of the eighteen built-in calendars can talk to any other by meeting at that number.

A word such as "morning" is also a span, and it depends on culture, not on the sun. English splits afternoon from evening at 18:00. Spanish runs one *tarde* through to 20:00:

```python
from datetime import date
from chronologia import daypart_span

tuesday = date(2027, 6, 8)
print(daypart_span(tuesday, "afternoon").end.isoformat())            # 2027-06-08T18:00:00
print(daypart_span(tuesday, "tarde", region="es").end.isoformat())  # 2027-06-08T20:00:00
```

## What it refuses to do

Some dates cannot be computed by anyone. The library does not pretend otherwise. A span's width and basis always tell the truth about what is knowable.

- **Moon-sighting months**. The religious Islamic month begins when witnesses *see* the new crescent. A future sighting has not happened. The answer is a two-day span labelled `predicted`. The *civil* calendar of Saudi Arabia is an official published table, so the library includes it as a table, as far as the table goes.
- **The Chinese calendar beyond its tables**. The Hong Kong Observatory tables make it exact from 1901 to 2099. Beyond that the true calendar needs astronomy, so the library stops.
- **Calendars that nobody controlled**. Before Julius Caesar, Roman priests added days for political reasons. No software can recover decisions that were never rules. The library supports the reconstructions of historians as reconstructions, with their uncertainty in view.
- **Dates that do not exist**. "29 February 2017" returns `None`, not 1 March. Pass `impossible="raise"` to get an `ImpossibleDateError` that names the reason.

## What each guide covers

| Topic | What you get | Guide |
|---|---|---|
| Who is this for? | Worked programs for archivists, historians, archaeologists, faith communities, astronomers, engineers and voice assistants. Start here. | [use-cases](docs/use-cases.md) |
| Reading human dates | `extract_timespan` turns a phrase into a span. Also durations, recurrences, candidates with character offsets, and how the vocabulary of a language works. | [extraction](docs/extraction.md) |
| Calendars | Eighteen calendars beside the Gregorian: Julian, Revised Julian, Hebrew, Islamic, Solar Hijri, Chinese (1901 to 2099), Coptic, Ethiopian, Armenian, Berber, ancient Egyptian, Maya Long Count, French Republican, Bahá'í and ISO week. The Islamic calendar has an arithmetic form and the Saudi Umm al-Qura table. | [calendars](docs/calendars.md) |
| Calendar reforms | Thirteen timelines: Rome, Britain, Sweden, Russia, Greece, Japan, and the days that Samoa, the Philippines and Alaska deleted or lived twice. Ask for a deleted day and you get a typed `NeverExisted`. | [timelines](docs/timelines.md) |
| Deep time | The geological chart (170 entries) and ten regional archaeological ages. A British Late Bronze Age is not a Mesopotamian one. Radiocarbon ages calibrate through the published curve. | [deep-time](docs/deep-time.md) |
| Eras and rulers | BC/CE, Anno Mundi, Byzantine and Hijri years, Holocene, Unix time, Julian Day and Before Present. Regnal years: nengō, Roman consuls and three Egyptian chronologies. Roman Kalends, Nones and Ides in twelve locales. | [eras-and-rulers](docs/eras-and-rulers.md) |
| Recurrence | RFC 5545 RRULE: "every third Tuesday", Labor Day, Friday the 13th. A rule that names a date no year has raises an error. | [recurrence](docs/recurrence.md) |
| Events | A spoken sentence into a calendar entry, and iCalendar files in both directions. | [events](docs/events.md) |
| Civil holidays | Holidays for 260 jurisdictions as computed rules with observed-shift policies. 32 of them carry subdivisions, and Portugal goes down to municipal depth (about 300 concelhos). | [civil-holidays](docs/civil-holidays.md) |
| Sun, moon and seasons | Sunrise, sunset, twilights, unequal hours and prayer times. Moon phases, solstices and equinoxes. Local mean time, leap seconds and the French Revolution's 10-hour clock. | [sun-moon-and-seasons](docs/sun-moon-and-seasons.md) |
| Timezones | Any `zoneinfo` zone as a timeline, with fall-back and spring-forward handled as typed answers. | [timezones](docs/timezones.md) |
| Beyond Earth | Mars Sol Date, Coordinated Mars Time and the Darian calendar. Cosmology: a Big Bang epoch as a span, the Hubble tension and Sagan's Cosmic Calendar. | [mars-and-beyond](docs/mars-and-beyond.md) |
| Comparison | A differential benchmark against `dateparser` and `dateutil` on the hand-derived corpora of the repository. | [benchmarks](docs/benchmarks.md) |

The [`examples/`](examples/) directory holds eight self-checking scripts. Run one with `python examples/01_extract_basics.py`.

Every algorithm and every number in the data files comes from a cited published source. The citations sit in the module docstrings and the data-file headers. Where sources disagree, both versions ship under different names. Where sources are silent, the library says so.

## Command line

The package installs a `chronologia` command. You can also run `python -m chronologia`. Each subcommand prints one line:

```bash
chronologia convert 2024-06-01 --to hebrew        # gregorian 2024-06-01 = hebrew 5784-02-24
chronologia extract "last summer"                 # -> [..., ...) (year)
chronologia holidays US 2024                       # one date + name per line
chronologia easter 2024                            # Easter 2024 (gregorian): 2024-03-31
chronologia when 1984-06?                          # -> [1984-06-01..., 1984-07-01...) [?]
```

A script or test can call the same entry point in-process. Give `main` an argument list. It prints to stdout and returns an exit code:

```python
from chronologia.__main__ import main

main(["easter", "2024"])                # prints: Easter 2024 (gregorian): 2024-03-31
main(["convert", "2024-06-01", "--to", "coptic"])
main(["when", "1984-06?"])
```

Years before the common era need argparse's `--` separator, so the leading `-` is not read as a flag: `chronologia convert --from julian --to gregorian -- -0043-03-15`.

## How well does it speak your language?

Sixty-one languages load. They are not all tested to the same depth, and three bands say how deep.

**Reviewed in depth:** English, Spanish, Portuguese, French, German, Dutch, Russian, Arabic and Hebrew. Each has a large phrase corpus that covers everyday speech, not only textbook forms: "quarter to four", "tonight at 8", "om de twee weken", "без пяти девять". Expect these languages to handle what a person types.

**Broadly covered:** Italian, Polish, Czech, Slovak, Slovenian, Croatian, Bulgarian, Ukrainian, Swedish, Danish, Norwegian (Bokmål and Nynorsk), Finnish,
Estonian, Hungarian, Greek, Turkish, Azerbaijani, Persian, Indonesian, Malay, Catalan, Galician, Romanian, Basque and Frisian. Each has its own test corpus. The tests run again whenever a shared mechanism changes, so the common constructions work. The idiomatic long tail is thinner, and bug reports help most there.

**Early:** Albanian, Aragonese, Armenian, Asturian, Belarusian, Bengali, Esperanto, Filipino, Georgian, Hausa, Hindi, Icelandic, Irish, Kabyle,
Korean, Latvian, Lithuanian, Macedonian, Maltese, Mirandese, Occitan, Serbian, Swahili, Tamil, Thai, Vietnamese and Welsh. The vocabulary is in place and the engine is shared, so a lot already works. No native speaker has read these languages end to end. Several omit constructions that their source grammars do not use in the same way:

- Welsh has no seasons and no millennium unit.
- Irish and Esperanto have no day parts.
- Georgian has no century unit and no "every" quantifier. Armenian omits several markers.
- Macedonian has no minutes-to-the-hour clock, because its own style guides count only forward from the hour.
- Swahili refuses its sunrise-counted clock. Hausa shows no such ambiguity, so it reads its spoken hour.
- Thai refuses a bare "N โมง" hour, because nothing in the phrase says which half of the day it names.
- Korean ships no single-syllable weekday abbreviations, because each one is also an everyday word (일 is the day, the numeral one and Sunday at once). It ships no spelled month names.
- Vietnamese reads no ordinals and no bare "năm" as five.

Occitan shows how a locale deepens. A native speaker reviewed its word lists, and "davant-ièr" reads as the day before yesterday.

These omissions are the design at work. A locale ships a construction only where its sources attest one. Where the sources conflict or say nothing, the phrase returns nothing, because a wrong span is worse than no span. To tell a deliberate refusal from a bug, read [when a language declines a phrase](docs/extraction.md#when-a-language-declines-a-phrase).

Suppose your language is in the second or third band and a phrase reads wrong. Report the phrase, what you expected and what you got. The [contributing guide](CONTRIBUTING.md) explains how a language gets deeper. The guide [adding a language](docs/adding-a-language.md) is the full walk-through for another language.

## How correctness is checked

AI wrote and orchestrated chronologia, and a human maintainer directs and reviews it. No single maintainer speaks all 61 languages, so the method has to carry the correctness. Every algorithm comes from a named source. Every gold test value comes from hand arithmetic or an independent source, never from the code under test.

Where no citable source exists, the library refuses and documents the gap. Each language has a corpus of real phrases with hand-derived spans. A parity test checks every language against English span for span. [docs/transparency.md](docs/transparency.md) lists the checks.

## Related projects

- **[ovos-date-parser](https://github.com/OpenVoiceOS/ovos-date-parser)** is the voice-facing layer. It builds on chronologia and adds what an assistant needs: saying a date aloud and session handling.
- **[numtag](https://github.com/TigreGotico/numtag)** finds every number in a text. It returns typed mentions with their spans and exact values. chronologia reads the numbers of 40 languages through it.
- **[ovos-spec-tools](https://github.com/OpenVoiceOS/ovos-spec-tools)** implements the OVOS formal specifications (template expander, locale loader, dialog renderer, language matcher, linter). chronologia loads its vocabulary files through it.

## License

Apache-2.0 © TigreGotico
