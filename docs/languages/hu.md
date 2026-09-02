# Hungarian (`hu`)

Hungarian runs the most complete counting-toward-the-hour clock of any locale
here. `negyed kilenc` is 08:15, `fél kilenc` is 08:30 and `háromnegyed kilenc`
is 08:45 — a quarter, a half and three quarters of the way *toward* nine,
never past eight. Estonian does the same with the same three fractions and is
unrelated to it; Slovenian and Croatian, the Slavic neighbours in contact with
Hungarian, name the half toward the coming hour but ship no quarter at all.
The rest of the locale is shaped by
agglutination: the case suffix that other languages spell as a separate
preposition arrives glued to the word, so a date, an hour and a weekday each
reach the parser as one token carrying its own grammar.

## What ships

**The date line** is big-endian, `YEAR MONTH DAY`, which is what CLDR 47's
`ca-gregorian` chart for `hu` gives at every level — full `y. MMMM d., EEEE`,
long `y. MMMM d.`, medium `y. MMM d.`, short `y. MM. dd.`. `lang.json`
disables the shared little-endian `calendar_date` outright and defines its own
in its place, with a month-led fallback for the year-less phrase. The
tokenizer runs with `ordinal_dot` on, so the Hungarian habit of closing a date
with a full stop (`2020. augusztus 15.`) parses as written.

**The spelled day of month** is a single-token ordinal the cardinal number
model does not read as a number at all. `pronounce_ordinal_hu` emits every
value from 1 to 31 as one word, so the whole range is derived from the shared
number model rather than a vocabulary file, and a second derivation adds the
possessive form the date construction actually takes — `tizenötödike`,
`huszonegyedike` — by appending the possessive ending in the vowel harmony the
pronouncer itself chose, with `elseje` handled as the suppletive it is.

**Months and weekdays** ship in the nominative and the inessive or
superessive that a "in May" / "on Monday" phrase uses — `január`/`januárban`,
`hétfő`/`hétfőn` — plus a possessive form for each weekday. The nominatives
match the CLDR 47 wide charts exactly.

**Day parts** are transcribed from the Unicode CLDR 47 day-period rules for
`hu`, and Hungarian is one of the few locales whose chart carries six named
bands rather than four. All six surfaces ship: `reggel` (morning; Wiktionary
`reggel`, adverb, "in the morning", glossed for roughly 6 to 9 a.m.),
`délelőtt` (forenoon; Wiktionary `délelőtt`, "before noon, in the forenoon",
roughly 9 a.m. to noon), `délután` (afternoon; Wiktionary `délután`, "in the
afternoon"), `este` (evening; Wiktionary `este`), `éjjel` (night; Wiktionary
`éjjel`, "at night") and `hajnal` (dawn; Wiktionary `hajnal`). The first four
double as clock meridiem cues, alongside the abbreviations `de.` and `du.`
that CLDR gives for AM and PM.

**Landmarks** are `éjfél`/`éjfélkor` (midnight) and `dél`/`délben` (noon),
each in the bare form and in the case the phrase actually takes.

**The toward-hour clock.** All three counting-toward fractions ship, gated by
`bare_half_to: true` and `bare_quarter_to: true` in `lang.json` and read
through a `FRACTION HOUR MERIDIEM? ZONE?` order. Two independent sources fix
the direction with worked numeric examples. Wiktionary's Hungarian `fél`,
under the numeral etymology rather than the verb one that opens the lemma,
glosses the clock sense as "half an hour before … o'clock … 30 minutes before
an hour rather than after" and works it out as `fél hétkor` = "at half past
six". Wiktionary's `háromnegyed` gives `Háromnegyed tíz van.` = "It's a
quarter to ten." A third source, Wiktionary's entry for the temporal suffix
`-kor`, lists all three fractions against the same hour in one place —
`negyed egy` 12:15, `fél egy` 12:30, `háromnegyed egy` 12:45 — which is the
cleanest single attestation of the system as a system. The project's own
corpus checks four hours of the half and five of the quarters against
independent arithmetic.

**The glued clock hour.** Colloquial Hungarian drops the "o'clock" word and
glues the temporal suffix straight onto the numeral: `háromkor` is "at three".
The cardinal back-end does not read the glued form, and folding it to a bare
digit would leave the clock frame no cue at all, so the twelve telling-time
surfaces are given as a closed table and each is split into a synthetic `at`
marker plus the hour, which the universal `at HOUR` order then binds. The
marker carries an empty raw text and a zero-width extent, so it never reaches
the remainder. `-kor` is cited to its own Wiktionary entry as the temporal
case suffix, which glosses `1 órakor` as "at 1 o'clock" and `1-kor` as "at 1".

**`hét` never folds.** Hungarian's word for "week" is also its word for
"seven", and the fold names it explicitly in an exclude set so the unit token
survives. `hétkor` ("at seven") is a distinct surface and is unaffected, so
both readings stay reachable. The attributive `két` (2) goes the other way and
is supplied explicitly, because the pronouncer emits only `kettő`.

**Fused thousands.** Hungarian glues the multiplier onto the scale word and
hyphenates the remainder — `kétezer-huszonnégy` is 2024 — and neither the run
set nor the number back-end composes the two. A wrapper validates the
multiplier prefix through the language's own extractor and composes the value
itself, so `kétezer-huszonnégy` reads as the year rather than as twenty-four.

**Relative offsets** are `múlva` (in/from now, trailing the count), `ezelőtt`
(ago, likewise trailing) and `óta` (since), each in the postposition slot
Hungarian puts them in; `lang.json`'s `positions` table declares `until` and
`from` as affixes and `since` as a postposition, which is what lets `-ig` and
`-tól`/`-től` be read as the suffixes they are. The deep-time construction
reads `millió` and `milliárd` alongside `ezer`.

**Determiners.** `előző` ("previous") and `következő` ("following") match the
CLDR 47 `hu` `dateFields.json` relative types exactly across week, month and
year — `előző hét` for relative-type--1, `következő hét` for relative-type-1
— and `ez` plus the article gives CLDR's `ez a hét` for relative-type-0. The
locale also ships the everyday `múlt`/`elmúlt` and `jövő`, which CLDR does not
use; Wiktionary carries both, `múlt` glossed "last (with weeks, months, years,
and larger time units)" and `jövő` glossed "next, coming (week, month, year,
or a larger time unit)".

**Named days** span all five positions around the anchor — `tegnapelőtt`,
`tegnap`, `ma`, `holnap`, `holnapután` — and are exactly what the CLDR 47 `hu`
`dateFields.json` day field gives for relative types −2 through +2.

**Quarters, ISO weeks, decades, centuries and millennia** resolve, with
`negyedév` for the quarter, `hét` for the ISO week, `évtized`, `század` and
`évszázad` for the decade and century, and `évezred` for the millennium.
Seconds ship a dedicated unit.

## Weaker provenance

**The grammar behind the clock.** All three fraction files name Rounds,
Carol H., *Hungarian: An Essential Grammar*, 2nd ed. (Routledge, 2009), its
section on telling the time. That is a real and standard reference, but it is
a printed book and the claim rests here on the Wiktionary attestations
instead, which carry the worked numeric examples the grammar is cited for.

**The quarter's citation.** `clock_fraction_15.voc` attributes the clock
sense to the Wiktionary lemma `negyed`. That lemma's Hungarian section has
three senses — the fraction "quarter, fourth", the musical crotchet, and a
city quarter — and no clock sense at all. The reading is well attested, but on
the `-kor` and `háromnegyed` lemmas rather than on that one. The `fél`
citation has a milder version of the same problem: the lemma opens on the
unrelated verb "to fear" and the numeral is a separate etymology further down,
which the file's bare "Wiktionary `fel`" does not say.

**The oblique month and weekday forms** ship one case each with no citation
recording which case, or whether one is enough — Hungarian has considerably
more than one candidate.

**`negyedév`** ships without a citation and without any statement of whether a
native alternative competes with it.

## What refuses

**The first hour of the toward-hour clock.** `fél egy` resolves to 00:30,
`negyed egy` to 00:15 and `háromnegyed egy` to 00:45, where the Wiktionary
`-kor` entry gives 12:30, 12:15 and 12:45 for the same three phrases. The
resolver subtracts one from the named hour and, for the first hour, that
lands on zero. A `toward_hour_12h` convention exists for exactly this and
turns the zero back into twelve; the Slavic toward-hour locales set it and
Hungarian does not. The same holds for Estonian, and for the Germanic locales
whose `halb eins` has the same shape, so this is a family-wide arrangement
rather than a Hungarian one — but it is the one place on this page where the
locale's answer and its citation disagree outright.

**Minutes counted to or past the hour.** The three counting-toward fractions
are the only fractional clock surfaces sourced, and no arbitrary-minute
construction ships.

**A fractional quantifier in an offset.** `fél óra múlva` ("in half an hour")
and `negyed óra múlva` ("in a quarter of an hour") resolve to one hour from
the anchor with the quantifier stranded, so the answer is confidently wrong by
thirty and forty-five minutes rather than refused. The quantifier table
carries both values; the offset construction does not read from it.

**A trailing case suffix on a digit.** The tokenizer shears the hyphen, so
`augusztus 15-én` resolves to the right day and leaves `én` in the remainder,
and `reggel 8-kor` resolves to 08:00 and leaves `kor`. The spelled forms
(`augusztus tizenötödike`, `nyolckor`) consume everything.

**A year-led quarter or half.** Hungarian puts the year first, and the quarter
and half-period constructions carry only the year-last orders the shared
grammar supplies. `2020 második negyedéve` and `2020 első fele` both return
the whole of 2020 with the qualifier stranded — the same silent widening in
both cases, and the more dangerous of the two failure modes because a whole
year is a plausible-looking answer.

**A decade written the Hungarian way.** `1990-es évek` returns the single year
1990 with `es évek` stranded. The decade unit is present; the `-es évek`
spelling that names a decade is not.

**A weekday range.** `hétfőtől péntekig` returns the span from the anchor to
Friday with `hétfőtől` stranded: the terminative `-ig` is read as an affix and
the ablative `-tól`/`-től` is listed in `marker_from.voc`, but the pair does
not compose over two weekdays.

**A duration in the terminative.** `három napig` ("for three days") does not
resolve. Estonian, German, Slovak and Croatian each carry a
`marker_recur_for.voc`; Hungarian does not, and `-ig` alone reaches only the
range construction.

**Dawn in the case a phrase uses.** `hajnal` ships as CLDR spells it, which is
the bare noun. Every other day part in this locale ships the adverb, so
`éjjel` resolves standing alone and `hajnalban` does not; `holnap hajnalban`
returns the whole of tomorrow with `hajnalban` stranded.

**Vague quantifiers.** `pár` and `néhány` ("a couple", "a few") are listed in
the quantifier table but reach no construction: `pár nap múlva` returns one
day from the anchor with `pár` stranded. `pár` is additionally listed under
two different values, 2 and 3. That is not a live ambiguity — the table is
flattened surface-first, so the later bucket wins and the entry under 2 has no
effect at all. Wiktionary's `pár` does carry both readings, the literal
"pair" and the vague "some, a few", but a quantifier table can hold only one
of them.

**A leading article.** `a hétvégén`, `a jövő héten` and `a hónap elején` all
resolve correctly and all leave the article in the remainder.

## Open questions for a native speaker

1. Should `fél egy` read as 12:30 or as 00:30 when nothing else in the phrase
   disambiguates? The cited source gives 12:30, but a speaker naming the
   half hour after midnight has to say something.
2. Is `pár` two or approximately three in a temporal phrase (`pár nap`), or
   does it resist a number entirely?
3. Which case should each month and weekday ship beyond the one on file, and
   is one enough for ordinary date phrases?
4. Does `negyedév` compete with a native alternative for a calendar quarter?
5. Is `hajnalban` the form a phrase uses, with `hajnal` reserved for the bare
   noun, or are both current adverbially?
