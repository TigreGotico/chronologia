# Dutch (`nl`)

<!-- agent-hint
covers: where each construction of the Dutch locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/nl/lang.json, chronologia/locale/nl/*.voc, chronologia/extract/numlayer.py:NUMTAG_LANGS, test/nl_corpus_nl/, test/test_xfail_open_issues_*.py
generated: no
verify: .venv/bin/python -m doctest docs/languages/nl.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/nl.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Dutch (`nl`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

`'s nachts` is a band that crosses midnight. That single fact governs how Dutch clock times land. `drie uur 's nachts` is 03:00, `elf uur 's nachts` is 23:00, and `twaalf uur 's nachts` is midnight. It is not a twelve-hour shift and it is not an AM half. The small hours one to five stay AM.

The late hours six to eleven are PM. Twelve is midnight. The AM ceiling follows the CLDR `nacht` band for Dutch, `[00:00, 06:00)`. The other three postposed day-part words behave straightforwardly: `'s ochtends` and `'s morgens` keep a bare twelve-hour reading in the AM half, `'s middags` and `'s avonds` push it into the PM half.

The `'s` itself is a fossilised genitive particle, from `des`. The tokenizer strips the apostrophe, so what reaches the grammar is a bare `s`, and the clock orders consume it optionally before the day-part word.

The half hour names the coming hour, as in German: `half acht` is 07:30.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan("drie uur 's nachts", "nl", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T03:00:00', '')

## What ships

**Weekdays and months** ship wide and abbreviated, with no recorded source.

**The date line** is little-endian, and Dutch is one of the languages that writes the dotted civil date. `15.06.2020` reads, as does `15-06-2020`. `ordinal_dot` is off.

**Relative offsets** are `over` forward and `geleden` backward, with the marker allowed on either side of the count and an optional indefinite article between.

**A quarter of an hour is a unit of its own.** `kwartier` is not a clock fraction in Dutch but a countable noun. It ships with its diminutive `kwartiertje` and both plurals. `over een kwartier` resolves to a fifteen-minute span a quarter of an hour ahead.

**The clock** counts forward with `over` and back with `voor` (`kwart over acht`, `kwart voor negen`) and the bare half names the coming hour. `middernacht` is midnight and `middag` is noon. `uur` is the o'clock word.

**Day parts** take their boundaries from the Unicode CLDR 47 day-period chart for `nl`, transcribed in `chronologia/dayparts.py`: `nacht` `[00:00, 06:00)`, `ochtend` `[06:00, 12:00)`, `middag` `[12:00, 18:00)`, `avond` `[18:00, 24:00)`. The surfaces are cited to the Algemeen Nederlands Woordenboek at the Instituut voor de Nederlandse Taal. The `avond` runs to midnight and the `nacht` takes over after it.

Dutch has a fused today-plus-band word for each band. `vanavond`, `vanochtend`, `vannacht` and `vanmorgen` ship as their own surfaces. They already name today's band, so they do not compose with the clock's future-roll rule. `vanmorgen` is the one worth explaining. It is a synonym of `vanochtend` that the ANW carries as its own entry. The `morgen` inside it is the older Dutch word for the morning itself, as in `goedemorgen`: not the `morgen` that means tomorrow everywhere else in this locale. The two never compete, because `vanmorgen` is a single fused token and not a split `van` plus `morgen`.

**Ranges** are `van … tot …` and `tussen … en …`, with `sinds` opening one that runs to the anchor and `tot` closing one that starts there.

**Quarters, ISO weeks and eras.** `het eerste kwartaal van 2020`, `week 12` and `44 v.Chr.` all resolve, along with an AD marker and a before-present marker.

**The Roman calendar anchors** ship in their Dutch vernacular forms `kalenden`, `nonen` and `iden`, cited to the Dutch Wikipedia articles on the Nones and the Ides, so `de iden van maart` resolves.

**The ordinal-last determiner** is `laatste`, the invariant attributive superlative of `laat`, cited to Van Dale, so `de laatste zaterdag van augustus` resolves.

## Weaker provenance

The Roman anchors rest on Wikipedia articles rather than on the ANW or Van Dale that the rest of the locale draws on.

The weekday and month names, the seasons and the holiday vocabulary carry no recorded source.

## What refuses

**The `middag` band as a day part.** `vanmiddag` returns nothing. `deze middag` resolves the noon point rather than the afternoon band, leaving `deze` in the remainder. The word `middag` is bound as the noon landmark, so the band it also names has no vocabulary of its own. The same collision German has between `Mittag` the hour and `Mittag` the point.

**A bare duration.** `twee weken` and `een kwartier` return nothing on their own. A quantity with no direction marker is still only a quantity. With one, `over een kwartier` reads.

**Recurrence.** `om de twee weken` returns nothing from the span edge. The `om de` frame is registered as a recurrence marker, and it is the recurrence edge that answers it.

## Open questions for a native speaker

1. How should the afternoon band be reachable at all, given that `middag` is also the noon point? `vanmiddag` and `'s middags` are ordinary Dutch and neither of them reads.
2. Is `half juni` the ordinary way to say mid-June? It resolves the whole month with `half` unread, because the mid-month part words are `midden` and `medio`.
3. Should the uninflected `komend` join `komende` as a "next" determiner? `komend weekend` leaves `komend` unread.
4. Are `kalenden`, `nonen` and `iden` the forms Dutch historical writing uses?

## Known limits

Each line is an open issue with a strict `xfail` test for this language. The most common cases come first. An example shows what the library gives on the test's own anchor date.

**Clocks and parts of the day**

- Some day-part words are not read, and a clock gives an eight-hour length. Example: `laat me vanmiddag weten dat ik de loodgieter moet bellen` gives no reading. [#1022](https://github.com/TigreGotico/chronologia/issues/1022)

- An evening word before the clock does not read as one time. Example: `vandaag 's avonds om 8:00` gives 2017-06-27 00:00, where the test expects 2017-06-27 20:00. [#1134](https://github.com/TigreGotico/chronologia/issues/1134)

- A date built from two parts loses one of them. Example: `binnen 3 uur` gives 2017-06-27 15:00, where the test expects 2017-06-27 16:04. [#1034](https://github.com/TigreGotico/chronologia/issues/1034)

- A clock with a dot between hour and minute gives no time. Example: `om 8.30` gives no reading. [#1047](https://github.com/TigreGotico/chronologia/issues/1047)

- The minutes after an alarm hour are dropped. [#1058](https://github.com/TigreGotico/chronologia/issues/1058)

- An evening word after `vandaag` gives the morning hour. Example: `om 8:00 vandaag 's avonds` gives 2017-06-27 08:00 with `s avonds` left over, where the test expects the evening hour. [#1081](https://github.com/TigreGotico/chronologia/issues/1081)

- A counted offset reads wrong. Example: `-1 uur` gives 01:00 tomorrow, where the test expects one hour earlier. [#1202](https://github.com/TigreGotico/chronologia/issues/1202)

- The meridiem after an abbreviated hour word is lost. Example: `om 8 u. 's avonds` gives 2026-11-23 08:00, where the test expects 2026-11-23 20:00. [#1312](https://github.com/TigreGotico/chronologia/issues/1312)

**Dates, ranges and weeks**

- The indefinite article before a day of a month reads as the first day. Example: `een dag van maart` gives 2027-03-02 00:00, where the test expects 2027-04-01 00:00. [#1306](https://github.com/TigreGotico/chronologia/issues/1306)

**Offsets, lengths and holidays**

- Text that is no date reads as a date, or the wrong reading wins. Example: `morgen om 8 of 9 mensen` gives 2026-10-18 08:00, where the test expects 2026-10-18 00:00. [#1035](https://github.com/TigreGotico/chronologia/issues/1035)

**Recurrence**

- A weekday or clock range in a recurrence loses its end. Example: `elke maandag tot en met vrijdag` gives `FREQ=WEEKLY;UNTIL=20261127T000000;BYDAY=MO`, where `elke maandag t/m vrijdag` gives `FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR`. [#1321](https://github.com/TigreGotico/chronologia/issues/1321)

**Events, zones, business days and the API**

- A clock preposition, a count of hours or a date word leaves the part of the day in the event summary. Example: `om twee uur in de middag morgen` gives 2026-01-30 14:00, where the test expects 2026-01-31 14:00. [#1060](https://github.com/TigreGotico/chronologia/issues/1060)

- `five minutes past the hour` adds an hour. Example: `vijf minuten na het uur` gives 65 min, where the test expects 5 min. [#1206](https://github.com/TigreGotico/chronologia/issues/1206)

- The event summary keeps the article and the day word before a day number. Example: `vergadering op de dag 5 december` gives vergadering op de dag, where the test expects 'vergadering'      - vergadering. [#1218](https://github.com/TigreGotico/chronologia/issues/1218)

- A bare clock with a zone skips the 12-hour rule. Example: `voor 9:30 utc` gives 2017-06-28 09:31 UTC, where the test expects 2017-06-27 21:31 UTC. [#1254](https://github.com/TigreGotico/chronologia/issues/1254)

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("nl")
    True
    >>> span, rest = extract_timespan("drie uur 's nachts", "nl", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T03:00:00', '')
    >>> span, rest = extract_timespan("elf uur 's nachts", "nl", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T23:00:00', '')
    >>> span, rest = extract_timespan('half acht', "nl", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T07:30:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('vanmiddag', "nl", anchor) is None
    True
    >>> extract_timespan('twee weken', "nl", anchor) is None
    True
    >>> extract_timespan('een kwartier', "nl", anchor) is None
    True
    >>> extract_timespan('om de twee weken', "nl", anchor) is None
    True

---
[← Danish](da.md) · [Home](../index.md) · [English →](en.md)
