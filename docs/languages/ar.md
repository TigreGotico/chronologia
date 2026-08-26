# Arabic (`ar`)

The week starts on Saturday and the weekend is Friday and Saturday. That is set
in `lang.json` as `week_start: saturday` with `weekend_start: 4`, and it is the
first thing to know because it changes what "next week" and "the weekend" mean
before any vocabulary is consulted.

The second is that Arabic is postpositional for its relative determiners —
`الأسبوع القادم`, the week the coming — so the locale sets
`marker_position: post`, while the offset markers `قبل` and `بعد` lead their
counts.

## What ships

**Weekdays and months** ship wide and abbreviated, with no recorded source.
Both month naming conventions ship together: the borrowed set — `يناير`,
`أكتوبر` — and the Levantine set — `كانون الثاني`, `تشرين الأول` — so a text
using either is read.

**The date line** is little-endian: `3 أكتوبر 1990`, with or without a linking
`من`.

**The Islamic civil calendar** ships its own month names alongside the
Gregorian ones, so `15 رمضان 1440` resolves to its Gregorian day.

**Relative offsets** are `قبل` and `منذ` for the past and `بعد` and `خلال` for
the future, in either order relative to the count.

**The dual is present in the vocabulary.** Arabic marks "exactly two" with a
distinct dual form rather than the plural, and the locale ships dual files for
the day, hour, minute and week — `يومان`, `يومين` and their siblings — beside
the singular and the plural.

**The clock** ships the hour as a feminine ordinal after `الساعة`, plus
quarter and half fractions. The two directions are `و` for the additive form
and `إلا` for the subtractive one, the latter in both its hamza spellings.
`منتصف الليل` and `نصف الليل` are midnight and `الظهر` is noon, and a
midnight-crossing night meridiem `ليلا` ships alongside the plain AM and PM
ones.

**Day parts** are the one vocabulary in this locale with an explicitly recorded
human check: the surfaces are marked as confirmed by a named native speaker in
the project's own issue tracker, and the band boundaries are cited to the
Unicode CLDR 47 day-period rules for `ar`. Four bands ship — `الصباح`,
`بعد الظهر`, `المساء` and `الليل`.

One exclusion is recorded and worth repeating. `الظهيرة` is *not* listed as an
afternoon surface. It names midday, and midday is bound as the noon clock
landmark, so listing it as a band surface was dead vocabulary — the noon
reading always won. Only `بعد الظهر`, literally "after noon", names the
afternoon band.

**Ranges** are `من … إلى …` and `بين … و …`. The from-and-to pair is cited to
Wright's *A Grammar of the Arabic Language* and to Badawi, Carter and Gully's
*Modern Written Arabic*, both for `من` as the point of origin and `إلى` as the
limit reached, and `بين` is cited to the same two grammars for governing two
coordinated terms joined by `و`. The vocabulary notes that `من` is written as
a free word and never a proclitic, so it tokenizes on its own, and that `إلى`
ships in its hamza-less spelling `الى` too, a ubiquitous orthographic variant.

**Quarters, ISO weeks, decades and eras.** `الربع الأول 2020`, `الأسبوع 12`,
the spelled decade `الثمانينات`, `44 ق.م` and `1990 م` all resolve, along with
a before-present marker. The half-year is `النصف الأول من 2020`, and the
vocabulary records that the attested surface carries the definite article,
citing *Lisān al-ʿArab* under the root ن‑ص‑ف for `نصف` as one of two equal
parts.

**Fuzzy month parts** are `أوائل`, `منتصف` and `أواخر`.

## Weaker provenance

The day-part band edges that actually resolve are the library's default
four-band cut — morning to noon, afternoon to six, a short evening, and a night
that wraps across midnight — rather than the `ar` rows transcribed in
`chronologia/dayparts.py`. The surfaces are the checked part; the exact
boundaries a phrase resolves to are not the ones the vocabulary comment names.

The weekday and month names, the clock words, the seasons and the holiday
vocabulary carry no recorded source. The locale sets `hemisphere` to null.

## What refuses

**The dual as a count.** `يومين` returns nothing on its own, and so does
`قبل يومين` — "two days ago", which is the ordinary way to say it. The dual
files ship, but no construction reaches them, so a dual noun is not read as a
count of two.

**A proclitic `و`.** `بين يناير ومارس` does not read as a range: the
conjunction is written glued to the following word and the tokenizer does not
split it, so `بين` and `مارس` are stranded. Spaced as `بين يناير و مارس` the
same phrase resolves. The half-past clock form `الثامنة والنصف` refuses for the
same reason, and it does not resolve spaced either.

**Seconds.** `قبل 30 ثانية` returns nothing. No second unit ships.

**`الليلة` for tonight.** The night band ships as `الليل` and `ليلة`; the
definite `الليلة` returns nothing.

## Open questions for a native speaker

1. Which construction should read the dual, and in which positions? `قبل
   يومين` and `أسبوعين` are the everyday forms and neither resolves.
2. Should the tokenizer split a proclitic `و`, and would splitting it break
   anything — words that legitimately begin with `و` are the obvious risk.
3. Which day-part boundaries are right for Arabic, given that the ones cited
   and the ones that resolve differ?
4. Do the two month-naming conventions ever collide in a way that reads the
   wrong month, given that both sets ship at once?
5. Is `الثامنة والنصف` the ordinary way to say half past eight, and what should
   the clock read for it?
