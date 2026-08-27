# Macedonian (`mk`)

Macedonian has no case system, which decides the whole shape of the locale.
Where the Russian or Croatian folds carry genitive tables for days, hours and
feminine ordinals, Macedonian needs none of that machinery: every relative-time
string is a bare noun phrase whose parts do not agree in case. The locale is
built on the analytic pattern Bulgarian uses, with two Macedonian-specific
complications — a postpositive definite article that can attach to any noun,
and a count form distinct from the general plural.

The clock is the other decision worth knowing before you read further.
Macedonian counts minutes forward from the hour already named, all the way to
fifty-nine. There is no "five to nine" construction, and the locale ships none.

## What ships

**Weekdays and months** come from Unicode CLDR 47, `cldr-dates-full/main/mk/ca-gregorian.json`,
in both the wide and abbreviated widths. The abbreviations are written with a
trailing dot in CLDR, which the tokenizer drops, so `сеп` matches as well as
`септември`. Sunday is `недела`, which is also the colloquial word for a week;
only the Sunday reading ships on the singular, and the week is `седмица`, CLDR's
own display name for that field, so the two surfaces never contend.

**The date line** is little-endian: day, month, year, with a literal trailing
`г.` abbreviating `година`. That comes from the `dateFormats` block of the same
CLDR file, and it is why `marker_year_word` accepts the bare `г` alongside
`година` and `годината`.

**Relative offsets** come from `dateFields.json` in the same CLDR release,
where every past pattern is `пред {0} …` and every future one `за {0} …`.
Wiktionary's Macedonian entry for `пред` supplies the "ago" sense directly
("се вселивме пред две години"). The named days — `вчера`, `денес`, `утре`,
`завчера`, `задутре` — are all CLDR relative-type entries; `денеска` and
`другиден` are the current variants Wiktionary lists alongside `денес` and
`задутре`.

Year is the one unit where Macedonian prefers a dedicated word to a
periphrasis. CLDR gives `лани` for last year and `догодина` for next year as
the full forms, with `минатата година` / `следната година` appearing only in
the short and narrow widths. Both ship. Every other unit uses the periphrastic
`минат-` / `следн-` adjective, which agrees in gender with its noun, so the
locale carries the whole inflected set rather than one representative form.

**The count form** is the trap the unit files exist to handle. Macedonian
distinguishes the plural a noun takes on its own from the shape it takes behind
a numeral. The plural of `ден` is `денови`, but five days ago is `пред 5 дена`,
and `дена` is what CLDR spells every counted day offset with. Only the count
form ships, because `денови` counts nothing. `час` behaves the same way:
general plural `часови`, count form `часа`. Wiktionary's entries for `ден` and
`час` give both forms; CLDR confirms which one the counting patterns use.

**The clock** is additive only. The evidence is a style guide at reper.net.mk
written specifically to teach how to write Macedonian times, whose worked
examples are `девет и петнаесет` (9:15), `девет и пол` (9:30) and, decisively,
`дваесет и еден и педесет` for 21:50 — twenty-one and fifty, counted forward.
`и` is the only direction word, and `пол` is the only fraction word. No
quarter-hour noun ships: the same guide writes the quarter with the minutes
spelled out. The hour noun carries the definite article when it names a clock
time (`три часот е`), so `часот` and `часа` are accepted alongside `час`.

**Day parts** follow the CLDR day-period rules for `mk` in
`cldr-core/supplemental/dayPeriods.json`, transcribed in `chronologia/dayparts.py`:
night 00:00–04:00 (`ноќе`), morning 04:00–10:00 (`наутро`), a second morning
band 10:00–12:00 (`претпладне`), afternoon 12:00–18:00 (`попладне`) and evening
18:00–24:00 (`навечер`), with midnight and noon as points. That is a six-band,
two-point system, and no further bands were invented to fill it out. The
stand-alone forms `утро` and `вечер` ship alongside the adverbial ones because
CLDR gives them for the same bands.

**Numerals** come from Wiktionary's `Module:number_list/data/mk`. Compounds
join tens to units with `и` (`дваесет и еден`), which is the same word the
clock uses as its direction marker; the fold in
`chronologia/extract/numfold_macedonian.py` handles the overlap. The
cardinal for one is gender-marked (`еден` / `една` / `едно`) and all three
forms are registered as quantifiers, so a feminine noun does not lose its
"one".

**Markers** are split between CLDR and the Macedonian Wikipedia article
"Предлози во македонскиот јазик", which catalogues the prepositions sense by
sense. `до` for "until" is its §До ("достигнување до извесен временски момент",
worked example `до полноќ`); `за` for a measured extent is its §За; `по` for
temporal succession is its §По; `меѓу` and `помеѓу` for "between" are its §Меѓу.
The rest — `пред`, `секој`, `овој`, `минат`, `следн-` — are Wiktionary entries
or CLDR relative-time patterns.

## Weaker provenance

`на` ships as the adnominal linker for phrases like `петтиот ден на месецот`.
Unlike the other markers it is not tied to a named section of the prepositions
article or to a CLDR pattern; it is the ordinary genitive-replacing linker of a
caseless Slavic language, and the locale uses it in that structural role only.

`другиден` for the day after tomorrow rests on Wiktionary listing it as a
synonym of `задутре`, not on a corpus attestation of its own.

## What refuses

**Minutes to the hour.** `без пет девет` returns nothing, and no
`clock_dir_to.voc` exists. This is an active refusal rather than a gap. Two
sources were checked specifically for it: the reper.net.mk style guide, built
to teach correct time expression, uses only additive forms including for the
half hour; and the Macedonian Wikipedia prepositions article has a dedicated
§Без covering every attested sense of `без` — lack (`без пари`, `без вода`) and
the conjunction `без да` — and names no temporal sense at all. A grammar
written to enumerate every sense of the word finding no clock sense is stronger
evidence than mere absence. Bulgarian has the construction; Bulgarian is not a
safe donor here.

**"Since" as a standalone marker.** `од понеделник` parses the weekday and
leaves `од` in the remainder. No dedicated temporal example for `од` turned up
in CLDR, in the prepositions article, or in targeted searching, so the locale
does not claim the sense. The `од … до …` range is a different matter and is
attested; what is refused is treating a bare `од X` as "since X".

**Century and millennium offsets.** `пред 2 века` returns nothing. `век` and
`милениум` are not among the CLDR `dateFields` units, so no count form for
either is attested, and none was invented.

**A quarter-hour word.** Macedonian writes the quarter as `и петнаесет` with
the minutes spelled out, so nothing binds a `четврт`-style fraction.

**The general plurals `денови` and `часови`** are deliberately absent from the
unit files. They are correct Macedonian, but they never appear behind a
numeral, which is the only position the offset construction reads.

## Open questions for a native speaker

1. Does a colloquial or regional minutes-to-the-hour form with `без` exist?
   Both sources consulted are prescriptive and written, so a casual spoken form
   is unattested rather than ruled out.
2. Is there a dedicated "since" construction, and is `од` it? A confirmation
   either way would let the sense ship or be recorded as genuinely absent.
3. What are the count plurals of `век` and `милениум`, if the words take one at
   all?
4. Does the purely additive clock still read naturally past `:45` in fast
   speech? The worked example that settles the direction only reaches `:50`.
