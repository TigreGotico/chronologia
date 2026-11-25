# Korean (`ko`)

<!-- agent-hint
covers: where each construction of the Korean locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/ko/lang.json, chronologia/locale/ko/vocab.json, chronologia/extract/numfold_korean.py, test/nl_corpus_ko/
generated: no
verify: .venv/bin/python -m doctest docs/languages/ko.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/ko.md && .venv/bin/python -c 'exec("import re,sys\nfrom datetime import datetime\nimport chronologia as C\ndef mins(d):\n    return (\"%.6f\" % (d.total_seconds() / 60)).rstrip(\"0\").rstrip(\".\")\ndef rem(r):\n    return \" and \\x60%s\\x60 left over\" % r if r else \"\"\ndef out(rd, tx, lg, an):\n    f = getattr(C, rd)\n    r = f(tx, lg, anchor=an) if rd == \"extract_duration\" else f(tx, lg, an)\n    if rd == \"extract_timespan\":\n        if r is None: return \"no reading\"\n        return \"%s to %s%s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), r.span.end.datetime().strftime(\"%Y-%m-%d %H:%M\"), rem(r.remainder))\n    if rd == \"extract_duration\":\n        if r is None: return \"no length\"\n        return \"a length of %s min%s\" % (mins(r.duration), rem(r.remainder))\n    if rd == \"extract_event\":\n        if r is None: return \"no event\"\n        return \"start %s, length %s, %s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), \"none\" if r.duration is None else mins(r.duration) + \" min\", \"summary \\x60%s\\x60\" % r.summary if r.summary else \"no summary\")\n    if r is None: return \"no rule\"\n    return \"the rule \\x60%s\\x60%s\" % (r.recurrence.to_string(), rem(r.remainder))\n\np=sys.argv[1]\nt=open(p).read()\nm=re.search(r\"\\n## Known limits\\n(.*?)(?=\\n---\\n|\\Z)\",t,re.S)\nbad=0\nn=0\ntot=0\nfor ln in (m[1].split(\"\\n\") if m else []):\n    if \"Example (\" not in ln: continue\n    tot+=1\n    g=re.search(r\"Example \\(reader \\x60(\\w+)\\x60, lang \\x60([\\w-]+)\\x60, anchor (\\d{4}-\\d\\d-\\d\\d \\d\\d:\\d\\d)\\): \\x60([^\\x60]+)\\x60 gives (.+?)\\. \\[#\\d+\\]\",ln)\n    if not g:\n        bad=1\n        print(\"example line does not parse:\",ln[:80])\n        continue\n    n+=1\n    o=out(g[1],g[4],g[2],datetime.strptime(g[3],\"%Y-%m-%d %H:%M\"))\n    if o!=g[5]:\n        bad=1\n        print(\"limit differs\",g[4],\"|\",g[5],\"|\",o)\nprint(\"known limits checked:\",n,\"of\",tot)\nsys.exit(bad)\n")' docs/languages/ko.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Korean (`ko`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by its own `numfold_korean` module in `chronologia/extract/`.

Korean writes every number twice over. The native series (`하나`, `둘`, `셋` …) counts the hours on a clock face. The Sino-Korean series (`일`, `이`, `삼` …) counts the minutes beside them, and every calendar field (day, month, year, week) besides. A bare numeral has no value of its own in this locale.

It has a value only in the company of the counter word that follows it. The wrong series in a slot names nothing at all rather than the number it would name elsewhere. `삼 시` (Sino "three" plus the hour counter) refuses. Only `세 시`, with the native numeral, is three o'clock.

That same fact repeats through the vocabulary: meaning lives in position, not in the string. The syllable `일` alone is the day, the Sino numeral one and Sunday at once. The syllable `월` alone is the month and Monday at once. Nothing inside either syllable decides which reading applies, so neither resolves anything on its own. Each is licensed only by standing next to a number, a date field, or a fixed calendar phrase that fixes its reading.

The clock counts forward from the hour just named. The phrase `세 시 십 분` is ten past three, never ten to it. The trailing word `전` is the one exception. When it closes the phrase, it turns the same minute count backward. The phrase `세 시 십 분 전` is ten minutes *before* three, 02:50. Because that marker is both obligatory for the backward reading and always final, the two directions never collide.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('세 시 십 분 전', "ko", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T02:50:00', '')

## What ships

**Day parts** come from the Unicode CLDR 47 day-period rule set for `ko` (`cldr/common/supplemental/dayPeriods.xml`), with each label taken from `ko`'s `ca-gregorian.json` `dayPeriods.format.wide`: `아침` (morning) `[03:00, 06:00)`, `오전` (the AM half, `[06:00, 12:00)`), `오후` (the PM half, `[12:00, 18:00)`), `저녁` (evening) `[18:00, 21:00)` and `밤` (night) `[21:00, 03:00)`. `오전` and `오후` do double duty as the clock's meridiem markers. Korean puts the meridiem word **before** the hour, as in `오전 9시`. That is the opposite of English order.

**Named days** span five points from two days before to two days after the anchor, sourced two ways. CLDR 47's `dateFields.json` gives the inner three: `어제` (relative-type -1, yesterday), `오늘` (relative-type 0, today) and `내일` (relative-type 1, tomorrow).

The two-day forms come from Wiktionary. They are `그저께` (the day before yesterday) and `모레` (the day after tomorrow). The locale reaches one step further than CLDR or Wiktionary individually attest. It ships the three-day forms too: `그끄저께` (two days before yesterday) and `글피` (two days after tomorrow). Both are cited to their own Wiktionary entries.

**Weekdays** are CLDR 47's `days.format.wide` set, indexed from Monday: `월요일`, `화요일`, and so on. CLDR also carries a single-syllable abbreviated form for each (`월 화 수 목 금 토 일`) but none of those ship, because every one of the seven is itself an ordinary, unrelated word: `일` is the day, the numeral one, and Sunday at once. `월` is the month and Monday. `수` is a number and the word for water. `금` is gold. Nothing in the string distinguishes the readings. Only a calendar grid does, and a grid is not prose a parser receives, so the bare abbreviation names no weekday in this locale.

**Months** are the CLDR 47 form, where the wide and abbreviated forms are identical. Each is a Sino-Korean numeral written as a digit plus the month word, as in `1월` for January. Two spelled-out forms exist for June and October outside the digit-plus-counter pattern: `유월` and `시월`. No citation backs their calendar reading. The locale leaves them unshipped on purpose and does not guess them onto the month slot.

**The date line** is `y년 MMMM d일`, CLDR's own long format. Every field carries its own trailing suffix word. The suffix `년` closes the year, and the suffix `일` closes the day of the month. Position alone licenses both suffixes.

The suffix `년` stands behind a year number. The suffix `일` stands immediately behind a day number inside a date. Each syllable is also an ordinary word on its own (`일` again the numeral one and the day counter, see above).

**The clock** is `MERIDIEM? HOUR 시 MINUTE 분` with an optional trailing direction word. `시` names the hour and reads as one only behind a numeral. It is also the ordinary word for a city and for a poem. `분` closes the minute count the same way, cited to CLDR's `timeFormats` pattern spelled out in full. `반` stands in for a thirty-minute count and reads forward from the hour just named, so `두 시 반` is 2:30. Elon.io's Korean-grammar page on `반, 전, 후` is the source. Korean Study Junkie's guide to telling time corroborates it and gives `열두시반` for 12:30. `전`, at the very end of the phrase, reverses the minute count to run backward from the following hour: `세 시 십 분 전` is 02:50, cited to the same Elon.io page. Landmark points are CLDR's own wide day-period words for midnight and noon, `자정` and `정오`.

**The particle `-에`** ("at," marking a point in time) is written directly onto the preceding noun with no space, as in `3시에`. The locale's tokenizer cuts it back off before it reads the noun underneath. Wiktionary's entry for `에` glosses it as marking the preceding noun as a temporal adverb naming a point in time.

**Relative offsets** are `NUM UNIT MARKER`, with the direction word closing the phrase: `후` for forward and `전` for backward, both cited to CLDR 47's `dateFields.json` relative patterns (`{0}일 후`, `{0}일 전`). `전` is the same syllable that reverses a clock's minute count. The two readings are told apart only by what precedes them. A clock reading requires a named hour in front, the offset marker does not.

**"This," "last" and "next"** attach in front of the noun they scope, all sourced to CLDR's relative-type fields for week and month: `이번` (this, relative-type 0: `이번 주`, `이번 달`), `지난` (last, relative-type -1: `지난주`, `지난달`) and `다음` (next, relative-type 1: `다음 주`, `다음 달`).

**Units** carry no separate plural surface, because Korean nouns mark no number at all. The counted and uncounted forms of a unit are the same word. The vocabulary ships that way on purpose and does not duplicate them. `일` counts days and `시간` counts hours, both cited to CLDR's own duration patterns (`{0}일 전`/`{0}일 후`, and the equivalent for hours). `시간` is distinct from bare `시`, which names the hour of the clock and is never a duration on its own.

## What refuses

A test pins every refusal. Each is a case where two ordinary Korean readings compete and nothing in the phrase chooses between them. Returning either would be a confident wrong answer with nothing to flag it as a guess.

**The wrong numeral series in a slot.** A Sino numeral in the hour slot (`삼 시`, `십 시`) refuses. A native numeral in the minute slot (`세 분`, `두 초`) refuses too. Only the native series names an hour and only the Sino series names a minute.

**The two worst homographs, standing alone.** Bare `일` and bare `월` name nothing on their own, for the reasons given above.

**An ordinary word that happens to look like numeral-plus-counter.** `만일` ("if") and `일일` ("daily") both segment cleanly into a Sino numeral plus the day counter. The locale carves out both by hand. It does not read them as "ten thousand days" and "one day." The segmenter also leaves whole a word that merely *contains* a counter syllable. The words `시일`, `일요일`, `오후` and `이번` all fail to split. The segmenter requires a numeral of the matching series to license its counter. It also requires the segmentation to cover the whole word, not a substring of it.

**A bare counter with no count in front of it.** `시`, `분`, `초`, `년`, `개월`, `주` on their own are not offsets.

**A month number the calendar cannot hold.** `13월`, `0월`, `99월` all refuse.

**A bare numeral with nothing counted.** The words `하나`, `열둘`, `이십오` and `삼천` name no date. In Korean they do not even name a plain number in isolation, since no counter has told the string which series it belongs to.

**A particle glued onto a compound.** Because `-에` and similar particles attach with no space, a phrase like `지난주에` or `열두시반에` must have the particle cut off before the noun underneath (`지난주`, `열두시반`) reaches the segmenter, tested directly by asserting the particle-stripped forms still segment correctly while the particle-attached forms do not split on their own.

## Open questions for a native speaker

1. Are `유월` and `시월` current enough in ordinary written use as month names? If so, should they ship despite carrying no independent calendar citation? Or are they reserved for set phrases and dates read aloud?
2. Is the single-syllable weekday abbreviation ever used unambiguously in running prose (for instance in a fixed schedule table) where context would resolve what the bare letter alone cannot?
3. Does `반` ever read backward from the following hour the way `전` does for whole minutes, or is "half past" always forward regardless of which half of the clock face it falls on?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("ko")
    False
    >>> span, rest = extract_timespan('세 시 십 분 전', "ko", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T02:50:00', '')
    >>> span, rest = extract_timespan('세 시 십 분', "ko", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T03:10:00', '')
    >>> span, rest = extract_timespan('오전 9시', "ko", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T09:00:00', '')
    >>> span, rest = extract_timespan('두 시 반', "ko", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T02:30:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('13월', "ko", anchor) is None
    True
    >>> extract_timespan('0월', "ko", anchor) is None
    True
    >>> extract_timespan('99월', "ko", anchor) is None
    True

---
[← Kabyle](kab.md) · [Home](../index.md) · [Latvian →](lv.md)
