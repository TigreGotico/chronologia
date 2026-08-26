# Belarusian (`be`)

Belarusian looks like Russian and is not Russian, and the two words this locale
would most likely have got wrong by assuming otherwise are the two most
load-bearing ones. The minute is `хвіліна`, not the Russian cognate `мінута`.
The hour is `гадзіна`, not `час` — in the hour sense `час` is a documented
dialectal Russianism, and it is also the ordinary word for "time". Both are
confirmed directly from the CLDR display names for the language, not inferred
from the family. Nothing in this locale was produced by translating the Russian
vocabulary, and a test pins Russian wording as unreadable so it cannot creep
back in.

The clock is the other thing worth knowing up front. Belarusian names the
*coming* hour throughout, like Russian, but the grammar of it splits at the
half hour in a way Russian's does not.

## What ships

**Weekdays and months** come from Unicode CLDR 47,
`cldr-dates-full/main/be/ca-gregorian.json`. Months ship in both widths,
because they do different jobs: the stand-alone nominative names a bare month,
and the format genitive is what follows a day number — `25 сакавіка`. Weekdays
ship the wide name plus the genitive a date phrase takes (`у панядзелак`,
`да панядзелка`). The date line is `d MMMM y 'г'.`, day then genitive month
then year with the standard abbreviation `г.`, which is why the year word
accepts `г` alongside `год`, `года` and `годзе`.

**Units** are CLDR display names with the four plural forms CLDR's
`relativeTimePattern-count-*` keys give — those are the real declined forms in
context rather than a paradigm reconstructed from a table. Day is
`дзень / дні / дзён / дня`, week `тыдзень / тыдні / тыдняў / тыдня`, and so on.
The century, decade and the seasons are not in CLDR's field set and come
instead from the Тлумачальны слоўнік беларускай мовы, the explanatory
dictionary of the Yakub Kolas Institute of Linguistics.

**Relative offsets** are CLDR's own patterns: `{0} X таму` for the past,
`праз {0} X` for the future. The deictic days — `пазаўчора`, `учора`, `сёння`,
`заўтра`, `паслязаўтра` — are the CLDR relative-type entries for the day field.

Year has two irregular single words rather than a periphrasis: `летась` for
last year and `сёлета` for this year, which CLDR gives as the year field's
relative-type--1 and relative-type-0. The fold in
`chronologia/extract/numfold_be.py` rewrites each into the determiner and noun
pair the resolver reads, because Wiktionary's own entries for both gloss them
as exactly that. Every other unit uses the periphrastic `у мінулым месяцы`,
`на мінулым тыдні` phrasing, so `мінулы`, `гэты` and `наступны` ship in the
full adjectival paradigm those phrases put them in rather than in the citation
form alone.

**The clock, first half.** From minute zero to thirty, Belarusian uses `на`
plus the accusative ordinal of the coming hour: `палова на пятую` is 04:30,
`чвэрць на сёмую` is 06:15. This is structurally unlike Russian, which uses a
bare genitive ordinal in the same slot with no preposition. The source is
Вінцук Вячорка's "Каторая гадзіна?" column for Радыё Свабода, which states the
rule explicitly and gives the worked examples.

**The clock, second half.** From thirty to sixty, the minutes are subtracted
from the coming hour with `без` (or, with a fraction, `за`):
`без дзесяці першая` is 12:50, `за квадранец восьмая` is 07:45,
`без чвэрці адзінаццаць` is 10:45. Two independent sources carry worked
examples here — Вячорка's column, and the Тлумачальны слоўнік under `чвэрць`
("Гадзіннік паказваў без чвэрці адзінаццаць") and under `без`
("Роўна без дваццаці восем вечара" = 19:40). The genitive minute counts that
follow the direction word ship as their own small vocabulary, bound only in
that position.

**The half and quarter hour** are dictionary-sourced. `палова` and `палавіна`
come from the Тлумачальны слоўнік sense "the moment corresponding to the middle
of some hour", with its own worked examples `палову пятай` (04:30) and
`палавіна восьмай вечара` (19:30). `чвэрць` is the same dictionary's first
sense, "a fourth part of an hour (fifteen minutes)".

**Naming the hour in answer to "when?"** uses `а` or `аб` with the locative
ordinal — `а другой`, `аб адзінаццатай` — and switches to `у` before a minute
count. That distinction is Вячорка's, including his own explicit note about the
exception. `апоўдні` and `апоўначы` come from the dictionary.

**Numerals** are extracted from Wiktionary's `Module:number list/data/be`, the
Lua data table its own numeral templates render from, giving matched cardinal
and ordinal pairs from zero through one hundred.

**Markers** outside the CLDR relative-time set are dictionary entries
throughout: `пасля` (after, governing the genitive), `да` and `перад` (before),
`паміж` / `між` (between), `з` / `ад` (from, since), `кожны` (every, with the
dictionary's own examples `Аўтобус ходзіць кожныя пяць мінут` and
`Кожны дзень`), `апошні` for the last weekday of a month.

## Weaker provenance

**`квадранец`**, the older Latinism for a quarter hour, is thinner than
`чвэрць` beside it. `чвэрць` is a numbered dictionary sense with a worked
clock example. `квадранец` rests on Вячорка's column, which attests it with a
literary citation from Цішка Гартны. It is not a dictionary-only ghost word,
but it is one source and one literary attestation rather than a lexicographic
entry.

**The first-half `на` construction** has one source. Вячорка states the rule
and gives examples, and the second-half construction beside it is corroborated
by the dictionary, but nothing independent was found for `на` plus the
accusative ordinal specifically.

**`травень` for May** does not ship. Wiktionary lists it and `май` as mutual
synonyms with no archaic or dialectal label on either in Belarusian — unlike
Russian, where the same dictionary explicitly tags the equivalent as archaic —
so it is live vocabulary. But CLDR 47 gives `май` as the sole calendar name in
both widths, and only that ships. `25 траўня` returns nothing.

## What refuses

The refusals below are each pinned by a test, so that closing one requires
deliberately revisiting the decision.

**Day-part bands.** `раніцай`, `удзень`, `вечарам`, `ноччу` name no time at
all, and `сёння раніцай` resolves the day with the day part left unread. This
is the finding, not an omission: CLDR has no `dayPeriodRuleSet` entry for
Belarusian, so the boundary hours that would turn `раніца` into a clock band
were never defined for the language. Inventing them is exactly what the pin
prevents.

**A spelled minute count in the first half of the hour.** Вячорка's rule covers
`пяць хвілін на трэцюю` (02:05) as well as the fraction forms, but the clock
resolver has no additive toward-hour branch for a numeric minute — its only
toward-hour path is the fixed fraction and its only numeric-minute path
subtracts. Reading it anyway would return 03:00, an hour and five minutes
wrong. The fraction forms of the same idiom, `палова на трэцюю` and
`чвэрць на трэцюю`, do ship.

**`да` as a clock direction.** Вячорка lists `да` alongside `без` and `за` for
the second half of the hour, and it is deliberately absent. `да` is also the
ordinary preposition for every range end and deadline in the language — `да
пяці гадзін`, `з 5 да 12 ліпеня` — and reading it as a clock direction would
turn those into clock times. `чвэрць да шостай` returns nothing;
`без чвэрці шостая` and `за чвэрць шостая` both give 05:45.

**The announcement register.** `другая гадзіна пяць хвілін` and
`шаснаццатая гадзіна трыццаць хвілін` are real formal Belarusian, but no
construction order binds a trailing minute count onto a named hour, so the
minutes would be silently dropped and the hour returned on the dot. The digit
form of the same time is what reads.

**Century and millennium counts.** `5 стагоддзяў таму`, `праз 10 стагоддзяў`
and anything with `тысячагоддзе` return nothing: CLDR carries no relative-time
patterns for those fields in Belarusian, so their plural forms are unsourced.
The ordinal century, sourced as an ordinary neuter noun, does read —
`20-е стагоддзе` gives the twentieth century.

**Compound ordinals past a hundred.** The numeral module tabulates them through
one hundred. Past that the pattern was not separately verified, so it is not
extrapolated.

**`залетась` and `пазалетась`.** Wiktionary lists both as derived from
`летась` and glosses both "two years ago" — one gloss for two distinct words,
which cannot both be right, and no source consulted separates them.

**A relative hour period.** CLDR gives `у гэту гадзіну` as the hour field's
relative-type-0, but the resolver has no sub-day relative period at all; the
English "this hour" is refused by the same path. Not a gap in this locale.

## Open questions for a native speaker

1. Is `травень` still current for the calendar month, as against the seasonal
   or poetic sense? If so it could ship as a recognition-only synonym.
2. What distinguishes `залетась` from `пазалетась`? Both are glossed "two years
   ago" and they cannot name the same year.
3. Is `квадранец` still used in speech, or is it now only literary?
4. Does an independent source corroborate the `на` plus accusative ordinal
   construction for the first half of the hour?
5. Are there attested boundary hours for `раніца`, `дзень`, `вечар` and `ноч`,
   or is the absence of a CLDR rule set a genuine reflection of the language?
6. What are the plural forms of `стагоддзе` and `тысячагоддзе` in counted
   relative-time phrases?
