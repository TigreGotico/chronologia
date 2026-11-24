# Swahili (`sw`)

<!-- agent-hint
covers: where each construction of the Swahili locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/sw/lang.json, chronologia/locale/sw/*.voc, chronologia/extract/numfold_bantu.py, test/nl_corpus_sw/
generated: no
verify: .venv/bin/python -m doctest docs/languages/sw.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/sw.md 'Taarifa ya Habari saa saba Mchana@13:00'
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Swahili (`sw`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by its own `numfold_bantu` module in `chronologia/extract/`.

Swahili has a clock this library will not read, and that is the single most important thing on this page. `saa tatu` returns nothing.

Swahili counts the hours of the day from sunrise. `Saa moja` is seven in the morning, `saa sita` is noon. Every reading is the Western hour minus six. That convention is alive in written prose, not only in speech: East African broadcasters title their own bulletins with it, publishing `Taarifa ya Habari saa saba Mchana` for a programme that airs at 13:00. But the Western reading is alive in written Swahili too, fixture tables and viewing guides for international sport, syndicated with time-zone-sensitive digital times, use 24-hour notation and never the sunrise count. The same string means two things six hours apart, and the genre that the reader already knows decides which one it means, not anything in the phrase.

Every wrong guess would be wrong by exactly six hours, which is the difference between breakfast and lunch, or between an evening and a small-hours appointment. So the locale reads the digital literal, which is unambiguous, and refuses the spoken hour outright.

The refusal is narrow on purpose. `saa` is also the noun for an hour of duration, and CLDR's own relative-time strings are built on it: `saa {0} zilizopita` is N hours ago. Those keep working.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('saa {0} zilizopita', "sw", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T00:05:00', '')

## What ships

**Weekdays** come from CLDR 47, `cldr-dates-full/main/sw/ca-gregorian.json`, where the abbreviated forms are the same strings as the wide ones. The `Juma-` series counts from Saturday. The numeral inside a name is two short of the Monday-first index the vocabulary files are numbered by: `Jumatatu` is `juma` + `tatu` (three), the third day of the cycle. `Jumapili` is `juma` + `pili` (two), which is why Sunday rather than Monday is the day whose name carries the numeral two. The locale's week starts on Saturday accordingly.

**Months** are the CLDR wide and abbreviated names from the same file.

**Relative offsets** work by noun-class agreement rather than by a separate "ago" word. CLDR's past pattern is the unit noun, the count, and an agreeing relative pronoun: `miaka {0} iliyopita` for N years ago, `wiki {0} zilizopita` for N weeks. That is the same pronoun the bare "last week" phrase uses, so in Swahili the marker that says "last week" says "N weeks ago" as well. The future is `baada ya`, literally "after", the same preposition that introduces a plain succession.

The relative pronoun agrees with the noun class of the unit it follows: `mwaka uliopita` and `mwezi uliopita` take the class 3/4 form, while `wiki iliyopita` and every weekday (`Jumatatu iliyopita`) take class 9/10. `zilizopita` is the class 9/10 plural CLDR counts with above one. All three ship together, because a marker slot is matched by surface: the noun the writer already chose decides which one is grammatical. A writer who chose correctly must be read.

**Day parts** take their bands from the CLDR 47 day-period rules for `sw`, transcribed in `chronologia/dayparts.py`: `alfajiri` 04:00-07:00, `asubuhi` 07:00-12:00, `mchana` 12:00-16:00, `jioni` 16:00-19:00, `usiku` 19:00-04:00. A bare band still answers (`usiku` names the night) because a band names no hour.

**Ranges** open with `kutoka` or `tangu` and close with `hadi` or `mpaka`. `kati ya X na Y` is the between frame, with `na` joining the bounds.

**Numerals** come from Wiktionary's `Module:number_list/data/sw`, `na` joins a tens word to its unit, as in `ishirini na tano` for twenty-five.

## What refuses

A test pins each refusal.

**The spoken hour**, as above. Every shape of `saa N` as a time of day is refused, in both conventions' worth of hours.

**A counted `saa` beside a day-part word.** `saa moja asubuhi` names one hour inside the morning. Returning the whole 07:00-12:00 morning band would hand a caller who asked for an hour a five-hour span, with the hour they asked about dropped into the remainder. The counted `saa` vetoes the band as well. Declining the band is not the same as asserting either clock reading, which stays unavailable.

**Century, millennium and decade.** `karne`, `milenia` and `muongo` are real nouns and their classes are known. Their counted forms follow from the productive concord rule. But a rule is not an attestation: no source consulted shows any of the three actually counted in running text. This library's scope units are read from real usage rather than derived. All three stay out, and the locale's units are exactly the seven CLDR counts, second, minute, hour, day, week, month, year.

**`juma` as a week.** It is class 5/6 and it is the other word for a week. The word inside every `Juma-` weekday name. Its class has no entry in CLDR's relative-time data and no attested last/this/next form was found. The mechanical `ma-` concord guess `juma lililopita` is not shipped and `juma` is not a unit at all. `wiki` already carries every week reading CLDR states, so nothing is lost. Refusing the noun costs none of the seven names built on it: `Jumatatu` and `Jumamosi` resolve as always.

**The ordinal register.** Swahili has a second way of naming a month (`mwezi wa kwanza` for January, the first month) and a general ordinal built from a class-agreeing connective plus the cardinal stem. CLDR does not carry the ordinal month register, the sources that do are tutorial-tier. The connective's shape per class was not confirmed for the units this locale reads. No ordinal vocabulary ships.

**The quarter.** CLDR gives Swahili a quarter field. It is the one unit whose relative forms use a different verb entirely: `robo ya mwaka inayofuata`, the quarter that *follows*, rather than the `ijayo` / `ujao` every other unit takes. This library's quarter constructions are built on a single quarter noun, and `robo ya mwaka` is three words with an internal genitive.

**Seasons.** East Africa's year is divided by rains, not by four temperate seasons, and no source consulted gives boundaries for `kiangazi`, `masika`, `vuli` or `kipupwe`. Boundaries nobody stated are not invented, and the locale ships no season vocabulary at all.

**Past-anchoring "since".** English `since Monday until Friday` reaches back to the most recent Monday, because English keeps "since" and "from" apart and only "since" looks backwards. Swahili's sources gloss `kutoka` and `tangu` together as "from/since" without separating the senses. The past-anchoring reading is not claimed for a closed range: `tangu Jumatatu hadi Ijumaa` reads forward like any other closed range. The open range still reaches back: `tangu jana` runs from yesterday to the anchor.

## Open questions for a native speaker

1. Is there any written cue that distinguishes the sunrise clock from the Western one, or does it genuinely depend on genre alone?
2. Are `karne`, `milenia` and `muongo` counted in ordinary running text, and with which concord?
3. What are `juma`'s class 5/6 last/this/next forms?
4. What is the class-agreeing connective for the ordinal register, per unit?
5. Do `kutoka` and `tangu` differ in whether they look backwards, as English "from" and "since" do?
6. Are there stated boundaries for the rain-season words?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("sw")
    False
    >>> span, rest = extract_timespan('saa {0} zilizopita', "sw", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T00:05:00', '')
    >>> span, rest = extract_timespan('miaka {0} iliyopita', "sw", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T00:05:00', '')
    >>> span, rest = extract_timespan('wiki {0} zilizopita', "sw", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T00:05:00', '')
    >>> span, rest = extract_timespan('mwaka uliopita', "sw", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2016-01-01T00:00:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('saa tatu', "sw", anchor) is None
    True

---
[← Spanish](es.md) · [Home](../index.md) · [Swedish →](sv.md)
