# Icelandic (`is`)

Icelandic names the **coming** hour on the half. `hálf tvö` is 01:30, not
02:30. Everything else about the clock follows from that: the quarter word
`kortér` takes its direction from the preposition beside it, `yfir` counting up
from the hour named and `í` counting down toward it, so `kortér yfir tvö` is
02:15 and `kortér í þrjú` is 02:45.

The second thing shaping this locale is that Icelandic prepositions govern
case, and the case is what carries the meaning. `fyrir` with the dative is
"ago"; the same word with the accusative means "before <event>", which is a
different construction the locale does not read. Because the construction
imposes the case and the count imposes the number, every indefinite form of a
unit noun is a surface of that unit, and the vocabulary files list them all.

## What ships

**Months** come from Unicode CLDR 47,
`cldr-dates-full/main/is/ca-gregorian.json`. Icelandic month names do not
decline, so the wide name is the only form the date construction reads,
alongside the calendar's own abbreviation.

**Weekdays** ship in the full declension from Wiktionary. The date form is the
accusative, bare or with the suffixed article — `á mánudaginn` — which is what
the bare temporal accusative uses.

**Relative offsets** are `fyrir` plus the dative for the past
(`fyrir tveimur árum`) and `eftir` plus the accusative for the future
(`eftir tíu mínútur`), both with Wiktionary's own worked examples. `síðan` may
optionally close a backward offset — `fyrir fimm mínútum síðan` — although the
dative already carries the meaning without it.

**The clock** reads `klukkan` (literally "the clock") or its abbreviation `kl.`
as the "at" marker. Between a minute count and the direction word, the optional
`mínútur` is accepted: `fimmtán mínútur yfir eitt` is 01:15. The half-hour
direction comes from Wiktionary's appendix on telling time in Icelandic, at the
1:30 row; `kortér` and both directional prepositions come from the `kortér`
entry itself.

**Day parts** take their band boundaries from the CLDR 47 day-period rule set
for `is`, transcribed in `chronologia/dayparts.py`, and their surfaces from the
CLDR period names with declensions from Wiktionary. The afternoon is a case
worth noting: CLDR's wide name `eftir hádegi` is two words, so the single-token
surface shipped is the abbreviated `síðdegis`.

**Named days** are `í dag`, `í gær`, `á morgun` and `í fyrradag`, each a
Wiktionary entry.

**The determiners** `þessi` (this), `næstur` (next) and `síðastliðinn` (last)
ship in the declensions Wiktionary gives, the weak forms being the ones a
temporal phrase uses: `næsta fimmtudag`, `í næstu viku`.

## What refuses

Each refusal below is pinned by a test.

**The day after tomorrow.** The one candidate a search turned up, `hinn
daginn`, ordinarily means "the other day", and no compositional form was
attested either. `yfirmorgun` returns nothing and the other candidates leave
their tokens unread, so no phrase in this locale names a day two ahead.

**"Since".** `frá og með` was never confirmed by a fetched source, so no
"since" vocabulary ships and an anchored open range such as
`frá og með mánudegi` or `síðan á mánudag` is refused.

**"For <duration>".** `í þrjá daga`, `í tvær vikur`, `í fimm mínútur` — the
duration marker has no citation, so a duration phrase must not be read as one.

**"Every".** `á hverjum degi`, `hvern dag`, `á hverjum mánudegi` all fail to
resolve. No "every" quantifier was independently fetched.

**From-to and between ranges.** `frá júní til ágúst` returns June alone with
`frá til ágúst` left in the remainder, and `milli júní og september` does not
close a span either. The governed cases of `frá` and `til` were never verified
with a worked example, so no range vocabulary ships.

**Clause conjunctions as offset markers.** `áður en` and `eftir að` introduce a
clause, not a quantity. Reading either as the prepositional `fyrir` or `eftir`
would invent an offset that the sentence does not state.

**`annar` as a spelled second.** `annar` is the ordinary Icelandic word for
"another" or "the other", so the ordinal fold refuses to claim every occurrence
of it as the digit two. `annar júní` returns the whole of June with `annar`
left in the remainder; the dotted `2. júní` is how the second of the month is
written and read.

**Calendar quarters and ISO week references.** `fyrsti ársfjórðungur` and
`3. vika` both refuse.

**Era vocabulary.** `44 f.Kr.` and `árið 1990 e.Kr.` leave the era marker
visible or refuse outright. No era vocabulary ships.

**Early, middle and late.** `í byrjun júní` and `í lok júní` return the month
with the part word left in the remainder.

**A spelled quantity with no direction marker.**
`þrjú hundruð og fimmtíu dagar` refuses: a quantity without a marker is still
only a quantity.

## Open questions for a native speaker

1. Is there a current word or phrase for the day after tomorrow?
2. Is `frá og með` the ordinary way to say "since", and what case does it take?
3. What is the "for <duration>" construction, and what case does it govern?
4. What are the "every" quantifier's forms in a temporal phrase?
5. Which cases do `frá` and `til` govern in a month-to-month range?
6. Are there attested era abbreviations?
