# Welsh (`cy`)

<!-- agent-hint
covers: where each construction of the Welsh locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/cy/lang.json, chronologia/locale/cy/*.voc, chronologia/extract/numfold_welsh.py, test/nl_corpus_cy/
generated: no
verify: .venv/bin/python -m doctest docs/languages/cy.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/cy.md && .venv/bin/python -c 'exec("import re,sys\nfrom datetime import datetime\nimport chronologia as C\ndef mins(d):\n    return \"%g\" % (d.total_seconds() / 60)\ndef rem(r):\n    return \" and \\x60%s\\x60 left over\" % r if r else \"\"\ndef out(rd, tx, lg, an):\n    f = getattr(C, rd)\n    r = f(tx, lg, anchor=an) if rd == \"extract_duration\" else f(tx, lg, an)\n    if rd == \"extract_timespan\":\n        if r is None: return \"no reading\"\n        return \"%s to %s%s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), r.span.end.datetime().strftime(\"%Y-%m-%d %H:%M\"), rem(r.remainder))\n    if rd == \"extract_duration\":\n        if r is None: return \"no length\"\n        return \"a length of %s min%s\" % (mins(r.duration), rem(r.remainder))\n    if rd == \"extract_event\":\n        if r is None: return \"no event\"\n        return \"start %s, length %s, summary \\x60%s\\x60\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), \"none\" if r.duration is None else mins(r.duration) + \" min\", r.summary)\n    if r is None: return \"no rule\"\n    return \"the rule \\x60%s\\x60%s\" % (r.recurrence.to_string(), rem(r.remainder))\n\np=sys.argv[1]\nt=open(p).read()\nm=re.search(r\"\\n## Known limits\\n(.*?)(?=\\n---\\n|\\Z)\",t,re.S)\nbad=0\nn=0\nfor ln in (m[1].split(\"\\n\") if m else []):\n    g=re.search(r\"Example \\(reader \\x60(\\w+)\\x60, lang \\x60([\\w-]+)\\x60, anchor (\\d{4}-\\d\\d-\\d\\d \\d\\d:\\d\\d)\\): \\x60([^\\x60]+)\\x60 gives (.+?)\\. \\[#\\d+\\]\",ln)\n    if not g: continue\n    n+=1\n    o=out(g[1],g[4],g[2],datetime.strptime(g[3],\"%Y-%m-%d %H:%M\"))\n    if o!=g[5]:\n        bad=1\n        print(\"limit differs\",g[4],\"|\",g[5],\"|\",o)\nprint(\"known limits checked:\",n)\nsys.exit(bad)\n")' docs/languages/cy.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Welsh (`cy`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by its own `numfold_welsh` module in `chronologia/extract/`.

Welsh changes a word's **first letter** according to what precedes it, and that one fact shapes this whole locale. A vocabulary listing only dictionary forms would silently fail on ordinary sentences. Every mutated surface a temporal construction can produce is enumerated in the vocabulary files rather than derived.

The year is the richest case. Its count form has three surfaces (the radical `blynedd`, the soft-mutated `flynedd` after the feminine two, and the nasal-mutated `mlynedd` after five) and all three name the same unit. `dwy flynedd yn ôl` and `tair blynedd yn ôl` differ by one year, not by which word the year is.

The clock counts the English way. `chwarter wedi naw` is 09:15 and `hanner awr wedi tri` is 03:30. The half is counted from the hour just named, so no toward-the-hour convention applies. Past the half hour Welsh switches to `i`, which counts down and triggers soft mutation on the hour it names: `chwarter i bedwar` is 03:45.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('chwarter wedi naw', "cy", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T09:15:00', '')

## What ships

**Months and weekdays** come from Unicode CLDR 47, `cldr-dates-full/main/cy/ca-gregorian.json`, each with its abbreviations and, where the initial is mutable, its mutated surface. March is `mawrth`, `fawrth` and `maw`, the soft mutation attested in running text as `ar y 14eg o Fawrth`. The mutation table itself is the English Wikipedia article on Welsh mutation.

**The date** links the day to the month with `o`, which triggers soft mutation on the month name (`y 3ydd o Orffennaf`) which is why every mutable month ships its mutated form.

**Relative offsets** are marked at opposite ends. `ymhen` opens a forward offset: `ymhen tair blynedd`, `ymhen mis`, both attested in Welsh Wikipedia running text. `yn ôl` **closes** a backward one: `chwe chan mlynedd yn ôl`, `bedair blynedd yn ôl`, likewise from running text.

**The determiners** trail their noun, which is why this locale marks its determiner position as postposed. `nesaf` is next (`yr wythnos nesaf`), `diwethaf` last. The demonstrative agrees in gender: `hwn` after a masculine noun, `hon` after a feminine one, as in `yr wythnos hon`.

**`bob`** is the lexicalised soft-mutated form of `pob`. It is the form the "every X" construction actually uses: `bob dydd` is the dictionary's own worked example and `bob dydd Llun` is attested in Welsh Wikipedia running text. The radical `pob` ships too, for the citation form.

**The clock's own words.** `am` opens a time and triggers soft mutation: `am dri o'r gloch`. `o'r gloch`, literally "of the bell", closes a named hour. `munud` may stand between a minute count and the direction word. Its soft-mutated `funud` ships beside it. The sources are Wiktionary's `chwarter` and `hanner` entries, a Wikibooks Welsh lesson carrying a full five-minute table, and Welsh Wikipedia running text for the `i` forms (`am chwarter i dri yn y prynhawn`).

**The article** ships in the surfaces its environment conditions: `y` before a consonant, `yr` before a vowel.

## What refuses

A test pins each refusal.

**The day after tomorrow.** `trennydd` appears on a dictionary entry only as the cross-referenced antonym of `echdoe`, with no running-text occurrence found at all and a second spelling in circulation. The day two ahead is not named. `echdoe`, the day before yesterday, is attested and does ship.

**Single-word year deixis.** Welsh has dedicated adverbs for "this year" and "last year" (`eleni` and `llynedd`) but no construction here reads a bare year-deictic adverb. They are left unread rather than wired to an approximation.

**"Since".** `ers` and `er` are attested as "since" and "for". But their governed forms and the register split between them were never pinned down. No open-range vocabulary ships. `ers dydd Llun` resolves the Monday and leaves `ers` in the remainder.

**"For <duration>".** `am` is shipped only as the clock preposition. Its durational sense (`am awr`, for an hour) has no separate marker, so `am dair blynedd` must not read as a duration.

**From-to and between ranges.** No worked example fixed the governed forms of a two-ended range, so `o Fehefin i Awst` and `rhwng Mehefin a Medi` cannot close a span.

**Before, after and until.** `cyn` is attested as a soft-mutation trigger with a worked example. But `ar ôl` and `tan` are not, and shipping one edge of the family alone would read a bounded phrase as an unbounded one. None of the three ships.

**The millennium.** The dictionary has no Welsh entry for a millennium noun at all, so the unit is absent rather than transliterated.

**Seasons.** The Welsh word for autumn is spelled exactly like the month October (`Hydref`) so a season table would make every October a season and every autumn a month. The whole family is left out until the collision can be resolved deliberately. `haf 2020` reads as the bare year with `haf` unconsumed.

**Weekend references.** `y penwythnos` does not resolve.

**Era vocabulary and calendar quarters.** `44 CC` and `3ydd chwarter` refuse. `1990 OC` returns the year 1990 with `OC` left in the remainder. `chwarter` ships as the clock fraction only. The calendar-quarter sense would need its own attested construction.

**ISO week references.** `wythnos 3` and `3ydd wythnos` refuse.

**The `ac`-joined vigesimal compounds.** A numeral appendix joins 41 to 99 with `ac` before a consonant, which the coordinator's own attested alternation contradicts. Rather than pick a side, those compounds are omitted. The decimal spelling covers the range.

**Reading a year by digit groups.** Welsh reads 1965 as `mil naw chwe pump`, a construction no order here implements. The phrase is pinned so it cannot resolve to that year by some other route.

**`mis` as a month-word introducer.** `ym mis Mawrth` is attested Welsh for "in March". The month resolves. But `ym mis` has no slot here and stays in the remainder rather than being silently swallowed.

**`yn y bore`** and the other articled day-part phrases need a locative construction this locale does not ship, so the day part in `dydd Llun nesaf yn y bore` is left unread.

**A spelled quantity with no marker.** `3 diwrnod`, `dwy flynedd` and `pum mlynedd` on their own refuse: a quantity without a direction marker is still only a quantity.

## Open questions for a native speaker

1. Is `trennydd` current for the day after tomorrow, and which spelling?

2. What do `ers` and `er` govern, and how do they divide by register?

3. Which cases and mutations does a two-ended `o … i …` range impose?

4. Are `ar ôl` and `tan` mutation triggers, and of which kind?

5. How should the `Hydref` collision between autumn and October be resolved?

6. Is a millennium noun in use at all?

7. Is 41-99 joined with `ac` or with `a` before a consonant?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("cy")
    False
    >>> span, rest = extract_timespan('chwarter wedi naw', "cy", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T09:15:00', '')
    >>> span, rest = extract_timespan('hanner awr wedi tri', "cy", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T03:30:00', '')
    >>> span, rest = extract_timespan('chwarter i bedwar', "cy", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T03:45:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('y penwythnos', "cy", anchor) is None
    True
    >>> extract_timespan('44 CC', "cy", anchor) is None
    True
    >>> extract_timespan('3ydd chwarter', "cy", anchor) is None
    True
    >>> extract_timespan('wythnos 3', "cy", anchor) is None
    True
    >>> extract_timespan('3ydd wythnos', "cy", anchor) is None
    True

---
[← Vietnamese](vi.md) · [Home](../index.md) · [West Frisian →](fy.md)
