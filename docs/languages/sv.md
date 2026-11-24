# Swedish (`sv`)

<!-- agent-hint
covers: where each construction of the Swedish locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/sv/lang.json, chronologia/locale/sv/*.voc, chronologia/extract/numlayer.py:NUMTAG_LANGS, test/nl_corpus_sv/, test/test_xfail_open_issues_*.py
generated: no
verify: .venv/bin/python -m doctest docs/languages/sv.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/sv.md && .venv/bin/python -c 'exec("import re,sys\nfrom datetime import datetime\nimport chronologia as C\ndef mins(d):\n    return (\"%.6f\" % (d.total_seconds() / 60)).rstrip(\"0\").rstrip(\".\")\ndef rem(r):\n    return \" and \\x60%s\\x60 left over\" % r if r else \"\"\ndef out(rd, tx, lg, an):\n    f = getattr(C, rd)\n    r = f(tx, lg, anchor=an) if rd == \"extract_duration\" else f(tx, lg, an)\n    if rd == \"extract_timespan\":\n        if r is None: return \"no reading\"\n        return \"%s to %s%s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), r.span.end.datetime().strftime(\"%Y-%m-%d %H:%M\"), rem(r.remainder))\n    if rd == \"extract_duration\":\n        if r is None: return \"no length\"\n        return \"a length of %s min%s\" % (mins(r.duration), rem(r.remainder))\n    if rd == \"extract_event\":\n        if r is None: return \"no event\"\n        return \"start %s, length %s, %s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), \"none\" if r.duration is None else mins(r.duration) + \" min\", \"summary \\x60%s\\x60\" % r.summary if r.summary else \"no summary\")\n    if r is None: return \"no rule\"\n    return \"the rule \\x60%s\\x60%s\" % (r.recurrence.to_string(), rem(r.remainder))\n\np=sys.argv[1]\nt=open(p).read()\nm=re.search(r\"\\n## Known limits\\n(.*?)(?=\\n---\\n|\\Z)\",t,re.S)\nbad=0\nn=0\ntot=0\nfor ln in (m[1].split(\"\\n\") if m else []):\n    if \"Example (\" not in ln: continue\n    tot+=1\n    g=re.search(r\"Example \\(reader \\x60(\\w+)\\x60, lang \\x60([\\w-]+)\\x60, anchor (\\d{4}-\\d\\d-\\d\\d \\d\\d:\\d\\d)\\): \\x60([^\\x60]+)\\x60 gives (.+?)\\. \\[#\\d+\\]\",ln)\n    if not g:\n        bad=1\n        print(\"example line does not parse:\",ln[:80])\n        continue\n    n+=1\n    o=out(g[1],g[4],g[2],datetime.strptime(g[3],\"%Y-%m-%d %H:%M\"))\n    if o!=g[5]:\n        bad=1\n        print(\"limit differs\",g[4],\"|\",g[5],\"|\",o)\nprint(\"known limits checked:\",n,\"of\",tot)\nsys.exit(bad)\n")' docs/languages/sv.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Swedish (`sv`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

The Nordic day has five parts where English has four. The extra one is the `förmiddag`: the late morning, `[10:00, 12:00)`, a band English cannot name in one word. The `morgon` that precedes it is correspondingly short: five hours, `[05:00, 10:00)`, handing over well before noon, and not the six-hour English morning. The rest of the table is `natt` `[00:00, 05:00)`, `eftermiddag` `[12:00, 18:00)` and `kväll` `[18:00, 24:00)`. All five come from the Unicode CLDR 47 day-period chart for `sv`, transcribed in `chronologia/dayparts.py`, with the surfaces cited to *Svensk ordbok utgiven av Svenska Akademien*, which glosses `eftermiddag` as the part of the day between lunchtime and evening.

The other early fact is that the half hour names the coming hour: `halv nio` is 08:30, not 08:00. `bare_half_to` is set for that.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('halv nio', "sv", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T08:30:00', '')

## What ships

**Weekdays and months** ship wide and abbreviated. The vocabulary cites Unicode CLDR 47 for most of them.

**The named days** are the best-cited small vocabulary in the locale: `idag`, `igår`, `imorgon`, `förrgår` and `övermorgon` each name the exact CLDR 47 `dateFields.json` relative-type entry they came from. Each ships both the solid spelling and the spaced one: `i dag`, `i går`, `i morgon`, `i förrgår`, `i övermorgon`.

**The date line** is little-endian with a bare cardinal day and an optional `den`: `den 3 oktober 1990`. `ordinal_dot` is off, and Swedish does not write the dotted civil date. The ISO form `2020-06-15` reads.

**Every day-part word ships in the definite singular beside the bare noun** (`eftermiddagen` next to `eftermiddag`, `kvällen` next to `kväll`) because the definite is the everyday form in `i eftermiddagen` and `under kvällen`. The `å`-less ASCII twins ship too, so `kvall` and `formiddag` match.

**Relative offsets** are `om` forward and `för … sedan` backward, and `lang.json` allows a wide set of orders including a leading `före` for a before-marker and quantifier-first forms. `halvannan` is registered as the one-and-a-half quantifier.

**Units ship in singular and plural** with a separate `unit1_` file each.

**The clock** counts forward with `över` and back with `i` (`kvart över åtta`, `kvart i nio`, `fem över åtta`) with `klockan` as the o'clock word. `midnatt` and `middag` are the landmark points.

**A spoken hour binds to a following day-part phrase as its meridiem.** `åtta på kvällen` reads 20:00. The fractional and relative-minute clock forms carry the same binding: `halv nio på kvällen` reads 20:30, `kvart i nio på kvällen` 20:45, `fem över sju på kvällen` 19:05. `på` is the connector. The five day-part nouns (`morgon`, `förmiddag`, `eftermiddag`, `kväll`, `natt`) double as the meridiem vocabulary, `morgon`/`förmiddag` shifting the AM side and `eftermiddag`/`kväll` the PM side. The shift is a flat twelve-hour move on the spoken 1-11 hour, the same rule the English, Spanish and Portuguese locales apply, not a lookup into the day-part's own CLDR band: the literal hour twelve is the one case where that shows. `tolv på förmiddagen` and `tolv på morgonen` both read as midnight rather than the late-morning noon a native speaker would mean. An hour spoken outside its day-part's own band (`ett på kvällen`, `fem på kvällen`) still takes the flat shift rather than declining. A day-part phrase with no hour in front of it is unaffected and still reads as the whole band.

**Ranges** are `från … till …` and `mellan … och …`, with `sedan` opening one that runs to the anchor and `till` closing one that starts there.

**Quarters, ISO weeks, decades and eras.** `första kvartalet 2020`, `vecka 12`, `80-talet`, `44 f.Kr.` and `1990 e.Kr.` all resolve, along with a before-present marker and the full deep-time period vocabulary.

**Fuzzy month parts** are `början av`, `mitten av` and `slutet av`.

**The ordinal-last determiner** is `sista`, cited to SAOL, so `sista måndagen i maj` resolves.

## Weaker provenance

Only the day parts, the named days and `sista` carry recorded sources. The weekday and month names, the clock words, the range markers, the seasons and the holiday vocabulary record none, which is a thinner citation record than the neighbouring Germanic locales have.

## What refuses

**The deictic day-part adverbs.** `i morse` and `inatt` return nothing. The band words themselves read when framed (`i kväll`, `i eftermiddag`, `på förmiddagen` all resolve) but the fused and suppletive deictic forms are not in the vocabulary.

**The dotted date.** `15.06.2020` returns nothing. Swedish writes the numeric date in the ISO order and `2020-06-15` reads.

**A bare duration.** `två veckor` returns nothing. A quantity with no direction marker is still only a quantity.

## Open questions for a native speaker

1. Should `i morse`, `inatt` and `i går kväll` ship as their own surfaces? `i morse` in particular is not `i morgon` and names the morning just past.
2. Does the `förmiddag` boundary at 10:00 match ordinary use, or does the `morgon` run later in speech than the CLDR table says?
3. Are the clock words and range markers as this locale ships them the standard set, or are there common alternatives missing?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("sv")
    True
    >>> span, rest = extract_timespan('halv nio', "sv", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T08:30:00', '')
    >>> span, rest = extract_timespan('åtta på kvällen', "sv", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T20:00:00', '')
    >>> span, rest = extract_timespan('halv nio på kvällen', "sv", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T20:30:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('i morse', "sv", anchor) is None
    True
    >>> extract_timespan('inatt', "sv", anchor) is None
    True
    >>> extract_timespan('15.06.2020', "sv", anchor) is None
    True
    >>> extract_timespan('två veckor', "sv", anchor) is None
    True

## Known limits

Each line is an open issue with a strict `xfail` test for this language. The lines are grouped by topic. An example names the reader that produced it, the language and the anchor date, and shows what that reader gives on the test's own phrase.

- A morning word loses its second word, and a phrase reads as the morning. Example (reader `extract_timespan`, lang `sv`, anchor 2017-06-27 13:04): `väck mig i morgon bitti` gives 2017-06-28 00:00 to 2017-06-29 00:00 and `väck mig bitti` left over. [#1025](https://github.com/TigreGotico/chronologia/issues/1025)

- The unit word after `and a quarter` or `and a half` stays in the remainder. Example (reader `extract_duration`, lang `sv`, anchor 2017-06-27 13:04): `två timmar och en kvart` gives a length of 135 min and `kvart` left over. [#1240](https://github.com/TigreGotico/chronologia/issues/1240)

- A count of hours or minutes before a holiday gives the day before at 00:00. Example (reader `extract_timespan`, lang `sv`, anchor 2026-09-25 12:00): `en kvart före jul` gives 2026-12-24 00:00 to 2026-12-25 00:00. [#1087](https://github.com/TigreGotico/chronologia/issues/1087)

- `before christmas` ends after Christmas Day, not when it starts. Example (reader `extract_timespan`, lang `sv`, anchor 2026-09-25 12:00): `före jul` gives 2026-09-25 12:00 to 2026-12-26 00:00. [#1097](https://github.com/TigreGotico/chronologia/issues/1097)

- Some number words give no length. Example (reader `extract_duration`, lang `sv`, anchor 2017-06-27 13:04): `starta en 9 minuters timer` gives no length. [#1211](https://github.com/TigreGotico/chronologia/issues/1211)

- The candidate list and the single-span reader disagree on one phrase. [#995](https://github.com/TigreGotico/chronologia/issues/995)

---
[← Swahili](sw.md) · [Home](../index.md) · [Tamil →](ta.md)
