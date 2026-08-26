# Polish (`pl`)

Polish splits its clock system, and the split is deliberate. Only the half hour
counts toward the coming hour — `wpół do dziewiątej` is half toward nine, 08:30
— while the quarter uses the ordinary past-and-to reading: `kwadrans po
dziewiątej` is a quarter past nine, 09:15, and `za kwadrans dziesiąta` is a
quarter to ten, 09:45. `bare_half_to` is therefore set in `lang.json` and
`bare_quarter_to` is deliberately not. The vocabulary cites PWN's Poradnia
Językowa and the Polish Academy of Sciences' *Wielki słownik języka polskiego*
for both halves of that system.

The other decision that shapes the locale is the same one Russian faces: the
ordinary Polish temporal phrase is locative, not nominative. `w zeszłym
tygodniu`, `w ubiegłym miesiącu`, `w tym roku` — listing citation forms alone
would leave the normal register unreadable, so the unit nouns and the
determiners ship their full paradigms, cited to PWN's inflection rules.

## What ships

**Weekdays and months** ship as a nominative and a genitive each, with no
recorded source. That is a narrower listing than the unit nouns get, and it has
consequences noted below.

**The date line** is little-endian, and Polish is one of the languages that
writes the dotted civil date, so `15.06.2020` reads. `ordinal_dot` is on.

**The unit nouns** ship complete, and the vocabulary names the awkward ones.
`tydzień` alternates its stem — `tydzień` against `tygodnia` — and the locative
`tygodniu` carries `w tym / zeszłym / przyszłym tygodniu`. `rok` is suppletive
in the plural, `rok` against `lata`. `miesiąc` ships its locative `miesiącu`
for the same reason. Each cites the PWN dictionary entry for the word.

**The determiners** ship complete too. `zeszły` and `ubiegły` are hard-stem,
`poprzedni` and `ostatni` soft-stem, and all four are listed across the
adjective declension; `przyszły` and `następny` cover "next". `ostatni` doubles
as the ordinal-last determiner behind `ostatni poniedziałek maja`.

The demonstrative `ten` ships across the pronominal paradigm with one form
withheld on purpose. The dative `temu` is deliberately absent, because in
Polish `temu` is the ago-marker — `dwa dni temu` — and admitting it as a "this"
determiner would read a past offset as a present one.

**Relative offsets** are `za` forward and `temu` backward.

**The clock** carries `po` and `za` as the two directions, cited to PWN's
Poradnia Językowa, `kwadrans` as the quarter and `wpół` as the half.
`południe` and `północ` are the landmark points, and the hour is stated as a
feminine ordinal — `o ósmej`.

**The eras** are `p.n.e.` and `n.e.`, each with a dot after every element, and
the vocabulary explains the spelling: the abbreviated elements are followed by
words beginning with vowels. PWN's *Wielki słownik ortograficzny* is cited for
both. The expanded `przed naszą erą` and `naszej ery` read too.

**Ranges** are `od … do …`. `między … a …` reads where the endpoints are
months or bare days.

**Quarters, ISO weeks and month parts.** `pierwszy kwartał 2020`, `tydzień 12`
and the month-third words `początek`, `połowa` and `koniec` all resolve.
`połowa` is also the period noun behind the half-year, cited to PWN's *Słownik
języka polskiego*, so `pierwsza połowa 2020` reads as the first half of that
year.

**Day parts** take their boundaries from the Unicode CLDR 47 day-period chart
for `pl`, transcribed in `chronologia/dayparts.py` as morning `[06:00, 12:00)`,
afternoon `[12:00, 18:00)`, evening `[18:00, 21:00)` and night
`[21:00, 06:00)`. Note the evening: Polish closes it at 21:00, three hours
earlier than the Germanic languages do, and the night wraps across midnight
rather than starting there. Two of the four bands have surfaces, both of them
the deictic adverbs these phrases actually use — `rano` for the morning and
`wieczorem`, the instrumental of `wieczór`, for the evening. Both cite
Wiktionary.

## Weaker provenance

The day-part surfaces rest on Wiktionary entries, weaker than the PWN sources
behind the clock, the eras and the paradigms.

The weekday and month names, the seasons and the holiday vocabulary carry no
recorded source.

## What refuses

**`między` with weekday endpoints.** `między poniedziałkiem a piątkiem`
returns nothing, and so does the `i` variant. `między` governs the
instrumental, and the weekday vocabulary ships only the nominative and the
genitive — `wtorek` and `wtorku`, not `wtorkiem`. The same frame with month or
day endpoints reads: `między czerwcem a sierpniem` and `między 3 a 10 lipca`
both resolve.

**The afternoon and the night as day parts.** `po południu` and `w nocy` return
nothing. Only the morning and evening bands have vocabulary, even though the
CLDR table gives all four.

**Decades.** `lata 80` and `lata osiemdziesiąte` return nothing. The locale
declares no decade construction and ships no decade words.

**Seconds.** `30 sekund temu` returns nothing. No second unit ships.

**A bare duration.** `dwa tygodnie` returns nothing. A quantity with no
direction marker is still only a quantity.

## Open questions for a native speaker

1. Which instrumental weekday forms should ship so that `między poniedziałkiem
   a piątkiem` reads? The full weekday paradigm is the obvious answer, but only
   the forms Polish actually uses temporally are wanted.
2. What are the ordinary surfaces for the afternoon and the night bands, and
   are they single words or prepositional phrases?
3. Should `lata 80` and `lata osiemdziesiąte` resolve as decades?
4. Does the CLDR evening boundary at 21:00 match how a Polish speaker uses
   `wieczorem`?
