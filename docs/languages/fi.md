# Finnish (`fi`)

Finnish has no prepositions to speak of. Where another language puts a word in
front of a noun to say "at", "from" or "until", Finnish puts a case ending on
the end of it: `maanantaista` is "from Monday", `perjantaihin` is "to Friday",
`kello kolmelta` is "at three o'clock". That is the fact that governs
everything on this page. A vocabulary file for Finnish is not a list of words
but a list of *forms*, and the constructions a locale can read are exactly the
ones whose case it happens to have shipped. Where a case is missing the phrase
does not degrade — it either returns nothing at all, or, more dangerously, it
resolves without the ending and returns a confident answer to a different
question.

## What ships

**Months** ship in four cases each: the nominative `elokuu`, the partitive
`elokuuta` that a day-led date takes, the genitive `elokuun` that leads a
month-led one, and the inessive `elokuussa` for "in August". The nominative set
matches the CLDR 47 `fi` `ca-gregorian` stand-alone wide chart and the
partitive set matches its format wide chart, which is partitive throughout for
Finnish. So `15. elokuuta 2020` and `elokuun 15.` reach the same day and
`elokuussa` reaches the month.

**Weekdays** ship in the nominative and the essive — `maanantai` and
`maanantaina` — and CLDR 47 accounts for both, the stand-alone wide chart
giving the nominative and the format wide chart the essive for six of the
seven. CLDR's format chart has Sunday in the nominative where the other six are
essive; the locale ships both forms for all seven and is the more complete for
it.

**The date line** is little-endian and dotted. CLDR 47 gives `d.M.y` for both
the medium and the short `fi` format, and the tokenizer runs with `dotted_date`
and `ordinal_dot` on, so `3.6.2020` resolves and so does the ordinal spelling
`15. elokuuta 2020`. Spelled ordinals fold from the number model's own
`pronounce_ordinal_fi`, which emits every day of the month as a single
compound word, so `viidestoista huhtikuuta` binds the fifteenth. Iso suomen
kielioppi §770 is the grammar reference the numeral module names for the
ordinal series.

**Relative offsets** are built from postpositions, not prepositions:
`kahden viikon päästä` is in two weeks, `kaksi viikkoa sitten` is two weeks
ago, `kolmen viikon kuluttua` is in three weeks. The numeral in the forward
frame is genitive, a form the number back-end does not read, so the genitives
one through twenty are given to the fold explicitly along with `puolen` and
`puolentoista`. The unit nouns ship in the nominative, partitive and genitive,
and the CLDR-attested oblique case beside them.

**Relative periods** take the case CLDR records for each field, and the
vocabulary comments name the chart and the exact strings. The week is adessive
(`viime viikolla`, `tällä viikolla`, `ensi viikolla`), the year essive
(`viime vuonna`, `tänä vuonna`, `ensi vuonna`), and the month inessive on the
short noun `kuu` rather than on `kuukausi` (`viime kuussa`, `tässä kuussa`,
`ensi kuussa`). Every one of those nine strings is in CLDR 47's `fi`
`dateFields` at the relative type the comment claims, and the demonstrative
ships in all three cases the three fields require — `tänä`, `tässä`, `tällä` —
for exactly that reason.

**The clock** binds a digit hour after `kello` or `klo`, or bare, and reads the
ablative telling-time forms as hours in their own right. `kello kolmelta` and
the bare `kolmelta` both give three o'clock, because the ablative numerals one
through twelve are listed explicitly and a bare one synthesises the missing
`kello`. Wiktionary's entry for the suffix `-lta` identifies the ablative;
Iso suomen kielioppi §1237 is cited alongside it for the telling-time use, and
that section could not be fetched to check. `keskiyöllä` and `keskipäivällä`
are midnight and noon, and both are CLDR 47's `fi` day-period labels for those
two points.

**The half hour runs toward the coming hour.** `puoli kymmenen` is 09:30, not
10:30 — the hour named is the one being approached. The reading is enabled by
`bare_half_to` and read through a `FRACTION HOUR` order, and twenty-six of the
locales here use the same flag. Fifteen locales additionally declare that a
toward-hour twelve means half past noon rather than half past midnight;
Finnish is not among them, and neither is either of the other two Uralic
locales, so `puoli yksi` resolves to 00:30.

**Named days** span the five positions around the anchor and are exactly CLDR
47's `fi` day field for relative types −2 through +2: `toissa päivänä`,
`eilen`, `tänään`, `huomenna`, `ylihuomenna`. The solid spelling
`toissapäivänä` ships beside the spaced one, and the comment's justification
holds up — CLDR's short and narrow charts write the same phrase solid as
`toissap.`

**The quarter** has two names in CLDR 47's `fi` `dateFields`, the long
`neljännesvuonna` and the short `neljänneksenä`, both essive, both attested in
the relative phrases; the vocabulary ships both alongside the nominative and
adessive forms. `Q3 2020` and `viikko 33` resolve through the Latin-letter and
week-number paths.

**Quantifier words** are declared for the approximate counts Finnish uses
instead of a numeral: `pari` for two, `muutama` for three, `puoli` for a half,
`neljännes` and `vartti` for a quarter. They reach the duration reader, where
`pari viikkoa` is fourteen days and `puoli tuntia` is thirty minutes.

**Fuzzy periods** read `alku`, `loppu` and `puoliväli` with their inessive and
adessive forms, so `elokuun alussa` and `elokuun lopussa` return the first and
last thirds of the month.

**Seasons, eras, business days and recurrence** all resolve. The seasons ship
in the nominative and adessive; the eras carry both the secular `eaa.`/`jaa.`
and the Christian `eKr.`/`jKr.`; `arkipäivä` and `työpäivä` drive the
business-day count; and `joka maanantai`, `päivittäin` and `viikoittain` all
come back as recurrences.

## Weaker provenance

**The ablative hour table has one reachable source and one that could not be
checked.** Wiktionary's `-lta` entry resolves and identifies the case, but it
says nothing about telling the time — its usage note only points at the general
appendix on Finnish nominal cases. The telling-time claim rests entirely on the
Iso suomen kielioppi section named beside it, and that site answers a fetch
with a challenge page rather than the text. The forms themselves are ordinary
and uncontroversial; it is the locator that is unconfirmed.

**No source is recorded for the case selection.** The month vocabulary ships
four cases and the weekday vocabulary two, and nothing on file says why those
and not others, or whether the set is complete for the constructions the locale
claims to read. The gaps below suggest it is not.

## What refuses

**The standard clock separator.** Finnish separates hours from minutes with a
period, not a colon. Kielikello, the Institute for the Languages of Finland's
journal, states it plainly — "Suomenkielisissä teksteissä kellonajan tunnit ja
minuutit erotetaan toisistaan pisteellä" — and gives `klo 9.15` and `klo 9.00`
as examples. CLDR 47 agrees: the `fi` short time format is `H.mm`. Neither
`klo 9.15` nor `kello 15.30` nor a bare `15.30` resolves. The colon spelling
does, so `15:30` works and the spelling every Finnish style guide prescribes
does not. `kello 15:30` has the converse problem and strands `kello`, because
the order that admits a colon-spelled clock has no slot for the preceding
o'clock word.

**Every case-marked range.** This is the largest gap on the page and it follows
directly from the language's own grammar. Finnish opens a range with the
elative and closes it with the illative — `maanantaista perjantaihin`,
`tammikuusta maaliskuuhun`, `yhdeksästä viiteen` — and no vocabulary file in
the locale ships an elative or an illative of a month, a weekday or a unit
noun. The months have nominative, partitive, genitive and inessive; the
weekdays have nominative and essive; the units have nominative, partitive,
genitive and one CLDR-attested oblique. So all three of those phrases return
nothing at all. What does work is the postpositional frame, `tammikuun ja
maaliskuun välillä`, and the two bound words `alkaen` and `asti`/`saakka`
declared as trailing markers.

**Those trailing markers reach only a bare year.** `2020 alkaen` and
`2022 asti` resolve. `1.6.2020 alkaen` returns the single day and strands
`alkaen`; `1.6.2020 asti` does the same. Written idiomatically the phrase needs
a case on the noun as well, and the case is not there: `vuodesta 2020 alkaen`
resolves the year but strands `vuodesta`, and `vuoteen 2022 asti` strands
`vuoteen`. The worst of the family is `elokuusta 2020 alkaen`, which strands
the month, reads what is left as "from 2020", and returns a span opening on the
first of January — a confident answer seven months wide of the phrase.

**The postposition for "after".** `vuoden 2020 jälkeen` resolves the year and
strands `jälkeen`, so the phrase reads as the year itself rather than as
everything past it. The engine allows a locale to declare where a marker sits
for four roles — until, since, for, from — and "after" is not one of them, so
there is no way to declare `jälkeen` as the postposition it is.

**Day parts.** No day-part vocabulary ships, and `chronologia/dayparts.py`
records CLDR day-period bands for forty-nine languages without Finnish among
them. CLDR 47's `fi` chart names five — `aamulla`, `aamupäivällä`,
`iltapäivällä`, `illalla`, `yöllä` — so `aamulla`, `illalla` and `yöllä`
resolve to nothing at all, and the two that do ship are registered only as
clock cues: `kello 9 aamupäivällä` is 09:00 and `kello 21 illalla` is 21:00
with `illalla` left in the remainder. Eleven of the locales here ship no
day-part vocabulary, so the shape is not unique, but Estonian and Hungarian —
the only other Uralic locales here — each ship all four.

**The half hour in the ablative.** `puoli kymmenen` resolves and
`puoli kymmeneltä` does not: the fraction order wants a bare hour, the ablative
hour fold produces a clock token instead, and the two do not compose. The
result is 10:00 with `puoli` stranded, which is thirty minutes and one hour
away from what the phrase says.

**The quantifier words in an offset.** `pari` and `muutama` are declared as two
and three and reach the duration reader correctly, but not the relative-offset
grammar. `pari viikkoa sitten` returns one week ago with `pari` in the
remainder, and `muutama viikko sitten` returns the same. The mechanism exists —
the English locale resolves "a couple of weeks ago" and "a few weeks ago" to
two and three weeks — so this is a wiring gap rather than an engine limit, and
it is the one gap on this page where the same locale answers the same word two
different ways depending on which reader sees it.

**Abbreviations.** CLDR 47 gives clipped month names for `fi` — `tammi`,
`helmi`, `maalis` and the rest — and two-letter weekdays, `su ma ti ke to pe
la`. Neither set ships, so `15. elo 2020` returns the whole of 2020 with the
day and month stranded, and `ma 15.6.2020` returns the day with `ma` left over.
Twenty-five of the locales here ship an abbreviated weekday file.

**The dotted date without a year.** `3.6.2020` resolves; `3.6.` on its own,
which is how a Finnish diary writes a day, returns nothing.

**The decade by its ordinary name.** Finnish names a decade with `-luku`
attached to the year — `1990-luku`, `1990-luvulla`. Neither resolves: the
scope-unit vocabulary has `vuosikymmen` and the year binds on its own, so both
return the single year 1990 and strand the decade word. Nine of the locales
here ship a spelled-decade vocabulary and this is not one of them.

**A bare ip.** `kello 9 ip.` resolves to 21:00, but `9 ip.` alone returns
nothing, because every meridiem-bearing clock order requires the o'clock word
in front.

## Open questions for a native speaker

1. Which cases of a month, a weekday and a unit noun does a date or range
   phrase actually need — is it the full elative and illative pair for each, or
   do the postpositional frames carry enough of the load in practice?
2. Is the period-separated clock (`klo 9.15`) genuinely dominant over the
   colon, or has the colon become common enough in running text that both
   should read?
3. Does `puoli yksi` mean half past twelve noon, half past midnight, or
   whichever of the two the context makes plausible?
4. Is `1990-luvulla` the ordinary way to name a decade in speech, or does
   `vuosikymmen` carry that weight outside written registers?
5. Are `pari` and `muutama` precise enough in a temporal offset to bind to two
   and three, or is the vagueness part of what a speaker means by them?
