# Irish (`ga`)

<!-- agent-hint
covers: where each construction of the Irish locale comes from, what it refuses and which questions a native speaker would settle
source: `chronologia/locale/ga/lang.json`, `chronologia/locale/ga/*.voc`, `chronologia/extract/numfold_irish.py`
generated: no
verify: python -m doctest docs/languages/ga.md && python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set()\nfor m in re.finditer(r\"`([^`]+)`[^.`\\n]{0,25}?\\b(?:is|are|reads|gives|=)\\s+(\\d\\d):(\\d\\d)\",pr):\n    ph=m[1]\n    if ph[0]==\"-\" or not re.search(r\"[^\\W\\d_]\",ph): continue\n    r=extract_timespan(ph,c,A)\n    if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2],m[3])\npm=re.sub(r\"`[^`]*`\",lambda m:m[0].replace(\". \",\".\\x01\"),pr)\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(r\"((?:`[^`]+`(?:,| and| or|, and)? ?)+)\\s*(?:both |each |all )?(?:returns?|gives?) (?:nothing|`None`)\",s): cl|=set(x.replace(\"\\x01\",\" \") for x in re.findall(r\"`([^`]+)`\",m[1]))\nex={ast.literal_eval(x) for x in re.findall(r\">>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\",t)}\nif cl!=ex: bad=1;print(\"refusals differ\",cl^ex)\nsys.exit(bad)\n")' docs/languages/ga.md
see: `docs/languages/index.md`, `docs/extraction.md`
-->

This page records where each construction of the Irish (`ga`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by its own `numfold_irish` module in `chronologia/extract/`.

Irish mutates a word's initial consonant, and unlike Welsh next door the rules
for *which* mutation a given trigger imposes are, in several places the temporal
constructions need, not stated by any source consulted. Where the sources
contradict each other or fall silent, this locale ships the unmutated reading
alone and refuses the mutated collocation rather than picking a side. Most of
the refusals below are that decision applied case by case.

The clock counts the English way and never the toward-the-hour way:
`leathuair tar éis a trí` is 03:30, an hour later than the reading some of
Irish's neighbours would give the same shape. Past the half hour it switches to
`chun` — `ceathrú chun a dó` is 01:45. Ulster substitutes `i ndiaidh` and
`go dtí` for the two directions, and both are accepted.

## What ships

**Weekdays and months** come from Unicode CLDR 47,
`cldr-dates-full/main/ga/ca-gregorian.json`. Each weekday ships in two shapes,
because they do different jobs: CLDR's citation form is already the adverbial
`Dé` compound meaning "on <day>", while the bare radical noun is what a
modified reference uses — `an Luan seo chugainn`, next Monday.

Months ship in four shapes: the bare name, the form after the noun `mí` in the
genitive (`mí Aibreáin`), the eclipsed form after the bare preposition `i`
(`i mBealtaine`), and the abbreviation. The declensions and the eclipsis come
from each headword's own Wiktionary tables.

**Relative offsets backward** are marked at the tail. `ó shin` is an adverb that
trails the quantity it counts back over: `cúig lá ó shin`, five days ago.

**Last and next** likewise trail their noun: `seo caite` and `seo chugainn`,
both glossed for nouns denoting a period of time.

**The clock's particle `a`** introduces an hour — `a trí a chlog` is three
o'clock — and the hour after it is the disjunctive cardinal, never the counting
form. The same particle also enumerates: `uimhir a 3` is number three and
`seomra a 5` is room five, neither of them a time. Nothing in the surface tells
the two uses apart, so every clock order that reads this particle requires
corroborating clock context — `a chlog`, a meridiem, or a fraction with its
direction. `uimhir a 3` accordingly resolves to nothing.

**Markers.** `idir` is "between", paired with `agus`, and in its plain spatial
and temporal sense it leaves both bounds unmutated. `ar feadh` is "for, over a
period of time", governing the genitive and mutating nothing itself. `ó` is
"from, since", and `i` / `in` is the locative that eclipses a following month
name.

The clock words come from Wiktionary entries for `tar éis`, `i ndiaidh`,
`chun`, `ceathrú`, `leathuair` and `a chlog`, corroborated by Omniglot's page
on time in Irish and by bitesize.irish's guide.

## What refuses

Each refusal is pinned by a test.

**The millennium.** `mílaois` is an attested noun, but no source gives its
genitive, its plural or any counted form, so no millennium unit ships.

**The decade.** Irish has no single-word "decade" attested. The compositional
`deich mbliana` is ten years, not a named decade, and reading it as one would
turn a duration into a calendar period.

**The century.** `céad` is at once "hundred", "century" and "first", and the
sources contradict each other on whether it mutates what follows. No century
unit ships, rather than one that conflates a hundred years with the first of
something.

**Lenited `chéad` as a hundred.** After the article, `chéad` is the ordinal
"first" and never the numeral, so folding it to 100 would invent a quantity
where the text states a rank.

**A counted teen split around its noun.** Irish puts the noun *inside* the
numeral — `ceithre bliana déag`, fourteen years — and no source gives that shape
for more than one noun. The fold refuses it rather than reading the leading
element alone and dropping the `déag`.

**The thirty-first.** The numerals table runs to the thirtieth. The thirty-first
is only described as a pattern, never spelled out in any source, so it is not
read.

**`ceathrú` as a spelled fourth.** It is at once "fourth" and the quarter of an
hour the clock speaks. Claiming every occurrence as the digit four would erase
the quarter from every clock phrase, so the ordinal reading is refused.

**Day parts.** CLDR has no day-period rule set for Irish at all — its authority
stops at the bare am/pm markers — so no time-of-day band ships, and `maidin`,
`tráthnóna` and `san oíche` are left unread.

**Seasons.** No season vocabulary was attested, so a season word never resolves
to a quarter of the year.

**Era vocabulary.** `44 RC` and `roimh Chríost` are refused or leave the marker
visible.

**A forward offset.** No "in <N> <units>" marker was attested, so
`i gceann trí lá` and `faoi cheann seachtaine` are refused rather than read
with the backward marker's sign — which would put the answer on the wrong side
of now.

**`ar feadh` alone.** It states how long something lasts, not when it happens.
On its own it anchors nothing and must not become an offset.

**Mutated `gach` collocations.** `gach` imposes h-prothesis on some nouns,
lenition on others and nothing on the rest, with no rule any source states. Only
the bare marker ships, so `gach Luan` resolves the Monday and leaves `gach` in
the remainder.

**Lenition after `ó`.** The same preposition lenites in one of its own cited
examples and leaves the radical in another. The contradiction is not resolved by
picking a side, so only the unmutated reading ships and `ó mhaidin` is not read.

**Lenited `idir`.** `idir … agus …` lenites both conjuncts only in its
"both … and …" sense, which is not a date range. The plain unmutated reading is
the one that ships.

**ISO week references and period parts.** `3ú seachtain` refuses;
`ag tús Meitheamh` returns the month with the part word left visible.

## Open questions for a native speaker

1. Does `mílaois` have an attested genitive, plural and counted form?
2. Is there a single-word decade, and how is a named decade such as "the
   seventies" expressed?
3. Does `céad` mutate what follows it in the century sense, and how is a
   century written so it cannot be read as a hundred?
4. How is the thirty-first of a month spelled out?
5. What is the ordinary "in <N> days" forward marker?
6. Which mutation does `gach` impose, and on what?
7. Does `ó` lenite in its temporal sense?
8. Does the t-prothesised `an tseachtain` need to ship alongside the radical
   `seachtain`? The radical form resolves; the prothesised one does not.

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("ga")
    False
    >>> span, rest = extract_timespan('leathuair tar éis a trí', "ga", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T03:30:00', '')
    >>> span, rest = extract_timespan('ceathrú chun a dó', "ga", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T01:45:00', '')
    >>> span, rest = extract_timespan('an Luan seo chugainn', "ga", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-07-03T00:00:00', '')
    >>> span, rest = extract_timespan('mí Aibreáin', "ga", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2018-04-01T00:00:00', '')

---
[← Indonesian](id.md) · [Home](../index.md) · [Italian →](it.md)
