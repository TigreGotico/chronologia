# Georgian (`ka`)

<!-- agent-hint
covers: where each construction of the Georgian locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/ka/lang.json, chronologia/locale/ka/*.voc, chronologia/extract/numfold_georgian.py, test/nl_corpus_ka/
generated: no
verify: .venv/bin/python -m doctest docs/languages/ka.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/ka.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Georgian (`ka`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by its own `numfold_georgian` module in `chronologia/extract/`.

Georgian counts in base twenty, and reading it any other way is confidently wrong on every value from twenty-one to ninety-nine. Between the score multiples (`ოცი` 20, `ორმოცი` 40, `სამოცი` 60, `ოთხმოცი` 80) a number is the score, plus `და` ("and"), plus a remainder drawn from the one-to-nineteen series. The whole thing is written as **one word**: `ოცდაათი` is "twenty-and-ten", thirty. `chronologia/extract/numfold_georgian.py` reads that structure. A tens-and-ones fold of the Germanic kind would not.

The adpositions are postpositions and they govern the genitive. `წინ` ("ago") and `შემდეგ` ("after") both trail the phrase they govern: `სამი თვის წინ` is three months ago. Modifiers, though, stand before their noun: `მომავალი წელი` is next year. Georgian is postpositional in its adposition system, not in its modifiers.

The clock names the hour being **approached**, with that hour in the genitive and no direction word at all: `ორის ნახევარი` is half toward two, 01:30.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('სამი თვის წინ', "ka", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-03-27T00:05:00', '')

## What ships

**Months and weekdays** come from Unicode CLDR 47, `cldr-dates-full/main/ka/ca-gregorian.json`, where the stand-alone and format forms are identical.

**Named days reach three out on each side of today**. One further than most languages name. Backward: `გუშინ`, `გუშინწინ`, and `გუშინწინისწინ`, which Wiktionary marks colloquial and rare. Forward: `ხვალ`, `ზეგ`, `მაზეგ`. Each is its own Wiktionary entry, and each entry carries the day-sequence coordinate-term list that confirms the series.

**Day parts** take their bands from the CLDR 47 day-period rule set for `ka`, transcribed in `chronologia/dayparts.py`, and ship in two forms apiece: the stand-alone wide name and the case-marked adverbial format form, with the declension from Wiktionary. Midnight and noon likewise ship the nominative and the dative, the dative being what CLDR lists for the day period.

**The millennium** ships. Its Wiktionary declension table is rendered, so the genitive the postpositions govern is attested rather than inferred, and `ორი ათასწლეულის წინ` reads.

## What refuses

A test pins each refusal.

**Every week duration.** `კვირა` names both Sunday and the week, under one dictionary entry whose seven-case declension is identical for the two senses. There is no morphological cue to tell them apart, and no source consulted establishes either as dominant in a counted phrase. The ambiguity is resolved by construction: `კვირა` binds the weekday slot alone, and every duration reading refuses. `ორი კვირის წინ` and `სამი კვირის შემდეგ` return nothing.

**A count before `კვირა`.** `ორი კვირა`, `10 კვირა` and the rest refuse too. A count before it can only be a span of weeks. This locale has no week unit to express one. The weekday reading is vetoed as well. Answering "Sunday" here and stranding the numeral would hand a caller who asked for a duration one specific day, which is a wrong span rather than an incomplete one. Declining the false weekday reading is not the same as asserting the unsourced week reading, which stays unavailable.

The veto is scoped to that one surface. A bare `კვირა`, and `მომავალი კვირა` or `გასული კვირა` after a relative marker, all resolve as Sunday, because a weekday-slot position admits only that sense. And an unambiguous weekday keeps the ordinary behaviour: `ორი ორშაბათი` resolves the Monday with the count left in the remainder, and `ორი ორშაბათი წინ` counts two Mondays back.

**The century.** `საუკუნე` is the word. But its Wiktionary entry carries no declension table at all (a genuine gap, confirmed through both the rendered page and the parse API) so the genitive the postpositions govern would have to be inferred from other `-ე` stems. It is omitted instead. The millennium, whose table *is* rendered, ships. The asymmetry is exactly that difference.

**Recurrence.** "Every" is attested only as the fused compound adverb `ყოველდღე` ("daily"), never as a quantifier heading a free noun phrase. It is not generalised to other units. The compound itself names no single span.

**"Since".** There is no dedicated postposition. It is either the periphrastic clause-level `მას შემდეგ რაც` or an extension of the plain "from" suffix `-დან`. Neither was confirmed with a temporal worked example that distinguishes it from "after" or "from".

**Ranges.** Georgian has two unrelated between-forms (the paired suffixes `-დან … -მდე` for a time range, and the separate word `შორის` for two entities) and the sources consulted disagree on which case `შორის` governs. Neither ships while that conflict is open.

**A bare "N o'clock".** No source consulted gives a plain "it is N o'clock" surface for Georgian (only the four minute-band idioms, of which just the half is modelled) so a bare count of hours stays a duration and names no time of day.

**The other minute bands.** The first half hour marks its relation by the genitive alone, with no direction word. The second half hour switches to a whole subordinate clause, `სამს რომ აკლია ოცდახუთი წუთი`, "three that lacks twenty-five minutes". Neither shape fits the slot model, so both refuse. The half construction does not approximate them.

**Seasons.** No season vocabulary is attested, so the season names stay unread rather than being taken from a bilingual word list.

**Meridiem markers.** CLDR gives Georgian no native am/pm surfaces (the fields hold the literal Latin `AM` and `PM`) so no meridiem vocabulary ships.

## Open questions for a native speaker

1. In a counted phrase, does `კვირა` mean weeks or Sundays, and is there a cue that settles it?

2. What is the declension of `საუკუნე`, and specifically its genitive?

3. Is there a quantifier "every" that heads a free noun phrase, or only the fused `ყოველდღე` series?

4. What is the ordinary "since Monday" construction?

5. Which case does `შორის` govern?

6. Is there a plain "it is N o'clock" surface?

7. Are the season names in ordinary use with definable boundaries?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("ka")
    False
    >>> span, rest = extract_timespan('სამი თვის წინ', "ka", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-03-27T00:05:00', '')
    >>> span, rest = extract_timespan('მომავალი წელი', "ka", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2018-01-01T00:00:00', '')
    >>> span, rest = extract_timespan('ორის ნახევარი', "ka", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T01:30:00', '')
    >>> span, rest = extract_timespan('ორი ათასწლეულის წინ', "ka", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('0017-06-27T00:05:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('ორი კვირის წინ', "ka", anchor) is None
    True
    >>> extract_timespan('სამი კვირის შემდეგ', "ka", anchor) is None
    True

---
[← Galician](gl.md) · [Home](../index.md) · [German →](de.md)
