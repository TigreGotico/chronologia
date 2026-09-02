# Czech (`cs`)

Czech names the half hour for the hour that has not arrived: `půl deváté` is
08:30, not 09:30, and `půl páté` is half past four. The hour in that phrase is
not a cardinal at all but a genitive-feminine *ordinal* agreeing with an
elided `hodiny` — literally "half of the ninth" — and that grammatical fact is
what keeps the construction alive, because a fold that reads spelled cardinals
never sees the ordinal and never merges it with the fraction word in front of
it. The second thing to know is that Czech's quarter hour runs on a different
grammar from its half hour, and the locale reads only the half.

## What ships

**The date line** is little-endian, `DAY MONTH YEAR?`, matching the CLDR 47
`ca-gregorian` chart for `cs` at every level — full `EEEE d. MMMM y`, long
`d. MMMM y`, medium `d. M. y`, short `dd.MM.yy`. `lang.json` adds an
"of"-linked order and a month-led one alongside the plain day-led shape, and
the tokenizer runs with `ordinal_dot` and `dotted_date` on, so both `15. srpna
2020` and the spelled `patnáctého srpna 2020` resolve to the same day.

**Months** ship in three shapes at once, and CLDR 47 accounts for all three.
The standalone nominative (`leden`) is what CLDR's `stand-alone` wide chart
gives; the genitive that follows a day ordinal (`ledna`) is CLDR's `format`
wide chart, which is genitive throughout for Czech; and the three-letter
clippings (`led`, `úno`, `bře`, `dub`, `kvě`, `čvn`, `čvc`, `srp`, `říj`,
`lis`, `pro`) are CLDR's `format` abbreviated chart character for character.
The locative that follows the preposition (`lednu`, `srpnu`) is shipped
alongside them without a recorded source. September is the one month whose
genitive and nominative coincide, `září`.

**Weekdays** ship in the nominative, with the accusative that a
`v <weekday>` phrase takes for the three weekdays whose accusative differs
(`středu`, `sobotu`, `neděli`) and a scattering of genitives; the nominative
set matches CLDR 47's wide weekday chart. No source is recorded for the
choice of oblique forms.

**Day parts** are transcribed from the Unicode CLDR 47 day-period rules for
`cs`, each shipping as the deictic adverb a phrase actually uses rather than a
dictionary citation form: `ráno` (morning, Wiktionary `ráno`, whose Czech
adverb sense is glossed "in the morning"), `odpoledne` (afternoon, Wiktionary
`odpoledne`, adverb, "during the afternoon"), `večer` (evening, whose
Wiktionary entry carries only a noun sense, so the adverbial use the locale
ships rests on the day-period data rather than on that entry). The same words
double as clock meridiem cues on an explicit hour,
`ráno` and `dopoledne` for AM, `odpoledne` and `večer` for PM, so `v 9 hodin
večer` is 21:00.

**Relative offsets** are `před` (ago, governing the instrumental) and `za`
(in/after, governing the accusative), with `v`/`ve` carrying "in" over a
calendar period. That last preposition is cited to its Wiktionary entry for
Czech, whose sense list gives the four temporal uses the locale needs
and glosses each with a worked example — `v šest hodin` ("at six o'clock",
accusative), `v pátek` ("on Friday", accusative), `v roce 2007` ("in the year
2007", locative) and `v lednu` ("in January", locative).

**Determiners.** `minulý` ("last/previous"), `příští` ("next") and `poslední`
("the last one of") each ship a full adjectival paradigm — `minulý` the hard
type across ten forms, `příští` and `poslední` the soft type, whose forms are
largely syncretic so that the base form covers most of the singular and only
`-ího/-ímu/-ím/-ích/-ími` stand apart. Wiktionary carries a complete
declension table for each of the three under its Czech `Adjective` heading.
The first two match the CLDR 47 `cs` `dateFields.json` relative types
directly and across three fields at once, which is unusually clean: week,
month and year all give `minulý ...` for relative-type--1 and `příští ...`
for relative-type-1, with no irregular of the kind Slovenian's `lani` forces.

**"This"** ships in two series, the formal `tento` (`tohoto`, `tomuto`,
`tomto`, `tímto`, `tato`, `této`, `tuto`, `touto`, `toto`, `tyto`, `těchto`,
`těmito`) and the colloquial `tenhle` (`tohohle`, `tomhle`, `tahle`, `tuhle`,
`tohle`). Wiktionary lists both as Czech demonstrative pronouns and gives
each a declension table built on the irregular `ten`.

**Landmarks** are `půlnoc` (midnight) and `poledne` (noon).

**The clock's toward-hour half.** `půl` plus the genitive-feminine ordinal of
the coming hour is the locale's only fractional clock surface, gated by
`bare_half_to: true` and `toward_hour_12h: true` in `lang.json` and read
through a `FRACTION HOUR MERIDIEM? ZONE?` order. The hour surfaces —
`první`, `druhé`, `třetí`, `čtvrté`, `páté`, `šesté`, `sedmé`, `osmé`,
`deváté`, `desáté`, `jedenácté`, `dvanácté` — are a closed table in the shared
Slavic number-folding module, applied as a post-pass after the cardinal fold
so that the fraction word and the hour can never merge into one run. Two
independent sources fix the direction with worked numeric examples.
Wiktionary's Czech `půl` carries a usage note saying the word means "half to"
when telling the time and glosses `je půl páté` as "half (past) four";
a Czech-for-foreigners grammar table gives `Je čtvrt na osm` for 7:15, `Je půl
osmé` for 7:30 and `Je tři čtvrtě na osm` for 7:45 under the rule that a Czech
speaker "always states the hour being approached". `půl páté` resolves to
04:30 and `půl deváté` to 08:30, and the corpus checks five hours of the
pattern against independent arithmetic, `půl první` among them, which the
twelve-hour convention flag turns into 12:30 rather than 00:30.

**`půl` stays out of the cardinal fold.** The shared Slavic hook
(`chronologia.extract.numfold_slavic:fold_cs`) keeps its closed extra-word set
down to `{dva, dvě, dvou, tři, čtyři}` — the oblique forms the number model's
nominative pronunciation misses — and deliberately excludes `půl`, because the
Czech number back-end reads it as 0.5 and folding it would erase the clock's
fraction word before the grammar ever saw it. The half-hour *duration* is
unaffected: `půl hodiny` and `čtvrt hodiny` reach the duration reader through
`lang.json`'s quantifier table and come back as thirty and fifteen minutes.

**Quarters, ISO weeks, decades, centuries and millennia** all resolve, with
`čtvrtletí` and `kvartál` as two live quarter words, `týden` for the ISO week,
`desetiletí` and `dekáda` for the decade, `století` for the century and
`tisíciletí` for the millennium. The millennium file carries the one comment
that explains itself: a neuter noun in `-í` spells its nominative singular and
plural alike, so the singular has to be listed separately or every
`tisíciletí` is read as a plural count.

**Named days** span all five positions around the anchor — `předevčírem`,
`včera`, `dnes`, `zítra`, `pozítří` — and are exactly what the CLDR 47 `cs`
`dateFields.json` day field gives for relative types −2 through +2.

**Era markers** are cited to the Internetová jazyková příručka of the Ústav
pro jazyk český, its page on purely graphic abbreviations
(`prirucka.ujc.cas.cz/?id=780`), which lists both the secular `př. n. l.` and
`n. l.` and the Christian `př. Kr.`. The spaced spelling is the one that page
recommends; the unspaced variants ship because they are widely typed.

**Ranges** run `od A do B` and `A až B`. The range conjunction is cited to the
same institute's dictionary entry for `až`, whose SSČ and SSJČ articles both
give the "up to a limit" sense with numeric examples (`na str. 5 až 10`,
`může přijít pět až deset lidí`).

## Weaker provenance

**The oblique weekday and month forms** carry no citation. The nominatives,
the format genitives and the abbreviations are all traceable to CLDR, but
nothing on file says which case `středu` or `lednu` is meant to serve or
whether the set shipped for each word is complete.

**`čtvrtletí` and `kvartál`** ship as unqualified synonyms for "quarter" with
no source distinguishing register — the same pair, and the same silence,
that the Bulgarian and Slovenian pages record for their own two quarter words.

**The half-period noun.** `marker_half.voc` names the *Slovník spisovného
jazyka českého* as the source for `polovina` and quotes a definition and an
example. The institute's entry for `polovina` does carry the sense, but the
gloss on file is a paraphrase rather than the wording printed there, the
example is not in the entry, and the definition actually belongs to the
shorter *Slovník spisovné češtiny* article on the same page rather than to the
SSJČ one named. The surface is sound; the locator is looser than it reads.

**The determiner and pronoun paradigms** are shipped with locators into the
Internetová jazyková příručka's expository section (`?id=310` for hard
adjectives, `?id=311` for soft, `?id=350` for demonstratives) that do not
resolve. The first two answer with the appliance's own "page not available"
notice under an HTTP 200, and the third resolves to an article about female
personal names. The paradigms themselves are correct and are carried by the
Wiktionary declension tables cited above; only the institute locators are
wrong.

**The clock's half-hour citation.** `clock_fraction_30.voc` attributes the
toward-hour reading to the Internetová jazyková příručka. That appliance's
page on time (`?id=820`, *Časové údaje*) covers written notation only — where
the separator goes, when to double-digit the hour — and says nothing about the
spoken `půl <ordinal>` at all. The direction is not in doubt, being carried by
the two sources named above, but it does not come from where the file says it
does.

## What refuses

**The quarter hour.** Czech says `čtvrt na devět` for 8:15 and `tři čtvrtě na
devět` for 8:45 — a quarter *onto* the coming hour, with the accusative after
`na`, an entirely different grammar from the genitive the half hour takes.
Neither resolves, and neither can: the linking `na` is in no vocabulary file
and the locale carries no `FRACTION na HOUR` order of the kind Ukrainian has
for its own `пів на` construction. `čtvrt` is present in
`clock_fraction_15.voc` and does reach the fraction table, but the resolver
declines any fraction other than the half unless a locale sets
`bare_quarter_to`, which Czech does not, so `čtvrt deváté` returns nothing
too. The quarter reaches only the duration path, where `čtvrt hodiny` is
fifteen minutes.

**Minutes counted to or past the hour.** `pět minut po deváté` and
`deset minut před devátou` do not resolve. There is a `MINUTE CLOCKDIR HOUR`
order in `lang.json`, but the hour-ordinal table it would need to read
(`deváté`) is genitive-feminine and the minute-count phrase takes different
cases on both sides, so the order never binds; `pět minut před devátou` is
read as a five-minute offset from the anchor and leaves `devátou` stranded.
`za pět minut devět` — the ordinary way to say five to nine — is read the same
way, as an offset five minutes ahead with `devět` stranded, which is a
confident answer to a question nobody asked.

**Spelled numbers in an oblique case.** Czech puts the numeral after `před` in
the instrumental (`před pěti lety`, `před dvěma dny`) and after `po dobu` in
the genitive (`po dobu tří dnů`), and the number model behind the fold reads
only nominatives, so none of these resolve. The corpus records the boundary
explicitly rather than papering over it, and the digit spellings (`před 2
lety`) cover the same ground.

**Night.** The CLDR 47 `cs` day-period chart gives `v noci` for the night
band, and no night daypart ships, so `v noci` returns nothing and `dnes v
noci` returns the whole of today with `v noci` stranded. `dopoledne` has the
converse problem: it is a meridiem cue but not a day part, so `dnes
dopoledne` returns the whole day and strands the word. Polish, Slovak and
Welsh are the only other locales with a morning daypart and no night one.
Belarusian ships no day-part vocabulary at all, so the shape is not simply a
Slavic one.

**A leading preposition on the clock and on the year.** `v půl deváté` and
`o půl deváté` — the two ordinary ways to say "at half past eight" — resolve to
08:30 but leave the preposition in the remainder, because the clock's fraction
order begins at the fraction word where the Slovenian and Croatian equivalents
begin at an optional `at?`. `v roce 2020` strands its `v` the same way, for a
different reason: the marker that order names is the future preposition `za`,
not the locative `v`. Most of the Slavic locales here compose `year_ref` from
that same `in GYEAR` order — Bulgarian and Belarusian lead theirs with other
markers, and Macedonian has no marker-led order at all.

**A missing month abbreviation.** Eleven of the twelve CLDR abbreviated month
names ship. `zář` does not, so `15. zář 2020` returns the whole of 2020 with
`15. zář` stranded where `15. srp 2020` returns the day.

**Mid-period by the other noun.** `polovina` and `prostředek` are the
mid-period words, so `v půlce května` — at least as ordinary in speech —
returns the whole of May with `v půlce` stranded.

## Open questions for a native speaker

1. Is `čtvrt na devět` worth wiring, and is the accusative after `na` the only
   linking grammar it takes? The half hour and the quarter hour disagree about
   case in a way no other locale here has to model.
2. What case do the shipped oblique weekday and month forms mark, and is the
   set complete for each word?
3. Are `čtvrtletí` and `kvartál` interchangeable for a calendar quarter, or
   does one belong to fiscal usage?
4. Is `v noci` the right single surface for the night band, or does colloquial
   Czech need `v noci` alongside a separate `večer`-adjacent form?
5. Does `půlka` compete with `polovina` in date phrases (`v půlce května`)
   strongly enough to ship, or is it too colloquial for a calendar reading?
