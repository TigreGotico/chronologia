# Spanish (`es`)

`de la noche` is not a twelve-hour shift, and getting that wrong is the fastest
way to be an hour or twelve out. Spanish uses the phrase across the whole
colloquial night, so `las diez de la noche` is 22:00 but `la una de la noche`
is 01:00 and `las doce de la noche` is midnight. The vocabulary encodes this as
a band rather than a uniform PM offset: the small hours one to five stay AM,
the evening hours six to eleven are PM, and twelve is midnight. The AM ceiling
follows the `madrugada` band, and the colloquial use of `de la noche` for the
small hours is cited to RAE's dictionary entry for *noche*.

The second thing to know is that `mañana` is two words in one. It is the
morning and it is also tomorrow, and the tomorrow reading wins. The locale
does not guess: `daypart_ref` in `lang.json` deliberately omits the bare order,
so the day-part reading only fires when an article, a demonstrative or `de`
licenses it. A bare `mañana` is tomorrow; `por la mañana` is the morning.

## What ships

**Weekdays and months** ship wide and abbreviated. The vocabulary records no
source for them.

**The date line** is `el 3 de octubre de 1990`, little-endian with `de` between
each part, and it also reads without the article and without the year. Spanish
additionally has a day-label idiom, `día 3 de octubre`, where `día` heads the
date rather than being part of it. The vocabulary cites RAE's *Ortografía* and
the *Diccionario panhispánico de dudas* under *día* for that being a genuine
temporal function word, and registers it as its own marker so that a leading
`día` gets folded into the consumed text exactly when the date it labels
actually bound — never when the date fails, so a `día` elsewhere in the
sentence is left alone. The slashed numeric form reads; the dotted one does
not.

**Relative offsets** are `dentro de` forward and `hace` backward, and
`lang.json` also accepts the count-first order with a trailing marker.

**The relative determiners** follow the noun — `el lunes pasado`, `la semana
que viene` — which is why the locale sets `marker_position: post`.

**Ranges** are the best-documented part of this locale. The `from` lead is
`de`, `desde`, `del` or `a partir de`, and the `to` boundary is `a`, `al` or
`hasta`, each cited in the vocabulary to a specific RAE work: `de` and `a` as
correlative point-of-departure and point-of-arrival prepositions from the
*Diccionario panhispánico de dudas*, `desde` and `hasta` from the *Diccionario
de la lengua española*, `a partir de` as a prepositional locution, and the
obligatory contractions `del` and `al` to RAE-ASALE's *Nueva gramática* and
*Ortografía*. The reason the from-lead matters structurally is that `a` is a
hyper-common preposition in Spanish, so a bare `A a B` is only trusted as a
range when a from-lead is present. `entre … y …` is the other frame, cited to
RAE's entry for *entre*.

**The clock** has two toward-the-hour constructions and they are not the same
shape. `las cuatro menos cuarto` subtracts from the hour already named;
`un cuarto para las cuatro` states the fraction first and then the hour it is
heading for. Both give 03:45, and the vocabulary keeps `menos` and `para`
separate for exactly that reason. Forward is `y` — `las ocho y media`, `las
ocho y cuarto`. `mediodía` and `medianoche` are points.

**Day parts** take their boundaries from the Unicode CLDR 47 day-period chart
for `es`, transcribed in `chronologia/dayparts.py`, with the surfaces cited to
RAE's dictionary. There are four bands and two of them have no English
equivalent. The `madrugada` is `[00:00, 06:00)`, the small hours, which English
has no single word for. The `mañana` runs `[06:00, 12:00)`. The `tarde` runs
`[12:00, 20:00)` — one span across what English splits into afternoon and early
evening, which RAE glosses as the part of the day between midday and nightfall.
The `noche` then runs `[20:00, 24:00)`. The frame Spanish puts in front of a
day part is `por`, cited to RAE's entry for *por*; unlike Galician `pola` and
Portuguese `pela` it does not contract with the article, so the article follows
it as its own word.

**Fuzzy month parts** are `principios de`, `mediados de` and `finales de`,
cutting the month into thirds.

**Quarters, ISO weeks, decades and eras.** `el primer trimestre de 2020`,
`semana 12`, `los años 80`, `44 a. C.` and `1990 d. C.` all resolve, and a
before-present marker ships. `la primera mitad de 2020` reads as the first
half-year, with `mitad` cited to RAE's dictionary.

**The Roman calendar anchors** ship in their Spanish vernacular forms
`calendas`, `nonas` and `idus`, cited to the Spanish Wikipedia article
*Calendario romano*, so `los idus de marzo` resolves.

**Habitual recurrence** is `los lunes`. The vocabulary holds only the plural
articles and says why: RAE's entry for *el* gives the plural article on a
weekday noun the habitual reading, while the singular `el lunes` names the
single next Monday, so excluding `el` and `la` makes the singular reading
structurally unreachable rather than merely guarded against. As a recurrence
this is answered by the recurrence edge; the span edge reads `los lunes` as
the next Monday and leaves the article in the remainder.

## Weaker provenance

The weekday and month names carry no recorded source. Nor do the seasons, and
the locale sets `hemisphere` to null, so a season does not resolve to a
southern-hemisphere reading for Spanish outside Spain.

The Roman calendar anchors rest on a Wikipedia article, which is a weaker
source than the RAE works the rest of the locale is built on.

## What refuses

**Seconds.** `hace 30 segundos` returns nothing. No second unit ships.

**The dotted date.** `15.06.2020` returns nothing, and it does not fall back
to reading 2020 as a bare year either. Spanish writes the numeric date with
slashes, and `15/06/2020` reads.

**A bare duration.** `quince días` returns nothing. A fortnight unit ships,
but a quantity with no direction marker is still only a quantity.

**A bare `mañana` as the morning.** It resolves, but as tomorrow. The morning
reading is not reachable without an article, a demonstrative or `de`, and that
is a refusal of the ambiguous reading rather than a gap.

## Open questions for a native speaker

1. Where exactly does `de la noche` stop being AM? The vocabulary puts the
   ceiling at five, following the `madrugada` band, but `las cinco de la
   mañana` and `las cinco de la madrugada` are both ordinary Spanish.
2. Should the seasons resolve differently for southern-hemisphere Spanish, and
   if so what would select that?
3. Are `calendas`, `nonas` and `idus` the forms Spanish historical writing
   uses, or does it keep the Latin?
4. Is `día` ever used in a way that would make folding a leading `día` into a
   date wrong?
