# Welsh (`cy`)

Welsh changes a word's **first letter** according to what precedes it, and that
one fact shapes this whole locale. A vocabulary listing only dictionary forms
would silently fail on ordinary sentences, so every mutated surface a temporal
construction can produce is enumerated in the vocabulary files rather than
derived.

The year is the richest case. Its count form has three surfaces — the radical
`blynedd`, the soft-mutated `flynedd` after the feminine two, and the
nasal-mutated `mlynedd` after five — and all three name the same unit.
`dwy flynedd yn ôl` and `tair blynedd yn ôl` differ by one year, not by which
word the year is.

The clock counts the English way. `chwarter wedi naw` is 09:15 and
`hanner awr wedi tri` is 03:30 — the half is counted from the hour just named,
so no toward-the-hour convention applies. Past the half hour Welsh switches to
`i`, which counts down and triggers soft mutation on the hour it names:
`chwarter i bedwar` is 03:45.

## What ships

**Months and weekdays** come from Unicode CLDR 47,
`cldr-dates-full/main/cy/ca-gregorian.json`, each with its abbreviations and,
where the initial is mutable, its mutated surface. March is `mawrth`, `fawrth`
and `maw`, the soft mutation attested in running text as `ar y 14eg o Fawrth`.
The mutation table itself is the English Wikipedia article on Welsh mutation.

**The date** links the day to the month with `o`, which triggers soft mutation
on the month name — `y 3ydd o Orffennaf` — which is why every mutable month
ships its mutated form.

**Relative offsets** are marked at opposite ends. `ymhen` opens a forward
offset: `ymhen tair blynedd`, `ymhen mis`, both attested in Welsh Wikipedia
running text. `yn ôl` **closes** a backward one: `chwe chan mlynedd yn ôl`,
`bedair blynedd yn ôl`, likewise from running text.

**The determiners** trail their noun, which is why this locale marks its
determiner position as postposed. `nesaf` is next (`yr wythnos nesaf`),
`diwethaf` last, and the demonstrative agrees in gender — `hwn` after a
masculine noun, `hon` after a feminine one, as in `yr wythnos hon`.

**`bob`** is the lexicalised soft-mutated form of `pob`, and it is the form the
"every X" construction actually uses: `bob dydd` is the dictionary's own worked
example and `bob dydd Llun` is attested in Welsh Wikipedia running text. The
radical `pob` ships too, for the citation form.

**The clock's own words.** `am` opens a time and triggers soft mutation —
`am dri o'r gloch`. `o'r gloch`, literally "of the bell", closes a named hour.
`munud` may stand between a minute count and the direction word, and its
soft-mutated `funud` ships beside it. The sources are Wiktionary's `chwarter`
and `hanner` entries, a Wikibooks Welsh lesson carrying a full five-minute
table, and Welsh Wikipedia running text for the `i` forms
(`am chwarter i dri yn y prynhawn`).

**The article** ships in the surfaces its environment conditions: `y` before a
consonant, `yr` before a vowel.

## What refuses

Each refusal is pinned by a test.

**The day after tomorrow.** `trennydd` appears on a dictionary entry only as
the cross-referenced antonym of `echdoe`, with no running-text occurrence found
at all and a second spelling in circulation, so the day two ahead is not named.
`echdoe`, the day before yesterday, is attested and does ship.

**Single-word year deixis.** Welsh has dedicated adverbs for "this year" and
"last year" — `eleni` and `llynedd` — but no construction here reads a bare
year-deictic adverb, so they are left unread rather than wired to an
approximation.

**"Since".** `ers` and `er` are attested as "since" and "for", but their
governed forms and the register split between them were never pinned down, so
no open-range vocabulary ships. `ers dydd Llun` resolves the Monday and leaves
`ers` in the remainder.

**"For <duration>".** `am` is shipped only as the clock preposition. Its
durational sense — `am awr`, for an hour — has no separate marker, so
`am dair blynedd` must not read as a duration.

**From-to and between ranges.** No worked example fixed the governed forms of a
two-ended range, so `o Fehefin i Awst` and `rhwng Mehefin a Medi` cannot close a
span.

**Before, after and until.** `cyn` is attested as a soft-mutation trigger with a
worked example, but `ar ôl` and `tan` are not, and shipping one edge of the
family alone would read a bounded phrase as an unbounded one. None of the three
ships.

**The millennium.** The dictionary has no Welsh entry for a millennium noun at
all, so the unit is absent rather than transliterated.

**Seasons.** The Welsh word for autumn is spelled exactly like the month
October — `Hydref` — so a season table would make every October a season and
every autumn a month. The whole family is left out until the collision can be
resolved deliberately. `haf 2020` reads as the bare year with `haf` unconsumed.

**Weekend references.** `y penwythnos` does not resolve.

**Era vocabulary and calendar quarters.** `44 CC`, `1990 OC` and `3ydd chwarter`
all refuse. `chwarter` ships as the clock fraction only; the calendar-quarter
sense would need its own attested construction.

**ISO week references.** `wythnos 3` and `3ydd wythnos` refuse.

**The `ac`-joined vigesimal compounds.** A numeral appendix joins 41 to 99 with
`ac` before a consonant, which the coordinator's own attested alternation
contradicts. Rather than pick a side, those compounds are omitted; the decimal
spelling covers the range.

**Reading a year by digit groups.** Welsh reads 1965 as `mil naw chwe pump`, a
construction no order here implements, and the phrase is pinned so it cannot
resolve to that year by some other route.

**`mis` as a month-word introducer.** `ym mis Mawrth` is attested Welsh for "in
March", and the month resolves, but `ym mis` has no slot here and stays in the
remainder rather than being silently swallowed.

**`yn y bore`** and the other articled day-part phrases need a locative
construction this locale does not ship, so the day part in
`dydd Llun nesaf yn y bore` is left unread.

**A spelled quantity with no marker.** `3 diwrnod`, `dwy flynedd` and
`pum mlynedd` on their own refuse: a quantity without a direction marker is
still only a quantity.

## Open questions for a native speaker

1. Is `trennydd` current for the day after tomorrow, and which spelling?
2. What do `ers` and `er` govern, and how do they divide by register?
3. Which cases and mutations does a two-ended `o … i …` range impose?
4. Are `ar ôl` and `tan` mutation triggers, and of which kind?
5. How should the `Hydref` collision between autumn and October be resolved?
6. Is a millennium noun in use at all?
7. Is 41–99 joined with `ac` or with `a` before a consonant?
