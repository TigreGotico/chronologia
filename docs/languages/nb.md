# Norwegian Bokmål (`nb`)

<!-- agent-hint
covers: where each construction of the Norwegian Bokmål locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/nb/lang.json, chronologia/locale/nb/*.voc, chronologia/extract/numlayer.py:NUMTAG_LANGS, test/nl_corpus_nb/, test/test_xfail_open_issues_*.py
generated: no
verify: .venv/bin/python -m doctest docs/languages/nb.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/nb.md 'fem over halv ti@09:35' 'kvart på ett@12:30' morgen@06:00 natt@06:00 'om kvelden@20:00' 'ti på halv ti@09:20' && .venv/bin/python -c 'exec("import re,sys\nfrom datetime import datetime\nimport chronologia as C\ndef mins(d):\n    return (\"%.6f\" % (d.total_seconds() / 60)).rstrip(\"0\").rstrip(\".\")\ndef rem(r):\n    return \" and \\x60%s\\x60 left over\" % r if r else \"\"\ndef out(rd, tx, lg, an):\n    f = getattr(C, rd)\n    r = f(tx, lg, anchor=an) if rd == \"extract_duration\" else f(tx, lg, an)\n    if rd == \"extract_timespan\":\n        if r is None: return \"no reading\"\n        return \"%s to %s%s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), r.span.end.datetime().strftime(\"%Y-%m-%d %H:%M\"), rem(r.remainder))\n    if rd == \"extract_duration\":\n        if r is None: return \"no length\"\n        return \"a length of %s min%s\" % (mins(r.duration), rem(r.remainder))\n    if rd == \"extract_event\":\n        if r is None: return \"no event\"\n        return \"start %s, length %s, %s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), \"none\" if r.duration is None else mins(r.duration) + \" min\", \"summary \\x60%s\\x60\" % r.summary if r.summary else \"no summary\")\n    if r is None: return \"no rule\"\n    return \"the rule \\x60%s\\x60%s\" % (r.recurrence.to_string(), rem(r.remainder))\n\np=sys.argv[1]\nt=open(p).read()\nm=re.search(r\"\\n## Known limits\\n(.*?)(?=\\n---\\n|\\Z)\",t,re.S)\nbad=0\nn=0\ntot=0\nfor ln in (m[1].split(\"\\n\") if m else []):\n    if \"Example (\" not in ln: continue\n    tot+=1\n    g=re.search(r\"Example \\(reader \\x60(\\w+)\\x60, lang \\x60([\\w-]+)\\x60, anchor (\\d{4}-\\d\\d-\\d\\d \\d\\d:\\d\\d)\\): \\x60([^\\x60]+)\\x60 gives (.+?)\\. \\[#\\d+\\]\",ln)\n    if not g:\n        bad=1\n        print(\"example line does not parse:\",ln[:80])\n        continue\n    n+=1\n    o=out(g[1],g[4],g[2],datetime.strptime(g[3],\"%Y-%m-%d %H:%M\"))\n    if o!=g[5]:\n        bad=1\n        print(\"limit differs\",g[4],\"|\",g[5],\"|\",o)\nprint(\"known limits checked:\",n,\"of\",tot)\nsys.exit(bad)\n")' docs/languages/nb.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Norwegian Bokmål (`nb`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

Bokmål names the **coming** hour on the half. `halv to` is 01:30, not 02:30, and `halv tolv` is 11:30. Bokmålsordboka states the rule under `halv` as "om klokkeslett: 30 minutter før en hel time", and its own worked example is the one that matters here: `klokka er halv ti, altså 09.30` **or** `21.30`. The dictionary gives the phrase two readings because the hour name is spoken in twelve-hour terms. The clock the phrase lands on is decided by context, not by the words. `bare_half_to` in `lang.json` turns the half on.

The quarters take their direction from the preposition. `over` counts up and `på` counts down, so `kvart over ett` is 01:15 and `kvart på ett` 00:45. Bokmålsordboka carries the same pair under `kvart`: "om klokkeslett: 15 minutter før eller etter en hel time", with `klokka kvart over ett` and `vi må gå kvart på fire` as its examples. Here too the dictionary's hour name is the twelve-hour one. See "The hour before one" below, which is the open decision of this locale.

The numeral matters in the hour slot. `ett` is the neuter of `en` and is the form the clock uses. The article `et` is not a numeral, and the locale does not read it as one. `halv ett` and `kvart på ett` resolve, `halv et` and `kvart på et` return nothing.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('halv to', "nb", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T01:30:00', '')

## What ships

**Weekdays and months** ship wide and abbreviated, cited to Unicode CLDR 47.

**The named days** come from Unicode CLDR 47, `cldr-dates-full/main/nb/dateFields.json`, whose five day relative-type entries are `i forgårs`, `i går`, `i dag`, `i morgen` and `i overmorgen`. Each ships beside a solid-spelled twin (`iforgårs`, `igår`, `idag`, `imorgen`, `iovermorgen`) and the bare `går`, `morgen`, `forgårs` and `overmorgen` ship as well. Those extra forms are not in the cited file.

The bare `morgen` costs something. It is registered as tomorrow, which is what `i morgen` means once the `i` is dropped. But `morgen` alone is also the ordinary word for the morning. A bare `morgen` resolves to tomorrow's whole day.

**The date line** is little-endian with a dotted ordinal day. `den 3. oktober 1990` and the bare `3. oktober 1990` both resolve. `ordinal_dot` is on and Bokmål writes the dotted civil date. `15.06.2020` reads, as does the ISO `2020-06-15`.

**Relative offsets** are `om` forward and `siden` backward, with `for` licensed as a leading before-marker, so both `for tre dager siden` and `tre dager siden` resolve. Units ship in singular and plural: the feminine `uka` beside `uken`, with a separate `unit1_` file each. `halvannen` is registered as the one-and-a-half quantifier. `om halvannen time` is an hour and a half ahead. English Wiktionary carries it as a Bokmål determiner, "one and a half", citing the Bokmål Dictionary.

**Decades** read off `marker_plural`, whose surfaces are `tallet` and `talet`, so `80-tallet` and `1980-tallet` both resolve to the 1980s. The spelled `åttitallet` does not.

**The clock** counts forward with `over` and back with `på`, takes `klokka`, `klokken` or `kl` as its at-marker, and reads `midnatt` and `middag` as the landmark points. The at-marker binds only in front of a *bare* hour: `klokka åtte` reads 08:00, but in `klokka halv to` and `klokka kvart over tre` the time is right and `klokka` is left in the remainder, because the locale declares no order that puts the at-marker in front of a fraction.

A minute count stacked on a half (`fem over halv ti` for 09:35, `ti på halv ti` for 09:20) resolves to 09:30 with `fem over` or `ti på` in the remainder. That is a wrong time, not a refusal.

The numeral `to` is a homograph of the English default range connector `to`, which the range splitter consults in every locale. The split runs before the clock is read. Where a Bokmål `to` sits between two independently resolvable pieces the range wins, so `to om ettermiddagen` returns the afternoon band with `to om` stranded. Most sentences are unaffected (`om to uker`, `de siste to uker` and `mandag klokka to` all read correctly) because a range needs both of its sides to parse on their own.

**No day-part meridiem ships.** This is the largest gap in the locale and it produces wrong times rather than refusals. Bokmål says the twenty-four-hour clock as a twelve-hour hour plus a trailing `om <daypart>`. There is no `clock_meridiem_*` vocabulary here to read it: `klokka åtte om kvelden` returns 08:00 with `om kvelden` in the remainder where a speaker means 20:00, `kvart over tre om ettermiddagen` returns 03:15 rather than 15:15. `klokka elleve om natta` returns 11:00 rather than 23:00. The hour survives, the half of the day is discarded, and the discarded words are visible in the remainder. Danish ships the equivalent vocabulary and reads all three. Ten of the sixty-one locales, Bokmål and Nynorsk among them, ship none.

**Day parts** take their band boundaries from the Unicode CLDR 47 day-period chart. The chart's Bokmål rows carry the period codes with no example words at all (every `nb` cell reads "missing") so the boundaries are read off the Norwegian (`no`) rows, which both written standards share: `natt` from 00:00, `morgen` from 06:00, `formiddag` from 10:00, `ettermiddag` from 12:00 and `kveld` from 18:00. The words are supplied per standard, and `chronologia/ dayparts.py` records that reasoning.

Four of the five bands ship as vocabulary, in the bare and definite forms: `natt`/`natta`/`natten`, `formiddag`/`formiddagen`, `ettermiddag`/`ettermiddagen`, `kveld`/`kvelden`. The `formiddag` is the late morning English cannot name in one word. Bokmålsordboka glosses it as "tid fra morgen til ettermiddag" and "tid mellom frokost og klokka tolv eller middagstid", which is the chart's 10:00-12:00 read loosely.

The `morgen` band is transcribed in `dayparts.py` but ships no vocabulary file, so it is unreachable and `om morgenen` returns nothing. That is the price of the tomorrow-word collision above. Nynorsk and German leave the morning band out as well. Swedish, Dutch, English, Frisian and Icelandic ship one.

A day-part word does bind to a day: `i morgen kveld` is tomorrow evening, `i går kveld` yesterday evening, `mandag kveld` Monday evening. The framed band words resolve on their own too, leaving the framing word in the remainder: `i kveld`, `i natt`, `om ettermiddagen`.

**Ranges** are `fra … til …` and `mellom … og …`, with `siden` opening one that runs to the anchor and `til`/`inntil` closing one that starts there.

**Quarters, ISO weeks and eras.** `første kvartal 2020`, `uke 12`, `44 f.Kr.` and `1990 e.Kr.` resolve, along with a before-present marker and the full deep-time period vocabulary.

**Fuzzy month parts** are `begynnelsen av`, `midten av` and `slutten av`.

**The ordinal-last determiner** is `siste`, so `siste mandag i mai` resolves. Bokmålsordboka gives it as "som kommer til slutt".

## The hour before one

A bare toward-hour phrase for one o'clock names the half hour before one, 00:30 or 12:30. It resolves to whichever of the two comes next after the anchor (ruling 17 in [the rulings](../rulings.md)): `halv ett` is 00:30 at 13:04 and 12:30 at 06:05. `toward_hour_12h` only renames hour 0 as 12 on that path. It changes no bare reading. This locale has no meridiem vocabulary, so `halv ett om ettermiddagen` cannot bind either. `kvart på ett` and `fem på ett` follow the same rule.

## Weaker provenance

The named days carry a precise CLDR locator. But the solid spellings and the bare `går`/`morgen`/`forgårs`/`overmorgen` beside them do not appear in that file and rest on nothing recorded.

The day-part *boundaries* are the CLDR chart, matching the transcription, but taken from the Norwegian rows rather than the Bokmål ones, which are empty. The gloss quoted in the vocabulary headers was checked against Bokmålsordboka and matches.

The clock words, the range markers, the seasons and the holiday vocabulary record no source. The weekday and month names cite Unicode CLDR 47.

## What refuses

**The article as a numeral.** `halv et`, `kvart på et` and `kvart over et` return nothing. Only `ett` reads in the hour slot.

**The dotted timetable clock.** `14.30` and `klokka 14.30` both return nothing, though the colon form `14:30` reads. The tokenizer splits on the dot for the dotted civil date and no timetable-clock reading is attempted.

**The spelled decade.** `åttitallet` returns nothing. The decade construction reads a digit plus a `tallet` surface, not a spelled decade name.

**A bare duration.** `to uker` returns nothing. A quantity with no direction marker is still only a quantity.

**The deictic morning adverb.** `i morges` returns nothing.

**Recurrence from the span edge.** `to ganger i uka` returns nothing. It is a frequency, and the recurrence edge is what answers it.

## Open questions for a native speaker

1. Should `halv ett` and `kvart på ett` read as 12:30 and 12:45? The two branches move together, so the answer has to cover both.

2. Which day-part surfaces should carry a meridiem, and in which forms? This is the change that would let `klokka åtte om kvelden` mean 20:00.

3. Is the `natt` band's AM ceiling at 06:00 right for `om natta`, or does the late evening claim more of it in speech?

4. Should a `morgen` day-part surface ship despite the collision with the tomorrow word?

5. Should `åttitallet` and the other spelled decade names resolve?

6. Is `14.30` the written clock Norwegian readers expect to be understood?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("nb")
    True
    >>> span, rest = extract_timespan('halv to', "nb", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T01:30:00', '')
    >>> span, rest = extract_timespan('halv tolv', "nb", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T11:30:00', '')
    >>> span, rest = extract_timespan('kvart over ett', "nb", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T01:15:00', '')
    >>> span, rest = extract_timespan('klokka åtte', "nb", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T08:00:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('halv et', "nb", anchor) is None
    True
    >>> extract_timespan('kvart på et', "nb", anchor) is None
    True
    >>> extract_timespan('om morgenen', "nb", anchor) is None
    True
    >>> extract_timespan('kvart over et', "nb", anchor) is None
    True
    >>> extract_timespan('14.30', "nb", anchor) is None
    True
    >>> extract_timespan('klokka 14.30', "nb", anchor) is None
    True
    >>> extract_timespan('åttitallet', "nb", anchor) is None
    True
    >>> extract_timespan('to uker', "nb", anchor) is None
    True
    >>> extract_timespan('i morges', "nb", anchor) is None
    True
    >>> extract_timespan('to ganger i uka', "nb", anchor) is None
    True

## Known limits

Each line is an open issue with a strict `xfail` test for this language. The lines are grouped by topic. An example names the reader that produced it, the language and the anchor date, and shows what that reader gives on the test's own phrase.

- A day word with an early, late or part-of-day word gives midnight. Example (reader `extract_timespan`, lang `nb`, anchor 2017-06-27 13:04): `vekk meg i morgen tidlig` gives 2017-06-28 00:00 to 2017-06-29 00:00 and `vekk meg tidlig` left over. [#1033](https://github.com/TigreGotico/chronologia/issues/1033)

- A common word that is no time word reads as a time word. Example (reader `extract_timespan`, lang `nb`, anchor 2017-06-27 13:04): `hei hvordan går det` gives 2017-06-26 00:00 to 2017-06-27 00:00 and `hei hvordan det` left over. [#990](https://github.com/TigreGotico/chronologia/issues/990)

- A morning or evening word that the reader does not join lets a lone clock take the other half of the day. Example (reader `extract_timespan`, lang `nb`, anchor 2017-06-27 13:04): `klokka 8 i kveld` gives 2017-06-28 08:00 to 2017-06-28 08:01 and `i kveld` left over. [#1071](https://github.com/TigreGotico/chronologia/issues/1071)

---
[← Mirandese](mwl.md) · [Home](../index.md) · [Norwegian Nynorsk →](nn.md)
