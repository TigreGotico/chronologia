# Hausa (`ha`)

<!-- agent-hint
covers: where each construction of the Hausa locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/ha/lang.json, chronologia/locale/ha/vocab.json, chronologia/extract/numfold_chadic.py, test/nl_corpus_ha/
generated: no
verify: .venv/bin/python -m doctest docs/languages/ha.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/ha.md && .venv/bin/python -c 'exec("import re,sys\nfrom datetime import datetime\nimport chronologia as C\ndef mins(d):\n    return (\"%.6f\" % (d.total_seconds() / 60)).rstrip(\"0\").rstrip(\".\")\ndef rem(r):\n    return \" and \\x60%s\\x60 left over\" % r if r else \"\"\ndef out(rd, tx, lg, an):\n    f = getattr(C, rd)\n    r = f(tx, lg, anchor=an) if rd == \"extract_duration\" else f(tx, lg, an)\n    if rd == \"extract_timespan\":\n        if r is None: return \"no reading\"\n        return \"%s to %s%s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), r.span.end.datetime().strftime(\"%Y-%m-%d %H:%M\"), rem(r.remainder))\n    if rd == \"extract_duration\":\n        if r is None: return \"no length\"\n        return \"a length of %s min%s\" % (mins(r.duration), rem(r.remainder))\n    if rd == \"extract_event\":\n        if r is None: return \"no event\"\n        return \"start %s, length %s, %s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), \"none\" if r.duration is None else mins(r.duration) + \" min\", \"summary \\x60%s\\x60\" % r.summary if r.summary else \"no summary\")\n    if r is None: return \"no rule\"\n    return \"the rule \\x60%s\\x60%s\" % (r.recurrence.to_string(), rem(r.remainder))\n\np=sys.argv[1]\nt=open(p).read()\nm=re.search(r\"\\n## Known limits\\n(.*?)(?=\\n---\\n|\\Z)\",t,re.S)\nbad=0\nn=0\ntot=0\nfor ln in (m[1].split(\"\\n\") if m else []):\n    if \"Example (\" not in ln: continue\n    tot+=1\n    g=re.search(r\"Example \\(reader \\x60(\\w+)\\x60, lang \\x60([\\w-]+)\\x60, anchor (\\d{4}-\\d\\d-\\d\\d \\d\\d:\\d\\d)\\): \\x60([^\\x60]+)\\x60 gives (.+?)\\. \\[#\\d+\\]\",ln)\n    if not g:\n        bad=1\n        print(\"example line does not parse:\",ln[:80])\n        continue\n    n+=1\n    o=out(g[1],g[4],g[2],datetime.strptime(g[3],\"%Y-%m-%d %H:%M\"))\n    if o!=g[5]:\n        bad=1\n        print(\"limit differs\",g[4],\"|\",g[5],\"|\",o)\nprint(\"known limits checked:\",n,\"of\",tot)\nsys.exit(bad)\n")' docs/languages/ha.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Hausa (`ha`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by its own `numfold_chadic` module in `chronologia/extract/`.

Hausa reads its clock the Western way, and that is worth saying first because the neighbouring locale in this tree does not. Swahili refuses the spoken hour outright: its traditional count runs from sunrise, both conventions live in written prose. Nothing in the phrase says which one a writer meant. Hausa was checked for the same ambiguity and does not have it. `ƙarfe` (literally the iron, the bell) leads the number. A following `na`-phrase names the part of the day. An hour is stated once and read once.

The evidence is arithmetic the sources do themselves. Hausa Wikipedia writes `ƙarfe 1:00 na rana (12:00 GMT)`. Nigeria runs an hour ahead of GMT, so that phrase is 13:00 and `na rana` is the afternoon. A school timetable runs `ƙarfe 7:30 zuwa 11:30 na safe, sai kuma 2:30 zuwa 6:00 na yamma`: 07:30 to 11:30 and again 14:30 to 18:00.

Elizabeth II is born `ƙarfe 02:40 (GMT)`, which is the hour the Western record gives. Twenty-four-hour literals appear unremarkably beside the twelve-hour ones (`ƙarfe 03:00 UTC`, `ƙarfe 13:00 na rana`). Nothing in the sample counts from sunrise, and the locale therefore reads both the digital literal and the spoken hour.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('ƙarfe 13:00 na rana', "ha", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T13:00:00', '')

## What ships

**Months** are the CLDR wide and abbreviated names, plus the genitive form a month name takes when a noun leans on it. That second register is what written Hausa actually uses (`watan Oktoban 2022`, `watan Fabrairun shekarar 2024`) and it was harvested by counting the frame `watan <month>` across ha.wikipedia.org rather than derived from a rule. The linker is `-n` for every month that ends in a vowel and absent for `Maris`, which ends in a consonant and stayed bare in every hit. Two months ship a second spelling because CLDR and written usage disagree: CLDR writes `Faburairu` where the press overwhelmingly writes `Fabrairu`, and CLDR writes `Afirilu` where usage prefers `Afrilu`. Both sides of each disagreement ship, because a writer who chose either must be read.

**Weekdays** are the CLDR wide names, with the three-letter abbreviations bound only beside a marker so a short form can never claim a span on its own. Friday ships twice: `ca-gregorian` doubles the m in `Jummaʼa` and `dateFields` does not. The modifier apostrophe folds to the plain one. All four spellings of the name resolve. The week starts on Monday, which is the CLDR default Nigeria inherits.

**Relative offsets** trail their marker, and the marker is a whole relative clause that agrees with the unit noun: `kwanaki uku da suka gabata` is three days ago, `watan da ya gabata` is last month, `shekara da ta gabata` is last year. The agreeing verb differs (`ya` masculine, `ta` feminine, `suka` plural) and all three ship, because the noun the writer already chose settles which one is grammatical. `gabata` and `wuce` are interchangeable in the frame and CLDR uses both. The future leads instead of trailing: `cikin kwanaki uku`, and `bayan kwanaki uku`, which is the ordinary "after" naming the same forward offset.

**The date line** is day, `ga`, month, year: `10 ga watan Oktoba 2022`, `26 ga Janairu, 1981`. CLDR's own patterns omit `ga` entirely, which is why this locale does not take its date order from CLDR alone. The particle is everywhere in written Hausa and the line is unreadable without it. `ranar` may open the line and `watan` may stand before the month name, both optional.

**Numerals** come from Wiktionary's `Module:number_list/data/ha`, with every value cross-checked against its own lemma entry. Their composition from ha.wikipedia.org, which habitually glosses a spelled number with the digits it means and so acts as its own worked-example oracle: `goma sha biyar (15)`, `ashirin da shida (26)`, `dubu ɗaya da ɗari tara da goma sha huɗu (1914)`, `dubu biyu da sha biyar (2015)`. Components read largest first, joined by `da`. A scale word leads its multiplier (`ɗari tara` is nine hundred).

The teens are `goma sha` plus a unit, and the `goma` is routinely dropped, as in `ranar sha ɗaya` for the eleventh. Both registers of the tens ship: the inherited `gomiya biyu` and the Arabic `ashirin`.

**Ranges** open with `daga`, close with `zuwa`. `tsakanin X da Y` is the between frame. `tun` is the past-anchored "since" and reaches backwards on its own or before `daga`.

## Weaker provenance

The `-r` variant of the month linker (`Satumbar`, `Oktobar`, `Disambar`) appeared in the corpus count. But only three, two and one time respectively against dozens for `-n`. It is a real alternation rather than a typo, but the sample is too thin to ship on, so only `-n` ships.

`shekaranjiya` rests on two comparative wordlists on ha.wikipedia.org that gloss it "day-before-yesterday" in English. That is two independent articles, but it is not a dictionary entry, and it is the thinnest attestation on this page.

## What refuses

A test pins each refusal.

**The half-hour on a clock.** `da rabi` is well attested on a duration (`awa daya da rabi` is an hour and a half) but no source consulted reads it on a time of day. No source establishes which direction such a reading would run. A fraction read backwards is wrong by half an hour in every reading while looking entirely normal. So the hour stands unchanged and the fraction stays in the remainder, where a caller can see it was not consumed.

**The one-word year deictics.** `bara`, `bana` and `badi` are last year, this year and next year, all three in CLDR and two of them with Wiktionary lemma entries. They are refused for an engine reason rather than a linguistic one. There is no construction for a year deixis carried by one word with no unit noun beside it, and adding one is a change to the engine, not to a locale. The phrasal forms answer instead.

**The coming weekday.** CLDR's relative-type-1 for a weekday is `Litinin mai zuwa`. The marker ships and works on every unit (`wata mai zuwa` is next month) but the phrase ends in `zuwa`, which is also this locale's range terminator. The range pass reads the raw token stream before multiword surfaces are glued back together. `Litinin mai zuwa` is therefore claimed by the open range "up to Monday". The test states what the phrase means and is expected to fail until the two can be told apart.

**A day-after-tomorrow word.** CLDR carries no relative-type-2 for Hausa, and nothing consulted attests one. The day-before-yesterday counterpart does ship.

**Seasons.** The rains divide the Hausa year, and no source consulted gives boundaries for `kaka`, `damina` or `rani`. Boundaries nobody stated are not invented.

**The quarter.** CLDR gives Hausa a quarter field. But every form is a phrase with an internal genitive (`kwata na gaba`, `wannan kwatan`) and this library's quarter constructions are built on a single quarter noun.

**Century, decade and millennium.** The locale's units are exactly the seven CLDR counts. `ƙarni` is a real noun for a century. But nothing consulted shows it counted or ordinal-scoped in running text, and scope units here are read from usage rather than derived from a rule.

**The two-letter weekday forms.** CLDR's `days.format.short` series is seven ordinary letter pairs, and `Ta` collides with the feminine genitive linker.

**Day-part bands.** CLDR ships no day-period rule set for Hausa at all. There are no boundaries to transcribe and no bands ship. `na safe`, `na rana`, `na yamma` and `na dare` are read only where they scope a stated hour, which needs no boundary. A band naming a span of its own would.

**Holidays.** No holiday vocabulary ships. The dates behind the names are a jurisdiction question rather than a vocabulary one.

## Open questions for a native speaker

1. Is there a clock reading of `da rabi`, and does it run forwards from the stated hour or back towards it?
2. Which months take the `-r` linker rather than `-n`, and is the choice lexical or free?
3. Is there a word for the day after tomorrow, and is `shekaranjiya` the ordinary word for the day before yesterday or a regional one?
4. What are the stated boundaries, if any, for `safe`, `rana`, `yamma` and `dare` when one of them stands alone rather than beside an hour?
5. Are `ƙarni` and a decade word counted in ordinary running text?
6. Does `tun` look backwards in a way `daga` does not, as English "since" and "from" do?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("ha")
    False
    >>> span, rest = extract_timespan('ƙarfe 13:00 na rana', "ha", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T13:00:00', '')
    >>> span, rest = extract_timespan('watan Oktoban 2022', "ha", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2022-10-01T00:00:00', '')
    >>> span, rest = extract_timespan('watan Fabrairun shekarar 2024', "ha", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2024-02-01T00:00:00', '')
    >>> span, rest = extract_timespan('kwanaki uku da suka gabata', "ha", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-24T00:05:00', '')

---
[← Greek](el.md) · [Home](../index.md) · [Hebrew →](he.md)
