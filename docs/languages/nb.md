# Norwegian Bokmål (`nb`)

Bokmål names the **coming** hour on the half. `halv to` is 01:30, not 02:30,
and `halv tolv` is 11:30. Bokmålsordboka states the rule under `halv` as "om
klokkeslett: 30 minutter før en hel time", and its own worked example is the
one that matters here: `klokka er halv ti, altså 09.30` **or** `21.30`. The
dictionary gives the phrase two readings because the hour name is spoken in
twelve-hour terms; the clock the phrase lands on is decided by context, not by
the words. `bare_half_to` in `lang.json` turns the half on.

The quarters take their direction from the preposition. `over` counts up and
`på` counts down, so `kvart over ett` is 01:15 and `kvart på ett` 00:45.
Bokmålsordboka carries the same pair under `kvart` — "om klokkeslett: 15
minutter før eller etter en hel time", with `klokka kvart over ett` and `vi må
gå kvart på fire` as its examples. Here too the dictionary's hour name is the
twelve-hour one. See "The hour before one" below, which is the open decision of
this locale.

The numeral matters in the hour slot. `ett` is the neuter of `en` and is the
form the clock uses; the article `et` is not a numeral, and the locale does not
read it as one. `halv ett` and `kvart på ett` resolve; `halv et` and `kvart på
et` return nothing.

## What ships

**Weekdays and months** ship wide and abbreviated, with no recorded source.

**The named days** come from Unicode CLDR 47,
`cldr-dates-full/main/nb/dateFields.json`, whose five day relative-type entries
are `i forgårs`, `i går`, `i dag`, `i morgen` and `i overmorgen`. Each ships
beside a solid-spelled twin — `iforgårs`, `igår`, `idag`, `imorgen`,
`iovermorgen` — and the bare `går`, `morgen`, `forgårs` and `overmorgen` ship
as well. Those extra forms are not in the cited file.

The bare `morgen` costs something. It is registered as tomorrow, which is what
`i morgen` means once the `i` is dropped, but `morgen` alone is also the
ordinary word for the morning. A bare `morgen` resolves to tomorrow's whole
day.

**The date line** is little-endian with a dotted ordinal day, so `den 3.
oktober 1990` and the bare `3. oktober 1990` both resolve. `ordinal_dot` is on
and Bokmål writes the dotted civil date, so `15.06.2020` reads, as does the ISO
`2020-06-15`.

**Relative offsets** are `om` forward and `siden` backward, with `for` licensed
as a leading before-marker, so both `for tre dager siden` and `tre dager
siden` resolve. Units ship in singular and plural, and the feminine `uka`
beside `uken`, with a separate `unit1_` file each. `halvannen` is registered as
the one-and-a-half quantifier, so `om halvannen time` is an hour and a half
from now; English Wiktionary carries it as a Bokmål determiner, "one and a
half", citing the Bokmål Dictionary.

**Decades** read off `marker_plural`, whose surfaces are `tallet` and `talet`,
so `80-tallet` and `1980-tallet` both resolve to the 1980s. The spelled
`åttitallet` does not.

**The clock** counts forward with `over` and back with `på`, takes `klokka`,
`klokken` or `kl` as its at-marker, and reads `midnatt` and `middag` as the
landmark points. The at-marker binds only in front of a *bare* hour: `klokka
åtte` reads 08:00, but in `klokka halv to` and `klokka kvart over tre` the time
is right and `klokka` is left in the remainder, because the locale declares no
order that puts the at-marker in front of a fraction.

A minute count stacked on a half — `fem over halv ti` for 09:35, `ti på halv
ti` for 09:20 — resolves to 09:30 with `fem over` or `ti på` in the remainder.
That is a wrong time, not a refusal.

The numeral `to` is a homograph of the English default range connector `to`,
which the range splitter consults in every locale, and the split runs before
the clock is read. Where a Bokmål `to` sits between two independently
resolvable pieces the range wins, so `to om ettermiddagen` returns the
afternoon band with `to om` stranded. Most sentences are unaffected — `om to
uker`, `de siste to uker` and `mandag klokka to` all read correctly — because a
range needs both of its sides to parse on their own.

**No day-part meridiem ships.** This is the largest gap in the locale and it
produces wrong times rather than refusals. Bokmål says the twenty-four-hour
clock as a twelve-hour hour plus a trailing `om <daypart>`, and there is no
`clock_meridiem_*` vocabulary here to read it: `klokka åtte om kvelden` returns
08:00 with `om kvelden` in the remainder where a speaker means 20:00, `kvart
over tre om ettermiddagen` returns 03:15 rather than 15:15, and `klokka elleve
om natta` returns 11:00 rather than 23:00. The hour survives, the half of the
day is discarded, and the discarded words are visible in the remainder. Danish
ships the equivalent vocabulary and reads all three; ten of the sixty-one
locales, Bokmål and Nynorsk among them, ship none.

**Day parts** take their band boundaries from the Unicode CLDR 47 day-period
chart. The chart's Bokmål rows carry the period codes with no example words at
all — every `nb` cell reads "missing" — so the boundaries are read off the
Norwegian (`no`) rows, which both written standards share: `natt` from 00:00,
`morgen` from 06:00, `formiddag` from 10:00, `ettermiddag` from 12:00 and
`kveld` from 18:00. The words are supplied per standard, and `chronologia/
dayparts.py` records that reasoning.

Four of the five bands ship as vocabulary, in the bare and definite forms:
`natt`/`natta`/`natten`, `formiddag`/`formiddagen`,
`ettermiddag`/`ettermiddagen`, `kveld`/`kvelden`. The `formiddag` is the late
morning English cannot name in one word; Bokmålsordboka glosses it as "tid fra
morgen til ettermiddag" and "tid mellom frokost og klokka tolv eller
middagstid", which is the chart's 10:00–12:00 read loosely.

The `morgen` band is transcribed in `dayparts.py` but ships no vocabulary file,
so it is unreachable and `om morgenen` returns nothing. That is the price of
the tomorrow-word collision above. Nynorsk and German leave the morning band
out as well; Swedish, Dutch, English, Frisian and Icelandic ship one.

A day-part word does bind to a day: `i morgen kveld` is tomorrow evening,
`i går kveld` yesterday evening, `mandag kveld` Monday evening. The framed
band words resolve on their own too, leaving the framing word in the
remainder — `i kveld`, `i natt`, `om ettermiddagen`.

**Ranges** are `fra … til …` and `mellom … og …`, with `siden` opening one that
runs to the anchor and `til`/`inntil` closing one that starts there.

**Quarters, ISO weeks and eras.** `første kvartal 2020`, `uke 12`, `44 f.Kr.`
and `1990 e.Kr.` resolve, along with a before-present marker and the full
deep-time period vocabulary.

**Fuzzy month parts** are `begynnelsen av`, `midten av` and `slutten av`.

**The ordinal-last determiner** is `siste`, so `siste mandag i mai` resolves.
Bokmålsordboka gives it as "som kommer til slutt".

## The hour before one

This is the open decision of the locale, and both readings are defensible.

What resolves today, in twenty-four-hour terms: `halv ett` is 00:30, `kvart på
ett` is 00:45, `fem på ett` is 00:55. What a speaker usually means, given that
Bokmålsordboka's own `halv ti` gloss offers 09.30 *or* 21.30 for one phrase, is
12:30, 12:45 and 12:55 as readily as the small-hours reading. The
`toward_hour_12h` convention exists for exactly this: where it is set, the hour
that rolls back from one to zero surfaces as twelve.

Bokmål does not declare it, and neither do Danish, German, Dutch, Frisian,
Swedish, Nynorsk, or Malay — eight locales that share the coming-hour half
without it, the set defined by the flag combination rather than by family;
Malay is not Germanic. The one Germanic locale that does set it is Icelandic.

Declaring it here would not be a targeted fix. The flag is read at three points
in the resolver, and the two that matter are the bare half and the *explicit*
subtractive direction. Turning it on moves `halv ett` to 12:30, which is the
intent, but it also moves `kvart på ett` to 12:45 and `fem på ett` to 12:55 —
readings a speaker who said them at midnight would find wrong in the other
direction. Nothing in the flag distinguishes the two branches.

The cost in tests is exactly two pinned cases in this locale's own corpus,
`('halv ett', 0, 30)` and `('kvart på ett', 0, 45)` in
`test/nl_corpus_nb/test_nb_clock.py`. The Danish and Swedish corpora pin the
same pair for their own spellings, and `test/test_engine_bare_half_to.py` pins
the same shape once more for German `halb eins`. A change here is a family
decision, not a Bokmål one.

Unlike Danish, this locale has no marked form that already reads the way a
native expects: with no meridiem vocabulary, `halv ett om ettermiddagen`
cannot bind either, so there is no working reading to compare the unmarked one
against.

## Weaker provenance

The named days carry a precise CLDR locator, but the solid spellings and the
bare `går`/`morgen`/`forgårs`/`overmorgen` beside them do not appear in that
file and rest on nothing recorded.

The day-part *boundaries* are the CLDR chart, fetched and matching the
transcription, but taken from the Norwegian rows rather than the Bokmål ones,
which are empty. The gloss quoted in the vocabulary headers was checked
against Bokmålsordboka and matches.

The weekday and month names, the clock words, the range markers, the seasons
and the holiday vocabulary record no source.

## What refuses

**The article as a numeral.** `halv et`, `kvart på et` and `kvart over et`
return nothing. Only `ett` reads in the hour slot.

**The dotted timetable clock.** `14.30` and `klokka 14.30` both return nothing,
though the colon form `14:30` reads. The tokenizer splits on the dot for the
dotted civil date and no timetable-clock reading is attempted.

**The spelled decade.** `åttitallet` returns nothing. The decade construction
reads a digit plus a `tallet` surface, not a spelled decade name.

**Seconds.** `30 sekunder siden` returns nothing. No second unit ships.

**A bare duration.** `to uker` returns nothing. A quantity with no direction
marker is still only a quantity.

**The deictic morning adverb.** `i morges` returns nothing.

**Recurrence from the span edge.** `to ganger i uka` returns nothing. It is a
frequency, and the recurrence edge is what answers it.

## Open questions for a native speaker

1. Should `halv ett` and `kvart på ett` read as 12:30 and 12:45? The two
   branches move together, so the answer has to cover both.
2. Which day-part surfaces should carry a meridiem, and in which forms? This is
   the change that would let `klokka åtte om kvelden` mean 20:00.
3. Is the `natt` band's AM ceiling at 06:00 right for `om natta`, or does the
   late evening claim more of it in speech?
4. Should a `morgen` day-part surface ship despite the collision with the
   tomorrow word?
5. Should `åttitallet` and the other spelled decade names resolve?
6. Is `14.30` the written clock Norwegian readers expect to be understood?
