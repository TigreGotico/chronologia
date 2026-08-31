# Greek (`el`)

Greek marks its determiners twice. `marker_position` sets `weekday_ref` and
`rel_period` to `post`, and the base grammar's `extend`/`override` entries add
a second, article-carrying order on top of the plain one — `την Τρίτη που
έρχεται` ("the Tuesday that is coming") reads the same offset as a bare
postposed marker, because Greek names a relative weekday with a postposed
relative clause rather than a prenominal adjective the way English or French
do. That construction, not a single determiner word, is the ordinary way to
say "next Tuesday" or "last Tuesday" in spoken Greek.

The clock is the second thing to know, and it resolves the same direction
English and Romanian do: additive past the hour, subtractive toward the next
one.

## What ships

**Day parts** are four bands transcribed from the Unicode CLDR 47 day-period
rules for `el`: `πρωί` `[04:00, 12:00)`, `απόγευμα` `[12:00, 17:00)`, `βράδυ`
`[17:00, 20:00)` and `νύχτα` `[20:00, 04:00)` (crossing midnight). Each noun's
gender and its accusative article are confirmed against its own Wiktionary
lemma: `πρωί`, `απόγευμα` and `βράδυ` are neuter (`το`), `νύχτα` is feminine
(`τη`, since it begins with a consonant outside the vowel/plosive set that
forces `την`). The same four nouns double as clock meridiem cues on an
explicit hour: `πρωί` is a no-op AM confirmation, `απόγευμα` and `βράδυ` are a
uniform +12 PM shift, and `νύχτα` routes through the shared midnight-crossing
night-meridiem split (small hours 1–5 stay AM, 6–11 are PM, twelve is
midnight).

**Recurrence is unimplemented.** `κάθε μέρα` ("every day") does not resolve;
`marker_every.voc` ships the connector word but no construction consumes it
yet, so a sentence built on `κάθε` binds only the temporal fragment it happens
to contain (a daypart, a clock time) and strands `κάθε` in the remainder.

**Weekdays and months** ship bare, in the nominative, with no recorded
source in the vocabulary comments.

**The date line** is little-endian (`DAY MONTH YEAR?`), matching the CLDR
`el` `ca-gregorian` chart at every level — full `EEEE d MMMM y`, long
`d MMMM y`, medium `d MMM y`, short `d/M/yy`.

**Relative offsets** are `πριν`/`πριν από` for the past and `σε`/`μετά` for
the future, with the marker able to lead the count (`πριν από τρεις μέρες`) or
trail it, and an indefinite-article order for a bare unit (`μια εβδομάδα`).

**The clock** ships two directions off the fixed hour, both cited in the
vocabulary to the *Λεξικό της Κοινής Νεοελληνικής* (Triantafyllidis
Institute, 1998) and to Triantafyllidis's own *Νεοελληνική Γραμματική* §403 on
time expressions, for the meridiem abbreviations, and confirmed independently
for the fraction words. `και` ("and") is additive: `τρεις και μισή` is 3:30,
`τρεις και τέταρτο` is 3:15. `παρά` ("minus/before") is subtractive from the
*next* hour: `τρεις παρά τέταρτο` is 2:45. Two independent sources with worked
numeric examples confirm the direction: the project's own test corpus, which
checks these exact phrases against independent arithmetic on a fixed anchor
and states explicitly that Greek "differs from the Continental-Germanic half"
— `και μισή` is half *past*, not half *to* — and a Greek-language learner's
guide (Preply), which glosses `Είναι μία και μισή` as "It is half past (one)"
and `Είναι δέκα παρά τέταρτο` as "It is quarter to (ten)", with `παρά`
explicitly said to work "exactly like the English 'to'". `τέταρτο`
("quarter") is independently confirmed at its Wiktionary lemma entry: "a
quarter, a fourth, one of four equal parts", with "quarter of an hour" given
as its own clock sense, deriving from the adjective `τέταρτος` ("fourth").
The landmarks are `μεσημέρι` (noon) and `μεσάνυχτα` (midnight), and the
meridiem markers `π.μ.`/`π. μ.`/`πμ` (AM, from `προ μεσημβρίας`, "before
midday") and `μ.μ.`/`μ. μ.`/`μμ` (PM, from `μετά μεσημβρίαν`, "after
midday") ship in their tight-dotted, spaced-dotted and dot-less spellings —
the vocabulary comment records that the dot-less forms are the ordinary
informal rendering in digital text, and the corpus's own regression test
documents why the dots matter mechanically: the tokenizer discards dots, so
an unlisted dot-less variant would silently fall into the remainder and read
a p.m. time twelve hours early.

**Determiners.** `περασμένη`/`προηγούμενη` ("last/previous") and `επόμενη`
("next") ship as prenominal adjectives, each with a postposed relative-clause
alternative for a weekday — `που πέρασε` ("that has passed") and `που
έρχεται` ("that is coming") — both cited to the *Λεξικό της Κοινής
Νεοελληνικής*, s.v. `περνώ`/`περασμένος` and `έρχομαι` respectively, as
fixed relative-marker surfaces rather than free relative clauses.
`τελευταίος` ("last" as an ordinal-last determiner, behind `η τελευταία
Δευτέρα του Μαΐου`) is cited to the same dictionary, s.v. `τελευταίος`.

**Ranges** are `μεταξύ`/`ανάμεσα` ("between") and `έως`/`μέχρι`/`ως`
("until"/"to").

**Quarters, ISO weeks, decades, centuries and millennia.** `τρίμηνο`
(quarter), `εβδομάδα` (ISO week), `δεκαετία` (decade), `αιώνας` (century) and
`χιλιετία` (millennium) all resolve — Greek is among the locales here that
ship a dedicated millennium unit rather than folding it into a numeral-plus-
scale construction.

**Seconds** ship a unit, `δευτερόλεπτο`/`δευτερόλεπτα`, unlike Persian,
Ukrainian and Romanian, none of which ship a seconds vocabulary at all. This
page did not find a positive corpus test exercising `N δευτερόλεπτα πριν`
("N seconds ago") end to end — see Weaker provenance.

**Fuzzy period parts** are `αρχές`/`αρχή` (early), `μέσα`/`μέση` (mid),
`τέλη`/`τέλος` (late).

**Eras** are `μ.χ.`/`μ. χ.` (AD, "μετά Χριστόν", after Christ) and `π.χ.`/
`π. χ.` (BC, "προ Χριστού", before Christ), each in tight- and spaced-dotted
form.

## Weaker provenance

The weekday and month names carry no recorded source, and neither do the
seasons or the holiday vocabulary.

The seconds unit ships without a verified positive test of "N seconds ago"
resolving end to end through `relative_offset`; it was not exercised as a
false claim on this page, but it was also not independently confirmed to
work, so it is listed here rather than folded into What ships without
qualification.

## What refuses

**`bare_half_to`.** The locale's conventions explicitly set `bare_half_to:
false`. A bare `μισή` or `μισή ώρα` reading as "half to the hour" with no
`παρά`/`και` marker present does not resolve as a clock time; the fraction
word only binds inside the full `HOUR CLOCKDIR FRACTION` shape.

## Open questions for a native speaker

1. Does `βράδυ` genuinely extend as a colloquial PM clock cue past its own
   CLDR band into the 21:00–23:00 hours (`εννιά/δέκα/έντεκα το βράδυ`), the
   way `tarde` does in Spanish and `abends` does in German, or does ordinary
   speech switch to `νύχτα` earlier than that?
2. Does the shared 5|6 hour cut used for the `νύχτα` night-meridiem split
   (small hours 1–5 read AM, 6–11 read PM) match how a Greek speaker actually
   parses an hour said with `νύχτα`, or does the boundary sit somewhere else
   in ordinary usage?
3. Does `N δευτερόλεπτα πριν` actually resolve today, and if it does not,
   is the missing piece the unit's wiring into `relative_offset` or
   something else?
4. Is the postposed relative-clause construction (`που πέρασε`/`που
   έρχεται`) the dominant spoken form for every weekday, or does it compete
   evenly with the prenominal adjective (`την περασμένη Τρίτη`) in ordinary
   registers?
