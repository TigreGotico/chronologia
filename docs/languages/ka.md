# Georgian (`ka`)

Georgian counts in base twenty, and reading it any other way is confidently
wrong on every value from twenty-one to ninety-nine. Between the score
multiples — `ოცი` 20, `ორმოცი` 40, `სამოცი` 60, `ოთხმოცი` 80 — a number is the
score, plus `და` ("and"), plus a remainder drawn from the one-to-nineteen
series, and the whole thing is written as **one word**: `ოცდაათი` is
"twenty-and-ten", thirty. `chronologia/extract/numfold_georgian.py` reads that
structure; a tens-and-ones fold of the Germanic kind would not.

The adpositions are postpositions and they govern the genitive. `წინ` ("ago")
and `შემდეგ` ("after") both trail the phrase they govern —
`სამი თვის წინ` is three months ago. Modifiers, though, stand before their
noun: `მომავალი წელი` is next year. Georgian is postpositional in its adposition
system, not in its modifiers.

The clock names the hour being **approached**, with that hour in the genitive
and no direction word at all: `ორის ნახევარი` is half toward two, 01:30.

## What ships

**Months and weekdays** come from Unicode CLDR 47,
`cldr-dates-full/main/ka/ca-gregorian.json`, where the stand-alone and format
forms are identical.

**Named days reach three out on each side of today** — one further than most
languages name. Backward: `გუშინ`, `გუშინწინ`, and `გუშინწინისწინ`, which
Wiktionary marks colloquial and rare. Forward: `ხვალ`, `ზეგ`, `მაზეგ`. Each is
its own Wiktionary entry, and each entry carries the day-sequence
coordinate-term list that confirms the series.

**Day parts** take their bands from the CLDR 47 day-period rule set for `ka`,
transcribed in `chronologia/dayparts.py`, and ship in two forms apiece: the
stand-alone wide name and the case-marked adverbial format form, with the
declension from Wiktionary. Midnight and noon likewise ship the nominative and
the dative, the dative being what CLDR lists for the day period.

**The millennium** ships. Its Wiktionary declension table is rendered, so the
genitive the postpositions govern is attested rather than inferred, and
`ორი ათასწლეულის წინ` reads.

## What refuses

Each refusal is pinned by a test.

**Every week duration.** `კვირა` names both Sunday and the week, under one
dictionary entry whose seven-case declension is identical for the two senses.
There is no morphological cue to tell them apart, and no source consulted
establishes either as dominant in a counted phrase. The ambiguity is resolved by
construction: `კვირა` binds the weekday slot alone, and every duration reading
refuses. `ორი კვირის წინ` and `სამი კვირის შემდეგ` return nothing.

**A count before `კვირა`.** `ორი კვირა`, `10 კვირა` and the rest refuse too.
A count before it can only be a span of weeks, and this locale has no week unit
to express one, so the weekday reading is vetoed as well. Answering "Sunday"
here and stranding the numeral would hand a caller who asked for a duration one
specific day, which is a wrong span rather than an incomplete one. Declining the
false weekday reading is not the same as asserting the unsourced week reading,
which stays unavailable.

The veto is scoped to that one surface. A bare `კვირა`, and `მომავალი კვირა` or
`გასული კვირა` after a relative marker, all resolve as Sunday, because a
weekday-slot position admits only that sense. And an unambiguous weekday keeps
the ordinary behaviour: `ორი ორშაბათი` resolves the Monday with the count left
in the remainder, and `ორი ორშაბათი წინ` counts two Mondays back.

**The century.** `საუკუნე` is the word, but its Wiktionary entry carries no
declension table at all — a genuine gap, confirmed through both the rendered
page and the parse API — so the genitive the postpositions govern would have to
be inferred from other `-ე` stems. It is omitted instead. The millennium, whose
table *is* rendered, ships; the asymmetry is exactly that difference.

**Recurrence.** "Every" is attested only as the fused compound adverb
`ყოველდღე` ("daily"), never as a quantifier heading a free noun phrase, so it is
not generalised to other units, and the compound itself names no single span.

**"Since".** There is no dedicated postposition: it is either the periphrastic
clause-level `მას შემდეგ რაც` or an extension of the plain "from" suffix `-დან`,
and neither was confirmed with a temporal worked example that distinguishes it
from "after" or "from".

**Ranges.** Georgian has two unrelated between-forms — the paired suffixes
`-დან … -მდე` for a time range, and the separate word `შორის` for two entities
— and the sources consulted disagree on which case `შორის` governs. Neither
ships while that conflict is open.

**A bare "N o'clock".** No source consulted gives a plain "it is N o'clock"
surface for Georgian — only the four minute-band idioms, of which just the half
is modelled — so a bare count of hours stays a duration and names no time of
day.

**The other minute bands.** The first half hour marks its relation by the
genitive alone, with no direction word; the second half hour switches to a whole
subordinate clause, `სამს რომ აკლია ოცდახუთი წუთი`, "three that lacks
twenty-five minutes". Neither shape fits the slot model, so both refuse rather
than being approximated by the half construction.

**Seasons.** No season vocabulary is attested, so the season names stay unread
rather than being taken from a bilingual word list.

**Meridiem markers.** CLDR gives Georgian no native am/pm surfaces — the fields
hold the literal Latin `AM` and `PM` — so no meridiem vocabulary ships.

## Open questions for a native speaker

1. In a counted phrase, does `კვირა` mean weeks or Sundays — and is there a cue
   that settles it?
2. What is the declension of `საუკუნე`, and specifically its genitive?
3. Is there a quantifier "every" that heads a free noun phrase, or only the
   fused `ყოველდღე` series?
4. What is the ordinary "since Monday" construction?
5. Which case does `შორის` govern?
6. Is there a plain "it is N o'clock" surface?
7. Are the season names in ordinary use with definable boundaries?
