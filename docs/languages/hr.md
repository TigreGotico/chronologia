# Croatian (`hr`)

Croatian names the half hour for the hour that has not arrived, and it does so
with a bare cardinal: `pola devet` is 08:30 and `pola tri` is 02:30. That
single fact separates it from most of its Slavic neighbours, where the same
construction takes a declined ordinal agreeing with an elided hour noun
(`půl deváté`, `pol deviatej`, `полдевятого`). Because the hour is an ordinary
cardinal, no ordinal table is needed to read it and no post-pass has to be run
after the number fold; only the fraction word itself has to be kept out of the
cardinal fold, so that `pola` survives to fill the clock's fraction slot. The
same wiring serves Serbian, which spells the construction identically.

The second thing to know is that the locale's ordinal-scope grammar is
declared as a replacement rather than an addition, and several readings the
shared base grammar would have provided are absent because of it. Those are
set out under *What refuses*.

## What ships

**The date line** is little-endian, `DAY MONTH YEAR?`, matching the CLDR 47
`ca-gregorian` chart for `hr` — full `EEEE, d. MMMM y.`, long `d. MMMM y.`,
medium `d. MMM y.`, short `dd. MM. y.`. The tokenizer runs with `ordinal_dot`
and `dotted_date` on, and `lang.json` adds an "of"-linked order and a
month-led one beside the plain day-led shape, so `15. siječnja 2020` and the
spelled `petnaestog siječnja 2020` both resolve to the fifteenth of January.
Compound days compose from a bare cardinal tens element and a declined unit,
with or without the linking `i`: `dvadeset trećeg svibnja` and
`dvadeset i trećeg svibnja` are both the twenty-third of May.

**Months** ship in three cases. The nominative (`siječanj`, `veljača`) is
CLDR 47's `stand-alone` wide chart for `hr` word for word; the genitive that
follows a day ordinal (`siječnja`, `veljače`) is the `format` wide chart,
which is genitive throughout for Croatian; and the locative that follows the
preposition (`siječnju`, `veljači`) ships alongside them without a recorded
source. November is the one adjectival month, `studeni`, and its oblique
forms follow the adjective rather than the noun.

**Weekdays** ship in the nominative, which matches CLDR 47's wide weekday
chart, with the accusative that a `u <weekday>` phrase takes for the three
whose accusative differs (`srijedu`, `subotu`, `nedjelju`) and a genitive for
each. No source is recorded for the choice of oblique forms, and the masculine
weekdays ship only nominative and genitive because their accusative is
syncretic with the nominative.

**Day parts** are transcribed from the Unicode CLDR 47 day-period rules for
`hr`, and all four bands ship. Each surface is the deictic adverb a phrase
actually uses: `ujutro` (morning), `popodne` (afternoon), `navečer` and
`uvečer` (evening), `noću` (night). Wiktionary's Serbo-Croatian entries carry
`ujutro` as an adverb glossed "in the morning", `navečer` as an adverb glossed
"in the evening, this evening", and `noću` as an adverb glossed "at night, by
night, in the night" and derived there as the instrumental of `noć`. So
`danas noću` runs from 21:00 to 04:00 and `sutra ujutro` from 04:00 to 12:00.
The same words double as clock meridiem cues on an explicit hour — `ujutro`
for AM, `popodne`, `poslijepodne` and `navečer` for PM — so `u 9 sati navečer`
is 21:00 and `pola devet navečer` is 20:30.

**Relative offsets** are `prije` (ago) and `za` (in/after), with `u` carrying
"in" over a calendar period. That last preposition is cited to its
Serbo-Croatian Wiktionary entry, whose preposition sense list gives "in, at"
with the locative and "to, into" with the accusative, each with a worked
example (`biti u školi`, `ići u školu`).

**The emphatic day filler.** A bare genitive plural `dana` trailing a
year, month or week count is the idiom `godinu dana`, `tjedan dana` —
literally "a year of days", meaning exactly one year — and not a genuine extra
day. It is read as filler, so `za godinu dana` is one year ahead and
`prije tjedan dana` one week back, both to the minute. Croatian and Serbian
are the only locales in the library that ship this surface at all.

**Determiners.** `prošli` and `prethodni` ("last, previous"), `sljedeći` and
`idući` ("next"), `posljednji` and `zadnji` ("last of a series"), and the
demonstrative `ovaj` ("this") each ship a full paradigm rather than a
nominative alone, because Croatian names a past year with the adverbial
genitive `prošle godine` and a past week with either the accusative
`prošli tjedan` or the genitive `prošlog tjedna`. The masculine
genitive and dative carry both the short and the long variant
(`-og`/`-oga`, `-om`/`-ome`), and the neuter forms are shipped because the
season nouns are neuter: `prošlo ljeto` and `prethodno proljeće` both resolve.
The Hrvatski jezični portal declension tables for `prošli` and `prethodan`
carry every form on file, including the `-omu` dative the locale does not
need.

**Unit nouns** ship full paradigms for `godina`, `mjesec` and `tjedan`, the
last with its fleeting-vowel stem (`tjedan` / `tjedna`). The genitive
`godine` is what carries the adverbial `prošle/ove/sljedeće godine`, all three
of which resolve to the whole calendar year.

**Era markers** are cited to two sources that agree. The Hrvatski pravopis of
the Institut za hrvatski jezik prescribes the spaced Christian pair under its
rule on abbreviations formed from an initial syllable — the rule lists
`po. Kr. (poslije Krista)` and `pr. Kr. (prije Krista)` in exactly that
wording — and the Hrvatski jezični portal entries for `p. Kr.` and `pr. n. e.`
gloss each and name the other as its counterpart, giving the secular pair
`pr. n. e.` / `n. e.` alongside. Both pairs ship, spaced and unspaced.
`500 pr. Kr.`, `500 pr. n. e.` and `500 prije Krista` all resolve to the same
year.

**The clock's toward-hour half.** `pola` plus the bare cardinal of the coming
hour is the locale's only fractional clock surface, gated by `bare_half_to`
and `toward_hour_12h` in `lang.json` and read through an
`at? FRACTION HOUR MERIDIEM? ZONE?` order. The optional leading preposition
means `u pola devet` and `o pola devet` resolve with nothing left over, which
the equivalent Czech and Slovenian orders do not manage. Two Wiktionary
sources fix the direction with worked numeric examples: the Serbo-Croatian
adverb `pola` carries `pola tri — 2:30` in its own sense list, and the
translation table under the English headword `half past`, whose example is
"half past one", gives `pola dva` with the qualifier "used with the following
hour". Both name the coming hour, and `pola tri` resolves to 02:30.
`toward_hour_12h` makes `pola jedan` 12:30 rather than 00:30.

**`pola` stays out of the cardinal fold, `pol` stays in.** The shared Slavic
hook keeps a closed extra-word set of oblique numerals the number model's
nominative pronunciation misses, and `pola` is deliberately excluded from it:
the Croatian number back-end reads it as 0.5, and folding it would erase the
clock's fraction word before the grammar saw it. Its shorter sibling `pol`
stays in, because that is the plain cardinal half of a duration — `pol sata`,
`sat i pol`, `dva i pol sata` — and not the clock word. The accepted cost is
that the timespan-composing `za pola sata` no longer reaches the clock; the
duration reader still answers thirty minutes for `pola sata` and ninety for
`sat i pol` through the quantifier table.

**Quarters and ISO weeks** resolve, with `kvartal` and `tromjesečje` as two
quarter words and `tjedan` for the ISO week, so `prvi kvartal 2020.` is the
first quarter and `tjedan 12` the twelfth ISO week.

**Named days** span all five positions around the anchor — `prekjučer`,
`jučer`, `danas`, `sutra`, `prekosutra`.

**Ranges** run `od A do B`, and the bare `A do B` shape works as well, so
`od ponedjeljka do petka` and `od 1. do 5. svibnja` both resolve.

## Weaker provenance

**The oblique weekday and month forms** carry no citation. The nominatives and
the format genitives are traceable to CLDR, but nothing on file says which
case `srijedu` or `siječnju` is meant to serve, or whether the set shipped for
each word is complete.

**`uvečer`** ships as an evening day part with no source of its own. The
Wiktionary entry cited for the file is `navečer`, which lists `uvečer` only in
its related-terms line, never as the lemma with a gloss of its own.

**`popodne` as an adverb.** The day-part file describes its surface as the
adverb "in the afternoon". The Wiktionary entry it cites carries a noun sense
and a noun declension and no adverb sense at all, so the adverbial use rests
on the CLDR day-period data rather than on that entry. It is the same shape of
gap the Czech page records for its own evening word.

**`kvartal` and `tromjesečje`** ship as unqualified synonyms with no source
distinguishing register, the same pair and the same silence the Bulgarian,
Czech and Slovenian pages record for their own two quarter words.

**The determiner paradigms** are cited to the Hrvatski jezični portal's
declension tables, and the two locators recorded for `prošli` and `prethodan`
resolve to exactly those entries with the full paradigm printed. The locators
for `sljedeći`, `idući`, `posljednji`, `zadnji` and the `ovaj` series are
generic — they name the portal and its search page rather than an entry — so
those paradigms are attributed but not located.

## What refuses

**The quarter hour, and every minute counted to or past the hour.** Croatian
says `četvrt do devet` for 8:45 and `devet i četvrt` for 9:15, and neither
resolves: the locale ships no quarter fraction, no clock-direction words and
no order that would bind them. `pet do devet` and `pet minuta poslije devet`
return nothing for the same reason. The quarter reaches only the duration
path, where `četvrt sata` is fifteen minutes.

**Every century, decade and millennium reading.** `20. stoljeće`,
`dvadeseto stoljeće` and `2. desetljeće` all return nothing, and
`u 20. stoljeću` is worse than nothing: the dotted twenty is claimed as a
clock hour and the phrase comes back as eight in the evening with `stoljeću`
stranded. The cause is structural rather than lexical. `lang.json` declares
its ordinal-scope grammar as an `override`, which replaces the shared base
list outright, and the base list is where `article? ORD SCOPE_UNIT` — the
order every century, decade and millennium reading runs through — is defined.
The century noun is in the vocabulary; no order reads it. Four other Slavic
locales declare the same override and lose the same reading, and Belarusian,
which also overrides, re-lists that one order and keeps it.

**Several other scoped-ordinal readings, for the same reason.** The base
grammar's "Nth weekday of a bare year" and "Nth weekday of this period"
orders go with it. `prvi ponedjeljak 2020` does not return the first Monday of
2020; it returns next Monday and drops the year, which is a confident answer
to a question nobody asked. `posljednja srijeda u mjesecu` returns next Wednesday, with
`posljednja u mjesecu` stranded: the weekday is read, but the ordinal-last
scoping is discarded.

**The final day of a month.** `prvi dan svibnja` resolves, because
`ORD UNIT MONTH` is declared; `posljednji dan svibnja` does not, because no
`ordlast UNIT MONTH` order is. The whole of May comes back instead, with
`posljednji dan` stranded.

**The CLDR genitive of November.** `studenoga` is what the CLDR 47 `format`
wide chart gives for the eleventh month, and only the shorter `studenog`
ships. So `15. studenog 2020` is the fifteenth of November and
`15. studenoga 2020` is the whole of 2020 with the day and month stranded.

**Month abbreviations.** None of the twelve CLDR abbreviated month names
(`sij`, `velj`, `ožu`, `tra`, `svi`, `lip`, `srp`, `kol`, `ruj`, `lis`, `stu`,
`pro`) ship, so `15. sij 2020` returns the whole of 2020.

**The two-word afternoon.** CLDR 47 gives `poslije podne` as the `format`
spelling of the afternoon band and `popodne` as the `stand-alone` one, and
only the one-word form ships. `danas poslije podne` therefore does not return
this afternoon; it decomposes into the noon landmark and returns the single
minute at 12:00.

**The singular hour noun on the clock.** `marker_oclock` holds only the plural
`sati`, so `u 9 sati` resolves cleanly while `u 1 sat` and `u 2 sata` — the
counted forms Croatian requires for one and for two through four — resolve to
the right hour but strand the noun.

**A neuter ordinal on the quarter word.** The ordinal fold derives its
surfaces from the masculine nominative the number model pronounces, and
`tromjesečje` is neuter. `prvi kvartal 2020.` resolves; `prvo tromjesečje
2020.` returns the whole of 2020 and strands the words that named the quarter.

## Open questions for a native speaker

1. Is `četvrt do devet` worth wiring, and does the quarter take the same
   toward-hour direction as `pola` or the English one? The half hour is
   attested twice over; the quarter is not attested here at all.
2. What case do the shipped oblique weekday and month forms mark, and is the
   set complete for each word?
3. Are `kvartal` and `tromjesečje` interchangeable for a calendar quarter, or
   does one belong to fiscal usage?
4. Does `uvečer` compete with `navečer` closely enough to earn a source of its
   own, and should it also be a PM clock cue? It is an evening day part but
   not a meridiem word, so `pola dvanaest navečer` binds and
   `pola dvanaest uvečer` strands.
5. Is `poslije podne` the spelling a speaker would type for the afternoon, or
   has `popodne` displaced it in ordinary writing?
