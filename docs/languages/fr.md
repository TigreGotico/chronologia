# French (`fr`)

The fact that decides the most in this locale is that French writes its numeric
date with slashes and not with dots. `15/06/2020` reads; `15.06.2020` returns
nothing at all. The dotted form is the official civil surface of German,
Russian, Polish, Czech, Finnish, Turkish and Dutch, and the parser reads it in
those locales, but it is not French and is not treated as French. Refusing it
is only half the rule: a numeral glued into a date-shaped run does not get to
be read as a lone year just because the run was rejected, so `15.06.2020`
answers nothing rather than answering 2020 with the day and the month quietly
gone. A year-first run is different — `2020.06.15` reads, because a four-digit
lead is year-first in every language.

The clock is the other thing to know early. French counts toward the coming
hour for the quarter to, `neuf heures moins le quart` being 08:45, which is
what `toward_hour_12h` in `lang.json` turns on, and it counts forward with
`et` for the quarter past and the half — `huit heures et quart`, `huit heures
et demie`.

## What ships

**Weekdays and months** ship wide and abbreviated. The vocabulary records no
source for them.

**The date line** is little-endian and takes the day as a bare cardinal:
`3 octobre 1990`, not an ordinal. `lang.json` sets `ordinal_dot` off, so a dot
after a numeral is never an ordinal marker in French, which is the same
decision that keeps the dotted date out. The slashed numeric form reads, and so
does the ISO-shaped year-first form on any separator.

**Relative offsets** run both ways with `dans` and `il y a`, and `lang.json`
allows the marker before or after the count, with an optional article and an
optional quantifier in either position. The quantifiers include `quelques` and
`plusieurs` for a vague three and `un`/`une` for one.

**The relative determiners** follow the noun in French, which is why the whole
locale is configured with `marker_position: post` — `la semaine prochaine`,
`lundi dernier`. `rel_period` is overridden to accept a leading article so
that the definite article on the noun does not block the read.

**The clock** carries `heures` as the hour word, `et` and `moins` as the two
directions, `quart` and `demi`/`demie` as the fractions, `du matin` and
`du soir` as the meridiem phrases, and `midi` and `minuit` as points. The
half word is cited to TLFi and Larousse under *moitié*, which the same
vocabulary file also supplies for the period sense ("l'une des deux parties
égales"), so `la première moitié de 2020` reads as the first half-year.

**Day parts** take their boundaries from the Unicode CLDR 47 day-period chart
for `fr`, transcribed in `chronologia/dayparts.py`, and the vocabulary cites
the Trésor de la langue française informatisé at CNRTL for the surfaces. There
are four bands and they are not the English four. The `nuit` is the small hours
`[00:00, 04:00)` — it is the beginning of the day named, not an English-shaped
night that starts the previous evening. The `matin` then opens at 04:00, two
hours before the English morning. The `après-midi` runs `[12:00, 18:00)`, and
the `soir` runs `[18:00, 24:00)` with no band between it and the nuit. The
hyphenated `après-midi` is canonicalised through the tokenizer, which splits
the hyphen into two tokens that the loader re-glues, and an ASCII-folded twin
ships for the same reason the pm meridiem keeps one.

**Ranges** are `du … au …` and `entre … et …`; `depuis` opens one that runs up
to the anchor and `jusqu'à` closes one that starts there.

**Quarters, ISO weeks, decades and eras.** `le premier trimestre 2020` and
`T1 2020` both resolve, as do `semaine 12`, `les années 80`, `les années
quatre-vingt`, `44 av. J.-C.` and `1990 ap. J.-C.`. A before-present marker
and the Julian, Unix, Anno Mundi and Holocene era prefixes all ship.

**Fuzzy month parts** are `début`, `mi-` and `fin`, which cut the month into
thirds: `début juin`, `mi-juin`, `fin juin`.

**The Roman calendar anchors** ship in both the Latin classical forms and the
French vernacular ones — `calendes`, `nones`, `ides` — cited to the French
Wikipedia article *Calendrier romain*, so `les ides de mars` resolves.

**Non-Gregorian calendars.** French carries month names for the Hebrew and
Islamic civil calendars and for the French Republican calendar, plus the
Japanese nengō era names. `15 ramadan 1440` resolves to its Gregorian day,
and so does `15 nisan 5785`.

**Habitual recurrence** is `les lundis`, and the vocabulary explains the
choice: the plural definite article on a weekday noun reads habitually, while
the singular `le lundi` is ambiguous between "next Monday" and "on Mondays"
and is deliberately excluded so that only the unambiguous plural fires. The
cited authorities are Larousse and Grevisse. This is a recurrence rather than
a span, so it is the recurrence edge that answers it and the span edge returns
nothing.

## Weaker provenance

The Hebrew and Islamic month vocabularies ship one spelling per month and
record no source for the French transliteration chosen. Hebrew Tishrei ships
as `tishrei` and `tishri`; the common French spelling `tichri` is absent.
Nothing in the repository says which transliteration convention was followed.

The French Republican month names ship in ASCII only — `vendemiaire`, not
`vendémiaire` — while the Gregorian months and the day parts carry their
accents. No source is recorded for the Republican set.

The weekday and month names carry no recorded source at all.

## What refuses

**The dotted date.** `15.06.2020`, `06.15.2020`, `15.6.2020` and
`le 15.06.2020` all return nothing, and none of them yields a bare year
either.

**Seconds.** `il y a 30 secondes` returns nothing. No second unit ships.

**A bare duration.** `quinze jours` returns nothing. A quantity without a
direction marker is still only a quantity — a fortnight unit does ship, but it
needs a marker to become a span.

## Open questions for a native speaker

1. Which transliteration convention should the Hebrew months follow, and
   should `tichri` and the other common French spellings ship alongside the
   ones already there?
2. Should the French Republican months carry their accents, and which
   spellings are standard in French historical writing?
3. Is the `nuit` really the small hours of the day named for a French reader,
   or does `cette nuit` said in the evening name the night that is beginning?
4. Does `le lundi` deserve a reading at all, given that it is genuinely
   ambiguous, and if so which of the two readings should win?
5. Should a Republican-calendar year (`an II`) be readable, and in what
   surface?
