# Aragonese (`an`)

Aragonese is a Pyrenean Romance language that sits between Spanish and
Catalan and shares a great deal of vocabulary with both. That is the whole
difficulty of the locale. A surface that looks Aragonese is very often simply
Spanish, and a surface that is genuinely Aragonese frequently differs from its
Spanish cognate only by a letter or an accent. Every group below was therefore
checked against an Aragonese source — the Aragonese Wiktionary, the Aragonese
Wikipedia, or a dictionary those two cite — rather than against a Spanish one.

The locale carries Spanish spellings deliberately alongside the Aragonese
ones. `día` sits next to `diya`, `año` next to `anyo`, `mediodía` next to
`meydia`, `tarde` next to `tardi`. Written Aragonese is not standardised in
practice and Castilian spellings appear constantly in real text, so accepting
them costs nothing and refusing them would lose ordinary sentences.

## What ships

**Months.** `chinero`, `chunyo`, `chuliol`, `setiembre`, `aviento` and
`deciembre` each have an Aragonese entry on the English Wiktionary; `aviento`
is from Latin *adventus*, and Wiktionary's entry compares it with Asturian
*avientu*. December ships both `aviento` and `deciembre`. The rest — `febrero`,
`marzo`, `abril`, `mayo`, `agosto`, `octubre`, `noviembre` — are identical to
their Spanish forms and are shipped as they stand.

**Weekdays.** `luns`, `miercres` and `dominche` are the three that separate
Aragonese from Spanish, and all three occur in Aragonese Wikipedia running
text. `martes`, `chueves`, `viernes` and `sabado` have Aragonese Wiktionary
entries; `chueves` is derived there from Latin *Iovis (dies)* with the variant
`chuebes`.

**The date line** is `15 de chinero de 2020` — day, `de`, month, `de`, year —
with an optional leading article. Day and month order is day-first.

**Relative offsets.** The past marker is `fa`, preposed: `fa tres diyas`, `fa
un anyo`. The future is `en` or `dentro`, also preposed: `en tres diyas`,
`dentro de tres diyas`. Both take the count-one quantifiers `un`, `una` and
`uno`, so `fa un anyo` reads without a digit.

**The clock.** Minutes are added with `e` and subtracted with `menos`, the
ordinary Ibero-Romance pattern: `as tres e meya` is 03:30, `as tres menos
quarto` is 02:45. The half is `meya` or `meyo`, the quarter `quarto`. Noon is
`meydia`, `meydiya` or `mediodía`; midnight is `meyanueyt` or `meyanuei`.

**The night band.** `de nueyt` is not a uniform twelve-hour shift. It is a band
that crosses midnight: hours one through five stay in the small hours, hours
six through eleven move to the evening, and twelve is midnight. All twelve
hours were checked, and `a la una de nueyt` is 01:00, `a las seis de nueyt` is
18:00, `a las once de nueyt` is 23:00, `a las doce de nueyt` is 00:00. The 5|6
cut is not from an Aragonese source. It is inherited from the sibling
Ibero-Romance locales, whose boundary comes from the Spanish, Catalan and
Portuguese reference dictionaries, and the locale file says so.

**Century and decade.** `sieglo` has an Aragonese Wiktionary entry, a
semi-learned borrowing from Latin *saeculum*, sourced there to Bal Palazios'
*Dizionario breu de a luenga aragonesa*. `decada` and `decenio` are not
entries there — the Aragonese Wiktionary carries `década`/`decenio` only with
Spanish sections — but both have Aragonese sections on the English
Wiktionary, `decada` from Latin *decadem*, with the *Diccionario ortografico
de l'aragonés* under further reading, and that is the source the vocabulary
file itself cites.

**The decade frame** is `os anyos 80`, the plural year noun with a two-digit
number. Only the plural `anyos` reaches that slot: the singular `anyo` names
one year and must not be read as a decade. The plural is sourced through the
Wiktionary entry for `anyo`, which cites the *Aragonario, diccionario
castellano–aragonés*.

**Markers.** `dimpués` and its variants for "after", `antis` and `denantes`
for "before", `dende` for "since", `dica` and `entro a` for "until", `a partir
de` for "from", `cada` for "every", `agora` and `ara` for the present.
`dica` and `dende` have Aragonese sections on the English Wiktionary deriving
them from Latin *de hinc ad* and *deinde*. The locative `en` used with a
month name — `en chinero` — is sourced in the locale file to the dictionary
of the Academia de l'Aragonés.

**Habitual recurrence** is `cada luns`. Answered as a recurrence, this is the
repeating Monday; asked for a span, it comes back as the next Monday with
`cada` left in the remainder.

## Weaker provenance

**`ivierno`.** The winter file lists `ivierno` and `hibierno`. Only
`hibierno` was found: it has an entry on the Aragonese Wiktionary with a full
noun paradigm. `ivierno` returned nothing on either the Aragonese Wiktionary
or the Aragonese Wikipedia, and the English Wiktionary has it only as Old
Spanish. It is the weakest surface on the page.

**`meyanueyt`, `pasadoman` and `antesdayere`** likewise returned no hits in
Aragonese Wikipedia text and have no Wiktionary entry. They are transparent
compounds of parts that are all attested — `meya` plus `nueyt`, `pasado` plus
`man`, `antes de ayere` — but the compounds themselves were not found.

**`tardi` as an afternoon word.** It ships as the PM meridiem. Aragonese
Wikipedia has it in quantity, but the great majority of those occurrences are
the adverb "late", as in `mas tardi`. The afternoon noun reading is the one the
locale needs and is the one less visible in the corpus.

**The 5|6 night cut** is transcribed from the sibling locales, not from an
Aragonese source, as the locale file states.

**A claim in the locale file that does not check out.** The decade file says
the Wiktionary entry for `decada` lists `decenio` as a synonym. Fetched, that
entry carries no synonym line. Both words are real and both have their own
Aragonese entries; the cross-reference between them is not where the comment
places it.

## What refuses

**Roman-numeral centuries.** `o sieglo XX` returns nothing, although Aragonese
Wikipedia writes centuries that way constantly. `20 seclo`-style digit forms
are what the century construction accepts.

**A trailing "before" or "after" on an offset.** `tres diyas antis` and `tres
diyas dimpués` both return nothing. The offset orders take the marker before
the count or after the unit, but the anchorless trailing reading of `antis` is
not among them.

**A bare duration.** `meya hora` and `tres horas e meya` return nothing. A
duration with no anchor is not a span.

## Known defects

These are wrong or lossy outputs, not refusals, and each is reproducible with
`extract_timespan(text, "an", anchor=datetime(2017, 6, 27, 13, 4))`.

A leading bare `a` is stranded whenever `a las` introduces a time. `a las tres
e meya` gives the right 03:30 but leaves `a` in the remainder, and so do `a las
tres e quarto` and `a las 15:30`. The at-marker file lists `las` but not the
two-word `a las`, so the preposition orphans. The value is correct; the span
does not cover the phrase.

`a las nueu de maitín` gives 09:00 and strands `maitín`. The morning file lists
`maitin` unaccented, and the unaccented form parses cleanly, but Aragonese
Wikipedia writes `maitín` far more often than `maitin`. The accented spelling
is the common one and the locale does not accept it.

`trimestre 3 2020` returns the whole of 2020 with `trimestre 3` stranded. This
is the worst shape a result can take: a plausible span over the wrong unit,
with the words that named the real unit thrown away.

`a las tres i meya` returns 03:00 with `i meya` stranded. `i` is not an
Aragonese conjunction and is not in the locale, so the input is arguably not
Aragonese — but the engine answers it with a wrong-hour span rather than
refusing.

## Open questions for a native speaker

1. Is `ivierno` a real Aragonese spelling of winter, or should the locale ship
   only `hibierno`?
2. Are `meyanueyt`, `pasadoman` and `antesdayere` the ordinary words, and are
   there commoner variants?
3. Does the night band really turn at six, or at some other hour in Aragonese?
4. Is `tardi` used as a noun for the afternoon, or is `tardada` the noun and
   `tardi` only the adverb?
5. Which is the everyday word for today, `hue` or `huei`?
