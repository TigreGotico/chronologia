# Dutch (`nl`)

`'s nachts` is a band that crosses midnight, and that single fact governs how
Dutch clock times land. `drie uur 's nachts` is 03:00, `elf uur 's nachts` is
23:00, and `twaalf uur 's nachts` is midnight. It is not a twelve-hour shift
and it is not an AM half: the small hours one to five stay AM, the late hours
six to eleven are PM, and twelve is midnight. The AM ceiling follows the CLDR
`nacht` band for Dutch, `[00:00, 06:00)`. The other three postposed day-part
words behave straightforwardly — `'s ochtends` and `'s morgens` keep a bare
twelve-hour reading in the AM half, `'s middags` and `'s avonds` push it into
the PM half.

The `'s` itself is a fossilised genitive particle, from `des`. The tokenizer
strips the apostrophe, so what reaches the grammar is a bare `s`, and the clock
orders consume it optionally before the day-part word.

The half hour names the coming hour, as in German: `half acht` is 07:30.

## What ships

**Weekdays and months** ship wide and abbreviated, with no recorded source.

**The date line** is little-endian, and Dutch is one of the languages that
writes the dotted civil date, so `15.06.2020` reads, as does `15-06-2020`.
`ordinal_dot` is off.

**Relative offsets** are `over` forward and `geleden` backward, with the marker
allowed on either side of the count and an optional indefinite article between.

**A quarter of an hour is a unit of its own.** `kwartier` is not a clock
fraction in Dutch but a countable noun, and it ships with its diminutive
`kwartiertje` and both plurals, so `over een kwartier` resolves to a
fifteen-minute span a quarter of an hour from now.

**The clock** counts forward with `over` and back with `voor` — `kwart over
acht`, `kwart voor negen` — and the bare half names the coming hour.
`middernacht` is midnight and `middag` is noon. `uur` is the o'clock word.

**Day parts** take their boundaries from the Unicode CLDR 47 day-period chart
for `nl`, transcribed in `chronologia/dayparts.py`: `nacht` `[00:00, 06:00)`,
`ochtend` `[06:00, 12:00)`, `middag` `[12:00, 18:00)`, `avond` `[18:00,
24:00)`. The surfaces are cited to the Algemeen Nederlands Woordenboek at the
Instituut voor de Nederlandse Taal. The `avond` runs to midnight and the
`nacht` takes over after it.

Dutch has a fused today-plus-band word for each band, and those ship as their
own surfaces because they already name today's band rather than composing with
the clock's future-roll rule: `vanavond`, `vanochtend`, `vannacht` and
`vanmorgen`. `vanmorgen` is the one worth explaining. It is a synonym of
`vanochtend` that the ANW carries as its own entry, and the `morgen` inside it
is the older Dutch word for the morning itself, as in `goedemorgen` — not the
`morgen` that means tomorrow everywhere else in this locale. The two never
compete, because `vanmorgen` is a single fused token and not a split `van` plus
`morgen`.

**Ranges** are `van … tot …` and `tussen … en …`, with `sinds` opening one that
runs to the anchor and `tot` closing one that starts there.

**Quarters, ISO weeks and eras.** `het eerste kwartaal van 2020`, `week 12` and
`44 v.Chr.` all resolve, along with an AD marker and a before-present marker.

**The Roman calendar anchors** ship in their Dutch vernacular forms
`kalenden`, `nonen` and `iden`, cited to the Dutch Wikipedia articles on the
Nones and the Ides, so `de iden van maart` resolves.

**The ordinal-last determiner** is `laatste`, the invariant attributive
superlative of `laat`, cited to Van Dale, so `de laatste zaterdag van
augustus` resolves.

## Weaker provenance

The Roman anchors rest on Wikipedia articles rather than on the ANW or Van Dale
that the rest of the locale draws on.

The weekday and month names, the seasons and the holiday vocabulary carry no
recorded source.

## What refuses

**The `middag` band as a day part.** `vanmiddag` returns nothing, and `deze
middag` resolves the noon point rather than the afternoon band, leaving `deze`
in the remainder. The word `middag` is bound as the noon landmark, so the band
it also names has no vocabulary of its own — the same collision German has
between `Mittag` the hour and `Mittag` the point.

**Decades.** `de jaren 80` returns nothing. The locale declares no decade
construction and ships no decade words, so neither the digit form nor a spelled
one reads.

**Seconds.** `30 seconden geleden` returns nothing. No second unit ships.

**A bare duration.** `twee weken` and `een kwartier` return nothing on their
own. A quantity with no direction marker is still only a quantity; with one,
`over een kwartier` reads.

**Recurrence.** `om de twee weken` returns nothing from the span edge. The
`om de` frame is registered as a recurrence marker, and it is the recurrence
edge that answers it.

## Open questions for a native speaker

1. How should the afternoon band be reachable at all, given that `middag` is
   also the noon point? `vanmiddag` and `'s middags` are ordinary Dutch and
   only the second of them reads.
2. Should `de jaren 80` and `de jaren tachtig` resolve, and which spelled
   decade forms are current?
3. Is `half juni` the ordinary way to say mid-June? It resolves the whole
   month with `half` unread, because the mid-month part words are `midden` and
   `medio`.
4. Should the uninflected `komend` join `komende` as a "next" determiner?
   `komend weekend` leaves `komend` unread.
5. Are `kalenden`, `nonen` and `iden` the forms Dutch historical writing uses?
