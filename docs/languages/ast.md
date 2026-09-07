# Asturian (`ast`)

Asturian is the thinnest-sourced of the Ibero-Romance locales here. Almost
nothing in its vocabulary files carries a citation: the three Roman-calendar
anchors name the Asturian Wikipedia, the night meridiem names the Spanish
locale it was copied from, and every other file — weekdays, months, seasons,
markers, units, eras — carries none at all. That is the fact a reader should
hold onto, because the locale's neighbour is Spanish and a great many Asturian
surfaces look like Spanish surfaces with the endings changed. Where this page
says a word is attested, it means the word was found in the *Diccionariu de la
Llingua Asturiana* published by the Academia de la Llingua Asturiana, not that
it resembles its Spanish cognate.

The other governing fact is that the Unicode day-period table has no Asturian
row. Its authority for this language stops at the bare meridiem markers, so no
time-of-day band ships and `pela mañana`, `pela tarde` and `pela nueche` — the
frames the Academia's own dictionary uses in its definitions — are not read as
parts of the day. What `pela mañana` does instead is a defect, and it is
listed below.

## What ships

**Weekdays and months.** The month names are the Asturian ones — `xineru`,
`xunetu`, `ochobre`, `payares`, `avientu` — with the Castilian-shaped
`noviembre` and `diciembre` alongside the last two. The Asturian forms were
confirmed in the Academia's dictionary, which dates the year as running from
`l'un de xineru` to `el trenta y un d'avientu`, glosses October as the `mes de
(les) castañes`, and puts All Souls' Day on the `día primeru de payares`.
`llunes` and `vienres` are dictionary headwords, glossed as the first and
fifth days of the week.

**The date line** is little-endian: `3 de xineru 1990`, `25 d'avientu`. The
apostrophe form of `de` before a vowel is in the of-marker vocabulary, so
`d'avientu` and `d avientu` both read.

**Relative offsets** run in both directions and in both orders. `hai` and
`fai` count backward, `en` and `dientro` forward. `dempués` and `enantes` are
dictionary headwords; `dientro` is one too, and the dictionary lists `dientro
de` as a locution under it.

**Last and next** follow their noun — the locale sets `marker_position:
post` — as `pasáu` and `viniente`. `viniente` is not a headword in the
dictionary but appears inside the entry for `añu`, in the locution `al otru
añu, al añu siguiente o viniente`, which is where it was checked.

**Ranges** are `de … a …`, `del … al …`, `dende …` and `hasta …`, with `ente …
y …` as the between-frame. `dende` and `hasta` are both dictionary headwords
with the temporal sense the locale uses, `hasta` glossed with the clock
example `Tuvimos hasta les cinco`.

**The clock** counts forward with `y` and backward with `menos`, and takes the
feminine plural article the language uses for hours: `a les ocho`, `les cinco
y media`, `les cinco menos cuartu`. That article is not decoration — the
dictionary lemmatises the hour itself as `cinco, les`, glossed as the fifth
hour from noon or from midnight.

**`de la nueche` is a band, not a shift.** `les diez de la nueche` is 22:00
and `les doce de la nueche` is midnight; the small hours one to five stay AM
and the evening hours six to eleven are PM. The dictionary's `nueche` entry
supports the span, glossing it as the stretch of time when there is no
sunlight.

**Non-Gregorian calendars.** Asturian is one of six locales that carry French
Republican month names — the others are English, French, Italian, Occitan and
Romanian — and it also carries the Hebrew and Islamic civil months, the
Japanese era names, a consulship marker and a `pridie` marker for Roman dates.
What that costs is set out below.

**Eras and geological periods.** `44 adc` resolves, along with the spelled
`enantes de Cristu`, an anno mundi marker, a Holocene era marker, a Julian day
marker, a Unix time marker, and twenty-eight geological period names from the
Archean to the Holocene.

**The Roman calendar anchors** ship in the Asturian vernacular forms
`calendes`, `nones` and `idus`, with the Latin forms kept alongside, cited to
the Asturian Wikipedia article *Calendariu romanu*. That article does contain
all three, in one sentence, which was checked.

## Weaker provenance

**The night band's boundary is Spanish, not Asturian.** The night meridiem
file says so in as many words: Asturian inherits the 5-versus-6 cut from the
Spanish, Catalan and Portuguese siblings, whose boundary rests on the Spanish
academy's dictionary, and native confirmation for Asturian is still open. This
is the one place in the locale where a Spanish source is doing the work for an
Asturian surface, and it is declared rather than hidden.

**`fasta` is not in the Academia's dictionary.** The until-vocabulary ships
`fasta` beside `hasta`, and a search of the dictionary returns the `hasta`
headword and nothing for `fasta`. It may be a regional variant the dictionary
does not lemmatise; on the evidence gathered it is unattested.

**`quevien` is not attested as one word.** The next-marker ships the joined
`quevien`, which the dictionary does not carry in any form. The two-word `que
vien` parses anyway, so nothing is lost by the joined form being wrong, but
nothing supports it either.

**The French Republican months are the French spellings, unadapted.**
`brumaire`, `nivose`, `ventose` and the rest are exactly the forms the French
locale ships, with no Asturian adaptation and no source. They also arrive
without the ordinal-and-anchor guard the Latin dates get, so a bare
`brumaire` resolves to a month-long span in the Gregorian year — see the
defects.

**`mediudía` is not the dictionary's noon word.** The noon landmark ships
`mediudía` and `mediudia`. The word that appears throughout the Academia's
definitions is `meudía`, which the locale does not carry at all, so `el
meudía` returns nothing.

**Everything else is uncited.** Weekday names, season names, unit nouns, era
spellings, the geological series, the Japanese era names and the Hebrew and
Islamic month lists all ship without a recorded source. The seasons in
particular are worth a native's eye: `seronda` for autumn and `branu` for
summer are the distinctively Asturian words, both confirmed in the dictionary,
but they ship beside the Castilian-shaped `otoñu` and `veranu`, which were
not.

## Unchecked and broken citations

Both citations the locale carries were fetched and hold. The Asturian
Wikipedia *Calendariu romanu* contains `calendes`, `nones` and `idus`. The
Spanish night-meridiem file that the Asturian one defers to does cite the
Spanish academy's `noche` entry for the small-hours usage, so the inherited
boundary has a source — a source about Spanish.

The Academia de la Llingua Asturiana's dictionary is a POST-driven search with
no per-word URL, so headwords are cited here by name rather than by link. Each
word named above as attested was looked up individually.

## Known defects

Every one of these is reproduced against the anchor 2017-06-27 13:04 with
`extract_timespan(text, "ast", anchor)`. They are wrong answers rather than
refusals, and a wrong span with a stranded remainder is worse than nothing at
all.

**The date line loses its year when the year is introduced by `de`.**
`3 de xineru de 1990` returns 2018-01-03 to 2018-01-04 with `de 1990` in the
remainder — twenty-eight years off, silently. The calendar-date orders reach
`DAY of? MONTH YEAR?` but never `DAY of MONTH of YEAR`, so the second `de`
breaks the match and the yearless reading wins with the future preference
pushing it into next January. `3 de xineru 1990` and `3 xineru 1990` are both
correct. `3 de xineru del 1990` fails the same way.

**A leading article is never claimed.** `el 3 de xineru` resolves the day and
leaves `el` behind; `el 3 de marzu`, `el mediudía`, `la medianueche`, `nel añu
1990` and `en xineru` all do the same with their own leading word. The
article vocabulary itself is generous — it folds in the
preposition-plus-article fusions `del`, `de la`, `al` and `a la`, the
indefinites and the demonstratives — but no calendar-date order offers an
article slot for any of it to fill, and the during-slot holds only `durante`,
so the locative `en` cannot be absorbed by a month either.

**Combining the two loses the clock as well.** `1 de xineru de 2020 a les
15:30` returns 2018-01-01 as a whole day with `de 2020 a les 15:30` in the
remainder: the wrong year, the wrong granularity, and a time of day thrown
away.

**A quarter reads as a whole year.** `el primer trimestre de 2020` returns
2020-01-01 to 2021-01-01 with `el primer trimestre de` in the remainder. Four
times too long. `la década de 1980` fails in the mirror image, returning the
single year 1980 with `la década de` stranded.

**Day-part phrases return tomorrow.** `pela mañana`, `de mañana` and `a la
mañana` all return 2017-06-28, the whole of the next day, because `mañana` is
in the morning-meridiem vocabulary and also in the named-day vocabulary as
*tomorrow*, and with no day-part band to reach, the tomorrow reading is the
only one available. `el sábadu pela mañana` returns the whole of Saturday with
`pela mañana` visible. `pela tarde`, `pela nueche` and a bare `nueche` return
nothing, which is the honest outcome; the morning cases are not.

**One o'clock does not parse.** `la una de la nueche` returns nothing, though
`les diez de la nueche` is correct, and the same gap holds with any other
meridiem. The night-clock test file records this as a pre-existing hole.

**Unadapted French Republican months bind unguarded.** `brumaire` alone
returns 2016-10-22 to 2016-11-21, and `1 de brumaire` returns 2017-10-22 — a
Gregorian span for a Republican month name, with the Republican year nowhere
in it. `18 de brumaire del añu VIII` returns 2017-11-08 and leaves `del añu
VIII` in the remainder, which is the one case where the discarded text is the
part that mattered.

**Declared quantifiers do not reach the offset rule.** The locale declares
`par` and `pareya` as two and `dellos`, `delles`, `unos`, `unes` as three, but
`un par de díes`, `dellos díes` and `un día` all return nothing.

**Two more return nothing where the vocabulary suggests they should.**
`dientro de tres díes` and `dempués de xunu` both fail, as do `los años 80`,
`el sieglu XX` and `ente selmana`.

## Open questions for a native speaker

1. Where does `de la nueche` stop being AM in Asturian specifically? The
   boundary in use is the Spanish one, and nothing Asturian has confirmed it.
2. What are the day-part bands? Nothing supplies them, so `pela mañana` and
   `pela tarde` cannot resolve to a stretch of the day at all.
3. Is `fasta` a real Asturian variant of `hasta`?
4. Is `meudía` or `mediudía` the standard noon word?
5. Are `otoñu` and `veranu` in ordinary use beside `seronda` and `branu`, and
   should both pairs ship?
6. Do the French Republican months have Asturian forms, and does anything
   Asturian actually use them?
7. Is `ente` or `entre` the ordinary between-preposition, and does `ente
   selmana` mean "on a weekday" as the dictionary's locution suggests?
