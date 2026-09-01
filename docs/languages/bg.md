# Bulgarian (`bg`)

Bulgarian is the analytic outlier of the Slavic locales here: no case system
survives on the noun, so "last week" and "next week" are carried entirely by
adjective agreement and Bulgarian's postposed definite article
(членуване) rather than by a declension the way Slovenian or Latvian would do
it — миналата седмица, "last-the week", with the article fused onto the
adjective, not the noun. That is the first thing to know about the locale;
the second is that its spoken clock names the half hour in the opposite
direction from Slovenian and Estonian — forward off the hour that has
passed, not toward the one coming.

## What ships

**The date line** is little-endian, `DAY MONTH YEAR?`, matching the CLDR 47
`ca-gregorian` chart for `bg` at every level — full `EEEE, d MMMM y 'г'.`,
long `d MMMM y 'г'.`, medium and short `d.MM.y 'г'.`/`d.MM.yy 'г'.`. `lang.json`
adds an "of"-linked order (`28 на май`, "the 28th of May") and a
during-led order (`през май 2030`) alongside the plain one. The linking
`на` binds a bare day number, not an ordinal-dotted one: `28-и на май`
strands `28-и на` in the remainder and returns the whole of May.

**Weekdays and months** ship bare, in the nominative, with no recorded
source in the vocabulary comments — the same gap Greek's page records for
the same two groups.

**Day parts** are transcribed from the Unicode CLDR 47 day-period rules for
`bg`, each ship as the deictic adverb a native phrase actually uses rather
than the dictionary citation form: `сутрин`/`сутринта` (morning, Wiktionary
`сутрин`), `следобед` (afternoon, Wiktionary `следобед`),
`вечер`/`вечерта` (evening, Wiktionary `вечер`), `нощем` (night, Wiktionary
`нощем`). The same nouns double as clock meridiem cues on an explicit hour —
`сутринта` for AM, `вечерта` and `следобед` for PM — confirmed by the
project's own test corpus (`test_nl_r168_clock_hour_word.py`), which checks
`в 9 часа следобед` against independent arithmetic and gets 21:00.

**Relative offsets** are `преди` (ago) and `след` (in/after), with `през`
governing a calendar period ("during/in") — cited at its Wiktionary entry
for the senses "through, via" and "during, in the course of" — kept distinct
from `в`, the same locative preposition `marker_at.voc`/`marker_of.voc`
already attest for "at"/"of" and which doubles as `през`'s synonym in this
sense (`в 2030` = "in 2030").

**Determiners.** `последен` ("last" as an ordinal-last determiner, "the last
Monday of May") ships in its full agreement-plus-article paradigm —
последният/последния/последната/последното/последните — cited to the
Institute for Bulgarian Language (БАН), *Официален правописен речник на
българския език*, членуване. `миналия(т)`/`миналата`/`миналото`/`миналите`
("last/previous") and `следващ(ият)`/`следваща(та)`/`следващо(то)`/
`следващи(те)` ("next") ship the same way, from the same source, and both
match the CLDR 47 `bg` `dateFields.json` relative-type values directly:
relative-type-1 (year) is `следващата година`, relative-type--1 is `миналата
година`. `предходен`/`предходна`/`предходно`/`предходни`, with the same
article forms, ships as the calendar-register synonym CLDR uses for the
week field — `dateFields.json` gives `предходната седмица` for
relative-type--1 — cited to the Institute's own *Речник на българския език*
entry for `предходен`, sense 2, whose own citations carry предходната,
предходния, предходното and предходните.

**"This"** (`този`/`тази`/`това`/`тези`, with the colloquial
`тоя`/`тая`/`туй`/`тия` variants) is cited to the Institute's *Официален
правописен речник*, показателни местоимения — Bulgarian's demonstrative is
itself definite and takes no additional article.

**Landmarks** are `полунощ` (midnight) and `обед`/`пладне` (noon, two live
synonyms).

**Quarters, ISO weeks, decades and centuries** resolve: `тримесечие`/
`квартал` (quarter, two registers — the native compound and the loanword),
`седмица` (ISO week), `десетилетие` (decade), `век` (century). No recorded
source ties `тримесечие`/`квартал` together as synonyms rather than as a
register split with a separate boundary; see Weaker provenance.

**Named days** span five positions around the anchor: `завчера`/`онзи ден`
(the day before yesterday, two live surfaces), `вчера` (yesterday), `утре`
(tomorrow), `вдругиден` (the day after tomorrow).

**The clock's hour noun** inflects for count the way a Bulgarian numeral
noun ordinarily does — bare `час` after "one" (`в 1 час`), the count form
`часа` after any other cardinal (`в 9 часа`) — confirmed directly by the
project's test corpus (`test_nl_r168_clock_hour_word.py`), which asserts
both forms are consumed into the clock construction rather than stranded in
the remainder.

**The clock's additive half hour.** Bulgarian counts the half hour forward
off the hour that has already passed rather than toward the one coming:
`осем и половина` is 8:30, not 7:30 — the opposite direction from the
Slovenian, Croatian and Czech siblings, which all name the hour ahead. Two
independent guides gloss the construction with worked numeric examples,
Wikibooks' *Bulgarian/Time* giving «Единайсет и половина» for 11:30 and
Preply's telling-the-time guide giving «Пет и половина» for 5:30, both under
the heading "half past". Both examples parse, the Wikibooks one because the
locale also reads Bulgarian's contracted teens and tens: «единайсет» is the
everyday spelling of eleven, and the long «единадесет» its formal twin. The
contracted series from eleven to nineteen, together with twenty, thirty and
sixty, is folded from Wiktionary lemmas; the further clippings that drop the
final consonant are not, having no lemma of their own, and forty is held out
because the number model beneath reads a compound built on it as its tail
alone. The locale reads it through `clock_fraction_30.voc`
(`половина`) and `clock_dir_past.voc` (`и`), wired into two `clock_time`
orders — `at HOUR CLOCKDIR FRACTION article? MERIDIEM? ZONE?` and the same
shape without the leading `at`. The joiner needs care because `и` is also
the conjunction Bulgarian's spelled compound numerals are built on
(`двадесет и едно`), so the cardinal fold would otherwise swallow it; a
dedicated fold pulls `и` back out of the bare cardinal set and reinstates it
as the clock's direction word.

**Numerals** are read through the shared Slavic cardinal-fold hook
(`chronologia.extract.numfold_slavic:fold_bg`) rather than a per-locale
vocabulary file — no locale ships numeral `.voc` files — and a spelled
number is recognised by asking `ovos_number_parser`'s Bulgarian back-end
what a token run is worth. The
fold's closed extra-word set for `bg` is `{два, две, три, половин}` — the
oblique/quantifier forms the parser's own nominative pronunciation would
otherwise miss.

## Weaker provenance

**Weekday and month names carry no recorded source**, and neither do the
seasons.

**`тримесечие` and `квартал`** ship as unqualified synonyms for "quarter"
with no citation distinguishing register or checking that both are
current — one is the native compound, the other a loanword from
international business usage, and nothing on file confirms they are
interchangeable in ordinary date phrases rather than one being the
calendar-quarter word and the other a fiscal-quarter word.

**`половин`/`половина`** ship for `half_period` ("first/second half of the
year") cited to the Institute for Bulgarian Language's online dictionary,
sense "one of the two equal parts of a whole". The two surfaces do different
jobs: `половина` is the clock's fraction word, while `половин` is folded as
a cardinal 0.5 by the numfold hook's extra-word set purely so `half_period`'s
quantifier slot can read it back, and it reaches no clock construction —
the same split Persian's page records, where an attested spelled fractional
clock reaches only the period construction.

## What refuses

**Minutes to or past the hour by count** (`девет без пет`, "five to nine")
does not resolve — the phrase is refused outright rather than partly read.
No minute-count clock construction is sourced for Bulgarian and none ships;
the half hour is the only fractional clock surface the locale carries.

## Open questions for a native speaker

1. The half-hour clock rests on two informal learner guides rather than a
   reference grammar. Does a corpus-backed dictionary or grammar confirm
   `... и половина` as ordinary written usage, and does `без` ("девет без
   пет") deserve the same treatment for minute counts?
2. What is the actual source for the weekday and month names? Both look
   uncontroversial, but nothing on file confirms the exact citation form
   used (e.g. whether `май` alone or a longer form is the dictionary
   headword).
3. Are `тримесечие` and `квартал` genuinely interchangeable for "quarter" in
   date phrases, or does one carry a fiscal connotation the other lacks?
4. Is `завчера` or `онзи ден` the more current everyday form for "the day
   before yesterday", or do they belong to different registers?
