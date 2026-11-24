# Maltese (`mt`)

<!-- agent-hint
covers: where each construction of the Maltese locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/mt/lang.json, chronologia/locale/mt/*.voc, chronologia/extract/numfold_maltese.py, test/nl_corpus_mt/
generated: no
verify: .venv/bin/python -m doctest docs/languages/mt.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/mt.md && .venv/bin/python -c 'exec("import re,sys\nfrom datetime import datetime\nimport chronologia as C\ndef mins(d):\n    return \"%g\" % (d.total_seconds() / 60)\ndef rem(r):\n    return \" and \\x60%s\\x60 left over\" % r if r else \"\"\ndef out(rd, tx, lg, an):\n    f = getattr(C, rd)\n    r = f(tx, lg, anchor=an) if rd == \"extract_duration\" else f(tx, lg, an)\n    if rd == \"extract_timespan\":\n        if r is None: return \"no reading\"\n        return \"%s to %s%s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), r.span.end.datetime().strftime(\"%Y-%m-%d %H:%M\"), rem(r.remainder))\n    if rd == \"extract_duration\":\n        if r is None: return \"no length\"\n        return \"a length of %s min%s\" % (mins(r.duration), rem(r.remainder))\n    if rd == \"extract_event\":\n        if r is None: return \"no event\"\n        return \"start %s, length %s, summary \\x60%s\\x60\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), \"none\" if r.duration is None else mins(r.duration) + \" min\", r.summary)\n    if r is None: return \"no rule\"\n    return \"the rule \\x60%s\\x60%s\" % (r.recurrence.to_string(), rem(r.remainder))\n\np=sys.argv[1]\nt=open(p).read()\nm=re.search(r\"\\n## Known limits\\n(.*?)(?=\\n---\\n|\\Z)\",t,re.S)\nbad=0\nn=0\nfor ln in (m[1].split(\"\\n\") if m else []):\n    g=re.search(r\"Example \\(reader \\x60(\\w+)\\x60, lang \\x60([\\w-]+)\\x60, anchor (\\d{4}-\\d\\d-\\d\\d \\d\\d:\\d\\d)\\): \\x60([^\\x60]+)\\x60 gives (.+?)\\. \\[#\\d+\\]\",ln)\n    if not g: continue\n    n+=1\n    o=out(g[1],g[4],g[2],datetime.strptime(g[3],\"%Y-%m-%d %H:%M\"))\n    if o!=g[5]:\n        bad=1\n        print(\"limit differs\",g[4],\"|\",g[5],\"|\",o)\nprint(\"known limits checked:\",n)\nsys.exit(bad)\n")' docs/languages/mt.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Maltese (`mt`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by its own `numfold_maltese` module in `chronologia/extract/`.

Maltese is a Semitic language written in the Latin alphabet with a heavy Romance vocabulary. Every one of those three facts shows up in this locale. The definite article assimilates to nine sun letters, so `il-` becomes `is-`, `it-`, `iċ-` and six more, and each allomorph is listed rather than derived. The weekdays are numbered from Sunday on the Semitic pattern. The months are Sicilian and Italian borrowings that take no article at all.

The direction of an offset is marked at the **tail**, not the head. `ilu` closes a backward offset (`jumejn ilu`, two days ago) and `oħra` closes a forward one. That single fact produces the locale's most consequential refusal.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('is-sitta u kwart', "mt", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T06:15:00', '')

## What ships

**Weekdays and months** come from CLDR 47, `cldr-dates-full/main/mt/ca-gregorian.json`. Weekdays ship only in their articled form, and deliberately: bare `tnejn` is the cardinal two, and bare `ġimgħa` is the noun "week", which this locale ships as its week unit. Only `it-tnejn` and `il-ġimgħa` are weekdays.

**The date line** is `15 ta' Awwissu` (day, the genitive linker `ta'`, month) which is CLDR's own long format for the language. The tokenizer drops the apostrophe.

**The dual.** Maltese has a dual number, and the number fold rewrites it before matching: `jumejn` becomes two plus `jiem`, `sentejn` two plus `snin`. The dual forms therefore do not appear in the unit files. They are handled upstream.

**The `-il` linker.** From eleven upward a Maltese numeral takes `-il` and puts the counted noun back in the singular: `ħdax-il jum`. The tokenizer shears the hyphen, so the linker arrives as its own token and the counted orders accept it as an optional connector.

**The clock** switches direction at the half hour. Before it, minutes are counted forward off the hour already named with `u` ("and"): `is-sitta u kwart` is 06:15, `is-sitta u nofs` is 06:30. After it, Maltese names the **coming** hour and takes the remaining minutes off it with `nieqes` ("less"): `it-tmienja nieqes kwart` is 07:45, `l-għaxra nieqes ħamsa` is 09:55. The sources are Preply's Maltese time guide and languagephrases.com's, plus Wiktionary for `nieqes`, `kwart` and `nofs` individually.

`fi` and its article contractions (`fil-`, `fis-`, `fit-` and the rest) are the ordinary way to state a time: `fis-sebgħa` is "at seven".

**Relative offsets.** The past is `ilu`, postposed and invariant. The future is a preposed frame plus a trailing `oħra`: CLDR spells the frame `fi żmien` ("within the time") for year, day and hour, `sa` ("up to") for week and minute, and month takes either. The trailing "another" agrees in gender, masculine `ieħor` with `xahar`, feminine `oħra` elsewhere.

**Last and next** are suppletive trailing phrases rather than particles. They are shipped as the phrases they are: `l-oħra` for last year, `li għadda` for a masculine month or a weekday, `li għaddiet` for the feminine week, `id-dieħel`, `d-dieħla`, `li ġej` and `ta' wara` for the coming period.

**`din il-ġimgħa`.** The feminine demonstrative and the article run together as one proclitic before a noun taking `il-`. That run is what distinguishes `din il-ġimgħa` (this week) from the weekday `Il-Ġimgħa` (Friday). The two share the same noun under the same article, so gender does the work: `ġimgħa` is feminine and takes `din`, while the masculine weekdays keep their own frame (`dan il-Ħadd`). The week reading is what CLDR states for the week field's relative-type-0. It is the only reading found in running text, in Maltese Wikipedia articles that spell `matul din il-ġimgħa` and `Din il-ġimgħa offriet kuntrast interessanti`, all of them a span of days.

**Markers** are Wiktionary entries: `wara` (after), `qabel` (before, and never "ago", which is `ilu`), `bejn` (between, in `bejn X u Y`), `minn` (from), `sa` (until), `mindu` (since), `kull` (every).

## Weaker provenance

**The clock idioms** rest on two language-learning guides agreeing with each other, plus Wiktionary for the individual words. No grammar was consulted for the direction switch at the half hour.

**The article allomorph list** is transcribed from the English Wikipedia article on Maltese grammar and a beginners' course chapter, not from a reference grammar.

## What refuses

A test pins each refusal.

**Day-part bands.** `filgħodu`, `filgħaxija`, `bil-lejl` and `wara nofsinhar` name no span. CLDR ships no day-period rule set for Maltese at all (only the borrowed AM and PM labels) so there are no boundaries to transcribe and none were invented from a dictionary gloss. `filgħodu` and `filgħaxija` do ship, but as clock markers that fix a spoken hour in one half of the day: `fis-sebgħa filgħodu` is 07:00.

**The day before yesterday.** CLDR carries no relative-type--2 field for Maltese and no other source names a word for it, so no surface ships. The day *after* tomorrow is sourced and does ship (`pitgħada`, with its attested variant `bitgħada`) which is what makes the asymmetry deliberate rather than an oversight.

**Decade and millennium.** Neither `deċennju` nor `millennju` has a dictionary entry to cite, so neither unit ships. The century does: `seklu ilu` reads.

**A future offset without its trailing marker.** `fi żmien sena` returns nothing, while `fi żmien sena oħra` reads as a year ahead. Both directions are marked at the tail, and the only way to accept a bare frame would be to accept a *preposed* direction marker. That would also accept the preposed `ilu`. That preposed `ilu` is a different lexeme: the person-inflected durative adverb in `Ili jumejn ma norqod` ("I haven't slept in two days"), which needs agreement with a subject this engine cannot read.

Reading it as "ago" would invert the direction of the sentence. So the offset orders accept `ilu` only in trailing position. The CLDR count-one and count-two future patterns that omit `oħra` are refused on that trade.

**Sibling and source-language phrasings.** Arabic, Hebrew, Italian, Spanish and French relative-time phrasings are pinned as unreadable. A Maltese locale cannot quietly answer text that is not Maltese.

**A month name inside a word.** `marzupan` is not March.

## Open questions for a native speaker

1. Is there a word for the day before yesterday?
2. Are `deċennju` and `millennju` in ordinary use, and how do they inflect?
3. Is a bare `fi żmien sena` idiomatic for "in a year", and if so what distinguishes it in writing from the durative `ilu` frame?
4. Does the clock's switch to `nieqes` happen exactly at the half hour, or earlier or later in practice?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("mt")
    False
    >>> span, rest = extract_timespan('is-sitta u kwart', "mt", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T06:15:00', '')
    >>> span, rest = extract_timespan('is-sitta u nofs', "mt", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T06:30:00', '')
    >>> span, rest = extract_timespan('it-tmienja nieqes kwart', "mt", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T07:45:00', '')
    >>> span, rest = extract_timespan('l-għaxra nieqes ħamsa', "mt", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T09:55:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('fi żmien sena', "mt", anchor) is None
    True
    >>> extract_timespan('oħra', "mt", anchor) is None
    True

---
[← Malay](ms.md) · [Home](../index.md) · [Mirandese →](mwl.md)
