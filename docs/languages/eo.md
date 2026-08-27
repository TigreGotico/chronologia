# Esperanto (`eo`)

Esperanto has no irregular numerals, no gender and no case government on a
counted noun, which makes it the simplest number fold in the library. What it
does have is a suffix distinction that carries meaning nothing else in this
locale carries, and getting it wrong would quietly turn a single appointment
into a standing weekly one.

`lundon` — the accusative — names one specific Monday. `lunde` — the adverbial
— means "on Mondays", habitually. They are not variants of one another, and
they are not folded into one vocabulary slot. The accusative belongs to the
date constructions; the adverbial belongs to recurrence, and it gains no
recurrence reading from a preceding `ĉiu` either.

## What ships

**Months and weekdays** come from Unicode CLDR 47,
`cldr-dates-full/main/eo/ca-gregorian.json`, where the wide format and
stand-alone forms are identical. Each ships in the nominative and the
accusative, the accusative being what the temporal idiom takes.

**The date** is an ordinal day, `de`, and the month: `la unua de januaro`.
`la` is the single invariant definite article, `de` the linking preposition.

**Relative offsets** use `antaŭ` for the past and `post` for the future.
Esperanto does not lexically distinguish "before X" from "X ago" — the same
preposition carries both, and the direction is read from context rather than
from a separate word. `post` is its attested antonym.

**The clock** has three constructions, and one of them counts the other way.

`kaj` and `post` both count **forward** from the hour named:
`la sesa kaj duono` is 6:30, and `duono post la sepa` is 7:30. This is the
English past-the-hour convention, not the toward-the-hour convention Icelandic
and Lithuanian use, and the locale therefore needs none of the toward-hour
guards those locales carry. Two independent accounts agree on the direction.

`antaŭ` counts **back** toward the coming hour: `kvarono antaŭ la sepa` is 6:45,
a quarter short of seven. It is the asymmetric member of the set.

`je` leads a clock reading (`je la sesa`), and `horo` is the optional formal
trailing "o'clock" noun beside the colloquial bare ordinal.

**Recurrence** ships in both attested shapes: the univerbated adverbs
`ĉiutage`, `ĉiusemajne`, `ĉiumonate`, `ĉiujare`, and the two-word determiner
plus accusative noun `ĉiun tagon`. The univerbated forms are regular `ĉiu-`
plus a unit stem plus the adverbial `-e`, the pattern Wiktionary's own `ĉiu`
entry lists.

**Named days** are the standard closed-class adverbs `hodiaŭ`, `hieraŭ`,
`morgaŭ`, with `antaŭhieraŭ` and `postmorgaŭ` formed by the productive `antaŭ-`
and `post-` prefixes.

**Midnight and noon** are `noktomezo` and `tagmezo`. `tagmezo` is attested
directly, with a worked example. `noktomezo` is the same productive compound —
`nokto` plus `mezo` — formed on the pattern the attested word establishes.

## Weaker provenance

**The clock idioms** rest on a language-learning grammar page, with a second
aggregate corroboration for the `post`-linked variant that was treated as
secondary rather than independently verified page by page.

**`ĉiun` as the distributive accusative** extends an attested pattern rather
than being attested itself. The temporal accusative is attested for single
occurrences, and Esperanto adjective-noun case agreement is regular, so
`ĉiun tagon` follows; but the determiner in the accusative was not separately
cited.

**`noktomezo`**, as above — regular compounding on an attested pattern.

**PIV, the *Plena Ilustrita Vortaro*,** the authoritative Esperanto dictionary,
was not consulted. Nor was Lernu's dedicated date-format page, which is what
would settle the year-inclusive date construction below.

## What refuses

**Day parts.** `matene`, `posttagmeze`, `vespere` and `nokte` all return
nothing, and `je la sesa vespere` parses only the clock part, leaving `vespere`
visibly stranded. The words exist in the lexicon; what does not exist is any
authority for their boundaries. CLDR ships Esperanto only the coarse am/pm
pair, and the language is absent from every locale grouping in the
supplemental day-period rule set, so it falls back to the root am/pm default.
Inventing band boundaries is what this refusal prevents. For the same reason no
am/pm meridiem marker ships either.

**A year on an absolute date.** `la unua de januaro 2024` resolves the day and
month and leaves `2024` unconsumed. Whether the year takes its own connector,
sits bare after the month, or uses something like `de la jaro` was not found in
an independently fetched source, so only the day-and-month form is wired.

**A two-word relative weekday shift.** `pasinta lundon`, `sekva lundon` and
`venonta lundon` resolve the bare weekday and leave the leading word in the
remainder. The only attested surfaces for "last Monday" and "next Monday" are
the fused compounds `pasintlunde` and `sekvalunde`, which are themselves
adverbial `-e` forms whose semantics — one occurrence or a recurring one — the
citation listing them does not resolve. Neither the fused nor the two-word form
is wired.

## Open questions for a native speaker

1. How is a full date with a year written and said? Does the year take a
   connector?
2. Does the duration noun in `antaŭ tri tagoj` stand in the nominative or the
   accusative? The attested example uses an adverb, not a counted noun.
3. Do `pasintlunde` and `sekvalunde` name a single occurrence or a recurring
   one?
4. Is there an editorially defensible band shape for the four day-part words,
   given that CLDR defines none?
5. Is a compound ordinal written solid or hyphenated — `dudektria` or
   `dudek-tria`?
