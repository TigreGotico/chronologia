# Occitan (`oc`)

Occitan sits next to Catalan and reads like it, and the temptation to fill the
Occitan locale from the Catalan one is the single largest risk to this page's
accuracy. Catalan's date grammar lets the article stand inside the date —
`article? DAY of MONTH` — but that order does not carry over, because the two
locales disagree about what an article is. Catalan's `marker_article` holds
only `el`, `la`, `els`, `les` and `l`. Occitan's also holds the contracted
prepositions `del`, `de la`, `al` and `a la`, so an optional leading article in
the date grammar would swallow the `del` of `la setmana del 20 de julhet` and
the week-of reading would die. Occitan's article vocabulary contains
contracted prepositions where Catalan's does not, which is exactly why Catalan
can afford a leading article slot in its date orders and Occitan cannot.

The visible cost is small and worth naming: `lo 3 d'octòbre de 1990` gives the
right day and leaves `lo` in the remainder, where the Catalan equivalent
consumes it.

The other thing to know is that Occitan carries no day-part vocabulary at all.
No band table exists for `oc` in `chronologia/dayparts.py` and no
`daypart_*.voc` file ships, so `al matin`, `a la vesprada` and `la nuèch` all
return nothing as spans. The same words work as clock meridiems — `dètz oras
del matin` is 10:00 and `quatre oras del ser` is 16:00 — but there is no
morning-shaped answer to ask for.

## What ships

**Weekdays and months** ship, with abbreviations for most months and none for
weekdays. Neither group records a source. `mai`, `junh` and `març` ship
without an abbreviation because their full forms are already short.

**The date line** is little-endian: `3 d'octòbre de 1990`, with `de` optional
between the parts and no article slot, for the reason above. The slashed
numeric form reads; the dotted one does not.

**Contractions** are handled at the number-folding layer rather than the
tokenizer. `split_contractions` is off in `lang.json`, and the Occitan fold
hook instead declares the proclitics `l`, `d`, `un`, `qu`, `n` and `s`, so
`d'octòbre` and `l'an` come apart there.

**Relative offsets** are `dins` forward and `fa` backward, and the grammar has
a quantifier slot Catalan's does not. `un parelh de jorns` counts two,
`qualques jorns` and `unes jorns` count three, and `mièja ora` counts half —
so `dins una mièja ora` resolves where the Catalan `dins de mitja hora`
returns nothing. Seventeen locales carry that quantifier slot; Catalan is not
among them.

**The relative determiners** follow the noun — `lo diluns passat`, `la setmana
que ven`, `lo diluns prochan` — and `marker_position` is `post`. The
"previous" forms come from a native-speaker review filed as
[ovos-date-parser issue 300](https://github.com/OpenVoiceOS/ovos-date-parser/issues/300),
which supplies `darrèr` and `darrièir` beside `darrièr` and prefers
`precedent(s)` over the alternative the reviewer was shown. The vocabulary
records that `darrèr` and `darrièir` are attested masculine only and that
`precedent` is invariable in gender, so no feminine spelling was invented for
them.

**Ranges** use `de`/`del` as the from-lead and `a`, `au`, `al`, `fins a` or
`fins au` as the to-boundary, with `entre … e …` as the other frame and
`dempuèi`, `despuèi`, `dempuei` or `dès` opening a since-range. None of these
carry a citation in the vocabulary.

**The clock** subtracts with `mens` or `manca` and adds with `e`. `miègjorn`
and `mièjanuèch` are points. The `h` clock form is enabled in the fold hook,
so `10h30` and `10 h 30` both read.

**The night meridiem** is a midnight-crossing band, as in Catalan and Spanish:
small hours one to five stay AM, evening hours six to eleven are PM, twelve is
midnight. Occitan's contribution is the surface list rather than the
mechanism. Issue 300 supplies `nuèch`, `nuèit`, `nèit`, `nèt`, `nèch` and
`nuòch` together with their a-initial twins, all twelve of which ship. The
same review supplies the afternoon and evening forms `après miègjorn`,
`après merende`, `aprèp merende`, `après dinnar`, `aprèp dinnar` and
`vesprada`.

**Eras** run wider than in most locales. Besides `acn` and `apc`, the fold
hook recognises the spelled-out `abans jèsus-crist` and `aprèp jèsus-crist`
and the secular wording `abans nòstra èra` and `de nòstra èra`, each in both
its accented and unaccented spelling, so `44 abans nòstra èra` and `1990 de
nòstra èra` resolve. Anno Mundi, Holocene, Julian Day and Unix era prefixes
ship as well.

**Non-Gregorian calendars.** Occitan is one of the six locales — with
Asturian, English, French, Italian and Romanian — that carry French
Republican month names, and it also carries Hebrew and Islamic civil months,
Japanese era names, the consulship and *pridie* markers of the Roman
calendar, and the full geological period series. Catalan carries none of it.

**Decades** ship twice over: `los ans 80` reads the digits and `los ans
ochanta` reads the spelled tens, which have their own `decade_word_*` files.

**Seasons** are `prima` and `primtemps` for spring, `estiu`, `auton` and
`tardor` for autumn, and `ivèrn`/`ivern`. `tardor` is the same word Catalan
uses, and it is not a borrowing from the Catalan locale: the Occitan
Wiktionary carries `tardor` in its Occitan section as a feminine noun naming
one of the four seasons, alongside `auton` from Latin *autumnus*. The locale
pins `hemisphere` to `north`, where Catalan leaves it unset.

**The weekend** is `dimenjada`, built on `dimenge` the way Catalan's `cap de
setmana` is not built on anything; the Occitan Wiktionary glosses it as
Saturday and Sunday. `weekend` and `week-end` ship beside it.

**Numerals.** The fold hook adds `uèit` and `uòch` as spellings of eight,
because the upstream number vocabulary reads only `uèch`; issue 300 supplies
the variants.

## Weaker provenance

Most of this locale carries no citation. Weekdays, months, seasons, units,
ranges, the era abbreviations and the Roman anchors all ship without a
recorded source, which is a thinner record than the Catalan locale's.

Three sources are named without a fetchable locator. The half-unit noun
`mitat` is attributed to the Congrès Permanent de la Lenga Occitana's dicod'Oc
under *mitat*; dicod'Oc did not answer at any address that could be
constructed for it, so that citation is unchecked. The Occitan Wiktionary
corroborates the word independently, glossing `mitat` as "una de las doas
parts d'un tot". The locative `en` used with month names is attributed to the
*Diccionari general occitan* under *en*, likewise unchecked; the Occitan
Wiktionary confirms `en` as an Occitan preposition but does not confirm the
month usage. The vocabulary also declines a form it records as `aprvèspre` on
the grounds that it is a typo; the review it comes from writes `après vèspre`,
so the reason for the exclusion is sound but the spelling quoted for it is
not the one in the source.

The Roman anchors ship in Latin — `kalends`, `kalendis`, `calends`, `nones`,
`nonis`, `ides`, `idibus` — with no source at all, where Catalan ships
vernacular forms with one. That is not obviously wrong, but it is untested:
the Occitan Wiktionary's `calendas` means the twelve days before Christmas,
not the Roman kalends, so the vernacular form Catalan uses would be the wrong
word here.

Issue 300 is a native speaker's review on a public tracker, not a published
description of the language. It is the strongest evidence this locale has for
the surfaces it covers, and it is still one speaker.

## What refuses

**Seconds.** `fa 30 segondas` returns nothing. No second unit ships.

**The dotted date.** `15.06.2020` returns nothing.

**Day parts.** `al matin`, `de matin`, `a la vesprada`, `lo ser` and `la
nuèch` all return nothing, for want of any band table.

**Holidays.** `Nadal` returns nothing. Thirty-six locales declare a
`holiday_ref` construction and Occitan is not one of them.

**The Catalan quarter clock.** `un quart de quatre` and `tres quarts de
quatre` return nothing. Catalan's count-toward-the-hour quarters are a
Catalan construction, and nothing attests them for Occitan, so the slot is
absent rather than borrowed.

**A bare duration.** `quinzena` returns nothing on its own.

**Roman-numeral centuries.** `lo sègle XX` returns nothing.

## Known defects

Reproduced with `extract_timespan(text, "oc", anchor=datetime(2017, 6, 27,
13, 4))`.

`10 oras 30` comes back as 10:00 with `30` stranded, and `10 oras e 30` as
10:00 with `e 30` stranded. The minute is dropped rather than the parse
failing. The same time written `10h30`, `10 h 30` or `dètz oras e mièja`
resolves to 10:30.

`una ora de la nuèch` returns nothing where `1 ora de la nuèch`, `doas oras de
la nuèch` and `dotze oras de la nuèch` all resolve. `una` is claimed by the
indefinite-article and quantifier vocabularies and never reaches the hour
slot, so the one o'clock hour is the only one with no spelled-out form.
Catalan's `la una de la nit` resolves.

`idus de març` comes back as the whole of March with `idus de` stranded.
`ides de març` is correct at 15 March; the Latin `idus` that the sibling
anchor files otherwise favour is missing from the ides file.

`1r de genièr` comes back as the whole of January with `1r de` stranded, where
`primièr de genièr` resolves to 1 January.

`lo primièr de genièr` resolves correctly but leaves `lo` in the remainder,
the same article cost as the date line.

## Open questions for a native speaker

1. The review that seeded much of this locale says `abans-ièr` is a French
   borrowing and that `davant-ièr`, `ièr delà`, `ièr delai` and `passat ièr`
   are the forms the reviewer knows. All five ship, with `abansièr` first.
   Should the borrowed form be dropped, or kept and demoted?
2. Should the Roman anchors stay Latin, or is there an Occitan vernacular set
   that does not collide with `calendas` in its Christmas sense?
3. What are the Occitan day-part bands, and do they cut where Catalan's six do
   or where French's do?
4. Is `dimenjada` the whole weekend or Sunday alone in ordinary use, given it
   is built on `dimenge`?
5. Does `en genièr` mean "in January" in the temporal sense the locale reads
   it as, and is there a published source for that beyond the dictionary
   entry named for it?
