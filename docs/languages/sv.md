# Swedish (`sv`)

The Nordic day has five parts where English has four, and the extra one is the
`förmiddag` — the late morning, `[10:00, 12:00)`, a band English cannot name in
one word. The `morgon` that precedes it is correspondingly short: five hours,
`[05:00, 10:00)`, handing over well before noon, and not the six-hour English
morning. The rest of the table is `natt` `[00:00, 05:00)`, `eftermiddag`
`[12:00, 18:00)` and `kväll` `[18:00, 24:00)`. All five come from the Unicode
CLDR 47 day-period chart for `sv`, transcribed in `chronologia/dayparts.py`,
with the surfaces cited to *Svensk ordbok utgiven av Svenska Akademien*, which
glosses `eftermiddag` as the part of the day between lunchtime and evening.

The other early fact is that the half hour names the coming hour: `halv nio` is
08:30, not 08:00. `bare_half_to` is set for that.

## What ships

**Weekdays and months** ship wide and abbreviated, with no recorded source.

**The named days** are the best-cited small vocabulary in the locale: `idag`,
`igår`, `imorgon`, `förrgår` and `övermorgon` each name the exact CLDR 47
`dateFields.json` relative-type entry they came from, and each ships both the
solid spelling and the spaced one — `i dag`, `i går`, `i morgon`,
`i förrgår`, `i övermorgon`.

**The date line** is little-endian with a bare cardinal day and an optional
`den`: `den 3 oktober 1990`. `ordinal_dot` is off, and Swedish does not write
the dotted civil date; the ISO form `2020-06-15` reads.

**Every day-part word ships in the definite singular beside the bare noun** —
`eftermiddagen` next to `eftermiddag`, `kvällen` next to `kväll` — because the
definite is the everyday form in `i eftermiddagen` and `under kvällen`. The
`å`-less ASCII twins ship too, so `kvall` and `formiddag` match.

**Relative offsets** are `om` forward and `för … sedan` backward, and
`lang.json` allows a wide set of orders including a leading `före` for a
before-marker and quantifier-first forms. `halvannan` is registered as the
one-and-a-half quantifier.

**Units ship in singular and plural** with a separate `unit1_` file each.

**The clock** counts forward with `över` and back with `i` — `kvart över åtta`,
`kvart i nio`, `fem över åtta` — with `klockan` as the o'clock word. `midnatt`
and `middag` are the landmark points.

**Ranges** are `från … till …` and `mellan … och …`, with `sedan` opening one
that runs to the anchor and `till` closing one that starts there.

**Quarters, ISO weeks, decades and eras.** `första kvartalet 2020`, `vecka 12`,
`80-talet`, `44 f.Kr.` and `1990 e.Kr.` all resolve, along with a
before-present marker and the full deep-time period vocabulary.

**Fuzzy month parts** are `början av`, `mitten av` and `slutet av`.

**The ordinal-last determiner** is `sista`, cited to SAOL, so `sista måndagen
i maj` resolves.

## Weaker provenance

Only the day parts, the named days and `sista` carry recorded sources. The
weekday and month names, the clock words, the range markers, the seasons and
the holiday vocabulary record none, which is a thinner citation record than the
neighbouring Germanic locales have.

## What refuses

**A twelve-hour clock time with a day-part phrase.** `åtta på kvällen` does not
resolve as 20:00. It resolves the evening band instead and leaves `åtta på` in
the remainder, so the hour is lost. The locale ships no meridiem vocabulary at
all — there is no `clock_meridiem_am` or `clock_meridiem_pm` file — so nothing
can shift a bare hour into the afternoon half.

**The deictic day-part adverbs.** `i morse` and `inatt` return nothing. The
band words themselves read when framed — `i kväll`, `i eftermiddag`,
`på förmiddagen` all resolve — but the fused and suppletive deictic forms are
not in the vocabulary.

**The dotted date.** `15.06.2020` returns nothing. Swedish writes the numeric
date in the ISO order and `2020-06-15` reads.

**Seconds.** `för 30 sekunder sedan` returns nothing. No second unit ships.

**A bare duration.** `två veckor` returns nothing. A quantity with no direction
marker is still only a quantity.

## Open questions for a native speaker

1. Which meridiem surfaces would make `åtta på kvällen` read as 20:00 —
   `på morgonen`, `på förmiddagen`, `på eftermiddagen`, `på kvällen`,
   `på natten` — and where does each of them put the twelve-hour boundary?
2. Should `i morse`, `inatt` and `i går kväll` ship as their own surfaces?
   `i morse` in particular is not `i morgon` and names the morning just past.
3. Does the `förmiddag` boundary at 10:00 match ordinary use, or does the
   `morgon` run later in speech than the CLDR table says?
4. Are the clock words and range markers as this locale ships them the standard
   set, or are there common alternatives missing?
