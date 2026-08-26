# Thai (`th`)

Thai is written without spaces between words, and it names the hours of the day
on a six-hour cycle whose word changes with the part of the day. Both facts
shape what this locale reads, and the second one is why `หกโมง` returns
nothing.

`หกโมงเช้า` is six in the morning and `หกโมงเย็น` is six in the evening. Strip
the day-part word and the sources consulted disagree: one glosses a bare
`หกโมงห้านาที` as an evening reading, another puts a bare `หกโมง` in the
morning. The two candidates are twelve hours apart, nothing inside the phrase
chooses between them, and a reader cannot tell a wrong answer from a right one
by looking at it. So the locale reads `ตี N` and `N ทุ่ม`, which carry their
half-day in the hour word itself, and any `โมง` phrase that names its day part;
a bare one it refuses.

## Word segmentation

Thai spaces phrases and sentences, not words, so a date phrase arrives as one
undivided run of letters and nothing in it marks where a slot should begin.
The locale cuts such a run into words only when the **whole** run is covered,
end to end, by surfaces it already knows — the shipped vocabulary plus the
numeral and hour words — taking the longest match at each step. A run it cannot
cover completely is passed on untouched.

That is a refusal, not a shortcut. Maximal-match segmentation would cut a
reading out of the middle of ordinary prose, and Thai has the homographs to
make that go wrong: `จันทร์` is Monday and also the moon, `อาทิตย์` is Sunday
and also the week, `ตี` is the small-hours word and also the everyday verb "to
hit", `ทุ่ม` is the evening hour word and also "to hurl". Requiring the cover
to consume the entire run means a numeral syllable inside an ordinary word is
never mistaken for a count: `สามารถ` ("to be able") opens with the syllable for
three and is left alone.

The consequence to know about: a date phrase written with no space between it
and the surrounding prose does not parse. `ฉันจะไป พรุ่งนี้` reads; the same
words with the space closed up do not. A closed range needs the phrase space
too — range detection runs before the segmenter, so
`ตั้งแต่ วันจันทร์ ถึง วันศุกร์` reads as a range while the same words run
together return one endpoint and leave the rest as remainder. A counted offset
is not affected: `สามวันหลังวันจันทร์` reads whole.

## What ships

**Weekdays** are the CLDR 47 wide and abbreviated forms from
`cldr-dates-full/main/th/ca-gregorian.json`. The wide form carries the `วัน`
("day") prefix and the abbreviation is the same word without it. Both registers
occur in running text — CLDR's own relative-time data writes bare
`จันทร์ที่แล้ว` for last Monday and full `วันอาทิตย์ที่แล้ว` for last Sunday —
so both are read, but the prefixless form binds only where a marker or a date
frames it. On its own `จันทร์` is as likely to be the moon.

**Months** are the wide and abbreviated names from the same file. The
abbreviations are dot-internal and dot-final (`ม.ค.`, `พ.ค.`), so both the
dotted surface and its token-canonical spelling are registered.

**Relative offsets** come from `dateFields.json`. Thai has no plural agreement,
so CLDR carries one pattern per direction and the unit noun never changes
shape. CLDR splits the past marker by unit when generating text — `ที่แล้ว` for
the year, `ที่ผ่านมา` for everything shorter — but both forms occur on input for
every unit, so both are read for all of them.

**Day parts** are transcribed from the CLDR supplemental day-period rules for
`th`. CLDR draws two afternoon rows and labels both `บ่าย`, so they are one
band, 12:00 to 16:00. The two evening rows are not joined: `เย็น` is the late
afternoon, 16:00 to 18:00, and `ค่ำ` the hours after dark, 18:00 to 21:00, and
one band across both would answer five hours for a word that means three. The
night wraps 21:00 round to dawn. `เที่ยง` and `เที่ยงคืน` add no boundary of
their own and ship as clock landmarks.

**Numerals** are the digit words and the ascending place words from Wiktionary's
`Module:number_list/data/th` and `Module:th-utilities`, joined by positional
concatenation with the three irregularities those modules state as conditionals:
a units digit of 1 after a higher place is `เอ็ด`, a tens digit of 1 drops its
digit word to leave bare `สิบ`, and a tens digit of 2 is `ยี่`. Those are the
only licensed spellings of their values, so `หนึ่งสิบ` and `สองสิบ` read as no
numeral at all rather than being invented into 10 and 20. Two variants read but
are never generated: `หนึ่ง` for a final 1 in place of `เอ็ด`, and `ซาว` for
twenty. Thai digits ๐-๙ need no handling — they are Unicode decimal digits and
the shared tokenizer already reads them.

**The clock** counts minutes forward from the hour just named; there is no
subtractive "minutes to the hour" form in either source consulted. `นาที` is
optional after the count and `ครึ่ง` is the half. The hour itself is named on
the six-hour cycle: `ตี` plus one to five for the small hours, a numeral plus
`ทุ่ม` for the evening starting at 19:00, a numeral plus `โมงเช้า` for the
morning, `บ่ายโมง` for 13:00 and `บ่าย` plus a numeral plus `โมง` for the early
afternoon.

**The Buddhist Era** is read from its marker. `พ.ศ.` selects the Buddhist
year-numbering, 543 ahead of the Common Era, and `ค.ศ.` selects the Common Era;
the conversion runs through the shared era registry, and a marked year composes
with a full date line the way CLDR's own `d MMMM G y` pattern writes one.

## Weaker provenance

The per-quarter hour words rest on two language-teaching sources and a
Wikipedia article rather than on a reference grammar, and only the readings all
three agree on ship. The `โมงเช้า` hours are read directly — `แปดโมงเช้า` is
08:00 — because every worked morning example in those sources takes that
reading; the traditional cycle would number the same hours one to five, which
is why only six through eleven are read.

The first day of the week is the library default, Monday. CLDR's supplemental
week data was not consulted for `th`, so the locale states no convention of its
own rather than asserting one it cannot cite.

## What refuses

**A bare `N โมง`**, with or without a minute tail, for the reason at the top of
this page. `หกโมงห้านาที`, `แปดโมงครึ่ง` and `เจ็ดโมงยี่สิบ` all return nothing.
The minute count fixes the minutes, never the half-day, so the whole phrase is
withdrawn rather than half-read.

**The late afternoon, 16:00 to 18:00.** The sources disagree about which word
covers it: one gives 16:00-18:00 to `โมงเย็น` and starts `ทุ่ม` at 19:00,
another runs `บ่าย` from 13:00 to 18:00, a third draws the afternoon quarter as
13:00-18:59. The disagreement is about the label rather than the arithmetic,
but it means `บ่ายสี่โมง` and `สี่โมงเย็น` may or may not be the same reading.
The band is omitted rather than awarded to a winner, so `บ่าย` counts to 15:00
and `โมงเย็น` is read only at `หกโมงเย็น`, 18:00, which one source works out in
full. A refused clock phrase is withdrawn whole, day-part word included:
`บ่ายสี่โมง` returns nothing rather than decaying into the bare `บ่าย` band and
answering four hours for a phrase that named one minute.

**`หนึ่งโมงเช้า` through `ห้าโมงเช้า`**, where the direct reading and the
traditional cycle collide.

**The sixth hour of a quarter.** The quarters run one to five and the sixth
hour has its own names, `ย่ำรุ่ง` at dawn and `ย่ำค่ำ` at dusk, so `หกทุ่ม` and
`ตีหก` are not forms the language has. The two `ย่ำ` words themselves are not
shipped: no source consulted works out a reading for either.

**The week reading of `อาทิตย์`.** The word is both Sunday and the week. The
locale gives the surface to Sunday and ships `สัปดาห์` for the week, so a count
on `อาทิตย์` counts Sundays and never quietly answers a stretch of weeks.

**A bare four-digit year is Common Era.** Reading it as Buddhist instead would
move every foreign date quoted in a Thai text by 543 years, and nothing in the
digits says which era is meant — CLDR's own long and full date patterns for
`th` carry the era field for exactly that reason. No digit threshold is used to
guess: a cut-off would be silently wrong on one side of itself and is not a
fact about the language.

**Seasons, decades and centuries.** No source was consulted for them.

## Open questions for a native speaker

- The boundary and the label for 16:00 to 18:59, where the three sources
  disagree.
- Whether the traditional six-hour hour words are still the default in written
  prose, or whether written Thai now uses 24-hour notation and reserves `ตี`
  and `ทุ่ม` for speech. No corpus evidence was gathered either way, and the
  answer changes how much of the clock is worth having.
- Whether a bare four-digit year with no era marker is read as Buddhist by
  default in ordinary Thai prose. If it is, the policy above is the safe
  reading rather than the natural one.
- Whether `นาที` is genuinely optional after every hour word or only after
  some.
- How often a date phrase is written glued to the surrounding prose with no
  phrase space. That frequency is what decides whether exact-cover segmentation
  is cautious or crippling.
- Whether the week starts on Sunday or Monday in ordinary Thai reckoning.
