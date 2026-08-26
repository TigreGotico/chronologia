# English (`en`)

English is the reference locale, and that is the honest headline. Its
vocabulary was written from native competence rather than assembled from cited
sources, so almost nothing in `chronologia/locale/en/` carries a provenance
comment — five files out of nearly three hundred, and each of those comments
explains a parsing decision rather than attesting a surface. Where the pages
for other languages can say which dictionary supplied a word, this one usually
cannot. What English has instead is the largest test corpus in the project, and
its refusals are argued in the corpus rather than in the vocabulary.

The second thing to know is what English does *not* write. `15.06.2020` returns
nothing, and so does `06.15.2020`. The dotted numeric date is the official
civil form of German, Russian, Polish, Czech, Finnish, Turkish and Dutch, and
the parser reads it there; English writes the numeric date with slashes and
writes nothing at all with dots in either order. An English caller who types
dots has not written a date, so the parser does not invent one — and it does
not fall back to reading the year either, because answering `2020` would tell
the caller a whole year had been asked for when a day had been.

## What ships

English carries the widest construction set of any locale, and the parts worth
naming are the ones that are structurally interesting rather than merely
present.

**Both slashed date orders read.** `15/06/2020` and `06/15/2020` both resolve
to 15 June 2020, settled by whichever component can only be a day. Where
neither can settle it, English reads month first: `06/07/2020` is 7 June.

**The nth-to-last idioms are three separate mechanisms**, and the vocabulary
keeps them apart on purpose. `next` in `next to last` is deliberately a
different table from the relative-marker `next` that shifts a whole scope
forward by one: "next to last" is not "next" plus "last" composing an offset,
it is one fixed idiom meaning minus two, and sharing a table would let the two
collide. The `to` of `<ordinal> to last` is likewise registered as a plain
grammar literal in addition to being one of the range connectives.
`penultimate` is a single-word synonym for the same thing, cited to
Merriam-Webster's gloss "next to the last", and the vocabulary records that it
is always minus two and never generalises the way the `<ordinal> to last`
idiom does — there is no "second-to-penultimate".

**`tonight` is a fused word, not a composition.** It ships in its own
today-fused day-part table because it already names today's night band, unlike
the plain band word `night`, which composes with the clock's own future-roll
rule.

**Non-Gregorian calendars, eras and deep time** all ship: Hebrew and Islamic
civil months, French Republican months, Japanese nengō era names, Egyptian and
other regnal series, Attic archon years, the Roman Kalends–Nones–Ides
counting system, the geological period vocabulary from the Archean to the
Holocene, and the Anno Mundi, Julian, Unix, Holocene and before-present eras.

**Jurisdiction-aware business days** ship for the United States, Great Britain,
Germany, France, Spain, Portugal and Brazil.

## Weaker provenance

Nearly everything. The weekdays, the months, the clock words, the day parts,
the seasons, the range markers, the era abbreviations, the non-Gregorian month
names and the geological periods all ship without a recorded source. This is
not a claim that they are doubtful — they are ordinary English — but a reader
who wants to know where a surface came from will not find an answer in the
vocabulary, and the four comments that do exist explain grammar rather than
attest words.

The one attested surface is `penultimate`, cited to Merriam-Webster.

## What refuses

English refusals are the most thoroughly argued in the project, because the
English corpus is where the residue-veto design is pinned.

**The dotted date, in either order.** `15.06.2020` and `06.15.2020` return
nothing and do not degrade to a bare year.

**A duration range dressed as a clock range.** `cook on low for 6 to 8 hours`
returns nothing from the span edge. It names a length of time, not two times of
day, and the subtractive-clock reading would otherwise hijack it — "6 to 8"
as six minutes to eight, a minute-wide span for a sentence about six hours,
with the unit stranded in the remainder. The discriminator is a
trailing duration unit with no clock cue; a genuine clock range carries a
meridiem or an explicit clock, so `6 to 8 pm`, `from 9 to 5` and `3:30 to 4:30`
all stay real timespans. The duration itself belongs to the duration edge, not
the span edge.

**An ordinal that does not exist inside its scope.** `the 13th month of 2026`
and `the 0th week of may` return nothing. There is no overflow projection: the
thirteenth month of 2026 is not January 2027. `the 12th month of 2026` resolves
normally, so the veto does not over-fire.

**An impossible calendar day.** `the 5th Monday of February` returns nothing
when that February has only four Mondays — and returns it rather than raising,
which is the hard never-raise contract. `day 32 of February` and `the 366th day
of the year 2017` refuse rather than falling back to the whole month or the
whole year; `the 365th day of the year 2017` resolves.

**An ordinal-weekday recurrence with a bounded or week-scoped tail.**
`every 3rd tuesday of next year`, `of last month`, `of next week` and their
siblings yield no recurrence rule at all. The alternative was worse than
nothing:
a weaker reading would have folded only the head into an unbounded three-week
cadence and stranded the tail, which is not a frequency error at the margin but
a different rule entirely.

**A bare duration.** `a fortnight` returns nothing; `in a fortnight` resolves.
A quantity with no direction marker is still only a quantity.

## Open questions

1. Should an unscoped `the second-to-last friday` resolve at all? It
   answers the same date as a plain `the last friday`, with the modifier
   stranded, where the month-scoped `the second to last friday of may`
   resolves correctly.
2. Is month-first the right default for an ambiguous slashed date? It is the
   American convention, and a British caller writing `06/07/2020` means 6 July.
3. Should the vocabulary carry sources at all for a native-competence locale,
   or is the corpus the right place for that record?
