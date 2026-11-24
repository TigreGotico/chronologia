# Icelandic (`is`)

<!-- agent-hint
covers: where each construction of the Icelandic locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/is/lang.json, chronologia/locale/is/*.voc, chronologia/extract/numfold_icelandic.py, test/nl_corpus_is/
generated: no
verify: .venv/bin/python -m doctest docs/languages/is.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/is.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Icelandic (`is`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by its own `numfold_icelandic` module in `chronologia/extract/`.

Icelandic names the **coming** hour on the half. `hálf tvö` is 01:30, not 02:30. Everything else about the clock follows from that: the quarter word `kortér` takes its direction from the preposition beside it, `yfir` counting up from the hour named and `í` counting down toward it. `kortér yfir tvö` is 02:15 and `kortér í þrjú` is 02:45.

The second thing shaping this locale is that Icelandic prepositions govern case. The case is what carries the meaning. `fyrir` with the dative is "ago". The same word with the accusative means "before <event>", which is a different construction the locale does not read. Because the construction imposes the case and the count imposes the number, every indefinite form of a unit noun is a surface of that unit. The vocabulary files list them all.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('hálf tvö', "is", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T01:30:00', '')

## What ships

**Months** come from Unicode CLDR 47, `cldr-dates-full/main/is/ca-gregorian.json`. Icelandic month names do not decline, so the wide name is the only form the date construction reads, alongside the calendar's own abbreviation.

**Weekdays** ship in the full declension from Wiktionary. The date form is the accusative, bare or with the suffixed article (`á mánudaginn`) which is what the bare temporal accusative uses.

**Relative offsets** are `fyrir` plus the dative for the past (`fyrir tveimur árum`) and `eftir` plus the accusative for the future (`eftir tíu mínútur`), both with Wiktionary's own worked examples. `síðan` may optionally close a backward offset (`fyrir fimm mínútum síðan`) although the dative already carries the meaning without it.

**The clock** reads `klukkan` (literally "the clock") or its abbreviation `kl.` as the "at" marker. Between a minute count and the direction word, the optional `mínútur` is accepted: `fimmtán mínútur yfir eitt` is 01:15. The half-hour direction comes from Wiktionary's appendix on telling time in Icelandic, at the 1:30 row, `kortér` and both directional prepositions come from the `kortér` entry itself.

**Day parts** take their band boundaries from the CLDR 47 day-period rule set for `is`, transcribed in `chronologia/dayparts.py`, and their surfaces from the CLDR period names with declensions from Wiktionary. The afternoon is a case worth noting: CLDR's wide name `eftir hádegi` is two words, so the single-token surface shipped is the abbreviated `síðdegis`.

**Named days** are `í dag`, `í gær`, `á morgun` and `í fyrradag`, each a Wiktionary entry.

**The determiners** `þessi` (this), `næstur` (next) and `síðastliðinn` (last) ship in the declensions Wiktionary gives, the weak forms being the ones a temporal phrase uses: `næsta fimmtudag`, `í næstu viku`.

## What refuses

A test pins each refusal.

**The day after tomorrow.** The one candidate, `hinn daginn`, ordinarily means "the other day". No compositional form was attested either. `yfirmorgun` returns nothing and the other candidates leave their tokens unread. No phrase in this locale names a day two ahead.

**"Since".** `frá og með` has no confirming source. No "since" vocabulary ships. `frá og með mánudegi` and `síðan á mánudag` return the next Monday, 2017-07-03, with `frá og með` and `síðan á` left in the remainder.

**"For <duration>".** `í þrjá daga`, `í tvær vikur`, `í fimm mínútur`: the duration marker has no citation, so a duration phrase must not be read as one.

**"Every".** `á hverjum degi` and `hvern dag` return nothing. `á hverjum mánudegi` returns the next Monday with `á hverjum` left in the remainder. No "every" quantifier was independently sourced.

**From-to and between ranges.** `frá júní til ágúst` returns June alone with `frá til ágúst` left in the remainder, and `milli júní og september` does not close a span either. The governed cases of `frá` and `til` were never verified with a worked example, so no range vocabulary ships.

**Clause conjunctions as offset markers.** `áður en` and `eftir að` introduce a clause, not a quantity. Reading either as the prepositional `fyrir` or `eftir` would invent an offset that the sentence does not state.

**`annar` as a spelled second.** `annar` is the ordinary Icelandic word for "another" or "the other". The ordinal fold refuses to claim every occurrence of it as the digit two. `annar júní` returns the whole of June with `annar` left in the remainder. The dotted `2. júní` is how the second of the month is written and read.

**Calendar quarters and ISO week references.** `fyrsti ársfjórðungur` and `3. vika` both refuse.

**Era vocabulary.** `44 f.Kr.` and `árið 1990 e.Kr.` leave the era marker visible or refuse outright. No era vocabulary ships.

**Early, middle and late.** `í byrjun júní` and `í lok júní` return the month with the part word left in the remainder.

**A spelled quantity with no direction marker.** `þrjú hundruð og fimmtíu dagar` refuses: a quantity without a marker is still only a quantity.

## Open questions for a native speaker

1. Is there a current word or phrase for the day after tomorrow?
2. Is `frá og með` the ordinary way to say "since", and what case does it take?
3. What is the "for <duration>" construction, and what case does it govern?
4. What are the "every" quantifier's forms in a temporal phrase?
5. Which cases do `frá` and `til` govern in a month-to-month range?
6. Are there attested era abbreviations?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("is")
    False
    >>> span, rest = extract_timespan('hálf tvö', "is", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T01:30:00', '')
    >>> span, rest = extract_timespan('kortér yfir tvö', "is", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T02:15:00', '')
    >>> span, rest = extract_timespan('kortér í þrjú', "is", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T02:45:00', '')
    >>> span, rest = extract_timespan('fimmtán mínútur yfir eitt', "is", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T01:15:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('yfirmorgun', "is", anchor) is None
    True
    >>> extract_timespan('á hverjum degi', "is", anchor) is None
    True
    >>> extract_timespan('hvern dag', "is", anchor) is None
    True
    >>> extract_timespan('fyrsti ársfjórðungur', "is", anchor) is None
    True
    >>> extract_timespan('3. vika', "is", anchor) is None
    True
    >>> extract_timespan('þrjú hundruð og fimmtíu dagar', "is", anchor) is None
    True

---
[← Hungarian](hu.md) · [Home](../index.md) · [Indonesian →](id.md)
