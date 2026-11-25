# Macedonian (`mk`)

<!-- agent-hint
covers: where each construction of the Macedonian locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/mk/lang.json, chronologia/locale/mk/vocab.json, chronologia/extract/numfold_macedonian.py, test/nl_corpus_mk/
generated: no
verify: .venv/bin/python -m doctest docs/languages/mk.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/mk.md && .venv/bin/python -c 'exec("import re,sys\nfrom datetime import datetime\nimport chronologia as C\ndef mins(d):\n    return (\"%.6f\" % (d.total_seconds() / 60)).rstrip(\"0\").rstrip(\".\")\ndef rem(r):\n    return \" and \\x60%s\\x60 left over\" % r if r else \"\"\ndef out(rd, tx, lg, an):\n    f = getattr(C, rd)\n    r = f(tx, lg, anchor=an) if rd == \"extract_duration\" else f(tx, lg, an)\n    if rd == \"extract_timespan\":\n        if r is None: return \"no reading\"\n        return \"%s to %s%s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), r.span.end.datetime().strftime(\"%Y-%m-%d %H:%M\"), rem(r.remainder))\n    if rd == \"extract_duration\":\n        if r is None: return \"no length\"\n        return \"a length of %s min%s\" % (mins(r.duration), rem(r.remainder))\n    if rd == \"extract_event\":\n        if r is None: return \"no event\"\n        return \"start %s, length %s, %s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), \"none\" if r.duration is None else mins(r.duration) + \" min\", \"summary \\x60%s\\x60\" % r.summary if r.summary else \"no summary\")\n    if r is None: return \"no rule\"\n    return \"the rule \\x60%s\\x60%s\" % (r.recurrence.to_string(), rem(r.remainder))\n\np=sys.argv[1]\nt=open(p).read()\nm=re.search(r\"\\n## Known limits\\n(.*?)(?=\\n---\\n|\\Z)\",t,re.S)\nbad=0\nn=0\ntot=0\nfor ln in (m[1].split(\"\\n\") if m else []):\n    if \"Example (\" not in ln: continue\n    tot+=1\n    g=re.search(r\"Example \\(reader \\x60(\\w+)\\x60, lang \\x60([\\w-]+)\\x60, anchor (\\d{4}-\\d\\d-\\d\\d \\d\\d:\\d\\d)\\): \\x60([^\\x60]+)\\x60 gives (.+?)\\. \\[#\\d+\\]\",ln)\n    if not g:\n        bad=1\n        print(\"example line does not parse:\",ln[:80])\n        continue\n    n+=1\n    o=out(g[1],g[4],g[2],datetime.strptime(g[3],\"%Y-%m-%d %H:%M\"))\n    if o!=g[5]:\n        bad=1\n        print(\"limit differs\",g[4],\"|\",g[5],\"|\",o)\nprint(\"known limits checked:\",n,\"of\",tot)\nsys.exit(bad)\n")' docs/languages/mk.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Macedonian (`mk`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by its own `numfold_macedonian` module in `chronologia/extract/`.

Macedonian has no case system, which decides the whole shape of the locale. Where the Russian or Croatian folds carry genitive tables for days, hours and feminine ordinals, Macedonian needs none of that machinery: every relative-time string is a bare noun phrase whose parts do not agree in case. The locale is built on the analytic pattern Bulgarian uses, with two Macedonian-specific complications. A postpositive definite article that can attach to any noun, and a count form distinct from the general plural.

The clock is the other decision worth knowing before you read further. Macedonian counts minutes forward from the hour already named, all the way to fifty-nine. There is no "five to nine" construction, and the locale ships none.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('минатата година', "mk", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2016-01-01T00:00:00', '')

## What ships

**Weekdays and months** come from Unicode CLDR 47, `cldr-dates-full/main/mk/ca-gregorian.json`, in both the wide and abbreviated widths. The abbreviations are written with a trailing dot in CLDR, which the tokenizer drops, so `сеп` matches as well as `септември`. Sunday is `недела`, which is also the colloquial word for a week. Only the Sunday reading ships on the singular. The week is `седмица`, CLDR's own display name for that field, so the two surfaces never contend.

**The date line** is little-endian: day, month, year, with a literal trailing `г.` abbreviating `година`. That comes from the `dateFormats` block of the same CLDR file, and it is why `marker_year_word` accepts the bare `г` alongside `година` and `годината`.

**Relative offsets** come from `dateFields.json` in the same CLDR release, where every past pattern is `пред {0} …` and every future one `за {0} …`. Wiktionary's Macedonian entry for `пред` supplies the "ago" sense directly ("се вселивме пред две години"). The named days (`вчера`, `денес`, `утре`, `завчера`, `задутре`) are all CLDR relative-type entries. `денеска` and `другиден` are the current variants Wiktionary lists alongside `денес` and `задутре`.

Year is the one unit where Macedonian prefers a dedicated word to a periphrasis. CLDR gives `лани` for last year and `догодина` for next year as the full forms, with `минатата година` / `следната година` appearing only in the short and narrow widths. Both ship. Every other unit uses the periphrastic `минат-` / `следн-` adjective, which agrees in gender with its noun. The locale carries the whole inflected set rather than one representative form.

**The count form** is the trap the unit files exist to handle. Macedonian distinguishes the plural a noun takes on its own from the shape it takes behind a numeral. The plural of `ден` is `денови`, but five days ago is `пред 5 дена`, and `дена` is what CLDR spells every counted day offset with. Only the count form ships, because `денови` counts nothing. `час` behaves the same way: general plural `часови`, count form `часа`. Wiktionary's entries for `ден` and `час` give both forms, CLDR confirms which one the counting patterns use.

**The clock** is additive only. The evidence is a style guide at reper.net.mk written specifically to teach how to write Macedonian times, whose worked examples are `девет и петнаесет` (9:15), `девет и пол` (9:30) and, decisively, `дваесет и еден и педесет` for 21:50, twenty-one and fifty, counted forward. `и` is the only direction word. `пол` is the only fraction word. No quarter-hour noun ships: the same guide writes the quarter with the minutes spelled out. The hour noun carries the definite article when it names a clock time (`три часот е`), so `часот` and `часа` are accepted alongside `час`.

**Day parts** follow the CLDR day-period rules for `mk` in `cldr-core/supplemental/dayPeriods.json`, transcribed in `chronologia/dayparts.py`: night 00:00-04:00 (`ноќе`), morning 04:00-10:00 (`наутро`), a second morning band 10:00-12:00 (`претпладне`), afternoon 12:00-18:00 (`попладне`) and evening 18:00-24:00 (`навечер`), with midnight and noon as points. That is a six-band, two-point system, and no further bands were invented to fill it out. The stand-alone forms `утро` and `вечер` ship alongside the adverbial ones because CLDR gives them for the same bands.

**Numerals** come from Wiktionary's `Module:number_list/data/mk`. Compounds join tens to units with `и` (`дваесет и еден`), which is the same word the clock uses as its direction marker. The fold in `chronologia/extract/numfold_macedonian.py` handles the overlap. The cardinal for one is gender-marked (`еден` / `една` / `едно`) and all three forms are registered as quantifiers. A feminine noun does not lose its "one".

**Markers** are split between CLDR and the Macedonian Wikipedia article "Предлози во македонскиот јазик", which catalogues the prepositions sense by sense. `до` for "until" is its §До ("достигнување до извесен временски момент", worked example `до полноќ`). `за` for a measured extent is its §За. `по` for temporal succession is its §По. `меѓу` and `помеѓу` for "between" are its §Меѓу. The rest (`пред`, `секој`, `овој`, `минат`, `следн-`) are Wiktionary entries or CLDR relative-time patterns.

## Weaker provenance

`на` ships as the adnominal linker for phrases like `петтиот ден на месецот`. Unlike the other markers it is not tied to a named section of the prepositions article or to a CLDR pattern. It is the ordinary genitive-replacing linker of a caseless Slavic language, and the locale uses it in that structural role only.

`другиден` for the day after tomorrow rests on Wiktionary listing it as a synonym of `задутре`, not on a corpus attestation of its own.

## What refuses

**Minutes to the hour.** `без пет девет` returns nothing, and no `clock_dir_to` exists. This is an active refusal rather than a gap. Two sources were checked specifically for it: the reper.net.mk style guide, built to teach correct time expression, uses only additive forms including for the half hour.

The Macedonian Wikipedia prepositions article has a dedicated §Без covering every attested sense of `без` (lack (`без пари`, `без вода`) and the conjunction `без да`) and names no temporal sense at all. A grammar written to enumerate every sense of the word finding no clock sense is stronger evidence than mere absence. Bulgarian has the construction. Bulgarian is not a safe donor here.

**"Since" as a standalone marker.** `од понеделник` parses the weekday and leaves `од` in the remainder. No dedicated temporal example for `од` exists in CLDR or in the prepositions article, so the locale does not claim the sense. The `од … до …` range is a different matter and is attested. What is refused is treating a bare `од X` as "since X".

**Century and millennium offsets.** `пред 2 века` returns nothing. `век` and `милениум` are not among the CLDR `dateFields` units. No count form for either is attested, and none was invented.

**A quarter-hour word.** Macedonian writes the quarter as `и петнаесет` with the minutes spelled out, so nothing binds a `четврт`-style fraction.

**The general plurals `денови` and `часови`** are deliberately absent from the unit files. They are correct Macedonian, but they never appear behind a numeral, which is the only position the offset construction reads.

## Open questions for a native speaker

1. Does a colloquial or regional minutes-to-the-hour form with `без` exist? Both sources consulted are prescriptive and written, so a casual spoken form is unattested rather than ruled out.

2. Is there a dedicated "since" construction, and is `од` it? A confirmation either way would let the sense ship or be recorded as genuinely absent.

3. What are the count plurals of `век` and `милениум`, if the words take one at all?

4. Does the purely additive clock still read naturally past `:45` in fast speech? The worked example that settles the direction only reaches `:50`.

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("mk")
    False
    >>> span, rest = extract_timespan('минатата година', "mk", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2016-01-01T00:00:00', '')
    >>> span, rest = extract_timespan('следната година', "mk", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2018-01-01T00:00:00', '')
    >>> span, rest = extract_timespan('пред 5 дена', "mk", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-22T00:05:00', '')
    >>> span, rest = extract_timespan('девет и петнаесет', "mk", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T09:15:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('без пет девет', "mk", anchor) is None
    True
    >>> extract_timespan('пред 2 века', "mk", anchor) is None
    True

---
[← Lithuanian](lt.md) · [Home](../index.md) · [Malay →](ms.md)
