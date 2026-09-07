# Catalan (`ca`)

The thing to know before anything else is that Catalan counts quarter hours
toward the hour that is coming, not away from the hour that has passed.
`dos quarts de nou` is 08:30, not 09:30 and not 08:15: it is the second of the
four quarters leading up to nine. `un quart de nou` is 08:15 and `tres quarts
de nou` is 08:45. The vocabulary gives this its own slot, `marker_quarters`,
holding `quart` and `quarts`, and the clock grammar leads with a dedicated
order — `QUARTS quarters of HOUR` — so the count is read before the hour it
counts toward. No other locale in the library ships a `marker_quarters` file;
the construction has no equivalent to borrow from, and the reading survives a
day-part frame, so `dos quarts de nou del vespre` is 20:30.

The second thing is `de la nit`. It is not a uniform twelve-hour shift but a
band that crosses midnight: `les deu de la nit` is 22:00, `la una de la nit`
is 01:00, and `les dotze de la nit` is midnight. The small hours one to five
stay AM, the evening hours six to eleven are PM, and twelve is midnight. The
AM ceiling follows the `matinada` band, and the colloquial reading is cited in
the vocabulary to the Institut d'Estudis Catalans' *Diccionari de la llengua
catalana* (DIEC2) under *nit*.

## What ships

**Weekdays and months** ship wide and abbreviated, and the two-letter weekday
abbreviations `dl dt dc dj dv ds dg` ship as their own vocabulary. Neither
group records a source.

**The date line** is `el 3 d'octubre de 1990`, little-endian, with the article
optional and `de` between the parts. The article is optional inside the date
grammar itself rather than being stripped beforehand, which is what lets `el 3
d'octubre` and `3 d'octubre` both come back clean. The slashed numeric form
reads; the dotted one does not.

**Relative offsets** are `dins`, `dintre` and `en` forward and `fa` backward,
with `enrere` and `endarrere` as trailing past markers, and the grammar takes
both the marker-first and the count-first order.

**The relative determiners** follow the noun — `el dilluns passat`, `la
setmana que ve`, `el dilluns vinent` — which is why the locale sets
`marker_position: post`.

**Ranges** carry the fullest citation record in the locale. The `from` lead is
`de`, `des de`, `del` or `a partir de` and the `to` boundary is `a`, `fins a`,
`fins` or `al`, each attributed in the vocabulary to a specific IEC work: `de`
and `a` as correlative point-of-departure and point-of-arrival prepositions in
DIEC2, `fins` as a limit of time in DIEC2 and in the *Gramàtica essencial de
la llengua catalana* (GEIEC), `a partir de` to Optimot, and the obligatory
contractions `del` and `al` to the IEC *Gramàtica de la llengua catalana*,
section 16.3. The from-lead matters structurally: `a` is a hyper-common
preposition, so a bare `A a B` is only trusted as a range when a from-lead is
present. `entre … i …` is the other frame, cited to DIEC2 under *entre*.

**The clock** subtracts with `menys` — `les quatre menys quart` is 03:45 —
and adds with `i`: `les vuit i mitja`, `les vuit i quart`. `migdia` and
`mitjanit` are points.

**Day parts** are six bands, more than any locale but Tamil and matched only
by German, taken from the Unicode CLDR 47 day-period chart for `ca` and
transcribed in `chronologia/dayparts.py`. The `matinada` is `[00:00, 06:00)`,
the `matí`
`[06:00, 12:00)`, the `migdia` an hour of its own at `[12:00, 13:00)`, the
`tarda` `[13:00, 19:00)`, the `vespre` `[19:00, 21:00)` and the `nit`
`[21:00, 24:00)`. Two of those cuts are worth naming. Catalan opens the
afternoon at 13:00, after an hour-wide noon; only German and Galician carve a
noon band the same way, and Spanish runs its `tarde` straight from twelve.
And Catalan holds the evening open until 21:00 before the night starts — among
the locales whose last band runs to midnight, only Galician and Basque start
it as late. The `vespre` is what makes room for that: the *Gran diccionari de
la llengua catalana* defines it as the "primeres hores de la nit", the early
evening that Spanish has no separate word for.

The `migdia` band ships no day-part vocabulary of its own, so `al migdia`
reaches you as the noon clock landmark, 12:00, rather than as the hour-wide
span.

**Fuzzy month parts** are `principis de`, `mitjan` and `finals de`, cutting
the month into thirds.

**Quarters, ISO weeks, decades and eras.** `el primer trimestre de 2020`,
`setmana 12`, `els anys 80`, `els anys vuitanta`, `44 aC` and `1990 dC` all
resolve, and a before-present marker ships. `la primera meitat de 2020` reads
as the first half-year, with `meitat` cited to DIEC2. The plural year noun
`anys` is kept in its own file away from the singular `any`, because the
*Gran diccionari* glosses `els anys vint` as the decade while `l'any 1931`
names a single year — separating them makes the wrong reading unreachable
rather than merely guarded against.

**Holidays** resolve: `Nadal` comes back as 25 December, by way of the
Andorran civil-holiday table, Catalan being Andorra's official language.

**The Roman calendar anchors** ship in their Catalan vernacular forms
`calendes`, `nones` and `ides`, cited to the Catalan Wikipedia article
*Calendari romà*.

**Habitual recurrence** is `cada dilluns` or `tots els dilluns`. Answered as a
recurrence, these are the repeating Mondays; asked for a span, they come back
as the next Monday with the quantifier left in the remainder.

## Weaker provenance

The weekday and month names carry no recorded source, and neither do the
seasons. The locale sets `hemisphere` to null, so a season never resolves to a
southern-hemisphere reading.

The Roman calendar anchors rest on a Wikipedia article, weaker than the IEC
works the rest of the locale is built on.

The DIEC2 citations name entries on a site that serves its dictionary bodies
from a script rather than in the page, so the entries were not fetched as
written text. Where the same words appear in the *Gran diccionari de la
llengua catalana*, that dictionary corroborates them: *entre* is glossed there
as "en el temps que separa dos moments, dos esdeveniments" and *meitat* as
"cadascuna de les dues parts iguals … en què és dividit un tot". The Optimot
and *Gramàtica de la llengua catalana* locators are named on trust and are
listed here as unchecked.

## What refuses

**Seconds.** `fa 30 segons` returns nothing. No second unit ships.

**The dotted date.** `15.06.2020` returns nothing and does not fall back to
reading 2020 as a lone year. Catalan writes the numeric date with slashes.

**A bare duration.** `quinze dies` returns nothing. A fortnight unit ships,
but a quantity with no direction marker is still only a quantity.

**Half a unit.** `fa mitja hora` returns nothing. `mitja` and `mig` are
declared as the half quantifier, but the relative-offset grammar has no
quantifier slot for them to fill, so only a bare numeral opens an offset.

**Roman-numeral centuries.** `el segle XX` returns nothing.

**Weekday abbreviations on their own.** `dj` returns nothing; the
abbreviations are only reachable inside a larger date.

## Known defects

These are wrong answers, not refusals, and each is reproduced with
`extract_timespan(text, "ca", anchor=datetime(2017, 6, 27, 13, 4))`.

`d'aquí a 3 hores` comes back as 2017-06-28 03:00 with `d'aquí hores` left in
the remainder. The `a 3` is being read as a clock time, so the phrase yields a
point three o'clock tomorrow morning instead of an offset three hours ahead.
`d'aquí a tres dies` returns nothing, which is the safe outcome; the hour unit
is the one that collides with the clock grammar.

`el darrer dilluns d'octubre` comes back as the whole of October with `el
darrer d` stranded, instead of 30 October. `marker_ordlast` holds only
`últim`, `última`, `ultim` and `ultima`; `darrer` is missing from it, and the
parse degrades to the bare month rather than failing. `l'últim dia de març`
resolves correctly, and the Occitan locale gets the same sentence right.

`idus de març` comes back as the whole of March with `idus de` stranded. The
Catalan Wikipedia article the anchors are cited to gives the day as "Idus o
Ides" and only `ides` ships, so `ides de març` is correct at 15 March while
its equally attested twin silently widens to the month.

`el 1r de gener` comes back as the whole of January with `el 1r de` stranded,
where `el primer de gener` resolves to 1 January. The ordinal suffix `r` is
declared, but the abbreviated ordinal does not reach the day slot.

`fins al 12 de juny` and `abans del 5 de juny` push their bound into 2018
while the other end stays at the anchor, producing a span nearly a year long.
The future preference is applied to the bound in isolation rather than
relative to the open end.

## Open questions for a native speaker

1. Where does `de la nit` stop being AM? The ceiling follows the `matinada`
   band at five, but `les cinc del matí` and `les cinc de la matinada` are
   both ordinary Catalan.
2. Should `dos quarts` accept a bare `quarts de nou` without a count, and is
   the half-quarter (`un quart i mig de nou`, 08:22 or 08:23) worth reading?
3. Is `darrer` in `el darrer dilluns d'octubre` the ordinary written form, or
   is `últim` the one to prefer once both are accepted?
4. Does the `migdia` band want a day-part surface of its own, so that `al
   migdia` names the hour rather than the point?
