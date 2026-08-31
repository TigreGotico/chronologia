# Persian (`fa`)

Persian ships two independent calendars for the same vocabulary of markers,
ranges and offsets, and the split between them is the first thing to
understand. `year_ref` defaults to the Solar Hijri (Jalali) calendar for a
bare four-digit year in the range 1200–1500 — the ordinary range of a
contemporary Persian date, such as `۱۴۰۳` — and falls through to Gregorian
outside that window or when the explicit `میلادی` ("Gregorian/AD") marker is
present. `calendar_date` reads Gregorian month names; `nongregorian_date`
reads the Solar Hijri month names against the same day/month/year orders. So
`۱۵ اسفند ۱۴۰۲` and `15 مارس 2024` both resolve, through two different
grammars sharing one vocabulary shape.

The second thing to know is the direction of the postpositional markers.
`marker_position` is set to `post`, so a determiner such as `آینده` ("next")
or `گذشته` ("last/past") follows the noun it modifies rather than leading
it, matching ordinary Persian word order — `هفتهٔ آینده`, the week the
coming, not a leading "next week".

## What ships

**Weekdays and months** ship without a recorded source. The Gregorian month
names are French-derived transliterations (`ژانویه`, `فوریه` …), the ordinary
form in Persian print and broadcast for a Gregorian date; the Solar Hijri
months (`فروردین` through `اسفند`) are a separate twelve-entry vocabulary keyed
`month_solar_hijri_arithmetic_N`, read only through the `nongregorian_date`
construction.

**The date line** is little-endian for both calendars: `DAY MONTH YEAR?` or
`MONTH DAY? YEAR?`, with the year optional in either order.

**Relative offsets** are `قبل از`/`پیش از`/`قبل` for the past and `بعد از`/
`پس از`/`بعد` for the future, trailing the count in the single fixed order
`NUM UNIT MARKER`.

**Ranges** are `از … تا …` for the bounded interval and `بین …` / `میان …`
for the coordinated pair. `از` is cited to the Dehkhoda Dictionary and the
Sokhan Comprehensive Dictionary, s.v. `از`, as the marker of the origin point
in time or place, correlative with `تا` for the terminal point — the
vocabulary's own comment gives `از ۵ ژوئن تا ۱۲ ژوئن` as the worked example.
`بین` and `میان` are cited to the same two dictionaries as governing two
coordinated terms joined by `و`, the same shape as Arabic `بين … و …`. `از` is
also the `since`-marker, the open reading of the same starting point, and the
vocabulary notes both roles trace to one entry.

**The locative prepositions** `در` ("in", governing a month) and `در` again as
`marker_of` are both cited to the Persian Wiktionary entry for `در`.

**Half and quarter quantifiers** ship as general-purpose fractions —
`نیم` for one half, `ربع` for one quarter — and resolve `نیم ساعت` to a
thirty-minute duration and `ربع ساعت` to a fifteen-minute one. Wiktionary's
entry for `ربع` glosses it "quarter, one-fourth" and gives `دو و ربع` ("two
and a quarter") as its own worked example for quarter-past-two on a clock —
confirming the fraction is the same word Persian speakers use for a spoken
clock time, not merely a duration word.

**The clock**, despite that, ships only two shapes: a bare digit clock
(`۱۵:۳۰`, `15:30`) and the marked hour `ساعت N` / `راس ساعت N`, plus the two
landmarks `ظهر` (noon) and `نیمه‌شب` (midnight). There is no `دو و ربع`-style
spelled fractional clock construction wired into `clock_time` — see Weaker
provenance.

**Day parts** take their boundaries from the Unicode CLDR 47 day-period chart
for `fa`: `night2` `[00:00, 01:00)`, `morning1` `[01:00, 04:00)`, `morning2`
`[04:00, 12:00)`, `afternoon1` `[12:00, 13:00)`, `afternoon2` `[13:00, 19:00)`,
`night1` `[19:00, 24:00)`. Three surfaces ship, each merging adjacent CLDR
bands into the single vocabulary a Persian speaker actually reaches for:
`صبح` (morning) for `morning2`, cited to CLDR `fa` `morning2` and to the
Persian Wiktionary entry for `صبح`; `بعدازظهر`/`عصر` (afternoon) for the
combined `afternoon1`+`afternoon2` span, cited to CLDR `fa`
`afternoon1`/`afternoon2`; and `شب` (night) for `night1`, cited to CLDR `fa`
`night1` and Wiktionary's entry for `شب`. The CLDR `morning1` (01:00–04:00)
and `night2` (00:00–01:00) bands have no shipped surface at all — no Persian
word in this vocabulary names the small hours between midnight and four as
their own band.

**Fuzzy period parts** are `اوایل`/`ابتدای`/`ابتدا` (early), `اواسط`/`وسط`/
`میانه` (mid), and `اواخر`/`آخر`/`پایان` (late).

**Quarters, ISO weeks, century and decade** resolve through `سه‌ماهه`/`فصل`
(quarter word), `هفته` (week number), `قرن` (century) and `دهه` (decade). `قرن`
and `دهه` both carry their own vocabulary comments: `قرن` as the standard
dictionary word for "century", and `دهه` as derived from `ده` ("ten") and the
standard word for a ten-year span.

**Seasons** are cited to the Dehkhoda Dictionary and the Sokhan Comprehensive
Dictionary, one entry each: `بهار` (spring), `تابستان` (summer), `پاییز`/
`پائیز` (fall, both hamza spellings listed since the tokenizer performs no
normalisation), and `زمستان` (winter).

**The weekend** is `آخر هفته`/`آخرهفته`, and `week_start` is set to Saturday
with `weekend_start: 3` — Thursday and Friday, the ordinary Iranian weekend,
rather than the Friday-Saturday weekend some other Persian-speaking regions
keep.

## Weaker provenance

The weekday names and the Gregorian month names carry no recorded source.
`hemisphere` is set to null in the locale's conventions, so seasonal
resolution does not lean on a fixed hemisphere assumption.

The short numeric CLDR date pattern for `fa` (`y/M/d`) orders year first,
while the long and full CLDR patterns (`d MMMM y`) order day first, matching
`dmy: true` in the locale's conventions. The two CLDR patterns disagree with
each other; this page follows the spelled-date pattern, which is what the
locale's `calendar_date` construction actually reads, and does not extend the
claim to bare numeric input.

## What refuses

**A spelled fractional clock time.** `دو و ربع` ("quarter past two") and any
`ساعت و نیم`-style half-past phrase return nothing: `ربع` and `نیم` are
general quantifiers wired to durations and to the scoped-ordinal grammar
(`ربع سوم`, "the third quarter"), never to `clock_time`. Wiktionary's own
`ربع` entry cites `دو و ربع` as the standard reading for quarter past two, so
this is an attested Persian clock idiom the locale does not read as a clock
time — flagged here as a defect, not fixed.

**Seconds.** No `unit_second` vocabulary ships, so `سی ثانیه پیش` ("30
seconds ago") returns nothing.

**The Solar Hijri year outside its window.** A bare four-digit year below
1200 or above 1500 is read as Gregorian rather than Jalali, by the
`calendar_year_range` guard in `lang.json`; a Jalali year outside that window
(a distant historical or far-future Persian date) is not reachable through a
bare year and needs the explicit calendar's own construction path.

**The small hours as a day part.** `صبح زود` ("early in the morning",
literally combining the `morning` surface with `early`) reaches the fuzzy
grammar, but nothing names the CLDR `night2`/`morning1` span (00:00–04:00) as
its own band — a phrase meaning specifically "the small hours" has no
dedicated surface.

## Open questions for a native speaker

1. Should `دو و ربع` / `ساعت سه و نیم`-style spelled fractional clock times be
   wired into `clock_time`, and does the "count past the hour" reading
   (Wiktionary's `دو و ربع` = quarter past two) hold for the half-hour form
   too, or does Persian switch direction the way Russian does?
2. Is Thursday–Friday the weekend to assume for every Persian-speaking
   region this locale serves, or should the Friday-Saturday convention be
   configurable?
3. Is there an ordinary Persian surface for the 00:00–04:00 span that the
   CLDR chart splits into `night2`/`morning1` but this vocabulary does not
   name at all?
4. Does the Solar Hijri calendar window (1200–1500) need widening for
   historical or far-future Jalali dates, and if so, by what guard?
