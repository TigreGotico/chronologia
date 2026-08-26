# Serbian (`sr`)

Serbian is written in two scripts, and the locale reads both. Every vocabulary
file lists the Latin and the Cyrillic surface side by side, so `dva sata` and
`два сата` are the same phrase to the extractor and neither script is the
privileged one.

Two facts decide most of what follows. The first is the paucal: a Serbian noun
counted by two, three or four stands in the **genitive singular**, and only from
five upward in the genitive plural. Reading a declension table carelessly gets
this backwards, labelling the genitive plural as the paucal form, and every
unit file here is built as `{1: nominative singular, 2–4: genitive singular,
5+: genitive plural}` for that reason. The second is `nedelja`, which names both
Sunday and — in some sources — the week. That ambiguity is resolved by
construction rather than by guessing, and it is the single largest source of
deliberate refusals in this locale.

## What ships

**Weekdays and months** ship in both scripts, with months carrying the genitive
that follows a day number as well as the nominative: `5. januara 2020` reads
as the fifth of January.

**Units** are Wiktionary declension tables, one per noun, with the paucal rule
applied. Some units syncretise: `dan` and `minut` have the same surface for the
genitive singular and the genitive plural, so `dva dana` and `pet dana` are
spelled alike, and the file lists one form for both. Others do not: hour is
`sat` / `sata` / `sati`, and its vocabulary file states explicitly that
`sata` is the genitive singular rather than the paucal, because that is the
mistake the table invites.

`sat` doubles as the "o'clock" word and inflects with the hour count exactly as
the duration unit does — `jedan sat`, `dva sata`, `pet sati` — which is why
naming the hour uses the same three surfaces.

**Relative offsets** use `pre` for the past and `za` for the future. `pre`
carries both frames: it is the offset marker in `pre tri dana` (three days ago)
and the ordinary preposition "before X". Both are wired, from the Wiktionary
entry and from Talkpal's guide to telling time.

**The clock** works in both directions. Additive: `dva i četvrt` is 2:15, with
`i` as the joining conjunction. Subtractive: `četvrt do tri` is 2:45, and
`petnaest do sedam` is 6:45. The half hour names the coming hour, so
`pola četiri` is 3:30 — attested by the Wikipedia article on date and time
notation in Serbia, by gospeakserbian's time guide and by Talkpal, three
independent accounts agreeing. The Wikipedia article notes it is the more
frequent of two live variants, a minority opposite usage existing.

`petnaest` is treated differently from `četvrt`. `četvrt` is a bare fraction
word that can stand on either side of the construction; `petnaest` is a literal
minute count valid only after a direction word, because Serbian does not say a
bare `petnaest sedam`. It therefore lives in its own class rather than among the
fractions.

**`dana` as a filler.** A bare genitive plural `dana` trailing a month, week or
year count is the emphatic idiom `mesec dana`, literally "a month of days",
meaning exactly one month and never an extra day. A genuine "+1 day" reads the
nominative `dan`. The locale knows the difference.

**Day parts** take their band boundaries from the CLDR 47 day-period rules for
`sr` and their surfaces from Wiktionary: `ujutru`, `popodne`, `uveče`, `noću`.

**Markers** are Wiktionary entries: `posle` (after), `pre` (before), `između`
with the genitive (between, glued with the ordinary conjunction `i`), `od`
(from, since), `do` (until, to), `svaki` (every).

## Weaker provenance

**The determiners `ovaj`, `prošli` and `sledeći`** are single-sourced to
Talkpal's Serbian time vocabulary. Because of that, only the attested nominative
and the ordinary feminine agreement the year phrase needs (`prošle godine`,
`sledeće godine`, `ove godine`) are shipped, rather than a full reconstructed
paradigm.

**The half-hour direction** is corroborated three ways, but one of those sources
itself records that a minority of speakers use the opposite direction. The
locale ships the majority reading. A Serbian speaker who means 4:30 by
`pola četiri` will be misread, and no construction distinguishes the two.

**Ekavian only.** The locale ships `vek`, not the Ijekavian `vijek`;
`pre dva vijeka` returns nothing. Only that one pair was checked against a
dictionary, so the Ijekavian variants of the other units are unverified rather
than deliberately excluded.

## What refuses

The `nedelja` refusals are all pinned by tests, and each exists because
answering the sub-reading would be worse than answering nothing.

**`nedelju dana`.** The trailing `dana` is exactly the cue that means WEEK in
real speech, but expressing that reading needs grammar this locale does not
have: nothing lets a bare weekday match widen into a week offset. Returning the
lone-Sunday reading and stranding `dana` would be a worse wrong answer than
none, so the whole phrase refuses.

**`prošle nedelje` and `sledeće nedelje`.** In the genitive, dictionaries give
"last week" as the default gloss, which conflicts with the weekday reading the
bare nominative gets. No source establishes either as dominant, so the phrase
refuses rather than silently picking a sense. The nominative
`prošla nedelja` is unambiguous and does resolve, as last Sunday.

**A count before `nedelja` or `nedelje`.** `dve nedelja`, `10 nedelja`,
`dve nedelje` — a count can only mean a span of weeks, since nobody counts
specific Sundays that way, but this locale ships no week duration unit under
`nedelja`. The count vetoes the weekday match and the phrase refuses. The veto
holds on both sides of a relative marker, since a marker fixes direction and
not sense. An unambiguous weekday is untouched: `dva ponedeljka` still resolves.

**`milenijum`.** No declension table was found in the sources consulted, so it
ships no unit file in either script and every phrasing of it refuses.

**The Ijekavian `vijek`**, as above.

What does work throughout is `sedmica`, the unambiguous week word:
`za sedmicu` is in a week, `pre sedmice` a week ago, `pre pet sedmica` five
weeks ago.

## Open questions for a native speaker

1. In `prošle nedelje`, does "last week" or "last Sunday" dominate in ordinary
   use — and is the answer stable enough to ship?
2. How common is the minority half-hour direction that reads `pola četiri` as
   4:30, and is there any cue that distinguishes it?
3. What is the declension of `milenijum`?
4. Should the Ijekavian variants ship alongside the Ekavian ones, and for which
   units do the two differ?
5. Are the determiner paradigms for `ovaj`, `prošli` and `sledeći` complete as
   shipped, or are ordinary temporal phrases missing a case?
