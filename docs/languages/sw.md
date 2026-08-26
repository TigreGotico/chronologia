# Swahili (`sw`)

Swahili has a clock this library will not read, and that is the single most
important thing on this page. `saa tatu` returns nothing.

Swahili counts the hours of the day from sunrise. `Saa moja` is seven in the
morning, `saa sita` is noon, and every reading is the Western hour minus six.
That convention is alive in written prose, not only in speech: East African
broadcasters title their own bulletins with it, publishing
`Taarifa ya Habari saa saba Mchana` for a programme that airs at 13:00. But the
Western reading is alive in written Swahili too — fixture tables and viewing
guides for international sport, syndicated with time-zone-sensitive digital
times, use 24-hour notation and never the sunrise count. The same string means
two things six hours apart, and which one it means is decided by the genre the
reader already knows they are in, not by anything present in the phrase.

Every wrong guess would be wrong by exactly six hours, which is the difference
between breakfast and lunch, or between an evening and a small-hours
appointment. So the locale reads the digital literal, which is unambiguous, and
refuses the spoken hour outright.

The refusal is narrow on purpose. `saa` is also the noun for an hour of
duration, and CLDR's own relative-time strings are built on it —
`saa {0} zilizopita` is N hours ago. Those keep working.

## What ships

**Weekdays** come from CLDR 47, `cldr-dates-full/main/sw/ca-gregorian.json`,
where the abbreviated forms are the same strings as the wide ones. The `Juma-`
series counts from Saturday, so the numeral inside a name is two short of the
Monday-first index the vocabulary files are numbered by: `Jumatatu` is
`juma` + `tatu` (three), the third day of the cycle, and `Jumapili` is
`juma` + `pili` (two), which is why Sunday rather than Monday is the day whose
name carries the numeral two. The locale's week starts on Saturday
accordingly.

**Months** are the CLDR wide and abbreviated names from the same file.

**Relative offsets** work by noun-class agreement rather than by a separate
"ago" word. CLDR's past pattern is the unit noun, the count, and an agreeing
relative pronoun — `miaka {0} iliyopita` for N years ago, `wiki {0} zilizopita`
for N weeks. That is the same pronoun the bare "last week" phrase uses, so in
Swahili the marker that says "last week" says "N weeks ago" as well. The
future is `baada ya`, literally "after", the same preposition that introduces a
plain succession.

The relative pronoun agrees with the noun class of the unit it follows:
`mwaka uliopita` and `mwezi uliopita` take the class 3/4 form, while
`wiki iliyopita` and every weekday — `Jumatatu iliyopita` — take class 9/10,
and `zilizopita` is the class 9/10 plural CLDR counts with above one. All three
ship together, because a marker slot is matched by surface: which one is
grammatical was decided by the noun the writer already chose, and a writer who
chose correctly must be read.

**Day parts** take their bands from the CLDR 47 day-period rules for `sw`,
transcribed in `chronologia/dayparts.py`: `alfajiri` 04:00–07:00, `asubuhi`
07:00–12:00, `mchana` 12:00–16:00, `jioni` 16:00–19:00, `usiku` 19:00–04:00.
A bare band still answers — `usiku` names the night — because a band names no
hour.

**Ranges** open with `kutoka` or `tangu` and close with `hadi` or `mpaka`.
`kati ya X na Y` is the between frame, with `na` joining the bounds.

**Numerals** come from Wiktionary's `Module:number_list/data/sw`; `na` joins a
tens word to its unit, as in `ishirini na tano` for twenty-five.

## What refuses

Each refusal below is pinned by a test.

**The spoken hour**, as above. Every shape of `saa N` as a time of day is
refused, in both conventions' worth of hours.

**A counted `saa` beside a day-part word.** `saa moja asubuhi` names one hour
inside the morning. Returning the whole 07:00–12:00 morning band would hand a
caller who asked for an hour a five-hour span, with the hour they asked about
dropped into the remainder, so the counted `saa` vetoes the band as well.
Declining the band is not the same as asserting either clock reading, which
stays unavailable.

**Century, millennium and decade.** `karne`, `milenia` and `muongo` are real
nouns and their classes are known, so their counted forms follow from the
productive concord rule. But a rule is not an attestation: no source consulted
shows any of the three actually counted in running text, and this library's
scope units are read from real usage rather than derived. All three stay out,
and the locale's units are exactly the seven CLDR counts — second, minute,
hour, day, week, month, year.

**`juma` as a week.** It is class 5/6 and it is the other word for a week — the
word inside every `Juma-` weekday name. Its class has no entry in CLDR's
relative-time data and no attested last/this/next form was found, so the
mechanical `ma-` concord guess `juma lililopita` is not shipped and `juma` is
not a unit at all. `wiki` already carries every week reading CLDR states, so
nothing is lost. Refusing the noun costs none of the seven names built on it:
`Jumatatu` and `Jumamosi` resolve as always.

**The ordinal register.** Swahili has a second way of naming a month —
`mwezi wa kwanza` for January, the first month — and a general ordinal built
from a class-agreeing connective plus the cardinal stem. CLDR does not carry
the ordinal month register, the sources that do are tutorial-tier, and the
connective's shape per class was not confirmed for the units this locale reads.
No ordinal vocabulary ships.

**The quarter.** CLDR gives Swahili a quarter field, and it is the one unit
whose relative forms use a different verb entirely — `robo ya mwaka inayofuata`,
the quarter that *follows*, rather than the `ijayo` / `ujao` every other unit
takes. This library's quarter constructions are built on a single quarter noun,
and `robo ya mwaka` is three words with an internal genitive.

**Seasons.** East Africa's year is divided by rains, not by four temperate
seasons, and no source consulted gives boundaries for `kiangazi`, `masika`,
`vuli` or `kipupwe`. Boundaries nobody stated are not invented, and the locale
ships no season vocabulary at all.

**Past-anchoring "since".** English `since Monday until Friday` reaches back to
the most recent Monday, because English keeps "since" and "from" apart and only
"since" looks backwards. Swahili's sources gloss `kutoka` and `tangu` together
as "from/since" without separating the senses, so the past-anchoring reading is
not claimed for a closed range: `tangu Jumatatu hadi Ijumaa` reads forward like
any other closed range. The open range still reaches back — `tangu jana` runs
from yesterday to the anchor.

## Open questions for a native speaker

1. Is there any written cue that distinguishes the sunrise clock from the
   Western one, or does it genuinely depend on genre alone?
2. Are `karne`, `milenia` and `muongo` counted in ordinary running text, and
   with which concord?
3. What are `juma`'s class 5/6 last/this/next forms?
4. What is the class-agreeing connective for the ordinal register, per unit?
5. Do `kutoka` and `tangu` differ in whether they look backwards, as English
   "from" and "since" do?
6. Are there stated boundaries for the rain-season words?
