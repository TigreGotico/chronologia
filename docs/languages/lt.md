# Lithuanian (`lt`)

<!-- agent-hint
covers: where each construction of the Lithuanian locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/lt/lang.json, chronologia/locale/lt/vocab.json, chronologia/extract/numfold_baltic.py, test/nl_corpus_lt/
generated: no
verify: .venv/bin/python -m doctest docs/languages/lt.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/lt.md && .venv/bin/python -c 'exec("import re,sys\nfrom datetime import datetime\nimport chronologia as C\ndef mins(d):\n    return (\"%.6f\" % (d.total_seconds() / 60)).rstrip(\"0\").rstrip(\".\")\ndef rem(r):\n    return \" and \\x60%s\\x60 left over\" % r if r else \"\"\ndef out(rd, tx, lg, an):\n    f = getattr(C, rd)\n    r = f(tx, lg, anchor=an) if rd == \"extract_duration\" else f(tx, lg, an)\n    if rd == \"extract_timespan\":\n        if r is None: return \"no reading\"\n        return \"%s to %s%s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), r.span.end.datetime().strftime(\"%Y-%m-%d %H:%M\"), rem(r.remainder))\n    if rd == \"extract_duration\":\n        if r is None: return \"no length\"\n        return \"a length of %s min%s\" % (mins(r.duration), rem(r.remainder))\n    if rd == \"extract_event\":\n        if r is None: return \"no event\"\n        return \"start %s, length %s, %s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), \"none\" if r.duration is None else mins(r.duration) + \" min\", \"summary \\x60%s\\x60\" % r.summary if r.summary else \"no summary\")\n    if r is None: return \"no rule\"\n    return \"the rule \\x60%s\\x60%s\" % (r.recurrence.to_string(), rem(r.remainder))\n\np=sys.argv[1]\nt=open(p).read()\nm=re.search(r\"\\n## Known limits\\n(.*?)(?=\\n---\\n|\\Z)\",t,re.S)\nbad=0\nn=0\ntot=0\nfor ln in (m[1].split(\"\\n\") if m else []):\n    if \"Example (\" not in ln: continue\n    tot+=1\n    g=re.search(r\"Example \\(reader \\x60(\\w+)\\x60, lang \\x60([\\w-]+)\\x60, anchor (\\d{4}-\\d\\d-\\d\\d \\d\\d:\\d\\d)\\): \\x60([^\\x60]+)\\x60 gives (.+?)\\. \\[#\\d+\\]\",ln)\n    if not g:\n        bad=1\n        print(\"example line does not parse:\",ln[:80])\n        continue\n    n+=1\n    o=out(g[1],g[4],g[2],datetime.strptime(g[3],\"%Y-%m-%d %H:%M\"))\n    if o!=g[5]:\n        bad=1\n        print(\"limit differs\",g[4],\"|\",g[5],\"|\",o)\nprint(\"known limits checked:\",n,\"of\",tot)\nsys.exit(bad)\n")' docs/languages/lt.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Lithuanian (`lt`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by its own `numfold_baltic` module in `chronologia/extract/`.

The rule that shapes this locale is that the numeral's **last digit** decides the form of a counted noun, not its size. A numeral ending in 1 (but not 11) takes the singular. One ending in 2 through 9, but not 12 through 19, takes the nominative plural. One ending in 0, and the whole teen range, takes the genitive plural.

So `21 diena`, `25 dienos`, `20 dienų`, `111 dienų`. This is not the Slavic pattern. The Slavic tables cannot be borrowed for it: `chronologia/extract/numfold_baltic.py` carries its own last-digit-keyed government with three noun cases per unit, plus the accusative that `prieš` imposes.

The spoken half hour names the coming hour. `pusė trijų` is 02:30, and the hour that follows `pusė` stands in the genitive.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('pusė trijų', "lt", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T02:30:00', '')

## What ships

**Months** ship in three forms from the Unicode CLDR 47 chart for `lt`: the stand-alone nominative, the genitive that the date construction actually uses, and the abbreviation. The genitive is the working form. A Lithuanian date is `kovo 1 d.`, "of March, day one".

**The date line** is `YEAR m. MONTH DAY d.`, as in `1990 m. kovo 1 d.`, where `m.` abbreviates `metai` (year) and `d.` abbreviates `diena` (day). Both abbreviations are Wiktionary-attested in exactly that calendar-date sense. `metai` is a plurale tantum, which is why the year vocabulary carries `metai`, `metų` and `metais` rather than a singular.

**The day of the month** reads either way. The written form is a bare digit (`liepos 5 d.`), and the spelled form is a feminine ordinal agreeing with an elided `diena` (`liepos penktoji`). Both resolve to the same date.

**Relative offsets** use `prieš` with the accusative for the past (`prieš valandą`, an hour ago) and `po` with the genitive for the future (`po trijų dienų`, in three days). Both are Wiktionary entries with the temporal sense given directly. Unit files therefore carry the genitive singular alongside the three government cases, because `po` governs it.

**The determiners** `šis` (this), `praeitas` (last) and `kitas` (next) ship in their full non-pronominal declensions from Wiktionary. The bare accusative is the ordinary "in" or "during" form: `šią savaitę` is this week.

**The clock** has two constructions. `pusė` plus the genitive of the coming hour gives the half hour (`pusė trijų` is 02:30, `pusė aštuonių` is 07:30) with `bare_half_to` in `lang.json` rolling the named hour back. `be` plus the genitive counts down toward the named hour: `be penkių trys` is 02:55. Wiktionary supplies both function words in the right government (`be` "without", with the genitive, `pusė` "half"), and Talkpal's guide to telling time in Lithuanian supplies the worked examples.

**Day parts** take their band boundaries from the CLDR 47 day-period chart for `lt`, transcribed in `chronologia/dayparts.py`, and ship as the CLDR period name plus the adverbial case the deictic phrase uses, declined from Wiktionary: `rytas` / `rytą` / `ryte`. The parallel sets for afternoon, evening and night. Midnight and noon are `vidurnaktis` and `vidurdienis`.

**Markers** are Wiktionary entries throughout: `po` (after), `prieš` (before), `tarp` with the genitive (between), `nuo` with the genitive (from, since), `iki` (until, and the closing half of a range), `kas` (every, as in `kas savaitę`), `ir` (and).

## Weaker provenance

**The clock constructions** rest on a language-learning site for their worked examples. Wiktionary attests the words and their case government, but the pairing of `pusė trijų` with 02:30 rather than 03:30 comes from Talkpal's time page. The direction is corroborated by several accounts and no counter-example was found, but a reference grammar was not consulted for it.

**`kas` as the distributive "every"** is a Wiktionary sense that itself cites Ambrazas's *Lithuanian Grammar* with page locators. The grammar was not consulted directly. What was read is Wiktionary's entry.

**Ambrazas (ed.) 1997, *Lithuanian Grammar*, Baltos lankos** was sought as the authority for numeral government and the clock direction and was not reached in full text. The government rule instead rests on triangulation across several independent tertiary accounts that agree on the last-digit keying and on the same worked examples.

## What refuses

A test pins each refusal.

**Calendar quarters.** `pirmasis ketvirtis`, `antras ketvirtis` and the bare `ketvirtis` all refuse. No quarter vocabulary was attested.

**ISO week references.** `3 savaitė`, `trečioji savaitė` and the like refuse.

**The quarter hour on the clock.** `be ketvirčio trys` and `ketvirtis po trijų` refuse. Only the half hour and the counted minutes-to form ship.

**An ordinal hour after `pusė`.** `pusė vienuoliktos` and `pusė trečios` refuse. The hour that `pusė` names is a cardinal genitive (`pusė vienuolikos`) and the ordinal shape was not attested, so it is not guessed at.

**Era vocabulary.** `44 pr. m. e.` and `prieš mūsų erą` are not read as eras. The abbreviation could not be attested, so the era marker leaves its pieces in the remainder.

**`paskutinis` as a relative marker.** `paskutinis penktadienis` resolves the Friday and leaves `paskutinis` visibly in the remainder rather than silently swallowing it. The word has no attested declension table here, so it is not wired as the "last weekday of the month" marker.

**The instrumental determiners.** `praeitais metais` and `kitais metais` refuse. The instrumental of `praeitas` and `kitas` could not be attested. The nominative and accusative are what ship.

**Early, middle and late.** `birželio pradžioje` returns the whole of June with the unread part word left in the remainder. No period-part vocabulary ships.

**A spelled quantity with no direction marker.** `du šimtai penkiasdešimt dienų` refuses, because a quantity without a marker is still only a quantity.

## Open questions for a native speaker

1. Do the individual weekday and month genitives all follow the regular pattern, spelling included? Only some were dictionary-checked. The rest follow a regular declension and are individually unverified.

2. Is the `pusė` + genitive half-hour direction confirmed by a reference grammar, and does the target hour stand in the case assumed here?

3. Is there an attested quarter-hour clock construction?

4. What is the standard era abbreviation, and how is it written?

5. Does `paskutinis` have a declension that would let it act as the "last Friday of the month" marker?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("lt")
    False
    >>> span, rest = extract_timespan('pusė trijų', "lt", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T02:30:00', '')
    >>> span, rest = extract_timespan('pusė aštuonių', "lt", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T07:30:00', '')
    >>> span, rest = extract_timespan('be penkių trys', "lt", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T02:55:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('ketvirtis', "lt", anchor) is None
    True
    >>> extract_timespan('be ketvirčio trys', "lt", anchor) is None
    True
    >>> extract_timespan('ketvirtis po trijų', "lt", anchor) is None
    True
    >>> extract_timespan('pusė vienuoliktos', "lt", anchor) is None
    True
    >>> extract_timespan('pusė trečios', "lt", anchor) is None
    True
    >>> extract_timespan('praeitais metais', "lt", anchor) is None
    True
    >>> extract_timespan('kitais metais', "lt", anchor) is None
    True
    >>> extract_timespan('du šimtai penkiasdešimt dienų', "lt", anchor) is None
    True

---
[← Latvian](lv.md) · [Home](../index.md) · [Macedonian →](mk.md)
