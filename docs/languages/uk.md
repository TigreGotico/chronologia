# Ukrainian (`uk`)

<!-- agent-hint
covers: where each construction of the Ukrainian locale comes from, what it refuses and which questions a native speaker would settle
source: `chronologia/locale/uk/lang.json`, `chronologia/locale/uk/*.voc`, `chronologia/extract/numlayer.py:NUMTAG_LANGS`
generated: no
verify: python -m doctest docs/languages/uk.md && python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set()\nfor m in re.finditer(r\"`([^`]+)`[^.`\\n]{0,25}?\\b(?:is|are|reads|gives|returns?|resolves? to|comes? back as|=)\\s+(\\d\\d):(\\d\\d)\",pr):\n    ph=m[1]\n    if ph[0]==\"-\": continue\n    r=extract_timespan(ph,c,A)\n    if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2],m[3])\npm=re.sub(r\"`[^`]*`\",lambda m:m[0].replace(\". \",\".\\x01\"),pr)\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(r\"((?:`[^`]+`(?:,| and| or|, and)? ?)+)\\s*(?:both |each |all )?(?:returns?|gives?) (?:nothing|`None`)\",s): cl|=set(x.replace(\"\\x01\",\" \") for x in re.findall(r\"`([^`]+)`\",m[1]))\nex={ast.literal_eval(x) for x in re.findall(r\">>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\",t)}\nif cl!=ex: bad=1;print(\"refusals differ\",cl^ex)\nsys.exit(bad)\n")' docs/languages/uk.md
see: `docs/languages/index.md`, `docs/extraction.md`
-->

This page records where each construction of the Ukrainian (`uk`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

Ukrainian temporal phrases lean on the same case system Russian does, and the
locale ships the same kind of answer: full paradigms rather than citation
forms, because the ordinary spoken register never uses the nominative for a
relative time. `цього тижня` ("this week") is genitive, `минулого місяця`
("last month") is genitive, `у наступному році` ("next year") is locative —
none of those is the dictionary headword — so `this`, `last` and `next` all
ship as complete adjectival or pronominal paradigms rather than single words,
each citing the *Український правопис* (2019) declension tables for the
paradigm type it follows.

The clock is a smaller story here than in Russian. Ukrainian names the half
hour toward the coming hour, and the locale reads it: `пів на другу` is 13:30
and `чверть на третю` is 14:15.

## What ships

**Weekdays and months** ship wide, and the months also ship a
prepositional-case form used after `в`/`у` — `у січні` — reflecting that
Ukrainian months decline. Neither carries a recorded source in the
vocabulary comments.

**The date line** is little-endian, and the dotted civil form (`15.06.2020`)
reads, matching the CLDR short pattern for `uk` (`dd.MM.yy`) and the long/full
patterns (`d MMMM y 'р'.`), both day-first.

**The unit nouns** ship full first-declension paradigms for `день`, `тиждень`,
`місяць`, `рік`, `година` and `хвилина`, each citing *Український правопис*
(2019) for its declension. `рік` is separately noted as suppletive in the
locative singular (`у році`) and regular elsewhere.

**The determiners** `минулий`/`попередній` ("last/previous"), `наступний`
("next"), `останній` ("last" as an ordinal-last determiner, behind
`останній понеділок травня`) and `цей` ("this") each ship their full paradigm,
citing the 2019 orthography's adjective and pronoun declension tables. The
vocabulary comment for `минулий` explains why the full paradigm is needed
rather than the bare nominative: the ordinary phrase is the adverbial genitive
`минулого тижня` or the locative `у минулому році`, and the nominative
`минулий тиждень` is the marked register. The comment for `цей` records a
deliberate omission: the dative `цьому` is listed, but the homograph `тому` is
not, because `тому` is also the ago-marker (`два дні тому`) and folding it
into the demonstrative paradigm would read a past offset as a present one.

**Relative offsets** are `через` for the future and `тому` for the past, in
either order relative to the count.

**Eras.** `н. е.` / `н.е.` (from `нашої ери`, "of our era") and `до н. е.` /
`до н.е.` (`до нашої ери`, "before our era") are both cited to the
*Український правопис*, §62, as general graphic abbreviations, spaced and
unspaced forms both listed since both are current typed variants.

**Ranges** use `між … і/та …` for a coordinated pair, and the vocabulary
records a close reading of `по` as a range terminator: with the accusative,
`по` makes the named day inclusive, cited to the *Словник української мови*
(11-volume SUM), volume 6, s.v. `по`, sense 13 — "used with a preposition з,
occasionally від, and a noun or ordinal numeral denoting a day, date or year
… to indicate the end of an action or state" — with the dictionary's own
examples `З березня по вересень 1917 року` and the 1966 party congress that
met "з 29 березня по 8 квітня", inclusive of 8 April. `з 5 по 12 червня`
therefore reads through 12 June inclusive, mirroring the same argument the
`ru` locale makes for Russian `по`.

**Quarters, ISO weeks, decades and seasons.** `квартал`, `тиждень`,
`десятиліття` and the seasons (`осінь`, `весна`, `літо`, `зима`, each with
its adverbial locative form — `восени`, `навесні`, `влітку`, `взимку`) all
resolve. `century` ships two synonyms, `століття` and `вік`.

**Fuzzy period parts** are `початок`/`початку` (early), `середина`/`середині`
(mid), `кінець`/`кінця` (late).

**Day parts** take their boundaries from the Unicode CLDR 47 day-period chart
for `uk`: `ніч` `[00:00, 04:00)`, `ранок` `[04:00, 12:00)`, `день`
`[12:00, 18:00)`, `вечір` `[18:00, 24:00)`. As in Russian, the surfaces
shipped are the deictic adverbs rather than the nouns — `вранці`/`зранку`
(morning), `вдень` (afternoon/daytime), `ввечері`/`увечері` (evening),
`вночі` (night) — because that is the form `сьогодні вранці`,
`вчора вночі` actually use. Each cites its Ukrainian Wiktionary adverb entry.

**"Yesterday"** ships both `вчора` and `учора`. The vocabulary comment notes
Wiktionary heads the entry at `учора` and lists `вчора` as an alternative
spelling — the ordinary у-/в- alternation — and that `учора` is also what
CLDR `dateFields` gives for `uk`, day relative-type `-1`. That match was
confirmed directly: CLDR's `day` field for `uk` gives `alaltäieri`-style
values at every offset — `позавчора` (-2), `учора` (-1), `сьогодні` (0),
`завтра` (1), `післязавтра` (2) — matching the shipped `named_day` vocabulary
at every offset, not only `-1`.

## Weaker provenance

The weekday and month names carry no recorded source, and neither do the
seasons' base forms (only their adverbial locatives are cross-checked against
Wiktionary).

Ukrainian has an attested spoken half-hour idiom.
`пів` ("half") is documented on Wiktionary as meaning "half to/till" — thirty
minutes before the *next* whole hour, explicitly contrasted there with
English "half past" — with the worked example "half past one" glossed as
literally "at half onto two". An independent explanation (goroh.pp.ua, a
Ukrainian dictionary and usage site, corroborated by a Ukrainian-language
lesson site) gives the same construction with a numeric anchor: `пів на другу`
names 13:30 (or 1:30), half of the way toward the *second* hour — the same
toward-the-coming-hour direction Russian `половина девятого` uses for 8:30,
not the "count past the current hour" direction. The locale reads `пів на другу`
as 13:30 and `чверть на третю` as 14:15.

## What refuses

**A bare `тому` collision.** Because `тому` is deliberately excluded from the
`цей` demonstrative paradigm (see What ships), a construction that needed the
dative of "this" spelled `тому` cannot use it — the marker is reserved for
the ago-offset.

## Open questions for a native speaker

1. Does `пів на <ORD>` generalise the way Russian's subtractive `без N` does,
   or is the coming-hour construction limited to the fixed half-hour point?
2. Is `по`'s inclusive reading, argued at length in the vocabulary for
   ranges, equally solid for every date type the `to`/`until` markers cover,
   or only for the day-of-month case the SUM examples give?
3. Are `вранці` and `зранку` fully interchangeable as the morning-band
   surface, or does one carry a register or regional preference the other
   does not?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("uk")
    True
    >>> span, rest = extract_timespan('пів на другу', "uk", datetime(2017, 6, 27, 12, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T13:30:00', '')
    >>> span, rest = extract_timespan('чверть на третю', "uk", datetime(2017, 6, 27, 12, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T14:15:00', '')
    >>> span, rest = extract_timespan('цього тижня', "uk", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-26T00:00:00', '')
    >>> span, rest = extract_timespan('минулого місяця', "uk", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-05-01T00:00:00', '')

---
[← Turkish](tr.md) · [Home](../index.md) · [Vietnamese →](vi.md)
