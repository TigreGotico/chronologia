# Irish (`ga`)

<!-- agent-hint
covers: where each construction of the Irish locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/ga/lang.json, chronologia/locale/ga/vocab.json, chronologia/extract/numfold_irish.py, test/nl_corpus_ga/
generated: no
verify: .venv/bin/python -m doctest docs/languages/ga.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/ga.md && .venv/bin/python -c 'exec("import re,sys\nfrom datetime import datetime\nimport chronologia as C\ndef mins(d):\n    return (\"%.6f\" % (d.total_seconds() / 60)).rstrip(\"0\").rstrip(\".\")\ndef rem(r):\n    return \" and \\x60%s\\x60 left over\" % r if r else \"\"\ndef out(rd, tx, lg, an):\n    f = getattr(C, rd)\n    r = f(tx, lg, anchor=an) if rd == \"extract_duration\" else f(tx, lg, an)\n    if rd == \"extract_timespan\":\n        if r is None: return \"no reading\"\n        return \"%s to %s%s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), r.span.end.datetime().strftime(\"%Y-%m-%d %H:%M\"), rem(r.remainder))\n    if rd == \"extract_duration\":\n        if r is None: return \"no length\"\n        return \"a length of %s min%s\" % (mins(r.duration), rem(r.remainder))\n    if rd == \"extract_event\":\n        if r is None: return \"no event\"\n        return \"start %s, length %s, %s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), \"none\" if r.duration is None else mins(r.duration) + \" min\", \"summary \\x60%s\\x60\" % r.summary if r.summary else \"no summary\")\n    if r is None: return \"no rule\"\n    return \"the rule \\x60%s\\x60%s\" % (r.recurrence.to_string(), rem(r.remainder))\n\np=sys.argv[1]\nt=open(p).read()\nm=re.search(r\"\\n## Known limits\\n(.*?)(?=\\n---\\n|\\Z)\",t,re.S)\nbad=0\nn=0\ntot=0\nfor ln in (m[1].split(\"\\n\") if m else []):\n    if \"Example (\" not in ln: continue\n    tot+=1\n    g=re.search(r\"Example \\(reader \\x60(\\w+)\\x60, lang \\x60([\\w-]+)\\x60, anchor (\\d{4}-\\d\\d-\\d\\d \\d\\d:\\d\\d)\\): \\x60([^\\x60]+)\\x60 gives (.+?)\\. \\[#\\d+\\]\",ln)\n    if not g:\n        bad=1\n        print(\"example line does not parse:\",ln[:80])\n        continue\n    n+=1\n    o=out(g[1],g[4],g[2],datetime.strptime(g[3],\"%Y-%m-%d %H:%M\"))\n    if o!=g[5]:\n        bad=1\n        print(\"limit differs\",g[4],\"|\",g[5],\"|\",o)\nprint(\"known limits checked:\",n,\"of\",tot)\nsys.exit(bad)\n")' docs/languages/ga.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Irish (`ga`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by its own `numfold_irish` module in `chronologia/extract/`.

Irish mutates a word's initial consonant, and unlike Welsh next door the rules for *which* mutation a given trigger imposes are, in several places the temporal constructions need, not stated by any source consulted. Where the sources contradict each other or fall silent, this locale ships the unmutated reading alone and refuses the mutated collocation rather than picking a side. Most of the refusals below are that decision applied case by case.

The clock counts the English way and never the toward-the-hour way: `leathuair tar éis a trí` is 03:30, an hour later than the reading some of Irish's neighbours would give the same shape. Past the half hour it switches to `chun`: `ceathrú chun a dó` is 01:45. Ulster substitutes `i ndiaidh` and `go dtí` for the two directions, and both are accepted.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('leathuair tar éis a trí', "ga", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T03:30:00', '')

## What ships

**Weekdays and months** come from Unicode CLDR 47, `cldr-dates-full/main/ga/ca-gregorian.json`. Each weekday ships in two shapes, because they do different jobs: CLDR's citation form is already the adverbial `Dé` compound meaning "on <day>", while the bare radical noun is what a modified reference uses: `an Luan seo chugainn`, next Monday.

Months ship in four shapes: the bare name, the form after the noun `mí` in the genitive (`mí Aibreáin`), the eclipsed form after the bare preposition `i` (`i mBealtaine`), and the abbreviation. The declensions and the eclipsis come from each headword's own Wiktionary tables.

**Relative offsets backward** are marked at the tail. `ó shin` is an adverb that trails the quantity it counts back over: `cúig lá ó shin`, five days ago.

**Last and next** likewise trail their noun: `seo caite` and `seo chugainn`, both glossed for nouns denoting a period of time.

**The clock's particle `a`** introduces an hour (`a trí a chlog` is three o'clock) and the hour after it is the disjunctive cardinal, never the counting form. The same particle also enumerates: `uimhir a 3` is number three and `seomra a 5` is room five, neither of them a time. Nothing in the surface tells the two uses apart. Every clock order that reads this particle requires corroborating clock context: `a chlog`, a meridiem, or a fraction with its direction. `uimhir a 3` accordingly resolves to nothing.

**Markers.** `idir` is "between", paired with `agus`, and in its plain spatial and temporal sense it leaves both bounds unmutated. `ar feadh` is "for, over a period of time", governing the genitive and mutating nothing itself. `ó` is "from, since". `i` / `in` is the locative that eclipses a following month name.

The clock words come from Wiktionary entries for `tar éis`, `i ndiaidh`, `chun`, `ceathrú`, `leathuair` and `a chlog`, corroborated by Omniglot's page on time in Irish and by bitesize.irish's guide.

## What refuses

A test pins each refusal.

**The millennium.** `mílaois` is an attested noun, but no source gives its genitive, its plural or any counted form, so no millennium unit ships.

**The decade.** Irish has no single-word "decade" attested. The compositional `deich mbliana` is ten years, not a named decade, and reading it as one would turn a duration into a calendar period.

**The century.** `céad` is at once "hundred", "century" and "first", and the sources contradict each other on whether it mutates what follows. No century unit ships, rather than one that conflates a hundred years with the first of something.

**Lenited `chéad` as a hundred.** After the article, `chéad` is the ordinal "first" and never the numeral, so folding it to 100 would invent a quantity where the text states a rank.

**A counted teen split around its noun.** Irish puts the noun *inside* the numeral (`ceithre bliana déag`, fourteen years) and no source gives that shape for more than one noun. The fold refuses it rather than reading the leading element alone and dropping the `déag`.

**The thirty-first.** The numerals table runs to the thirtieth. The thirty-first is only described as a pattern, never spelled out in any source, so it is not read.

**`ceathrú` as a spelled fourth.** It is at once "fourth" and the quarter of an hour the clock speaks. Claiming every occurrence as the digit four would erase the quarter from every clock phrase, so the ordinal reading is refused.

**Day parts.** CLDR has no day-period rule set for Irish at all (its authority stops at the bare am/pm markers) so no time-of-day band ships. `maidin`, `tráthnóna` and `san oíche` are left unread.

**Seasons.** No season vocabulary was attested, so a season word never resolves to a quarter of the year.

**Era vocabulary.** `44 RC` and `roimh Chríost` are refused or leave the marker visible.

**A forward offset.** No "in <N> <units>" marker was attested, so `i gceann trí lá` and `faoi cheann seachtaine` are refused rather than read with the backward marker's sign. That would put the answer on the wrong side of the anchor.

**`ar feadh` alone.** It states how long something lasts, not when it happens. On its own it anchors nothing and must not become an offset.

**Mutated `gach` collocations.** `gach` imposes h-prothesis on some nouns, lenition on others and nothing on the rest, with no rule any source states. Only the bare marker ships, so `gach Luan` resolves the Monday and leaves `gach` in the remainder.

**Lenition after `ó`.** The same preposition lenites in one of its own cited examples and leaves the radical in another. The contradiction is not resolved by picking a side, so only the unmutated reading ships and `ó mhaidin` is not read.

**Lenited `idir`.** `idir … agus …` lenites both conjuncts only in its "both … and …" sense, which is not a date range. The plain unmutated reading is the one that ships.

**ISO week references and period parts.** `3ú seachtain` refuses. `ag tús Meitheamh` returns the month with the part word left visible.

## Open questions for a native speaker

1. Does `mílaois` have an attested genitive, plural and counted form?

2. Is there a single-word decade, and how is a named decade such as "the seventies" expressed?

3. Does `céad` mutate what follows it in the century sense, and how is a century written so it cannot be read as a hundred?

4. How is the thirty-first of a month spelled out?

5. What is the ordinary "in <N> days" forward marker?

6. Which mutation does `gach` impose, and on what?

7. Does `ó` lenite in its temporal sense?

8. Does the t-prothesised `an tseachtain` need to ship alongside the radical `seachtain`? The radical form resolves. The prothesised one does not.

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
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('44 RC', "ga", anchor) is None
    True
    >>> extract_timespan('roimh Chríost', "ga", anchor) is None
    True
    >>> extract_timespan('i gceann trí lá', "ga", anchor) is None
    True
    >>> extract_timespan('faoi cheann seachtaine', "ga", anchor) is None
    True
    >>> extract_timespan('3ú seachtain', "ga", anchor) is None
    True

---
[← Indonesian](id.md) · [Home](../index.md) · [Italian →](it.md)
