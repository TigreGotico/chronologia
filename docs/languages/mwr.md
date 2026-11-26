# Marwari (`mwr`)

<!-- agent-hint
covers: where each construction of the Marwari locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/mwr/lang.json, chronologia/locale/mwr/*.voc, chronologia/extract/numfold_indic.py, test/nl_corpus_mwr/
generated: no
verify: .venv/bin/python -m doctest docs/languages/mwr.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/mwr.md && .venv/bin/python -c 'exec("import re,sys\nfrom datetime import datetime\nimport chronologia as C\ndef mins(d):\n    return (\"%.6f\" % (d.total_seconds() / 60)).rstrip(\"0\").rstrip(\".\")\ndef rem(r):\n    return \" and \\x60%s\\x60 left over\" % r if r else \"\"\ndef out(rd, tx, lg, an):\n    f = getattr(C, rd)\n    r = f(tx, lg, anchor=an) if rd == \"extract_duration\" else f(tx, lg, an)\n    if rd == \"extract_timespan\":\n        if r is None: return \"no reading\"\n        return \"%s to %s%s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), r.span.end.datetime().strftime(\"%Y-%m-%d %H:%M\"), rem(r.remainder))\n    if rd == \"extract_duration\":\n        if r is None: return \"no length\"\n        return \"a length of %s min%s\" % (mins(r.duration), rem(r.remainder))\n    if rd == \"extract_event\":\n        if r is None: return \"no event\"\n        return \"start %s, length %s, %s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), \"none\" if r.duration is None else mins(r.duration) + \" min\", \"summary \\x60%s\\x60\" % r.summary if r.summary else \"no summary\")\n    if r is None: return \"no rule\"\n    return \"the rule \\x60%s\\x60%s\" % (r.recurrence.to_string(), rem(r.remainder))\n\np=sys.argv[1]\nt=open(p).read()\nm=re.search(r\"\\n## Known limits\\n(.*?)(?=\\n---\\n|\\Z)\",t,re.S)\nbad=0\nn=0\ntot=0\nfor ln in (m[1].split(\"\\n\") if m else []):\n    if \"Example (\" not in ln: continue\n    tot+=1\n    g=re.search(r\"Example \\(reader \\x60(\\w+)\\x60, lang \\x60([\\w-]+)\\x60, anchor (\\d{4}-\\d\\d-\\d\\d \\d\\d:\\d\\d)\\): \\x60([^\\x60]+)\\x60 gives (.+?)\\. \\[#\\d+\\]\",ln)\n    if not g:\n        bad=1\n        print(\"example line does not parse:\",ln[:80])\n        continue\n    n+=1\n    o=out(g[1],g[4],g[2],datetime.strptime(g[3],\"%Y-%m-%d %H:%M\"))\n    if o!=g[5]:\n        bad=1\n        print(\"limit differs\",g[4],\"|\",g[5],\"|\",o)\nprint(\"known limits checked:\",n,\"of\",tot)\nsys.exit(bad)\n")' docs/languages/mwr.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Marwari (`mwr`) locale comes from and which ones it refuses. Digits, ASCII or Devanagari, are read through `numfold_indic` in `chronologia/extract/`. Spelled numbers wait on the numtag Marwari lexicon.

Marwari sources are few. The locale ships only the surfaces that a source attests, so it is small.

## Try it

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('3 दिनां में', "mwr", datetime(2017, 6, 27, 13, 4))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-30T13:04:00', '')

## What ships

**Months** are the Gregorian names of CLDR 47, locale `raj` (Rajasthani), as babel 2.18.0 ships them. CLDR has no `mwr` locale.

**The day word** आज (today) is the first word of the time-adverb list in Swami Narottamdas, *Rājasthānī Vyākaraṇ*, §270, p. 69.

**Units** are दिन / दिनां (day) and बरस / बरसां (year), from Narottamdas §270 and from example sentences in Bahal 1964.

**Relative offsets** postpose their marker: `3 दिनां में`, `2 दिन पछै`. में is in Bahal 1964 ("थोडा दिनां में", in a few days). पछै is in Narottamdas §270 and in the Shekhawati specimen of Grierson 1908, LSI vol. IX part 2.

**The clock** reads digit times, with the CLDR `raj` meridiem names सबेरे and सांम, and a digit hour before बज्या: `4 बज्या`. बज्या is in Lalas, *Rājasthānī Sabad Kos*, book p. 3737, which prints it as वज्या; both spellings are read.

## What refuses

`काल` and `परसूं` are refused: each names a day in either direction (issue #1484), and only the verb shows which.

Spelled numbers are not read until the numtag Marwari lexicon ships. The clock words बजे and बज्यां wait on a native answer, so a time such as 4 बजे returns no reading. The weekday names are left out: the bench sentences put unsourced words such as पछलै and आगलै before them, and a bare weekday then reads the wrong week.

## Open questions for a native speaker

- Which direction does काल take in each tense, and is there a one-way form?
- Which weekday names do speakers use (सुकरवार, सनीचर, बिस्पतवार)?
- Which words mean next and last before a weekday?

## Checked examples

    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('काल', "mwr", anchor) is None
    True
    >>> extract_timespan('परसूं', "mwr", anchor) is None
    True
