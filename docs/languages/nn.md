# Norwegian Nynorsk (`nn`)

<!-- agent-hint
covers: where each construction of the Norwegian Nynorsk locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/nn/lang.json, chronologia/locale/nn/*.voc, chronologia/extract/numlayer.py:NUMTAG_LANGS, test/nl_corpus_nn/, test/test_xfail_open_issues_*.py
generated: no
verify: .venv/bin/python -m doctest docs/languages/nn.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/nn.md nn@00:00 && .venv/bin/python -c 'exec("import re,sys\nfrom datetime import datetime\nimport chronologia as C\ndef mins(d):\n    return (\"%.6f\" % (d.total_seconds() / 60)).rstrip(\"0\").rstrip(\".\")\ndef rem(r):\n    return \" and \\x60%s\\x60 left over\" % r if r else \"\"\ndef out(rd, tx, lg, an):\n    f = getattr(C, rd)\n    r = f(tx, lg, anchor=an) if rd == \"extract_duration\" else f(tx, lg, an)\n    if rd == \"extract_timespan\":\n        if r is None: return \"no reading\"\n        return \"%s to %s%s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), r.span.end.datetime().strftime(\"%Y-%m-%d %H:%M\"), rem(r.remainder))\n    if rd == \"extract_duration\":\n        if r is None: return \"no length\"\n        return \"a length of %s min%s\" % (mins(r.duration), rem(r.remainder))\n    if rd == \"extract_event\":\n        if r is None: return \"no event\"\n        return \"start %s, length %s, %s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), \"none\" if r.duration is None else mins(r.duration) + \" min\", \"summary \\x60%s\\x60\" % r.summary if r.summary else \"no summary\")\n    if r is None: return \"no rule\"\n    return \"the rule \\x60%s\\x60%s\" % (r.recurrence.to_string(), rem(r.remainder))\n\np=sys.argv[1]\nt=open(p).read()\nm=re.search(r\"\\n## Known limits\\n(.*?)(?=\\n---\\n|\\Z)\",t,re.S)\nbad=0\nn=0\ntot=0\nfor ln in (m[1].split(\"\\n\") if m else []):\n    if \"Example (\" not in ln: continue\n    tot+=1\n    g=re.search(r\"Example \\(reader \\x60(\\w+)\\x60, lang \\x60([\\w-]+)\\x60, anchor (\\d{4}-\\d\\d-\\d\\d \\d\\d:\\d\\d)\\): \\x60([^\\x60]+)\\x60 gives (.+?)\\. \\[#\\d+\\]\",ln)\n    if not g:\n        bad=1\n        print(\"example line does not parse:\",ln[:80])\n        continue\n    n+=1\n    o=out(g[1],g[4],g[2],datetime.strptime(g[3],\"%Y-%m-%d %H:%M\"))\n    if o!=g[5]:\n        bad=1\n        print(\"limit differs\",g[4],\"|\",g[5],\"|\",o)\nprint(\"known limits checked:\",n,\"of\",tot)\nsys.exit(bad)\n")' docs/languages/nn.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Norwegian Nynorsk (`nn`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

The half hour names the coming hour: `halv to` is 01:30, not 02:30. `bare_half_to` is set for that. The quarter takes its direction from the word beside it, `over` counting up from the named hour and `på` counting down toward it. `kvart over to` is 02:15 and `kvart på tre` is 02:45.

The fact that shapes everything else is a pair of collisions in the day vocabulary. `i morgon` is tomorrow and `morgon` is the morning. `i går` is yesterday while `går` is what the verb *å gå* does in the present tense. This locale ships the bare halves of both pairs as day names, and both collisions fire.

Nynorsk shares its written month names, most of its clock words and its numeral system with Bokmål. A locale assembled carelessly reads as Bokmål with a few words changed. This one does not: the weekdays are `måndag`, `laurdag` and `sundag` rather than the Bokmål `mandag`, `lørdag` and `søndag`. The units are `månad`, `veke` and `time`.

The determiners are `førre` and `komande`. The one-and-a-half quantifier is `halvannan`. The season is `sommar`. The two Bokmål forms that did get in are named under weaker provenance below.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('halv to', "nn", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T01:30:00', '')

## What ships

**Weekdays and months** ship wide and abbreviated. The vocabulary cites Unicode CLDR 47 for most of them.

**The named days** cite CLDR 47 `dateFields.json` for `nn`. The citation holds exactly: the day rows there read `i førgår`, `i går`, `i dag`, `i morgon` and `i overmorgon`. All five of those surfaces ship and resolve cleanly. What CLDR does not carry is the nine additional surfaces shipped beside them: `idag`, `igår`, `går`, `imorgon`, `morgon`, `forgårs`, `iforgårs`, `overmorgon` and `iovermorgon`. Those are uncited, and two of them cause the defects listed below.

**The date line** is little-endian and Nynorsk writes the dotted civil date. `15.06.2020` reads, as do `15-06-2020` and the ISO `2020-06-15`. `ordinal_dot` is on and the dotted ordinal day is the ordinary written form: `15. juni 2020`. Spelled ordinals read too (`fyrste juni`, `andre juni`, `tjueandre juni`) and the locale supplies its own `calendar_date` orders rather than the shared ones.

**Relative offsets** are `om` forward and `sidan` backward, with `for` optional in front of a backward count: `om tre dagar`, `for tre dagar sidan`. `halvannan` works as the one-and-a-half quantifier in both directions.

**The clock** reads `klokka` or `kl` as the "at" marker, with `midnatt` and `middag` as the landmark points. `kl 14` reads as a bare 24-hour hour.

**The meridiem after a clock.** A day-part word after the hour fixes its half of the day. The phrases `klokka åtte om kvelden` and `klokka åtte i kveld` read 20:00. The phrase `klokka seks om morgonen` reads 06:00. The file `clock_meridiem_am.voc` lists `morgonen`, `føremiddagen` and `formiddagen`.

The file `clock_meridiem_pm.voc` lists `ettermiddagen`, `ettermiddag`, `kvelden` and `kveld`. Each comes from a Nynorskordboka example such as "klokka sju om morgonen" or "om kvelden i dag". The bare `morgon` stays out of both lists because it also names tomorrow. The clock orders take `om` or `i` between the hour and the word.

**Day parts** are `natt` `[00:00, 06:00)`, `føremiddag` `[10:00, 12:00)`, `ettermiddag` `[12:00, 18:00)` and `kveld` `[18:00, 24:00)`, transcribed in `chronologia/dayparts.py`, each in the bare and the definite form. The five-part Nordic day is why `føremiddag` exists. It is the late morning that English cannot name in one word. The `morgon` that precedes it is correspondingly short.

The boundaries come from the CLDR 47 supplemental day-period chart. The chart does carry an `nn` row. It gives exactly these boundaries (00:00, 06:00, 10:00, 12:00, 18:00) but every surface name in that row is marked missing. The Bokmål `nb` row is identical in both respects.

The names live only in the generic Norwegian `no` row, and they are Bokmål: `morgen`, `formiddag`, `ettermiddag`, `kveld`. The boundaries this locale uses are therefore its own row's whether they are read from `no` or from `nn`. Only the names would have been Bokmål had they been taken from the chart, and they were not. They come from Nynorskordboka instead.

That citation checks out. The Nynorskordboka entry for `føremiddag` at `ord.uib.no` glosses it *tid frå morgon til ettermiddag* and *periode frå frukost til klokka tolv eller middagstid*, which is the 10:00-to-noon band the locale ships. It gives `føremiddagen` as the definite singular. The vocabulary files quote that gloss with the Norwegian vowels transliterated to ASCII, so `frå` appears there as `fra`. That is the same transliteration the file headers apply to `Språkrådet`, not a Bokmål reading of the source.

**Ranges** are `frå … til …` and `mellom … og …`, with `sidan` opening one that runs to the anchor and `til` closing one that starts there.

**Quarters, ISO weeks, decades and eras.** `fyrste kvartal 2020`, `veke 12`, `80-talet`, `44 f.kr.` and an AD marker all resolve, along with a before-present marker and the full deep-time period vocabulary.

**Fuzzy month parts** are `byrjinga av`, `midten av` and `slutten av`.

**The ordinal-last determiner** is `siste`, cited to Nynorskordboka, so `siste måndag i mai` resolves. The dictionary carries `siste` as an inflected form of the lemma `sist`.

## Weaker provenance

Two Bokmål forms ship. `tallet` sits beside the Nynorsk `talet` in the decade-marker vocabulary. `80-tallet` resolves in a Nynorsk locale. `formiddag` and `formiddagen` sit beside `føremiddag` and `føremiddagen`. Both are the kind of surface a Nynorsk writer might actually type, and neither does any harm, but neither is Nynorsk and neither is cited.

Outside the weekday and month names, the day parts, the named days, `siste`, the second and the clock and date lead words, nothing in this locale records a source. The clock words, the range markers, the seasons and the numeral vocabulary carry none.

## The half hour toward one

A bare toward-hour phrase for one o'clock names the half hour before one, 00:30 or 12:30. It resolves to whichever of the two comes next after the anchor (ruling 17 in [the rulings](../rulings.md)): `halv eitt` is 00:30 at 13:04 and 12:30 at 06:05. `toward_hour_12h` only renames hour 0 as 12 on that path. It changes no bare reading. The fraction orders take no meridiem word, so `halv eitt om ettermiddagen` returns 00:30 and leaves `om ettermiddagen` in the remainder. `kvart på eitt` and `fem på eitt` follow the same rule.

## What refuses

**A day-part word after a fraction or a night hour.** `halv åtte om kvelden` returns 07:30 and leaves `om kvelden`. `klokka elleve om natta` returns 11:00 and leaves `om natta`. The band words resolve on their own (`kvelden` alone is 18:00 to midnight). But the fraction orders bind no meridiem, and the night word is on no meridiem list. Such a time comes back as its morning twin with the day-part word stranded.

**The morning band.** `morgonen` returns nothing. `chronologia/dayparts.py` declares a `morgon` band at `[06:00, 10:00)` for this locale. But no vocabulary file supplies its surfaces, so the band is unreachable. The tomorrow vocabulary claims the bare `morgon` instead.

**A bare duration.** `tre veker` and `14 dagar` return nothing. A quantity with no direction marker is still only a quantity.

**A recurrence.** `kvar dag` and `dagleg` return nothing. The "every" and frequency words ship but no construction reads them.

**A spelled half or quarter of an hour.** `om ein halv time` and `om eit kvarter` return nothing, although `om halvannan time` reads.

**A forward-looking "after".** `etter måndag` returns nothing.

**A four-digit clock.** `14.30` and `klokka 14.30` return nothing. The dotted form reads as a date, not a time.

## Known defects

Each returns a wrong or partial answer rather than nothing.

`eg går til butikken` ("I walk to the shop") → 26 June, yesterday, with remainder `eg til butikken`. The bare `går` ships as a yesterday surface, and it is also the present tense of *å gå*, one of the commonest verbs in the language. CLDR gives `i går` and only `i går`.

`god morgon` → 28 June, tomorrow, with remainder `god`. `måndag morgon` returns Monday and strands `morgon`. The bare `morgon` ships as a tomorrow surface. In Nynorsk it is also, and more basically, the morning. CLDR gives `i morgon`.

`tolv om natta` → the night band 00:00 to 06:00 of the anchor day, with remainder `tolv om`. The hour is dropped and a six-hour band is returned in place of a point in time.

`halv åtte om kvelden` → 07:30 with remainder `om kvelden`. The meridiem gap of the fraction orders.

`i forgårs` → 25 June with remainder `i`. The vocabulary ships `forgårs` and `i førgår` but not `i forgårs`, so the commonest spelling of the phrase parses with its preposition stranded. `i førgår` parses clean.

`i natt`, `i kveld`, `i helgi`, `i juni` and `i 1990` all return the right span with `i` in the remainder. `under juni` strands `under`. `frå måndag` returns the whole of the following Monday and strands `frå`. An open range starting at a weekday is silently reduced to that weekday.

`kvar måndag` → the next single Monday with remainder `kvar`.

## Open questions for a native speaker

1. Said in the middle of the afternoon, does `halv eitt` mean 00:30 or 12:30, and is one of the two clearly the ordinary reading?
2. What is the connector that binds a day part to a spoken hour, and which day-part forms take it?
3. Should the bare `går` and `morgon` be day names at all, given the verb and the noun they collide with?
4. What are the ordinary surfaces for the morning band, and does the 10:00 boundary with `føremiddag` match how the words are used?
5. Is `helgi` current beside `helga`, and is `weekend` written in Nynorsk?
6. Which of `fjerdedel` and `kvart` is the ordinary quarter-of-an-hour word?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("nn")
    True
    >>> span, rest = extract_timespan('halv to', "nn", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T01:30:00', '')
    >>> span, rest = extract_timespan('kvart over to', "nn", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T02:15:00', '')
    >>> span, rest = extract_timespan('kvart på tre', "nn", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T02:45:00', '')
    >>> span, rest = extract_timespan('kvelden', "nn", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T18:00:00', '')
    >>> span, rest = extract_timespan('klokka åtte om kvelden', "nn", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T20:00:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('morgonen', "nn", anchor) is None
    True
    >>> extract_timespan('tre veker', "nn", anchor) is None
    True
    >>> extract_timespan('14 dagar', "nn", anchor) is None
    True
    >>> extract_timespan('kvar dag', "nn", anchor) is None
    True
    >>> extract_timespan('dagleg', "nn", anchor) is None
    True
    >>> extract_timespan('om ein halv time', "nn", anchor) is None
    True
    >>> extract_timespan('om eit kvarter', "nn", anchor) is None
    True
    >>> extract_timespan('etter måndag', "nn", anchor) is None
    True
    >>> extract_timespan('14.30', "nn", anchor) is None
    True
    >>> extract_timespan('klokka 14.30', "nn", anchor) is None
    True

## Known limits

Each line is an open issue with a strict `xfail` test for this language. The lines are grouped by topic. An example names the reader that produced it, the language and the anchor date, and shows what that reader gives on the test's own phrase.

- A common word that is no time word reads as a time word. Example (reader `extract_timespan`, lang `nn`, anchor 2017-06-27 13:04): `hei korleis går det` gives 2017-06-26 00:00 to 2017-06-27 00:00 and `hei korleis det` left over. [#990](https://github.com/TigreGotico/chronologia/issues/990)

---
[← Norwegian Bokmål](nb.md) · [Home](../index.md) · [Occitan →](oc.md)
