# Slovak (`sk`)

Slovak names the hour with a declined ordinal agreeing with an elided
`hodina`: `o druhej` is two o'clock, `o ôsmej` is eight, and the ordinal
stands in the feminine locative because the preposition `o` governs it. That
class is the one piece of morphology the locale owns outright — the cardinal
number model behind the fold reads nominatives and never emits `druhej`, so a
closed table of twelve surfaces is folded to its digit in a pass of its own.
It is also the reason Slovak reads no fractional clock at all, which is the
second thing to know and is set out below.

## What ships

**The date line** is little-endian, `DAY MONTH YEAR?`, matching the CLDR 47
`ca-gregorian` chart for `sk` at every level — full `EEEE d. MMMM y`, long
`d. MMMM y`, medium and short `d. M. y`. The tokenizer runs with `ordinal_dot`
and `dotted_date` on, so both the written `15. januára 2020` and the spelled
`pätnásteho januára 2020` resolve to the fifteenth of January. The spelled day
is a genitive ordinal agreeing with an elided day noun, and Slovak declines
both elements of a compound (`dvadsiateho tretieho`), so the day fold has to
claim the tens element before the cardinal fold can take it for a bare number.

**Months** ship in four cases at once. The nominative (`január`, `marec`) is
CLDR 47's `stand-alone` wide chart; the genitive that follows a day ordinal
(`januára`, `marca`) is the `format` wide chart, genitive throughout for
Slovak; the locative that follows the preposition (`januári`, `marci`) and the
instrumental (`januárom`) ship alongside them without a recorded source. So
`v januári` is the whole of January.

**Weekdays** ship in the nominative, matching CLDR 47's wide weekday chart,
with the accusative a `v <weekday>` phrase takes for the three whose
accusative differs (`stredu`, `sobotu`, `nedeľu`) and a genitive for each of
the masculine ones. No source is recorded for the choice of oblique forms.

**Day parts** are transcribed from the Unicode CLDR 47 day-period rules for
`sk`, each shipping as the form a phrase actually uses rather than a citation
form. `ráno` is the morning band, `popoludní` the afternoon and `večer` the
evening, so `dnes ráno` runs from 04:00 to 12:00, `dnes popoludní` from 12:00
to 18:00 and `dnes večer` from 18:00 to 22:00. The afternoon surface is the
locative singular of `popoludnie`, which is the spelling CLDR's own `format`
chart gives and which the Wiktionary declension table for that noun prints in
its locative row. The same words double as clock meridiem cues on an explicit
hour — `ráno` and `dopoludnia` for AM, `poobede`, `popoludní`, `podvečer` and
`večer` for PM — so `o deviatej večer` is 21:00 and `o deviatej ráno` is
09:00.

**The spoken hour.** The feminine locative ordinal that names the hour
(`jednej`, `druhej`, `tretej` ... `dvanástej`) is a closed table folded to its
digit after the cardinal pass, and it feeds the ordinary `at HOUR` order, so
`o druhej` and `o druhej hodine` are both two o'clock. This is a literal
named hour, not a toward-hour reading: the preposition plus locative simply
names the hour it says.

**Relative offsets** are `pred` (ago, governing the instrumental) and `za`,
`o` and `cez` (in/after). Direction is a fact of the marker, so `pred 5 rokmi`
is five years back and `o 5 rokov` five years ahead, both to the minute, and
`o päť minút` is five minutes ahead of the anchor.

**Determiners.** `minulý` and `posledný` ("last, previous"), `budúci` and
`nasledujúci` ("next"), and the demonstrative `tento` ("this") each ship a
full paradigm rather than a nominative alone, `minulý` and `posledný` on the
hard `pekný` pattern and `budúci` and `nasledujúci` on the soft `cudzí` one.
The oblique forms are what the ordinary phrasings need: `minulého roka` is the
genitive "last year" and `v minulom týždni` the locative "last week".
`posledný` also serves as the ordinal-last determiner, in full concord with
the weekday it scopes, so `posledný piatok v júni` is the last Friday of June.

**Unit nouns** ship full paradigms. `rok` carries both attested genitive
singulars, `roka` and `roku`, because the locative phrasings need the second
and the counted ones the first.

**Century.** `v 20. storočí` and `20. storočie` both resolve to the years 1900
through 1999. The locative `storočí` is spelled exactly like the genitive
plural — the form Slovak counts centuries with from five up — so behind the
preposition the century reading and a bare count of centuries are the same two
words. The written ordinal dot is what tells them apart, and the order that
binds the locative requires it: `v 20. storočí` resolves and `v 20 storočí`,
`v päť storočí` and `päť storočí` all refuse rather than answering with the
twentieth century. The declension is carried by the Wikislovník entry for
`storočie`, whose table gives locative singular `storočí` and genitive plural
`storočí` alike.

**Era markers** ship in both the secular and the Christian pair,
`pred n. l.` / `n. l.` and `pred Kr.` / `po Kr.`, together with the spelled-out
`pred naším letopočtom` and `nášho letopočtu` and the shorter `pr. n. l.` and
`p. n. l.` that circulate alongside. All four abbreviations match the CLDR 47
`sk` era chart, which gives `pred Kr.` and `po Kr.` as the primary pair and
`pred n. l.` and `n. l.` as the alternates. `500 pr. n. l.` resolves to the
right year in the right direction.

**Quarters, ISO weeks and decades** all resolve, with `štvrťrok` and `kvartál`
as two quarter words, `týždeň` for the ISO week and `desaťročie` for the
decade, so `prvý štvrťrok 2020` is the first quarter of 2020, `týždeň 12` the
twelfth ISO week and `2. desaťročie` the years 10 through 19.

**Named days** span all five positions around the anchor — `predvčerom`,
`včera`, `dnes`, `zajtra`, `pozajtra`.

**Scoped ordinals** are declared as an extension of the shared base grammar
rather than a replacement, so every base reading survives beside the locale's
own additions. `tretí pondelok v marci 2020` is the third Monday of March
2020, `posledná streda v mesiaci` the last Wednesday of this month, and
`prvý pondelok 2020` and `posledný pondelok 2020` the first and last Mondays
of that year.

**Ranges** run `od A do B`, so `od pondelka do piatku` and
`od 1. mája do 5. mája` both resolve.

## Weaker provenance

**Every citation into the Slovak Academy's dictionary portal is unverified
here.** The determiner paradigms, the unit-noun paradigms, the hour-ordinal
table, the day-ordinal table and both era files are attributed to
`slovnik.juls.savba.sk` — the Jazykovedný ústav Ľ. Štúra collection, and the
right authority for all of them. That host answers an automated client with a
JavaScript browser check rather than the entry: every request returns HTTP 200
with a page that says only that JavaScript is required, so none of those
locators can be confirmed without a browser. Treat the attributions as
unchecked rather than as absent evidence; the surfaces themselves are
ordinary Slovak and several are corroborated by CLDR.

**The preposition `v`.** Its file cites the English Wiktionary entry for `v`,
Slovak section, glossed "in". That section carries an alternative form, an
etymology, a pronunciation and a preposition heading with a
definition-requested marker in place of any sense — the gloss "in, inside, at"
belongs to the Slovene section immediately below it. The Slovak Wikislovník
page of the same name is the article for the Latin letter. Neither supports
the citation. The surface is not in doubt; the locator is wrong on both
wiktionaries.

**`ráno`.** Its file records that neither Wiktionary carries a Slovak `ráno` —
the English entry has a Czech section only, and Wikislovník has no page — and
falls back on the CLDR chart, whose `sk` row spells the morning band with this
exact surface. Both halves of that hold.

**The oblique weekday and month forms** carry no citation. The nominatives and
the format genitives are traceable to CLDR, but nothing on file says which
case `stredu` or `januári` is meant to serve, or whether the set shipped for
each word is complete.

**`štvrťrok` and `kvartál`** ship as unqualified synonyms with no source
distinguishing register, the same pair and the same silence the Bulgarian,
Czech and Slovenian pages record for their own two quarter words.

## What refuses

**The whole fractional clock.** `pol deviatej` is the ordinary Slovak for
08:30, and it returns nothing; so do `štvrť na deväť` and `tri štvrte na
deväť`, and so does the minute-counted `päť minút po deviatej`. No fraction
vocabulary ships and no order would read it. Of the eleven Slavic locales in
the library, Slovak is the only one that ships no clock fraction at all.

The refusal is deliberate and its reasoning is recorded with the number fold.
Slovak names the coming hour with the same declined ordinal it uses for the
literal hour — `pol druhej` is 1:30, attested in the Wiktionary translation
table under the English headword `half past`, whose worked example is "half
past one" — so the Croatian wiring, a bare cardinal behind a `bare_half_to`
flag, does not transfer: it would need an ordinal-aware toward-hour
construction of its own. And unlike Croatian's `pola`, Slovak's `pol` is a
genuine cardinal number word carrying the duration half (`pol hodiny` is
thirty minutes, `hodina a pol` ninety), so it cannot simply be lifted out of
the cardinal fold the way `pola` was. Both halves of that reasoning still
hold: `pol hodiny` and `štvrť hodiny` reach the duration reader through the
quantifier table and come back as thirty and fifteen minutes, and the
toward-hour ordinal is exactly the class the hour table already owns for the
literal reading, which is why folding it there would collide.

**A century before the era.** `20. storočie pred n. l.` does not return a span
two thousand years before the era; it is read as a twenty-century offset back
from the anchor and returns the years 17 to 117, with the era marker stranded.
The counted phrasing `20 storočí pred naším letopočtom` refuses outright,
which is the safer of the two behaviours, and `v 20. storočí pred n. l.`
returns the twentieth century of the common era and strands the marker.

**Spelled numbers in an oblique case.** Slovak puts the numeral after `pred`
in the instrumental, and the number model behind the fold reads only
nominatives, so `pred piatimi rokmi` returns nothing where `pred 5 rokmi`
resolves. The digit spelling covers the same ground.

**Night.** The CLDR 47 `sk` day-period chart gives `v noci` for the night
band, and no night day part ships, so `v noci` returns nothing and
`dnes v noci` returns the whole of today with `v noci` stranded. `dopoludnia`
has the converse problem: it is a meridiem cue but not a day part, so
`dnes dopoludnia` returns the whole day and strands the word. Czech, Polish
and Welsh share the shape — a morning day part and no night one.

**A leading preposition on a digit clock, and on the year and the period.**
The clock's first order begins at the clock itself rather than at an optional
`at?`, so `o 8:30` and `o 20:30` resolve to the right minute and leave the
preposition in the remainder. `v roku 2020`, `v minulom týždni`,
`v tomto týždni` and `v minulom roku` strand their `v` for the same reason on
their own orders, as do `cez víkend`, `na jar` and `v lete`.

**The final day of a month.** `prvý deň mája` resolves, because
`ORD UNIT MONTH` is declared; `posledný deň mája` does not, because no
`ordlast UNIT MONTH` order is. Yesterday comes back instead, with `mája`
stranded.

**`až` as a range word.** `od 1. mája do 5. mája` resolves and
`1. máj až 5. máj` does not: `až` is in no vocabulary file, so the first date
is returned alone and the rest of the range is stranded.

**Month abbreviations.** None of the twelve CLDR abbreviated month names
(`jan`, `feb`, `mar`, `apr`, `máj`, `jún`, `júl`, `aug`, `sep`, `okt`, `nov`,
`dec`) ship, so `15. jan 2020` returns the whole of 2020.

## Open questions for a native speaker

1. Is `o 9 hodín` nine o'clock or nine hours from now? The hour noun's
   genitive plural is in the clock vocabulary, so it reads as the clock, while
   the two-to-four form takes the offset: `o 2 hodiny` is two hours ahead and
   `o 9 hodín` is 09:00. The same construction therefore splits on the
   numeral's grammar alone, and the minute counterpart `o 9 minút` takes the
   offset reading throughout.
2. Is an ordinal-aware toward-hour construction worth building for
   `pol deviatej`, and does the quarter (`štvrť na deväť`) take the accusative
   after `na` as its only linking grammar?
3. What case do the shipped oblique weekday and month forms mark, and is the
   set complete for each word?
4. Are `štvrťrok` and `kvartál` interchangeable for a calendar quarter, or
   does one belong to fiscal usage?
5. Is `v noci` the right single surface for the night band, or does the
   locative phrase need a nominal partner?
