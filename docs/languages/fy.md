# West Frisian (`fy`)

<!-- agent-hint
covers: where each construction of the West Frisian locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/fy/lang.json, chronologia/locale/fy/*.voc, chronologia/extract/numlayer.py:NUMTAG_LANGS, test/nl_corpus_fy/, test/test_xfail_open_issues_*.py
generated: no
verify: .venv/bin/python -m doctest docs/languages/fy.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/fy.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the West Frisian (`fy`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

The half hour names the coming hour. `healwei fiven` is 04:30, not 05:30. The word itself says so: `healwei` is "halfway", the point halfway toward the hour that follows. `bare_half_to` is set for that. The quarter word `kertier` takes its direction from the preposition beside it instead, `oer` counting up from the named hour and `foar` counting down toward it. `kertier oer twa` is 02:15 and `kertier foar trije` is 02:45.

The second governing fact is a collision the vocabulary has to work around. `moarn` is tomorrow and `moarns` is the morning. The two are one word apart, and only the adverbial `moarns` names the day part. The bare noun is left out of the morning band on purpose, and `moarn` resolves to the whole of the following day.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('healwei fiven', "fy", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T04:30:00', '')

## What ships

**Weekdays and months** ship wide and abbreviated, with no recorded source.

**The named days** are `hjoed`, `juster`, `moarn`, `eargister`/`eergister` and `oaremoarn`/`oarmoarn`, none of them carrying a citation. They cannot come from CLDR: the CLDR 47 `dateFields.json` for `fy` has Dutch in the day rows (`gisteren`, `vandaag`, `morgen`, `eergisteren`, `Oermorgen`) so the day names shipped here are the Frisian ones CLDR does not have. `hjoed`, `juster` and `moarn` each have a West Frisian entry on the English Wiktionary. `eargister` and `oaremoarn` have no entry there and rest on no source.

**The date line** is little-endian with a bare cardinal day: `15 juny 2020` resolves, as does `15-06-2020` and the ISO `2020-06-15`. `ordinal_dot` is off and the ordinal instead takes a written suffix, so `de 2e juny` reads.

**Relative offsets** are `oer` forward and `lyn` backward (`oer trije dagen`, `trije dagen lyn`) with the marker allowed on either side of the count and an optional indefinite `in` between.

**The clock** reads `om` as the "at" marker and `oere` as the o'clock word, with `middernacht` and `middei` as the landmark points. `middei` is midday, a point. The afternoon band is `middeis`, and the two are kept apart deliberately.

**The spoken hour takes an inflected form of its own before a fraction.** `ienen`, `twaen`, `trijen`, `fjouweren`, `fiven`, `seizen`, `sânen`, `achten`, `njoggenen`, `tsienen`, `alven` and `tolven` are supplied as a fixed word-to-value map in `chronologia/extract/numlayer_fy.py`, because numtag reads only the uninflected cardinals. Frisian Wikipedia has each form after `healwei` or `kertier` (for example "Haadstjoertiid", "Klaas Koelstra" and "T.S. Eliot"). The uninflected form still reads, so `healwei ien` and `healwei ienen` both land on 00:30.

**Day parts** are `nachts` `[00:00, 06:00)`, `moarns` `[06:00, 12:00)`, `middeis` `[12:00, 18:00)` and `jûns` `[18:00, 24:00)`, transcribed in `chronologia/dayparts.py`. The boundaries are the Dutch ones. CLDR 47 ships no West Frisian day-period row at all. The locale borrows the `nl` row on the grounds that West Frisian is co-official in Fryslân alongside Dutch. The surfaces are cited to the Frisian dictionary material at `gtb.ivdnt.org`.

**Ranges** are `fan … oant …` and `tusken … en …`, with `sûnt` opening one that runs to the anchor and `oant` closing one that starts there.

**Quarters, ISO weeks, eras and fuzzy month parts.** `earste kwartaal fan 2020`, `wike 12`, `44 f.kr.`, `yn 1990`, `begjin juny`, `midden juny` and `ein juny` all resolve, along with the full deep-time period vocabulary and a before-present marker.

## Weaker provenance

Only three surfaces in this locale carry a source that can be read: `yn` and `foarich` cite West Frisian Wiktionary entries. Both entries do carry a West Frisian section, `foarich jier` and `folgjend jier` cite the CLDR 47 `fy` year rows. Those rows do read `foarich jier` and `folgjend jier`. Everything else ships uncited.

The day-part citation is the weakest link that still works. `gtb.ivdnt.org` hosts Frisian dictionaries, the *Wurdboek fan de Fryske taal* among them. But no individual lemma behind that citation is checked. The citation names the source as *Frysk Wurdboek*, which is a different Fryske Akademy work from the *Wurdboek fan de Fryske taal* the portal actually carries. Treat the day-part surfaces as attested by an institution, not by a located entry. `moarns` is the one that can be checked elsewhere: its English Wiktionary entry glosses it "in the morning" and points at the *Wurdboek fan de Fryske taal* for the same word.

`healwei` (the word the whole clock turns on) has no citation and no Wiktionary entry in any language. Frisian Wikipedia carries running-text attestations of the construction rather than a dictionary one: an article on a New Year's custom has `Om healwei ienen Aldjiersnacht is de útbarsting fan de yn de buorren`, which places `healwei ienen` in the small hours and so agrees with the 00:30 the locale returns. A band name, `Trije Minuten Foar Healwei Fiven`, attests `foar` combining with `healwei`. Frisian Wikipedia also has an article titled *Healwei*, and that one is a hamlet on Terschelling and is not evidence about the clock.

## The half hour toward one

A bare toward-hour phrase for one o'clock names the half hour before one, 00:30 or 12:30. It resolves to whichever of the two comes next after the anchor (ruling 17 in [the rulings](../rulings.md)): `healwei ienen` is 00:30 at 13:04 and 12:30 at 06:05. `toward_hour_12h` only renames hour 0 as 12 on that path. It changes no bare reading. This locale binds no meridiem word (see the refusals below). A following day-part word does not change the reading. `kertier foar ienen` and `fiif foar ienen` follow the same rule.

## What refuses

**Any day-part word after a clock time.** `acht oere jûns` returns 08:00 and leaves `jûns` in the remainder. `healwei acht jûns` returns 07:30 and leaves `jûns`. The band words resolve perfectly well on their own (`jûns` alone is 18:00 to midnight) but nothing binds one to a preceding hour as a meridiem. Every evening time in this locale comes back as its morning twin with the evening word stranded beside it. This is the locale's largest gap and the reason the half-hour question above has no workaround.

**The dotted civil date.** `15.06.2020` returns nothing. `dotted_date` is off for this locale and the hyphenated and ISO forms are what read.

**A bare duration.** `trije wiken` and `fjirtjin dagen` return nothing. A quantity with no direction marker is still only a quantity.

**A recurrence.** `eltse moandei` returns the next single Monday and leaves `eltse` in the remainder, `eltse dei` and `deistich` return nothing. The "every" and frequency words ship but no construction reads them.

**`no` as a present-time word.** It is listed in `marker_present.voc` and resolves to nothing on its own.

**Fused today-plus-band words.** `fanjûn` and `fannacht` return nothing. Dutch ships its equivalents as their own surfaces, Frisian does not.

**A four-digit clock.** `14.30` and `om 14.30 oere` return nothing.

## Known defects

Each of these returns a wrong or partial answer rather than nothing, which is worse than a refusal.

`acht oere jûns` → 08:00 with remainder `jûns`. The meridiem gap, stated above.

`om healwei ienen` → 00:30 with remainder `om`. The "at" marker is read before a bare or spelled hour but not before a fraction. The one construction Frisian Wikipedia attests verbatim does not fully parse.

`fan moandei` → the whole of the following Monday with remainder `fan`. An open range that starts at a weekday is not read, and the marker is dropped silently.

`de 15e fan juny` → 15 June with remainder `de`. The article is not consumed before an ordinal day.

`oer healwei twa` → 01:30 with remainder `oer`. The forward-offset marker is stranded in front of a clock time instead of refusing.

## Open questions for a native speaker

1. Said in the middle of the afternoon, does `healwei ienen` mean 00:30 or 12:30, and is one of the two clearly the ordinary reading?
2. What is the connector that binds a day part to a spoken hour, and which day-part forms take it?
3. Are `eargister` and `oaremoarn` the ordinary words for the day before yesterday and the day after tomorrow, and are there other spellings?
4. Is the inflected hour set (`ienen`, `twaen`, …) complete and correct, and does it appear anywhere but before a fraction?
5. Are there fused today-plus-band words on the Dutch model?
6. Does the Dutch day-period table match Frisian use, or do the bands sit differently?

## Known limits

Each line is an open issue with a strict `xfail` test for this language. The most common cases come first. An example shows what the library gives on the test's own anchor date.

- A day-part word after a clock time does not move the hour. Example: `om 8 oere jûns` gives 2026-01-31 08:00, where the test expects 2026-01-30 20:00. [#1220](https://github.com/TigreGotico/chronologia/issues/1220)

- A spelled hour reads as 20 hours, not 24. Example: `fjouwer en tweintich oeren lyn` gives 2026-01-29 14:00, where the test expects 2026-01-29 10:00. [#1226](https://github.com/TigreGotico/chronologia/issues/1226)

- A lone digit suffix reads as an ordinal ending. Example: `om 8 te begjinnen` gives begjinnen, where the test expects 'te begjinnen'      - te begjinnen   ? ---. [#1228](https://github.com/TigreGotico/chronologia/issues/1228)

- Text that is no date reads as a date, or the wrong reading wins. Example: `february 30 2020` gives the year 2020 with `february 30` left over, where the test expects no date. [#1035](https://github.com/TigreGotico/chronologia/issues/1035)

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("fy")
    True
    >>> span, rest = extract_timespan('healwei fiven', "fy", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T04:30:00', '')
    >>> span, rest = extract_timespan('kertier oer twa', "fy", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T02:15:00', '')
    >>> span, rest = extract_timespan('kertier foar trije', "fy", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T02:45:00', '')
    >>> span, rest = extract_timespan('healwei ienen', "fy", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T00:30:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('15.06.2020', "fy", anchor) is None
    True
    >>> extract_timespan('trije wiken', "fy", anchor) is None
    True
    >>> extract_timespan('fjirtjin dagen', "fy", anchor) is None
    True
    >>> extract_timespan('eltse dei', "fy", anchor) is None
    True
    >>> extract_timespan('deistich', "fy", anchor) is None
    True
    >>> extract_timespan('fanjûn', "fy", anchor) is None
    True
    >>> extract_timespan('fannacht', "fy", anchor) is None
    True
    >>> extract_timespan('14.30', "fy", anchor) is None
    True
    >>> extract_timespan('om 14.30 oere', "fy", anchor) is None
    True

---
[← Welsh](cy.md) · [Home](../index.md)
