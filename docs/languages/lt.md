# Lithuanian (`lt`)

The rule that shapes this locale is that the form of a counted noun is decided
by the numeral's **last digit**, not by its size. A numeral ending in 1 — but
not 11 — takes the singular; one ending in 2 through 9, but not 12 through 19,
takes the nominative plural; one ending in 0, and the whole teen range, takes
the genitive plural. So `21 diena`, `25 dienos`, `20 dienų`, `111 dienų`. This
is not the Slavic pattern, and the Slavic tables cannot be borrowed for it:
`chronologia/extract/numfold_baltic.py` carries its own last-digit-keyed
government with three noun cases per unit, plus the accusative that `prieš`
imposes.

The spoken half hour names the coming hour. `pusė trijų` is 02:30, and the hour
that follows `pusė` stands in the genitive.

## What ships

**Months** ship in three forms from the Unicode CLDR 47 chart for `lt`: the
stand-alone nominative, the genitive that the date construction actually uses,
and the abbreviation. The genitive is the working form — a Lithuanian date is
`kovo 1 d.`, "of March, day one".

**The date line** is `YEAR m. MONTH DAY d.`, as in `1990 m. kovo 1 d.`, where
`m.` abbreviates `metai` (year) and `d.` abbreviates `diena` (day). Both
abbreviations are Wiktionary-attested in exactly that calendar-date sense.
`metai` is a plurale tantum, which is why the year vocabulary carries `metai`,
`metų` and `metais` rather than a singular.

**The day of the month** reads either way. The written form is a bare digit
(`liepos 5 d.`), and the spelled form is a feminine ordinal agreeing with an
elided `diena` (`liepos penktoji`). Both resolve to the same date.

**Relative offsets** use `prieš` with the accusative for the past
(`prieš valandą`, an hour ago) and `po` with the genitive for the future
(`po trijų dienų`, in three days). Both are Wiktionary entries with the
temporal sense given directly. Unit files therefore carry the genitive singular
alongside the three government cases, because `po` governs it.

**The determiners** `šis` (this), `praeitas` (last) and `kitas` (next) ship in
their full non-pronominal declensions from Wiktionary. The bare accusative is
the ordinary "in" or "during" form: `šią savaitę` is this week.

**The clock** has two constructions. `pusė` plus the genitive of the coming
hour gives the half hour — `pusė trijų` is 02:30, `pusė aštuonių` is 07:30 —
with `bare_half_to` and `toward_hour_12h` in `lang.json` rolling the named hour
back. `be` plus the genitive counts down toward the named hour: `be penkių trys`
is 02:55. Wiktionary supplies both function words in the right government
(`be` "without", with the genitive; `pusė` "half"), and Talkpal's guide to
telling time in Lithuanian supplies the worked examples.

**Day parts** take their band boundaries from the CLDR 47 day-period chart for
`lt`, transcribed in `chronologia/dayparts.py`, and ship as the CLDR period
name plus the adverbial case the deictic phrase uses, declined from Wiktionary:
`rytas` / `rytą` / `ryte`, and the parallel sets for afternoon, evening and
night. Midnight and noon are `vidurnaktis` and `vidurdienis`.

**Markers** are Wiktionary entries throughout: `po` (after), `prieš` (before),
`tarp` with the genitive (between), `nuo` with the genitive (from, since), `iki`
(until, and the closing half of a range), `kas` (every, as in `kas savaitę`),
`ir` (and).

## Weaker provenance

**The clock constructions** rest on a language-learning site for their worked
examples. Wiktionary attests the words and their case government, but the
pairing of `pusė trijų` with 02:30 rather than 03:30 comes from Talkpal's time
page. The direction is corroborated by several accounts and no counter-example
was found, but a reference grammar was not consulted for it.

**`kas` as the distributive "every"** is a Wiktionary sense that itself cites
Ambrazas's *Lithuanian Grammar* with page locators. The grammar was not
consulted directly; what was read is Wiktionary's entry.

**Ambrazas (ed.) 1997, *Lithuanian Grammar*, Baltos lankos** was sought as the
authority for numeral government and the clock direction and was not reached in
full text. The government rule instead rests on triangulation across several
independent tertiary accounts that agree on the last-digit keying and on the
same worked examples.

## What refuses

Each refusal below is pinned by a test.

**Seconds.** `prieš 30 sekundžių` and `po 45 sekundžių` return nothing. No
second unit ships.

**Calendar quarters.** `pirmasis ketvirtis`, `antras ketvirtis` and the bare
`ketvirtis` all refuse. No quarter vocabulary was attested.

**ISO week references.** `3 savaitė`, `trečioji savaitė` and the like refuse.

**The quarter hour on the clock.** `be ketvirčio trys` and `ketvirtis po trijų`
refuse. Only the half hour and the counted minutes-to form ship.

**An ordinal hour after `pusė`.** `pusė vienuoliktos` and `pusė trečios` refuse.
The hour that `pusė` names is a cardinal genitive — `pusė vienuolikos` — and
the ordinal shape was not attested, so it is not guessed at.

**Era vocabulary.** `44 pr. m. e.` and `prieš mūsų erą` are not read as eras;
the abbreviation could not be attested, so the era marker leaves its pieces in
the remainder.

**`paskutinis` as a relative marker.** `paskutinis penktadienis` resolves the
Friday and leaves `paskutinis` visibly in the remainder rather than silently
swallowing it. The word has no attested declension table here, so it is not
wired as the "last weekday of the month" marker.

**The instrumental determiners.** `praeitais metais` and `kitais metais` refuse.
The instrumental of `praeitas` and `kitas` could not be attested; the nominative
and accusative are what ship.

**Early, middle and late.** `birželio pradžioje` returns the whole of June with
the unread part word left in the remainder. No period-part vocabulary ships.

**A spelled quantity with no direction marker.**
`du šimtai penkiasdešimt dienų` refuses, because a quantity without a marker is
still only a quantity.

## Open questions for a native speaker

1. Do the individual weekday and month genitives all follow the regular pattern,
   spelling included? Only some were dictionary-checked; the rest follow a
   regular declension and are individually unverified.
2. Is the `pusė` + genitive half-hour direction confirmed by a reference
   grammar, and does the target hour stand in the case assumed here?
3. Is there an attested quarter-hour clock construction?
4. What is the standard era abbreviation, and how is it written?
5. Does `paskutinis` have a declension that would let it act as the
   "last Friday of the month" marker?
