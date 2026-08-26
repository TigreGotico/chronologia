# Latvian (`lv`)

Two facts about Latvian shape the whole locale. The first is that a date
behaves differently depending on whether it stands alone or sits inside a
sentence: the dateline puts the month in the nominative, the sentence-embedded
date puts it in the locative. The second is that the counted noun's form is a
fact about the numeral, not about the noun — and Latvian states that twice
over, through two independent systems that the fold in
`chronologia/extract/numfold_latvian.py` keeps deliberately apart.

The spoken half hour is the surface most likely to surprise a reader who knows
another Baltic or Slavic language only loosely. `pusčetri` is 03:30, not 04:30:
the prefix names the hour being counted *toward*.

## What ships

**Months** ship in three shapes: the nominative and the abbreviation from
Unicode CLDR 47 for `lv`, plus the locative from the Wiktionary declension
table for each name. The locative is what a sentence-embedded date uses —
`3. maijā`, "on May 3rd" — while the nominative heads a dateline,
`2017. gada 29. maijs`. Both orders parse, and the year word `gada` (genitive)
and `gadā` (locative) ship alongside the nominative `gads` because the dateline
is built on that genitive.

**Weekdays** likewise come from CLDR 47, wide and abbreviated, with the
locative, genitive and accusative added from Wiktionary's declension tables.
The locative is the adverbial "on Monday" form: `sanāksme ir pirmdienā`.

**Relative offsets** are governed by `pirms` (ago) and `pēc` (in), both of which
put their phrase in the dative. Wiktionary's entry for `pirms` gives the adverb
sense with the worked example `pirms diviem gadiem`. The number of the counted
noun follows the CLDR plural rule for Latvian: singular when the numeral ends
in 1 and is not 11, plural otherwise. So `pirms gada` and `pirms 21 gada`
against `pirms 11 gadiem` and `pirms 20 gadiem`. The singular surfaces as the
genitive singular and the plural as the *dative* plural — `gadiem`, `dienām`,
not the genitive plural `gadu`, `dienu`, which is a distinct cell in every
Latvian declension. CLDR 47 `dateFields.json` for `lv` spells that pair out for
every unit, and the Wiktionary tables confirm it cell by cell.

**The bare count** is the second government system, and it is a register split
rather than a rule. After 11–19 and the round tens, a bare count has two live
surfaces: formal, with the noun in the genitive plural (`vienpadsmit gadu`),
and colloquial, leaving the noun in the case the sentence otherwise wants,
which for a bare count is the nominative (`vienpadsmit gadi`). The split is
corroborated across several sources, but none of them gives a mechanical
trigger for which register a given text uses. The locale therefore ships both
surfaces and never infers a register from the input. `counting_registers()`
states which forms are admissible for a given count and deliberately refuses to
choose between them.

**The clock** reads a fused half-hour compound. Latvian writes `pus` joined
onto the masculine nominative plural of the hour being counted toward, all in
one word, so the fold splits it into the `FRACTION HOUR` pair the clock order
needs and `bare_half_to` plus `toward_hour_12h` in `lang.json` roll the named
hour back by one. The direction comes from pronuncia.io's guide to telling time
in Latvian, which gives `Ir pusastoņi` for 7:30 and `pusčetri` for half past
three, and from a second independent survey repeating the same rule with the
same worked example, `pusseptiņi` for 6:30 and `pusčetri` for 3:30.

**Day parts and landmarks** take their band boundaries from the CLDR 47
day-period chart for `lv`, transcribed in `chronologia/dayparts.py`. Each ships
as the nominative noun plus the locative the adverbial phrase uses — `rīts` and
`rītā`, `vakars` and `vakarā`. Midnight is `pusnakts` / `pusnaktī`.

**Numerals** are transcribed from Wiktionary declension tables and headwords,
paradigm by paradigm: 0–9 from the individual tables, 10 and the teens from
their headwords (whose tables fill only the instrumental and locative cells,
every other being the bare indeclinable headword), 20–90 from the cardinal
box, `simts` for a hundred, and the `tūkstotis` table for a thousand. Teens are
whole numerals in Latvian and never continue a composed run, so
`divdesmit vienpadsmit` is not a number and is not read as one.

**Ordinals** ship in the definite masculine nominative singular only. That is
the citation form Wiktionary attests as a headword for each value, and it is
also the only safe one: the definite feminine `-ā` is homographic with the
locative that carries the adverbial date, so shipping it would make every
`maijā` neighbour ambiguous. A compound inflects its last element only, the
tens staying a bare cardinal — `divdesmit piektais`.

**Markers** are Wiktionary entries throughout: `pirms` (before, ago), `pēc`
(after, in), `starp` (between, with the accusative), `no` (from, since), `līdz`
(until, and the closing half of a range), `katrs` (every, in its full
declension), `un` (and), `puse` (half, as the period noun of "the first half of
the year").

`nākamais` for "next" ships in its full definite declension from Wiktionary,
with the locative being the ordinary "during next week" form that CLDR
relative-type-1 gives as `nākamajā nedēļā`.

## Weaker provenance

**The `pus-` half-hour compounds** rest on thinner ground than the rest of the
clock. Both sources for the direction are web guides — pronuncia.io and a
second independent survey — not a reference grammar. They agree with each other
on the rule and on a shared worked example, which is why the construction
ships, but no dictionary or grammar was consulted for it.

**`pagājušajā`** ships as the only form of the backward determiner. It is the
locative definite form that CLDR 47 `dateFields.json` gives for
relative-type--1 (`pagājušajā nedēļā`, `pagājušajā gadā`). The participle has
no dictionary declension table to transcribe, so the remaining cells would have
been guesses and were left out. A phrase using any other case of "last" will
not parse.

**`pusdienlaikā`** ships for noon in the locative alone. That is the form CLDR
gives, and the nominative of the compound appears in no dictionary consulted.

**Prauliņš, *Latvian: An Essential Grammar* (Routledge)** was sought and not
reached; no accessible copy turned up. Nothing on this page depends on it, but
it remains the best available check on the numeral-register trigger and on the
short adverbial weekday forms.

## What refuses

**The short adverbial weekday form, for every day but Monday.** `pirmdien`
parses; `otrdien` and `trešdien` return nothing. Monday is the one value
attested in running text. The other six follow an obvious regular pattern —
drop the final `-a` — but a regular pattern is not an attestation, so they were
left out rather than invented.

**`pusviens` for 12:30.** Every hour from two upward takes the masculine
nominative plural in the compound, which is the only shape the sources attest.
`viens` is a singular that declines for gender, no source gives the compound
at all, and choosing between `pusviens` and `pusviena` would be inventing a
surface. A test pins the omission so it cannot be closed by accident.

**Ranges over month names in the cases the idiom actually uses.**
`no jūnijs līdz augusts` parses, because the nominative is in the vocabulary;
the idiomatic `no jūnija līdz augustam` does not, because the genitive `no`
governs and the dative `līdz` governs are not shipped for month names. Month
vocabulary carries the nominative, the locative and the abbreviation, those
being what CLDR and the date constructions attest.

**Genitive datelines.** An earlier reading of the sources suggested Latvian
dates take a genitive month. It could not be reproduced: the one source that
appeared to say so shows only nominative and locative month forms in its own
date examples, and its prose most likely mislabels the locative. No genitive
date construction ships.

**Minutes to the hour.** `bez piecām deviņi` returns nothing. No
minutes-to-the-hour construction was sourced, so none was built; the half hour
is the only fractional clock surface the locale reads.

## Open questions for a native speaker

1. Are the short adverbial weekday forms — `otrdien`, `trešdien` and the rest —
   current, and are they spelled by simply dropping the final `-a`?
2. What triggers the formal genitive-plural register against the colloquial
   nominative after 11–19 and the round tens? Both surfaces are accepted; the
   question is whether anything in a text predicts which one a writer used.
3. Does `pusviens` exist for 12:30, and if so is it `pusviens` or `pusviena`?
4. Which case do month names take in a `no … līdz …` range, and should those
   forms ship?
5. Is there a minutes-to-the-hour clock construction at all?
6. What is the nominative of the noon compound whose locative is
   `pusdienlaikā`?
