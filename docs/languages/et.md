# Estonian (`et`)

Estonian's spoken clock counts toward the hour that has not arrived yet, the
same direction as Slovenian and unrelated to it — `pool üheksa` is 8:30, not
9:30, and the same counting-toward logic extends to quarters: `veerand
üheksa` is 8:15 and `kolmveerand üheksa` is 8:45. That three-way fraction
system rests on a numeral-folding pass that has to read a case system the
parser's own cardinal words do not carry.

## What ships

**The date line** is little-endian. `lang.json` lists `calendar_date` in
`base_grammar.disable` and defines its own in its place, with the orders
`DAY MONTH YEAR?` and `MONTH DAY? YEAR?` — day-led first, month-led as the
fallback — matching the CLDR 47 `ca-gregorian` chart for `et` at every
level: full `EEEE, d. MMMM y`, long `d. MMMM y`, medium `d. MMM y`, short
`dd.MM.yy`.
Estonian spells the day of month with a single-word ordinal the cardinal
number model does not read as a number at all (`viieteistkümnes aprill`,
"the fifteenth of April"); a tens-prefix pre-pass merges a spoken compound
tens ordinal into one day token before the fold reads it, mirroring the
equivalent Slavic-family pre-pass. `pronounce_ordinal_et` supplies the day
values 1–20 and 30 as one word each and the compound tens 21–29/31 as two
words, so the whole ordinal range is derived from the shared number model
rather than a per-locale vocabulary file.

**Weekdays and months** ship in the nominative plus the adessive case that
"on Monday" / "in May" phrases use — `esmaspäev`/`esmaspäeval`,
`jaanuar`/`jaanuari`/`jaanuaris`/`jaanuaril`, `mai`/`maikuu`/`mais`/`mail` —
with no recorded citation for the case choice beyond the surfaces
themselves being attested by the project's own date-sweep test corpus
(`test_et_full_date_sweep.py`, `test_et_month_year_sweep.py`).

**Day parts** are transcribed from the Unicode CLDR 47 day-period rules for
`et`, each shipping as the adessive adverb a phrase actually uses:
`hommikul` (morning, Wiktionary `hommik`, adessive `hommikul`),
`pärastlõunal` (afternoon, EKI Sõnaveeb `pärastlõuna`), `õhtul` (evening,
Wiktionary `õhtu`, adessive `õhtul`), `öösel` (night, Wiktionary `öö`,
adessive `öösel`). The same adverbs double as clock meridiem cues on an
explicit hour, alongside the abbreviations `e.l.` (AM, "enne lõunat",
before noon) and `p.l.` (PM, "pärast lõunat", after noon).

**Landmarks** are `kesköö`/`keskööl` (midnight, bare and adessive) and
`keskpäev`/`keskpäeval`/`lõuna` (noon, two live surfaces).

**The clock's toward-hour fractions.** All three counting-toward
constructions — half, quarter and three-quarter — are cited to Erelt, Mati
(ed.), *Estonian Language*, Linguistica Uralica Supplementary Series 1
(Estonian Academy Publishers, 2003), its time-expression section, and to EKI
Eesti Keele Instituut's *Sõnaveeb* entries for `pool`, `veerand` and
`kolmveerand` in their clock senses. A second, independent source with a
worked numeric example (colanguage.com's telling-the-time guide, corroborated
by omniglot.com's Estonian time page) confirms the direction: "half an hour
is always subtracted from the next hour", glossing `pool üheksa` as 8:30 —
literally "half nine" naming the hour ahead. The project's own test corpus
checks the half-hour reading against independent arithmetic across four
hours (`pool üheksa` → 08:30, `pool kaheksa` → 07:30, `pool kaksteist` →
11:30, `pool kümme` → 09:30) and separately checks the quarter and
three-quarter readings the same way. The convention flags
`bare_half_to: true` and `bare_quarter_to: true` in `lang.json`, and the
`clock_time` construction carries a dedicated `FRACTION HOUR MERIDIEM?
ZONE?` order alongside the whole-hour `kell H` shape.

**`pool` survives the cardinal fold intact.** The Estonian numfold hook
(`chronologia.extract.numfold_agglutinative:fold_et`) folds spelled genitive
numerals into digits for the "N units ago/from now" slot — `ühe`, `kahe`,
`kolme`, ... `kümne`, plus `poole` (0.5) and `pooleteist` (1.5). That
genitive `poole` is a distinct word from the clock fraction's nominative
`pool`: the fold set never contains `pool` itself, so the clock's fraction
word is never at risk of being read as a bare number and dropped before the
grammar sees it — the same danger the Slavic module's Czech and Ukrainian
entries were built to dodge, avoided here simply because the two case forms
do not collide.

**Relative offsets** are `tagasi` (ago, trailing the count) and a
leading-marker order, with the deep-time construction (`N SCALE aastat
tagasi`, "N thousand/million/billion years ago") reading `aastatuhat`/
`aastatuhande` (millennium).

**Determiners.** `eelmine`/`eelmisel` ("last/previous") and `järgmine`/
`järgmisel`/`tulev`/`tuleval` ("next", two live stems) match CLDR 47 `et`
`dateFields.json`'s week-field relative types directly: relative-type--1 is
`eelmine nädal`, relative-type-1 is `järgmine nädal` — and the year field
gives the same regular pattern, `eelmine aasta`/`järgmine aasta`, unlike
Slovenian's irregular `lani`.

**Quarters, ISO weeks, decades, centuries and millennia** resolve:
`kvartal`/`kvartali`/`kvartalis` (quarter), `nädal` (ISO week, read via the
`week_num` construction), `aastakümme` implied by `scope_unit_decade`,
`sajand` implied by `scope_unit_century`, and `aastatuhat` in a dedicated
`unit_millennium.voc` — the ordinary arrangement across the locales here,
rather than leaving "a thousand years" to a numeral-plus-scale paraphrase.

**Seconds** ship a dedicated unit, `sekund`/`sekundi`/`sekundit`.

**Named days** span all four positions around the anchor: `üleeile` (the day
before yesterday), `eile` (yesterday), `homme` (tomorrow), `ülehomme` (the
day after tomorrow). All four are exactly what the CLDR 47 `et`
`dateFields.json` day field gives for relative types −2, −1, +1 and +2.

## Weaker provenance

**The weekday and month oblique-case choices** (which of the several cases
each ships) rest on the project's own test-corpus attestation rather than a
grammar citation naming the case by name.

**`kvartal`** ships without a citation distinguishing it from any native
alternative.

## What refuses

**Minutes to or past the hour by count** (`viis minutit üle poole`-style
counting) does not resolve. The three counting-toward fractions — half,
quarter, three-quarter — are the only fractional clock surfaces sourced,
and no arbitrary-minute construction ships.

That is the only refusal. In particular the "Nth
weekday of month" construction (`märtsi kolmas esmaspäev`, "the third Monday
of March") resolves, despite the name of the regression test covering it:
`test_et_ordinal_weekday_xfail.py` is a holdover from the bug the test
guards against, not a marker of expected failure — the file carries no
`xfail` decorator, and its own docstring records that the construction "now
binds correctly".

## Open questions for a native speaker

1. What case do the shipped oblique weekday and month forms actually mark,
   and are the case sets complete for every day and month?
2. Does `kvartal` compete with any native Estonian alternative for
   "quarter", the way Bulgarian and Slovenian each carry two live quarter
   words?
