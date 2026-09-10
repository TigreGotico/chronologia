# Danish (`da`)

Danish names the **coming** hour on the half. `halv to` is 01:30, not 02:30,
and `halv tolv` is 11:30. The Danish Wikipedia article *Klokken* states the
rule as a subtraction — `"Halv ...[indsæt timetal]" (en halv time fratrukket)`
— alongside the two quarter forms, `"Kvart i ..."` a quarter subtracted and
`"Kvart over ..."` a quarter added. `bare_half_to` in `lang.json` is what turns
the half on; the quarters take their direction from the preposition beside
them, `over` counting up and `i` counting down.

The same article records the fact that governs everything awkward about this
locale: everyday Danish reckons the clock in two twelve-hour cycles, `"Et" til
"tolv", underforstået 'timer' (2 cykler på en dag)`, and normally speaks it
`kun op til et halvt døgn` — its worked example turns 18:49 into `kvart i syv`.
The locale resolves the hour that rolls back past one in the two-cycle
twelve-hour reading a Danish speaker means, so `halv et` is 12:30 and `kvart i
et` is 12:45. See "The hour before one" below.

## What ships

**Weekdays and months** ship wide and abbreviated, with no recorded source.

**The named days** come from Unicode CLDR 47,
`cldr-dates-full/main/da/dateFields.json`, whose five day relative-type entries
are `i forgårs`, `i går`, `i dag`, `i morgen` and `i overmorgen`. Each ships
beside a solid-spelled twin — `iforgårs`, `igår`, `idag`, `imorgen`,
`iovermorgen` — and the bare `går`, `morgen`, `forgårs` and `overmorgen` ship
as well. Those extra forms are not in the cited file.

The bare `morgen` is the one that costs something. It is registered as
tomorrow, which is what CLDR's `i morgen` means once the `i` is dropped, but
`morgen` on its own is also the ordinary Danish word for the morning. A bare
`morgen` therefore resolves to tomorrow's whole day.

**The date line** is little-endian with a dotted ordinal day: `den 3. oktober
1990` resolves, so does the bare `3. oktober 1990`. `ordinal_dot` is on and
Danish writes the dotted civil date, so `15.06.2020` reads, as does the ISO
`2020-06-15`.

**The dotted timetable clock.** Resolved by native review: `14.30` and
`klokken 14.30` now read the same as the colon form `14:30`. The
`dotted_clock` tokenizer mode was already built (originally for Finnish, CLDR
47 fi short time pattern `H.mm`) but was opt-in and off by default; declaring
it for Danish was the whole fix. The mode's own guards keep it from
colliding with the dotted date it is matched after (`3.6.2020` still reads
whole) and with plain decimals (`1.000`, `2.5` still fall through to the
number rule) — verified against both, plus the combined case `3. oktober
klokken 14.30`, which now also resolves the clock half instead of leaving it
in the remainder.

**Relative offsets** are `om` forward and `siden` backward, with `for` licensed
as a leading before-marker, so both `for tre dage siden` and `tre dage siden`
resolve. Units ship in singular and plural with a separate `unit1_` file each.

**The clock** counts forward with `over` and back with `i`, takes `klokken` or
`kl.` as its at-marker, and reads `midnat` and `middag` as the landmark points.
The o'clock marker binds only in front of a *bare* hour: `klokken otte` reads
08:00 cleanly, but in `klokken halv to` and `klokken kvart over tre` the time
is right and the word `klokken` is left in the remainder, because the locale
declares no order that puts the at-marker in front of a fraction.

A minute count stacked on a half — `fem over halv ti`, ordinary Danish for
09:35 — resolves to 09:30 with `fem over` in the remainder. That is a wrong
time, not a refusal, and it is the sharpest edge in the locale after the two
below.

**A spoken hour binds to a following `om <daypart>` phrase as its meridiem.**
`klokken otte om aftenen` is 20:00, `kvart over tre om eftermiddagen` 15:15,
`klokken ni om formiddagen` 09:00. The definite surfaces `morgenen` and
`formiddagen` hold the hour in the AM half and `eftermiddagen` and `aftenen`
push it into the PM half, a flat twelve-hour move on the spoken 1–11 hour.
`natten` is separate: it is a band that crosses midnight, so `klokken tre om
natten` is 03:00, `klokken elleve om natten` is 23:00 and `klokken tolv om
natten` is midnight, with the AM ceiling following the CLDR `nat` band.

Three things about that binding are worth knowing before relying on it.

The at-marker is required. Without `klokken`, a spoken hour in front of `om
<daypart>` does not bind at all: `tre om eftermiddagen` returns the whole
afternoon band 12:00–18:00 with `tre om` in the remainder, and every other
spelled hour behaves the same way. Only the digit and the `klokken` forms
reach the meridiem.

The hour word `to` is unusable there even with the at-marker. `klokken to om
eftermiddagen` returns the afternoon band with `klokken om` stranded, and
`klokken to om natten` the night band. The Danish numeral `to` is a homograph
of the English default range connector `to`, which the range splitter consults
in every locale, and the split runs before the clock is read. The collision is
independent of the day-part binding and shows up wherever a Danish `to` sits
between two independently resolvable pieces.

The literal hour twelve reads wrong on the morning side. `klokken tolv om
formiddagen` is midnight rather than noon, and the fractional forms inherit it
one hour lower still: `halv tolv om formiddagen` is 23:30 and `kvart i tolv om
formiddagen` 23:45, where a Danish speaker means 11:30 and 11:45. The meridiem
attaches to the hour *as spoken*, twelve is rewritten to zero on the AM side,
and only then does the fraction roll the hour back. None of these leave a
remainder.

**Day parts** take their band boundaries from the Unicode CLDR 47 day-period
chart, whose Danish rows read `nat` from 00:00, `morgen` from 05:00,
`formiddag` from 10:00, `eftermiddag` from 12:00 and `aften` from 18:00. All
five ship as vocabulary: four in both the bare and the definite form
(`nat`/`natten`, `formiddag`/`formiddagen`, `eftermiddag`/`eftermiddagen`,
`aften`/`aftenen`); `morgen` ships definite-only (see below). The
`formiddag` is the late morning English cannot name in one word.

The `morgen` band is transcribed in `chronologia/dayparts.py`. Resolved by
native review: it ships now, but only under its DEFINITE surface
`morgenen` — deliberately excluding the bare `morgen` that sibling
dayparts (`aften`/`aftenen`, `nat`/`natten`) both ship. Bare `morgen` stays
reserved for the relative-day "tomorrow" reading; `morgenen` never appears
in that idiom (`i morgen` is always the bare form), so it carries no such
ambiguity, and the same surface was already used safely as a meridiem
marker (`klokken ni om morgenen` == 09:00, above). `om morgenen` alone now
resolves to the band.

**Ranges** are `fra … til …` and `mellem … og …`, with `siden` opening one that
runs to the anchor and `indtil`/`til` closing one that starts there.

**Quarters, ISO weeks and eras.** `første kvartal 2020`, `uge 12`, `44 f.Kr.`
and `1990 e.Kr.` resolve, along with a before-present marker and the full
deep-time period vocabulary.

**Fuzzy month parts** are `begyndelsen af`, `midten af` and `slutningen af`.

**The ordinal-last determiner** is `sidste`, so `sidste mandag i maj` resolves.
The vocabulary file cites Den Danske Ordbog.

**`halvanden`**, the ordinary Danish word for 1.5 (Den Danske Ordbog; from Old
Norse *halfr annarr*), is declared as the `1.5` quantifier. Resolved by native
review: `extract_number_da('halvanden')` misreads it as a bare `0.5`, so a
fixed word-map override in `numfold_germanic.fold_da` intercepts the token
before the (wrong) number-parser value ever folds it, mirroring German
`anderthalb` and Dutch `anderhalve`. `halvanden time siden` now resolves to
1.5 hours ago rather than half an hour ago.

## The hour before one

Resolved by native review: Danish sets `toward_hour_12h`. What a Danish
speaker most often means, given that the everyday clock runs in two
twelve-hour cycles, is 12:30 for `halv et` and 12:45 for `kvart i et` — half
past noon, not half past midnight. `toward_hour_12h` is exactly this: where
it is set, the hour that rolls back from one to zero surfaces as twelve.

Danish is now the second Germanic locale to declare it, alongside Icelandic;
German, Dutch, Frisian, Swedish, and both Norwegian standards still don't.
This was scoped to Danish only — Swedish and Bokmål pin the same 00:30/00:45
shape for their own spellings and were left as-is, since the doc's own
framing called this a family decision, not a Danish one, and a native review
of one locale isn't grounds to flip its siblings.

The flag is read at three points in the resolver, and the two that matter
moved together as expected: `halv et` now resolves to 12:30 and `kvart i et`
to 12:45, pinned in `test/nl_corpus_da/test_da_clock.py`. Full local test
suite re-run clean after the change (159419 passed, only 3 pre-existing,
unrelated `test_packaging.py` errors from a missing `build` module in this
environment).

The marked forms already read the way a native expects and did not move: the
day-part binding gives `halv et om eftermiddagen` 12:30 and `kvart i et om
eftermiddagen` 12:45, same as before.

## Weaker provenance

The named days carry a precise CLDR locator, but the solid spellings and the
bare `går`/`morgen`/`forgårs`/`overmorgen` that ship beside them do not appear
in that file and rest on nothing recorded.

Den Danske Ordbog is the source named in the day-part and `sidste` vocabulary
headers, and `ordnet.dk` refuses automated retrieval — every request answers
`202` with an empty body — so those citations are **unchecked here**. The
Danish Wiktionary entries were fetched instead and agree with them:
`formiddag` is glossed "Tidspunkt før middag, om morgenen", `eftermiddag`
"Tidspunkt ca. mellem kl. 12 og 18", `middag` the point around twelve when the
sun stands highest, and `sidste` "Modsat første". The day-part *boundaries* do
not depend on the dictionary at all; they are the CLDR chart, which was
fetched and matches the transcription exactly.

The weekday and month names, the clock words, the range markers, the seasons
and the holiday vocabulary record no source.

## What refuses

**`ét` with its acute.** `halv ét` returns nothing. The bare `et` reads, and
the accented numeral that Danish orthography uses to distinguish the numeral
from the article is not in the vocabulary.

**Decades.** `80'erne` and `firserne` return nothing. The locale declares no
decade construction; Bokmål declares one and reads `80-tallet`.

**Seconds.** `30 sekunder siden` returns nothing. No second unit ships.

**A bare duration.** `to uger` returns nothing. A quantity with no direction
marker is still only a quantity.

**The deictic day-part adverbs.** `i morges` returns nothing, and `i morgen
tidlig` resolves tomorrow with `tidlig` unread. The framed band words do
resolve, leaving the framing `i` or `om` in the remainder: `i eftermiddag`,
`i aften`, `i nat` and `om eftermiddagen` all return their band.

## Open questions for a native speaker

1. Is `tre om eftermiddagen`, with no `klokken`, ordinary enough to need to
   bind? It is the form that returns a six-hour band.
2. Is `klokken seks om natten` 06:00 or 18:00 in ordinary use? The band split
   puts it at 18:00.

Resolved: whether `halvanden` ships as the 1.5 quantifier — see `halvanden`
under "What ships" above.

Resolved: whether a `morgen` day-part surface should ship despite the
collision with the tomorrow word — see the `morgen` paragraph under "What
ships" above (shipped definite-only, `morgenen`).

Resolved: whether `halv et` and `kvart i et` read as 12:30 and 12:45 — see
"The hour before one" above.

Resolved: whether `14.30` should read as a clock — see "The dotted timetable
clock" under "What ships" above.
