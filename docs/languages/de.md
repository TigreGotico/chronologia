# German (`de`)

Two decisions shape this locale, and both are about the clock. German names
the half hour by the hour it is heading toward, so `halb acht` is 07:30 and
never 08:30; `bare_half_to` in `lang.json` is what turns that on. And in the
south, in the east and in Austria the same forward-looking logic extends to the
quarters — a bare `viertel neun` is 08:15 and `dreiviertel neun` is 08:45,
three quarters of the way to nine. Western and northern German has no such
bare forms and says `viertel nach acht` and `viertel vor neun` instead, which
is a different parse path entirely, so shipping both costs nothing: the bare
quarters only add readings for strings that would otherwise have gone
unparsed. The vocabulary names Bastian Sick's *Zwiebelfisch* column "Von
Viertel nach acht bis viertel neun" as the source for the regional forms.

The other thing worth knowing before reading further is that German writes its
civil date with dots and the day first — `15.06.2020` — and the corpus names
DIN 5008 as the authority for that surface.

## What ships

**Weekdays and months** ship in the wide and abbreviated widths. The
vocabulary records no source for them; they are the ordinary CLDR-standard
German names, and the abbreviations are written without the trailing dot
because the tokenizer strips it.

**The date line** is little-endian throughout, which `dmy` in `lang.json`
declares. Three shapes read. The spelled form is `3. Oktober 1990`, where the
ordinal dot is a genuine ordinal marker — `ordinal_dot` is on, capped at two
digits so a four-digit year can never be mistaken for one. The dotted civil
form is `15.06.2020`, and it reads all three components or none: a run like
`15.13.2020` or `31.02.2020` names no date, and crucially the year inside it
does not get to be read on its own either, because answering `2020` there
would hand the caller a whole-year span with the day and month silently gone.
The same all-or-nothing rule covers the slash and dash separators. A trailing
sentence dot is punctuation, not a fourth component, so `15.06.2020.` still
reads.

**Relative offsets** run in both directions with `in` and `vor` —
`in drei Tagen`, `vor fünf Minuten` — and `lang.json` allows the marker on
either side of the count. Units ship in singular and plural, with a separate
`unit1_` singular file per unit so that "one day" and "two days" pluralise
correctly rather than sharing one lexeme.

**The relative determiners** are where German is unusually generous, and the
vocabulary says why. Besides `letzt-`, everyday German uses `vorig-` and
`vergangen-` for a past weekday, and all three are attributive adjectives
taking the full strong, weak and mixed endings, so `marker_last.voc` lists
every ending rather than a stem. The source named is Duden's inflection tables
for *vorig*, *vergangen* and *letzter*. `letzt-` doubles as the ordinal
determiner in `der letzte Montag im Mai`, from the same Duden entry.

**The clock** carries, alongside the bare regional quarters, the ordinary
`viertel nach` and `viertel vor` directional forms, `Uhr` as the o'clock word,
`um` as the "at" marker, and midnight and noon as points. Only one timezone
offset ships, UTC.

**Day parts** are where German diverges hardest from English, and the
vocabulary spells it out. German splits into `Morgen`, `Vormittag`, `Mittag`,
`Nachmittag`, `Abend` and `Nacht`, where `Vormittag` is the half English has no
word for at all — Duden glosses it as the "Zeit zwischen Morgen und Mittag".
All six band boundaries come from the Unicode CLDR 47 day-period chart for `de`
and are transcribed in `chronologia/dayparts.py`: Nacht `[00:00, 05:00)`,
Morgen `[05:00, 10:00)`, Vormittag `[10:00, 12:00)`, Mittag `[12:00, 13:00)`,
Nachmittag `[13:00, 18:00)` and Abend `[18:00, 24:00)`.

Two consequences of that table are worth naming. The Nachmittag opens at 13:00,
after an hour-wide Mittag, and not at noon the way the English afternoon does.
And the Nacht is the small hours of the day named, not the evening — the Abend
holds the evening through to midnight on its own, so `heute Nacht` is
00:00–05:00 of today.

Only four of the six bands have vocabulary. `Mittag` is bound as the noon clock landmark instead, so
`heute Mittag` resolves to the point 12:00 rather than to the hour-wide band.
`Morgen` has no day-part vocabulary because the word is already taken:
`morgen` is "tomorrow", and a locale cannot read the same token both ways
without guessing. The four that do ship — Vormittag, Nachmittag, Abend, Nacht —
each carry both the noun form and the adverbial `-s` form, so `abends` reads as
well as `Abend`.

**The month framing marker** is `im`, the fusion of `in` and `dem`, which is
the standard frame for a calendar month in `im Januar`. The vocabulary cites
Wiktionary's German entry for *im*. `während` covers the explicit "during"
reading and ships in both the umlauted and the ASCII spelling, as several
German surfaces do.

**Ranges** open with `von`, `vom` or `ab` and close with `bis`. The vocabulary
cites Duden's entry for *von* for `vom` being the fused form of *von dem* and
the ordinary temporal range opener paired with `bis`, as in `vom 3. bis
10. Juli`. `zwischen … und …` reads as a range too, and `seit` opens one that
runs up to the anchor.

**Decades** read both spelled and written — `die achtziger Jahre` and
`die 80er Jahre` resolve alike.

**Quarters, ISO weeks and eras.** `erstes Quartal 2020` and `Q1 2020` both
resolve. ISO weeks read as `Woche 12` and `KW 12`. The eras are `v. Chr.` and `n. Chr.`
with their expanded forms, the secular `v. u. z.` beside them, and a
before-present marker.

**The Roman calendar anchors** ship in their German vernacular forms
`Kalenden`, `Nonen` and `Iden`, cited to the German Wikipedia article
*Römischer Kalender*, so `Iden des März` resolves.

## Weaker provenance

The bare toward-the-hour quarters rest on a single named source, and a widely
read newspaper column rather than a grammar. The reading is not in doubt — the
column exists to explain exactly this split — but it is regional, and the
locale ships it for all German without a dialect switch. Nothing in the
locale distinguishes a southern speaker's `viertel neun` from a northern
speaker's, so a northern text that happens to contain those two words in that
order will be read as a time.

The weekday and month names carry no recorded source at all. They are not in
doubt either, but the page cannot point at what was consulted.

## What refuses

**Seconds.** `vor 30 Sekunden` and `in 30 Sekunden` return nothing. No second
unit ships in the locale, even though the English locale has one.

**A dotted pair with no year.** `15. 6.` returns nothing, and so does
`am 15. 6. kommen wir`. Those are two ordinals; with no four-digit year to
anchor the pattern, no date may be fabricated from them.

**Malformed dotted runs.** `1.2.3.4`, `15..06.2020`, `15.06.`, `0.0.0`,
`99.99.9999`, `31.02.2020`, `32.06.2020` and `15.13.2020` all refuse, and so
does the thousands-grouped number `1.000.000`. A run that continues past the
shape — `15.06.20201` — refuses too, on every separator alike.

**A bare two-digit year.** `44`, `99` and `7` return nothing. `lang.json` sets
`bare_year_min_digits` to four, so a short bare number is never promoted to a
year.

**`halb` on its own.** With no hour and no landmark after it, `halb` is not a
time.

**A season in the genitive.** `während des Sommers` returns nothing, because
the season vocabulary ships only the bare nominative — `Sommer`, `Frühling`,
`Herbst`, `Winter` — and `während des` requires the genitive. The nominative
forms read perfectly well: `im Sommer`, `letzten Sommer` and the adjectival
`früher Frühling` all resolve.

**`Kalenderwoche` written out.** The abbreviation `KW 12` reads and so does
`Woche 12`, but the full compound `Kalenderwoche 12` returns nothing; only the
abbreviation is in the week-number vocabulary.

**The morning as a day part.** `morgens` returns nothing, and
`heute Morgen` resolves the whole of today with `Morgen` left in the
remainder rather than narrowing to 05:00–10:00. The collision with `morgen`
"tomorrow" is the reason; the band exists in the CLDR table but has no surface
bound to it.

**A bare holiday offset marker.** `nach Ostern` returns nothing on its own. A
holiday offset needs a measured distance — `zwei Wochen nach Ostern` and
`vierzehn Tage nach Ostern` both resolve to the same day.

**The penultimate weekday of a month.** `der vorletzte Freitag im Mai`
resolves the whole of May and leaves `der vorletzte` in the remainder. Only
`letzt-` is wired as an ordinal-last determiner; there is no
next-to-last vocabulary.

**A bare duration.** `vierzehn Tage` returns nothing. A quantity with no
direction marker is still only a quantity, and this is the library's rule
rather than anything German.

## Open questions for a native speaker

1. Should the bare toward-the-hour quarters be gated behind a regional
   variant rather than shipped for all German? The current setting reads
   `viertel neun` as 08:15 in a northern text as readily as in a Bavarian one.
2. Do the seasons need their genitive forms so that `während des Sommers`
   reads, and are there other case-marked contexts that would need the same?
3. Is `Kalenderwoche` common enough in running text to belong in the
   week-number vocabulary alongside `KW`?
4. How should `Morgen` and `morgens` be told apart from `morgen` "tomorrow"?
   The distinction is capitalisation in writing and context in speech, and
   neither is available to a case-folding tokenizer.
5. Does the Nacht band really start at midnight for a German reader, given
   that `heute Nacht` said in the evening usually means the coming night?
6. Are `Kalenden`, `Nonen` and `Iden` the forms a German text actually uses,
   or is the Latin left untranslated in most modern writing?
