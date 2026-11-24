# Romanian (`ro`)

<!-- agent-hint
covers: where each construction of the Romanian locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/ro/lang.json, chronologia/locale/ro/*.voc, chronologia/extract/numlayer.py:NUMTAG_LANGS, test/nl_corpus_ro/, test/test_xfail_open_issues_*.py
generated: no
verify: .venv/bin/python -m doctest docs/languages/ro.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/ro.md noapte@00:00 && .venv/bin/python -c 'exec("import re,sys\nfrom datetime import datetime\nimport chronologia as C\ndef mins(d):\n    return (\"%.6f\" % (d.total_seconds() / 60)).rstrip(\"0\").rstrip(\".\")\ndef rem(r):\n    return \" and \\x60%s\\x60 left over\" % r if r else \"\"\ndef out(rd, tx, lg, an):\n    f = getattr(C, rd)\n    r = f(tx, lg, anchor=an) if rd == \"extract_duration\" else f(tx, lg, an)\n    if rd == \"extract_timespan\":\n        if r is None: return \"no reading\"\n        return \"%s to %s%s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), r.span.end.datetime().strftime(\"%Y-%m-%d %H:%M\"), rem(r.remainder))\n    if rd == \"extract_duration\":\n        if r is None: return \"no length\"\n        return \"a length of %s min%s\" % (mins(r.duration), rem(r.remainder))\n    if rd == \"extract_event\":\n        if r is None: return \"no event\"\n        return \"start %s, length %s, %s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), \"none\" if r.duration is None else mins(r.duration) + \" min\", \"summary \\x60%s\\x60\" % r.summary if r.summary else \"no summary\")\n    if r is None: return \"no rule\"\n    return \"the rule \\x60%s\\x60%s\" % (r.recurrence.to_string(), rem(r.remainder))\n\np=sys.argv[1]\nt=open(p).read()\nm=re.search(r\"\\n## Known limits\\n(.*?)(?=\\n---\\n|\\Z)\",t,re.S)\nbad=0\nn=0\ntot=0\nfor ln in (m[1].split(\"\\n\") if m else []):\n    if \"Example (\" not in ln: continue\n    tot+=1\n    g=re.search(r\"Example \\(reader \\x60(\\w+)\\x60, lang \\x60([\\w-]+)\\x60, anchor (\\d{4}-\\d\\d-\\d\\d \\d\\d:\\d\\d)\\): \\x60([^\\x60]+)\\x60 gives (.+?)\\. \\[#\\d+\\]\",ln)\n    if not g:\n        bad=1\n        print(\"example line does not parse:\",ln[:80])\n        continue\n    n+=1\n    o=out(g[1],g[4],g[2],datetime.strptime(g[3],\"%Y-%m-%d %H:%M\"))\n    if o!=g[5]:\n        bad=1\n        print(\"limit differs\",g[4],\"|\",g[5],\"|\",o)\nprint(\"known limits checked:\",n,\"of\",tot)\nsys.exit(bad)\n")' docs/languages/ro.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Romanian (`ro`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

Romanian is the deepest calendar locale in the project outside the reference locales: alongside the Gregorian calendar it ships the Roman calendar (kalends, nones, ides), the French Republican calendar, the Hebrew calendar, the Islamic civil calendar, and Japanese regnal eras, all through Romanian vernacular vocabulary or a mix of vernacular and retained Latin/foreign forms. The scale of that surface is worth stating up front. Most of this page's citation weight sits on the everyday layer (weekdays, months, the clock, the day parts, ranges), where a Romanian speaker actually lives. The calendar layer is mechanically wired rather than richly sourced.

The second thing to know is the definite article. Romanian attaches it as an enclitic (`luni` is Monday, `lunea` is "on Monday" in the sense that governs `lunea trecută`, "last Monday") and the weekday vocabulary ships both forms because the articulated one is the ordinary written shape in a relative phrase.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('lunea trecută', "ro", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-26T00:00:00', '')

## What ships

**Weekdays** ship bare and articulated, each cited to dexonline (the _Dicționarul explicativ al limbii române_) and to DOOM (the Romanian Academy's orthographic-orthoepic dictionary) for the definite-article form of each day name: `luni`/`lunea`, `marți`/`marțea`, `miercuri`/`miercurea`, `joi`/`joia`, `vineri`/`vinerea` and `sâmbătă`/`sâmbăta`. The word `duminică` is the exception. Its file ships only the two diacritic spellings of the bare noun (`duminică`/`duminica`). It has no dexonline/DOOM citation comment and no articulated `duminica` form with the enclitic article. It is the one weekday in the set without the citation that the other six carry.

**Months** ship bare with a three-letter abbreviation (`ianuarie`/`ian`), and every month name cites Unicode CLDR 47.

**The date line** is little-endian in both the spelled and the dotted civil form (`dotted_date: true`), matching every level of the CLDR `ro` `ca-gregorian` chart: full `EEEE, d MMMM y`, long `d MMMM y`, medium `d MMM y`, short `dd.MM.y`. Day comes first throughout, unlike Persian's short pattern.

**Relative offsets** are `acum` for the past (`acum trei zile`, "three days ago") and `peste`/`în` for the future, plus a quantifier-led order (`o săptămână`, `câțiva ani`) that reads `un`/`o` (one), `pereche` (a pair, two) and `câțiva`/`câteva` (a few, three) as counts. The counts can stand in either position relative to the unit and marker.

**The clock** is additive past the hour and subtractive toward it, the same direction English uses. The word `și` ("and") leads the fraction past the hour: `trei și un sfert` is 3:15 and `nouă și jumătate` is 9:30. The word `fără` ("without") subtracts from the *next* hour: `patru fără un sfert` is 3:45. Two independent sources with worked numeric examples confirm that direction. One is the project's own test corpus (`trei și un sfert` → 3:15, `patru fără un sfert` → 3:45, checked against independent arithmetic on a fixed anchor). The other is Romania Insider's Romanian-language lesson. It glosses `Este unu și un sfert` as "It's quarter past one" and `Două fără un sfert` as "It's quarter to two". That is the same hour-relative-to-:30 switch that the shipped vocabulary encodes. `sfert` ("quarter") is independently confirmed at its Wiktionary lemma entry, glossed "quarter" or "fourth", with `pătrime`/ `pătrar` given as synonyms. The entry also gives a Church Slavic borrowing history that produced Ukrainian `чверть` too. That is the same root family with an unrelated surface. The landmarks are `amiază`/`amiaza`/`prânz`/`pranz` (noon) and `miezulnoptii` (midnight), and the meridiem words `dimineața` (literally "in the morning", doubling as the AM marker) and `seara` ("in the evening", the PM marker).

**Day parts** take their boundaries from the Unicode CLDR 47 day-period chart for `ro`, cross-checked directly against the CLDR JSON `dayPeriodRuleSet`: `dimineață` `[05:00, 12:00)`, `după-amiaza` `[12:00, 18:00)`, `seară` `[18:00, 22:00)`, `noapte` `[22:00, 05:00)`. The vocabulary comments also cite dexonline for the surfaces themselves. Two things are worth flagging in how these were shipped. First, `după-amiaza` is registered as a glued multi-token surface rather than the bare noun, because the tokenizer splits the hyphen and, without the glued form, the resulting bare `amiaza` half of `după-amiaza` collided with `amiaza` the noon landmark and lost to it. Second, Romanian is the only locale among the ones documented on this site where the CLDR chart lists `noapte` twice (once at 00:00 and again at 22:00) because the night band genuinely wraps across midnight. The vocabulary comment notes this is a deliberate join rather than a duplicate entry.

**Ranges** are `între … și …` and `de la … (până) la …`.

**Quarters, ISO weeks, decades, centuries and millennia.** `trimestrul` reads a numbered or ordinal quarter, `săptămâna` an ISO week. The spelled decades `douăzeci`, `treizeci` … `nouăzeci` each ship their own file rather than a shared number grammar, `secol` (century) and `mileniu` (millennium) both resolve, the latter one of 31 locales that ship a dedicated millennium unit.

**Eras.** `d.hr.`/`după hristos`/`dupa hristos` (AD) and `î.hr.`/`i.hr.`/ `înainte de hristos` (BC) both ship spaced and unspaced abbreviation variants. `bp`/`ani înainte de prezent` (before present), `anno mundi` and an "era holocenă/umană" (Holocene/Human Era) marker also resolve, alongside Julian day number and Unix time prefixes.

**The Roman calendar** (kalends, nones and ides) ships both the Latin classical forms (`kalendis`, `nonis`, `idibus`) and Romanian vernacular ones (`calendele`, `nonele`, `idele`), cited to the Romanian Wikipedia article "Calendarul roman", which names all three together: "... calendele, idele și nonele".

**Fuzzy month/period parts** are `început`/`inceput` (early), `mijloc` (mid), `sfârșit`/`sfarsit`/`final` (late).

## Weaker provenance

The weekday names carry stronger provenance than most locales documented here: dexonline and DOOM for Monday to Saturday, and Unicode CLDR 47 for Sunday. The month names cite Unicode CLDR 47, but the seasons, the holiday vocabulary, and the French Republican, Hebrew, Islamic civil and Japanese-regnal calendar month lists do not. These ship as bare transliterations without a cited source.

The clock-direction claim rests on a Romanian-language-learning source (Romania Insider) rather than a linguistic reference grammar. It is independent of the project's own tests and gives worked numeric examples. But a formal grammar citation for the :30 switch point was not located and would strengthen this page.

## What refuses

**A bare quantifier with no direction.** `câțiva ani` alone, with no `acum`, `peste` or similar marker, is a count without a direction and is not expected to resolve to a specific offset, consistent with the general pattern (also documented for Russian) that a quantity needs a marker to become a point in time.

## Open questions for a native speaker

1. Is the :30 switch from `și` to `fără` as clean in ordinary speech as the Romania Insider source states, or do speakers vary near the boundary (`trei și douăzeci și cinci` vs `patru fără douăzeci și cinci`)?
2. Do the French Republican, Hebrew, and Islamic civil month vocabularies need a Romanian-specific citation, or is the bare transliteration what Romanian sources actually use for these calendars?
3. Should `duminică` carry the same dexonline/DOOM citation and an articulated form the way the other six weekdays do, and if the enclitic article genuinely does not attach to `duminică` the way it attaches to `luni`/`lunea`, is that worth a comment recording the reason?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("ro")
    True
    >>> span, rest = extract_timespan('lunea trecută', "ro", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-26T00:00:00', '')
    >>> span, rest = extract_timespan('acum trei zile', "ro", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-24T00:05:00', '')
    >>> span, rest = extract_timespan('trei și un sfert', "ro", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T03:15:00', '')
    >>> span, rest = extract_timespan('nouă și jumătate', "ro", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T09:30:00', '')

## Known limits

Each line is an open issue with a strict `xfail` test for this language. The lines are grouped by topic. An example names the reader that produced it, the language and the anchor date, and shows what that reader gives on the test's own phrase.

- Text that is no date reads as a date, or the wrong reading wins. Example (reader `extract_timespan`, lang `ro`, anchor 2017-06-27 13:04): `mai vorbim` gives 2018-05-01 00:00 to 2018-06-01 00:00 and `vorbim` left over. [#1035](https://github.com/TigreGotico/chronologia/issues/1035)

- `peste o jumătate de oră` gives no span. Example (reader `extract_timespan`, lang `ro`, anchor 2026-01-30 10:00): `peste o jumătate de zi` gives no reading. [#1191](https://github.com/TigreGotico/chronologia/issues/1191)

---
[← Portuguese](pt.md) · [Home](../index.md) · [Russian →](ru.md)
