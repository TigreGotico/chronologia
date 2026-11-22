# Italian (`it`)

<!-- agent-hint
covers: where each construction of the Italian locale comes from, what it refuses and which questions a native speaker would settle
source: `chronologia/locale/it/lang.json`, `chronologia/locale/it/*.voc`, `chronologia/extract/numlayer.py:NUMTAG_LANGS`
generated: no
verify: python -m doctest docs/languages/it.md && python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\">>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\",t)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/it.md
see: `docs/languages/index.md`, `docs/extraction.md`
-->

This page records where each construction of the Italian (`it`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

The decision worth knowing before anything else is what `notte` means. In this
locale it is the small hours of the day named — `[00:00, 06:00)` — so
`domani notte` is tomorrow between midnight and six, not tomorrow evening. The
vocabulary argues the point rather than asserting it: the `sera` already holds
the hours from six in the evening to midnight, so the `notte` has nowhere else
to be, and re-cutting it to the English wrapping night would contradict the
CLDR chart the band comes from.

The second is that Italian does not write the dotted date. `15.06.2020` returns
nothing, and it does not fall back to reading 2020 either — a numeral visibly
glued into a date-shaped run does not get to be read as a lone year just
because the run was rejected. Italian writes the numeric date with slashes, and
`15/06/2020` reads.

## What ships

**Weekdays and months** ship wide and abbreviated, with no recorded source.

**The date line** is little-endian with a bare cardinal day: `3 ottobre 1990`,
optionally with the article, optionally with `di` between day and month.
`ordinal_dot` is off, so a dot after a numeral is never an ordinal marker.

**Relative offsets** run both ways with `fra`/`tra` and `fa`, and `lang.json`
allows the marker on either side of the count, with optional indefinite
articles and quantifiers in both positions. The vague quantifiers are `alcuni`,
`alcune` and `qualche` for three, and `paio` and `coppia` for two.

**Units ship in singular and plural** with a separate `unit1_` file per unit,
so a count of one and a count of many take the right lexeme.

**The relative determiners** follow the noun, so the locale sets
`marker_position: post` — `lunedì scorso`, `la prossima settimana` — and
`rel_period` is overridden to accept a leading article.

**The clock** counts forward with `e` and back with `meno`: `le otto e un
quarto`, `le otto e mezza`, `le nove meno un quarto`. The fraction takes its
own article, which is why the grammar orders thread an optional `article` slot
between the direction word and the fraction. `mezzogiorno` and `mezzanotte`
are points, and `di sera` and `di mattina` supply the meridiem. The half word
`mezza`/`mezzo` doubles as the period noun `metà`, cited to Treccani's
*Vocabolario della lingua italiana*, so `la prima metà del 2020` reads as the
first half-year.

**Day parts** take their boundaries from the Unicode CLDR 47 day-period chart
for `it`, transcribed in `chronologia/dayparts.py`: `notte` `[00:00, 06:00)`,
`mattina` `[06:00, 12:00)`, `pomeriggio` `[12:00, 18:00)`, `sera`
`[18:00, 24:00)`. The surfaces are cited to Treccani, which glosses
`pomeriggio` as the part of the day between midday and sunset. Unlike
Portuguese and Spanish, Italian reads the bare day-part word: `mattina` and
`notte` resolve on their own. None of the four Italian day-part nouns doubles
as a different temporal word, which is what forces the bare order off in those
locales.

**Fuzzy month parts** are `inizio`, `metà` and `fine`, cutting the month into
thirds.

**Quarters, ISO weeks, decades and eras.** `il primo trimestre 2020`,
`settimana 12`, `gli anni 80` and `44 a.C.` resolve, along with an AD marker, a
before-present marker, and the Julian, Unix, Anno Mundi and Holocene era
prefixes.

**The Roman calendar** is unusually complete here. Both the Latin classical
forms and the Italian vernacular ones — `calende`, `none`, `idi` — ship, cited
to the Italian Wikipedia article *Calendario romano*, and the grammar carries
the full `ante diem` and `pridie` counting orders, not just the bare anchor
day. `le idi di marzo` resolves.

**Non-Gregorian calendars.** Italian carries month names for the Hebrew and
Islamic civil calendars and for the French Republican calendar, plus the
Japanese nengō era names. `15 ramadan 1440` resolves to its Gregorian day.

## Weaker provenance

The Roman anchors and the Hebrew, Islamic and French Republican month
vocabularies rest on weaker or unrecorded sources than the Treccani citations
behind the day parts. The Roman anchors cite a Wikipedia article; the
non-Gregorian month names record no source at all, and ship one spelling per
month with no transliteration convention named.

The weekday and month names carry no recorded source.

## What refuses

**The dotted date.** `15.06.2020` returns nothing and does not yield a bare
year.

**A bare duration.** `quindici giorni` returns nothing. A fortnight unit
ships, but a quantity with no direction marker is still only a quantity.

## Open questions for a native speaker

1. Does `domani notte` really name tomorrow's small hours for an Italian
   speaker, or the night that begins tomorrow evening? The band table forces
   the first reading; ordinary usage may not agree.
2. Which transliteration should the Hebrew and Islamic months follow, and are
   the shipped spellings the ones Italian writing uses?
3. Should the French Republican months carry their Italian forms rather than
   the ASCII French ones?
4. Are `calende`, `none` and `idi` the forms Italian historical writing uses?
   The Latin forms ship alongside them, so a text that keeps the Latin also
   reads.

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("it")
    True
    >>> span, rest = extract_timespan('domani notte', "it", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-28T00:00:00', '')
    >>> span, rest = extract_timespan('3 ottobre 1990', "it", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('1990-10-03T00:00:00', '')
    >>> span, rest = extract_timespan('lunedì scorso', "it", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-26T00:00:00', '')
    >>> span, rest = extract_timespan('la prossima settimana', "it", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-07-03T00:00:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('15.06.2020', "it", anchor) is None
    True
    >>> extract_timespan('quindici giorni', "it", anchor) is None
    True

---
[← Irish](ga.md) · [Home](../index.md) · [Kabyle →](kab.md)
