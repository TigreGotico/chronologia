# Maltese (`mt`)

Maltese is a Semitic language written in the Latin alphabet with a heavy
Romance vocabulary, and every one of those three facts shows up in this locale.
The definite article assimilates to nine sun letters, so `il-` becomes `is-`,
`it-`, `iċ-` and six more, and each allomorph is listed rather than derived.
The weekdays are numbered from Sunday on the Semitic pattern. The months are
Sicilian and Italian borrowings that take no article at all.

The direction of an offset is marked at the **tail**, not the head. `ilu`
closes a backward offset — `jumejn ilu`, two days ago — and `oħra` closes a
forward one. That single fact produces the locale's most consequential refusal.

## What ships

**Weekdays and months** come from CLDR 47,
`cldr-dates-full/main/mt/ca-gregorian.json`. Weekdays ship only in their
articled form, and deliberately: bare `tnejn` is the cardinal two, and bare
`ġimgħa` is the noun "week", which this locale ships as its week unit. Only
`it-tnejn` and `il-ġimgħa` are weekdays.

**The date line** is `15 ta' Awwissu` — day, the genitive linker `ta'`, month —
which is CLDR's own long format for the language. The tokenizer drops the
apostrophe.

**The dual.** Maltese has a dual number, and the number fold rewrites it before
matching: `jumejn` becomes two plus `jiem`, `sentejn` two plus `snin`. The dual
forms therefore do not appear in the unit files; they are handled upstream.

**The `-il` linker.** From eleven upward a Maltese numeral takes `-il` and puts
the counted noun back in the singular: `ħdax-il jum`. The tokenizer shears the
hyphen, so the linker arrives as its own token and the counted orders accept it
as an optional connector.

**The clock** switches direction at the half hour. Before it, minutes are
counted forward off the hour already named with `u` ("and"): `is-sitta u kwart`
is 06:15, `is-sitta u nofs` is 06:30. After it, Maltese names the **coming**
hour and takes the remaining minutes off it with `nieqes` ("less"):
`it-tmienja nieqes kwart` is 07:45, `l-għaxra nieqes ħamsa` is 09:55. The
sources are Preply's Maltese time guide and languagephrases.com's, plus
Wiktionary for `nieqes`, `kwart` and `nofs` individually.

`fi` and its article contractions — `fil-`, `fis-`, `fit-` and the rest — are
the ordinary way to state a time: `fis-sebgħa` is "at seven".

**Relative offsets.** The past is `ilu`, postposed and invariant. The future is
a preposed frame plus a trailing `oħra`: CLDR spells the frame `fi żmien`
("within the time") for year, day and hour, `sa` ("up to") for week and minute,
and month takes either. The trailing "another" agrees in gender — masculine
`ieħor` with `xahar`, feminine `oħra` elsewhere.

**Last and next** are suppletive trailing phrases rather than particles, and
they are shipped as the phrases they are: `l-oħra` for last year, `li għadda`
for a masculine month or a weekday, `li għaddiet` for the feminine week;
`id-dieħel`, `d-dieħla`, `li ġej` and `ta' wara` for the coming period.

**`din il-ġimgħa`.** The feminine demonstrative and the article run together as
one proclitic before a noun taking `il-`, and that run is what distinguishes
`din il-ġimgħa` (this week) from the weekday `Il-Ġimgħa` (Friday) — the same
noun under the same article. Gender does the work: `ġimgħa` is feminine and
takes `din`, while the masculine weekdays keep their own frame (`dan il-Ħadd`).
The week reading is what CLDR states for the week field's relative-type-0, and
it is the only reading found in running text, in Maltese Wikipedia articles that
spell `matul din il-ġimgħa` and `Din il-ġimgħa offriet kuntrast interessanti`,
all of them a span of days.

**Markers** are Wiktionary entries: `wara` (after), `qabel` (before — and
never "ago", which is `ilu`), `bejn` (between, in `bejn X u Y`), `minn` (from),
`sa` (until), `mindu` (since), `kull` (every).

## Weaker provenance

**The clock idioms** rest on two language-learning guides agreeing with each
other, plus Wiktionary for the individual words. No grammar was consulted for
the direction switch at the half hour.

**The article allomorph list** is transcribed from the English Wikipedia
article on Maltese grammar and a beginners' course chapter, not from a
reference grammar.

## What refuses

Each refusal is pinned by a test.

**Day-part bands.** `filgħodu`, `filgħaxija`, `bil-lejl` and `wara nofsinhar`
name no span. CLDR ships no day-period rule set for Maltese at all — only the
borrowed AM and PM labels — so there are no boundaries to transcribe and none
were invented from a dictionary gloss. `filgħodu` and `filgħaxija` do ship, but
as clock markers that fix a spoken hour in one half of the day:
`fis-sebgħa filgħodu` is 07:00.

**The day before yesterday.** CLDR carries no relative-type--2 field for
Maltese and no other source names a word for it, so no surface ships. The day
*after* tomorrow is sourced and does ship — `pitgħada`, with its attested
variant `bitgħada` — which is what makes the asymmetry deliberate rather than
an oversight.

**Decade and millennium.** Neither `deċennju` nor `millennju` has a dictionary
entry to cite, so neither unit ships. The century does: `seklu ilu` reads.

**A future offset without its trailing marker.** `fi żmien sena` returns
nothing, while `fi żmien sena oħra` reads as a year ahead. Both directions are
marked at the tail, and the only way to accept a bare frame would be to accept
a *preposed* direction marker — which would also accept the preposed `ilu`.
That preposed `ilu` is a different lexeme: the person-inflected durative adverb
in `Ili jumejn ma norqod` ("I haven't slept in two days"), which needs agreement
with a subject this engine cannot read. Reading it as "ago" would invert the
direction of the sentence. So the offset orders accept `ilu` only in trailing
position, and the CLDR count-one and count-two future patterns that omit `oħra`
are refused on that trade.

**Sibling and source-language phrasings.** Arabic, Hebrew, Italian, Spanish and
French relative-time phrasings are pinned as unreadable, so a Maltese locale
cannot quietly answer text that is not Maltese.

**A month name inside a word.** `marzupan` is not March.

## Open questions for a native speaker

1. Is there a word for the day before yesterday?
2. Are `deċennju` and `millennju` in ordinary use, and how do they inflect?
3. Is a bare `fi żmien sena` idiomatic for "in a year", and if so what
   distinguishes it in writing from the durative `ilu` frame?
4. Does the clock's switch to `nieqes` happen exactly at the half hour, or
   earlier or later in practice?
