# Slovenian (`sl`)

<!-- agent-hint
covers: where each construction of the Slovenian locale comes from, what it refuses and which questions a native speaker would settle
source: `chronologia/locale/sl/lang.json`, `chronologia/locale/sl/*.voc`, `chronologia/extract/numlayer.py:NUMTAG_LANGS`
generated: no
verify: python -m doctest docs/languages/sl.md
see: `docs/languages/index.md`, `docs/extraction.md`
-->

This page records where each construction of the Slovenian (`sl`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

Slovenian tells the half hour the way a reader coming from English would not
expect: `pol devetih` is 8:30, not 9:30 — "half toward nine", counting
forward to the hour that has not arrived yet rather than back from the one
that has passed. The hour in that phrase is a *declined* cardinal rather
than a bare one — `devetih` is the genitive/locative plural of `devet`
("nine"). numtag reads it as 9 and reads `pol` as a fraction, and the fold
keeps `pol` a word, so the clock reads the fraction and the hour apart.

## What ships

**The date line** is little-endian, `DAY MONTH YEAR?`, matching the CLDR 47
`ca-gregorian` chart for `sl` at every level — full `EEEE, d. MMMM y`, long
`d. MMMM y`, medium `d. MMM y`, short `d. M. yy`. `lang.json` also accepts a
month-led order (`maj 3. 2017`) alongside the day-led one.

**Weekdays and months** ship in the nominative and one oblique form each —
`ponedeljek`/`ponedeljka`, `januar`/`januarja`/`januarju`/`januarjem` — with
no recorded source for which case each oblique form serves; see Weaker
provenance.

**Day parts** are transcribed from the Unicode CLDR 47 day-period rules for
`sl`, each shipping as the deictic adverb a phrase actually uses rather than
a dictionary citation form: `zjutraj` (morning, Wiktionary `zjutraj`),
`popoldan`/`popoldne` (afternoon, two live spellings, Wiktionary
`popoldne`), `zvečer` (evening, Wiktionary `zvečer`), `ponoči` (night,
Wiktionary `ponoči`). The same adverbs double as clock meridiem cues on an
explicit hour — `zjutraj` for AM, `popoldne`/`zvečer` for PM.

**Relative offsets** are `pred` (ago/before) and `po` (after), each
ordinarily governing the ablative/locative case in running Slovenian, though
no case-form citation is recorded for either preposition beyond the bare
headword; see Weaker provenance.

**Determiners.** `prejšnji`/`prejšnjega`/`prejšnjemu`/`prejšnjem`/
`prejšnjim`/`prejšnja`/`prejšnje`/`prejšnjo`/`prejšnjih`/`prejšnjimi`
("last/previous") ship in the full adjectival paradigm across all three
genders that the three temporal units this locale needs actually span —
masculine `teden` (week), masculine `mesec` (month), neuter `leto` (year) —
cited to Fran (ZRC SAZU), *SSKJ2* / *Slovenski pravopis*, s.v. `prejšnji`.
`pretekli`/`preteklega`/.../`preteklo`/`preteklih` ships as a synonym stem.
`naslednji` and `prihodnji` ("next/following"), each in the same full
paradigm, are cited to the same dictionary, s.v. `naslednji`. Both match
CLDR 47 `sl` `dateFields.json`'s week-field relative types directly:
relative-type--1 is `prejšnji teden`, relative-type-1 is `naslednji teden`.
The year field is the one CLDR does not compose from these determiners at
all — relative-type--1 is the irregular `lani`, not `prejšnje leto` — and
that irregular is not shipped; see What refuses.

**"This"** ships in the full pronominal paradigm — `ta`/`tega`/`temu`/
`tem`/`te`/`tej`/`to`/`ti`/`teh`/`temi` — cited to Fran (ZRC SAZU), *SSKJ2*,
s.v. `ta`.

**Landmarks** are `polnoč` (midnight) and `poldne` (noon).

**The clock's toward-hour half.** `pol` ("half") plus the genitive/locative
plural of the coming hour's cardinal is the locale's only fractional clock
surface, gated by `bare_half_to: true` and `toward_hour_12h: true` in
`lang.json` and a dedicated `at? FRACTION HOUR MERIDIEM? ZONE?` clock order.
`clock_fraction_30.voc` cites ZRC SAZU's Jezikovna svetovalnica (Fran/ISJFR),
telling the time — `pol` plus the declined hour counts toward the coming
hour — and a second, independent web guide (ling-app.com's Slovenian time
guide) corroborates the direction with a worked example of its own: "if the
clock reads 1:30, you would say it's half two, or *pol dve*". That guide's
citation form is the nominative `pol dve`, and both it and the declined
`pol dveh` resolve to 01:30. The project's own test
corpus checks the pattern against independent arithmetic across five hours
(`pol devetih` → 08:30, `pol desetih` → 09:30, `pol osmih` → 07:30, `ob pol
enih` → 12:30, `pol dvanajstih` → 11:30) and separately asserts that a bare
`pol` with no following hour is not a clock reading at all.

**`pol` stays a word.** numtag reads the Slovenian numbers in every case
form (`numlayer_slavic.py`), and it reads `pol` as the fraction 0.5. The fold
keeps a fraction that numtag reads as a fraction as a word, so the clock
reads `pol devetih`, and `lang.json`'s `quantifiers` table maps
`"0.5": ["pol"]` for the duration `pol ure`. numtag reads the declined hours
`devetih`, `desetih` and `osmih`; it does not read `enih`, so the fold reads
`enih` through the nominative `ena`.

**Quarters, ISO weeks, decades and centuries** resolve: `četrtletje`/
`kvartal`/`kvartala` (quarter, two registers), `teden` (ISO week), no
recorded source for either.

**Named days** span `predvčerajšnjim` (the day before yesterday), `včeraj`
(yesterday), `jutri` (tomorrow), `pojutrišnjem` (the day after tomorrow).

**Numerals** are read by numtag rather than a per-locale vocabulary file,
exactly as in Bulgarian; Slovenian has no dedicated numeral `.voc` files.

## Weaker provenance

**The oblique weekday and month forms** (`ponedeljka`, `januarja`,
`januarju`, `januarjem`) ship with no citation recording which case each
serves or whether the set is complete — genitive, locative and instrumental
are the likely candidates given Slovenian's six-case system, but nothing on
file confirms that against a declension table.

**`pred` and `po`** ship as bare headwords with no case-government citation,
though both are used throughout the corpus in phrases that plainly expect a
specific case on the following noun.

**`četrtletje`/`kvartal`** ship as unqualified synonyms with no source
distinguishing register the way the Bulgarian page's equivalent pair does
not either.

## What refuses

**`lani` for "last year".** CLDR 47 `sl` `dateFields.json` gives the
irregular `lani` for relative-type--1 on the year field, not a composed
`prejšnje leto`. `lani` is not in the vocabulary and a phrase built on it
does not parse; only the regular `prejšnje leto` (built compositionally from
the shipped determiner plus the shipped noun) resolves.

**Minutes counted to or past the hour.** `pol` toward the hour is the only
fractional clock surface the locale ships, and a minute count wrapped around
it is silently discarded rather than refused: `pet čez pol devetih` ("five
past half nine") resolves to 08:30 with `pet čez` left in the remainder, so
the five minutes vanish without the phrase failing. The plain minute counts
an ordinary speaker uses — `dvajset čez štiri` (4:20), `pet do enajstih`
(10:55) — do not resolve at all.

## Open questions for a native speaker

1. Should `lani` ship as an irregular alternative to `prejšnje leto` for
   "last year", given that CLDR treats it as the primary form rather than a
   variant?
2. What case do the oblique weekday and month forms actually mark, and is
   the set of forms shipped for each complete?
3. Are `četrtletje` and `kvartal` genuinely interchangeable for "quarter",
   or does one carry a fiscal or bureaucratic connotation the other lacks?
4. Does `pretekli` compete evenly with `prejšnji` for "last/previous" in
   ordinary registers, or is one clearly dominant?


---
[← Slovak](sk.md) · [Home](../index.md) · [Spanish →](es.md)

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("sl")
    True
    >>> span, rest = extract_timespan('pol devetih', "sl", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T08:30:00', '')
    >>> span, rest = extract_timespan('prejšnji teden', "sl", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-19T00:00:00', '')
    >>> span, rest = extract_timespan('naslednji teden', "sl", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-07-03T00:00:00', '')
    >>> span, rest = extract_timespan('prejšnje leto', "sl", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2016-01-01T00:00:00', '')

---
[← Slovak](sk.md) · [Home](../index.md) · [Spanish →](es.md)
