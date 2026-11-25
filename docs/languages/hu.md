# Hungarian (`hu`)

<!-- agent-hint
covers: where each construction of the Hungarian locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/hu/lang.json, chronologia/locale/hu/vocab.json, chronologia/extract/numlayer.py:NUMTAG_LANGS, test/nl_corpus_hu/, test/test_xfail_open_issues_*.py
generated: no
verify: .venv/bin/python -m doctest docs/languages/hu.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/hu.md && .venv/bin/python -c 'exec("import re,sys\nfrom datetime import datetime\nimport chronologia as C\ndef mins(d):\n    return (\"%.6f\" % (d.total_seconds() / 60)).rstrip(\"0\").rstrip(\".\")\ndef rem(r):\n    return \" and \\x60%s\\x60 left over\" % r if r else \"\"\ndef out(rd, tx, lg, an):\n    f = getattr(C, rd)\n    r = f(tx, lg, anchor=an) if rd == \"extract_duration\" else f(tx, lg, an)\n    if rd == \"extract_timespan\":\n        if r is None: return \"no reading\"\n        return \"%s to %s%s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), r.span.end.datetime().strftime(\"%Y-%m-%d %H:%M\"), rem(r.remainder))\n    if rd == \"extract_duration\":\n        if r is None: return \"no length\"\n        return \"a length of %s min%s\" % (mins(r.duration), rem(r.remainder))\n    if rd == \"extract_event\":\n        if r is None: return \"no event\"\n        return \"start %s, length %s, %s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), \"none\" if r.duration is None else mins(r.duration) + \" min\", \"summary \\x60%s\\x60\" % r.summary if r.summary else \"no summary\")\n    if r is None: return \"no rule\"\n    return \"the rule \\x60%s\\x60%s\" % (r.recurrence.to_string(), rem(r.remainder))\n\np=sys.argv[1]\nt=open(p).read()\nm=re.search(r\"\\n## Known limits\\n(.*?)(?=\\n---\\n|\\Z)\",t,re.S)\nbad=0\nn=0\ntot=0\nfor ln in (m[1].split(\"\\n\") if m else []):\n    if \"Example (\" not in ln: continue\n    tot+=1\n    g=re.search(r\"Example \\(reader \\x60(\\w+)\\x60, lang \\x60([\\w-]+)\\x60, anchor (\\d{4}-\\d\\d-\\d\\d \\d\\d:\\d\\d)\\): \\x60([^\\x60]+)\\x60 gives (.+?)\\. \\[#\\d+\\]\",ln)\n    if not g:\n        bad=1\n        print(\"example line does not parse:\",ln[:80])\n        continue\n    n+=1\n    o=out(g[1],g[4],g[2],datetime.strptime(g[3],\"%Y-%m-%d %H:%M\"))\n    if o!=g[5]:\n        bad=1\n        print(\"limit differs\",g[4],\"|\",g[5],\"|\",o)\nprint(\"known limits checked:\",n,\"of\",tot)\nsys.exit(bad)\n")' docs/languages/hu.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Hungarian (`hu`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

Hungarian runs the most complete counting-toward-the-hour clock of any locale here. `negyed kilenc` is 08:15, `fél kilenc` is 08:30 and `háromnegyed kilenc` is 08:45. They name a quarter, a half and three quarters of the way *toward* nine, never past eight. Estonian does the same with the same three fractions and is unrelated to it. Slovenian and Croatian, the Slavic neighbours in contact with Hungarian, name the half toward the coming hour but ship no quarter at all. The rest of the locale is shaped by agglutination: the case suffix that other languages spell as a separate preposition arrives glued to the word. A date, an hour and a weekday each reach the parser as one token carrying its own grammar.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('negyed kilenc', "hu", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T08:15:00', '')

## What ships

**The date line** is big-endian, `YEAR MONTH DAY`, which is what CLDR 47's `ca-gregorian` chart for `hu` gives at every level, full `y. MMMM d., EEEE`, long `y. MMMM d.`, medium `y. MMM d.`, short `y. MM. dd.`. `lang.json` disables the shared little-endian `calendar_date` outright and defines its own in its place, with a month-led fallback for the year-less phrase. The tokenizer runs with `ordinal_dot` on, so the Hungarian habit of closing a date with a full stop (`2020. augusztus 15.`) parses as written.

**The spelled day of month** is a single-token ordinal. numtag reads the bare ordinal for every value from 1 to 31. The whole range comes from numtag rather than a vocabulary file. numtag does not read the possessive form the date construction takes (`tizenötödike`, `huszonegyedike`) so chronologia strips the possessive ending, which follows the vowel harmony of the ordinal, and has numtag read the remaining ordinal. `elseje` is handled as the suppletive it is.

**Months and weekdays** ship in the nominative and the inessive or superessive that a "in May" / "on Monday" phrase uses (`január`/`januárban`, `hétfő`/`hétfőn`) plus a possessive form for each weekday. The nominatives match the CLDR 47 wide charts exactly.

**Day parts** are transcribed from the Unicode CLDR 47 day-period rules for `hu`, and Hungarian is one of the few locales whose chart carries six named bands rather than four. All six surfaces ship: `reggel` (morning, Wiktionary `reggel`, adverb, "in the morning", glossed for roughly 6 to 9 a.m.), `délelőtt` (forenoon, Wiktionary `délelőtt`, "before noon, in the forenoon", roughly 9 a.m. to noon), `délután` (afternoon, Wiktionary `délután`, "in the afternoon"), `este` (evening, Wiktionary `este`), `éjjel` (night, Wiktionary `éjjel`, "at night") and `hajnal` (dawn, Wiktionary `hajnal`). The first four double as clock meridiem cues, alongside the abbreviations `de.` and `du.` that CLDR gives for AM and PM.

**Landmarks** are `éjfél`/`éjfélkor` (midnight) and `dél`/`délben` (noon), each in the bare form and in the case the phrase actually takes.

**The toward-hour clock.** All three counting-toward fractions ship, gated by `bare_half_to: true` and `bare_quarter_to: true` in `lang.json` and read through a `FRACTION HOUR MERIDIEM? ZONE?` order. Two independent sources fix the direction with worked numeric examples. Wiktionary's Hungarian `fél`, under the numeral etymology rather than the verb one that opens the lemma, glosses the clock sense as "half an hour before … o'clock … 30 minutes before an hour rather than after" and works it out as `fél hétkor` = "at half past six". Wiktionary's `háromnegyed` gives `Háromnegyed tíz van.` = "It's a quarter to ten." A third source, Wiktionary's entry for the temporal suffix `-kor`, lists all three fractions against the same hour in one place (`negyed egy` 12:15, `fél egy` 12:30, `háromnegyed egy` 12:45) which is the cleanest single attestation of the system as a system. The project's own corpus checks four hours of the half and five of the quarters against independent arithmetic.

**The glued clock hour.** Colloquial Hungarian drops the "o'clock" word and glues the temporal suffix straight onto the numeral: `háromkor` is "at three". The cardinal back-end does not read the glued form, and folding it to a bare digit would leave the clock frame no cue at all. The twelve telling-time surfaces are given as a closed table and each is split into a synthetic `at` marker plus the hour, which the universal `at HOUR` order then binds. The marker carries an empty raw text and a zero-width extent. It never reaches the remainder. `-kor` is cited to its own Wiktionary entry as the temporal case suffix, which glosses `1 órakor` as "at 1 o'clock" and `1-kor` as "at 1".

**The sublative of a clock hour and of a length.** The sublative `-ra`/`-re` follows a count of units. The phrase `három órára` reads 15:00 at 13:04. The phrase `öt percre` is a length of five minutes. The surfaces `napra`, `órára`, `percre`, `hónapra`, `hétre`, `másodpercre` and `évre` ship.

Each cites the declension table of its Wiktionary entry. The word `órára` also serves as a clock word. So `tedd át a megbeszélést három órára` reads 15:00 and leaves `tedd át a megbeszélést` in the remainder.

**`hét` never folds.** Hungarian's word for "week" is also its word for "seven". The fold names it explicitly in an exclude set so the unit token survives. `hétkor` ("at seven") is a distinct surface and is unaffected, so both readings stay reachable. The attributive `két` (2) goes the other way and is supplied explicitly, because the pronouncer emits only `kettő`.

**Fused thousands.** Hungarian glues the multiplier onto the scale word and hyphenates the remainder (`kétezer-huszonnégy` is 2024) and neither the run set nor the number back-end composes the two. A wrapper validates the multiplier prefix through the language's own extractor and composes the value itself. `kétezer-huszonnégy` reads as the year rather than as twenty-four.

**Relative offsets** are `múlva` (in, trailing the count), `ezelőtt` (ago, likewise trailing) and `óta` (since), each in the postposition slot Hungarian puts them in, `lang.json`'s `positions` table declares `until` and `from` as affixes and `since` as a postposition, which is what lets `-ig` and `-tól`/`-től` be read as the suffixes they are. The deep-time construction reads `millió` and `milliárd` alongside `ezer`.

**Determiners.** `előző` ("previous") and `következő` ("following") match the CLDR 47 `hu` `dateFields.json` relative types exactly across week, month and year (`előző hét` for relative-type--1, `következő hét` for relative-type-1) and `ez` plus the article gives CLDR's `ez a hét` for relative-type-0. The locale also ships the everyday `múlt`/`elmúlt` and `jövő`, which CLDR does not use. Wiktionary carries both: `múlt` glossed "last (with weeks, months, years, and larger time units)" and `jövő` glossed "next, coming (week, month, year, or a larger time unit)".

**Named days** span all five positions around the anchor (`tegnapelőtt`, `tegnap`, `ma`, `holnap`, `holnapután`) and are exactly what the CLDR 47 `hu` `dateFields.json` day field gives for relative types −2 through +2.

**Quarters, ISO weeks, decades, centuries and millennia** resolve, with `negyedév` for the quarter, `hét` for the ISO week, `évtized`, `század` and `évszázad` for the decade and century, and `évezred` for the millennium. Seconds ship a dedicated unit.

## Weaker provenance

**The grammar behind the clock.** All three fraction files name Rounds, Carol H., *Hungarian: An Essential Grammar*, 2nd ed. (Routledge, 2009), its section on telling the time. That is a real and standard reference. But it is a printed book and the claim rests here on the Wiktionary attestations instead, which carry the worked numeric examples the grammar is cited for.

**The quarter's citation.** `clock_fraction_15` attributes the clock sense to the Wiktionary lemma `negyed`. That lemma's Hungarian section has three senses (the fraction "quarter, fourth", the musical crotchet, and a city quarter) and no clock sense at all. The reading is well attested, but on the `-kor` and `háromnegyed` lemmas rather than on that one. The `fél` citation has a milder version of the same problem: the lemma opens on the unrelated verb "to fear" and the numeral is a separate etymology further down, which the file's bare "Wiktionary `fel`" does not say.

**The oblique month and weekday forms** ship one case each with no citation recording which case, or whether one is enough, Hungarian has considerably more than one candidate.

**`negyedév`** ships without a citation and without any statement of whether a native alternative competes with it.

## What refuses

**Minutes counted to or past the hour.** The three counting-toward fractions are the only fractional clock surfaces sourced, and no arbitrary-minute construction ships.

**A year-led quarter or half.** Hungarian puts the year first. The quarter and half-period constructions carry only the year-last orders the shared grammar supplies. `2020 második negyedéve` and `2020 első fele` both return the whole of 2020 with the qualifier stranded. The same silent widening in both cases, and the more dangerous of the two failure modes because a whole year is a plausible-looking answer.

**A decade written the Hungarian way.** `1990-es évek` returns the single year 1990 with `es évek` stranded. The decade unit is present. The `-es évek` spelling that names a decade is not.

**A weekday range.** `hétfőtől péntekig` returns the span from the anchor to Friday with `hétfőtől` stranded: the terminative `-ig` is read as an affix and the ablative `-tól`/`-től` is listed in `marker_from`. But the pair does not compose over two weekdays.

**A duration in the terminative.** `három napig` ("for three days") does not resolve. Estonian, German, Slovak and Croatian each carry a `marker_recur_for`. Hungarian does not, and `-ig` alone reaches only the range construction.

**Dawn in the case a phrase uses.** `hajnal` ships as CLDR spells it, which is the bare noun. Every other day part in this locale ships the adverb. `éjjel` resolves standing alone and `hajnalban` does not. `holnap hajnalban` returns the whole of tomorrow with `hajnalban` stranded.

**A leading article.** `a hétvégén`, `a jövő héten` and `a hónap elején` all resolve correctly and all leave the article in the remainder.

## Open questions for a native speaker

1. Should `fél egy` read as 12:30 or as 00:30 when nothing else in the phrase disambiguates? The cited source gives 12:30, but a speaker naming the half hour after midnight has to say something.
2. Is `pár` two or approximately three in a temporal phrase (`pár nap`), or does it resist a number entirely?
3. Which case should each month and weekday ship beyond the one on file, and is one enough for ordinary date phrases?
4. Does `negyedév` compete with a native alternative for a calendar quarter?
5. Is `hajnalban` the form a phrase uses, with `hajnal` reserved for the bare noun, or are both current adverbially?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("hu")
    True
    >>> span, rest = extract_timespan('negyed kilenc', "hu", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T08:15:00', '')
    >>> span, rest = extract_timespan('fél kilenc', "hu", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T08:30:00', '')
    >>> span, rest = extract_timespan('háromnegyed kilenc', "hu", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T08:45:00', '')

## Known limits

Each line is an open issue with a strict `xfail` test for this language. The lines are grouped by topic. An example names the reader that produced it, the language and the anchor date, and shows what that reader gives on the test's own phrase.

- A digit clock with the suffix `-kor` after the particle `fel` is not read: `ébressz fel 7-kor` gives no reading, while `ébressz 7-kor` reads 19:00. A part of the day before a sublative hour gives the whole band: `állíts be egy ébresztőt reggel hétre` gives 06:00 to 12:00 and leaves `állíts be egy ébresztőt hétre`. Example (reader `extract_timespan`, lang `hu`, anchor 2017-06-27 13:04): `ébressz fel 7-kor egy hangoskönyvvel` gives no reading. [#1020](https://github.com/TigreGotico/chronologia/issues/1020)

- A word for next or last beside a season, month or week stays in the remainder. Example (reader `extract_timespan`, lang `hu`, anchor 2017-06-27 13:04): `1999 nyara` gives 1999-01-01 00:00 to 2000-01-01 00:00 and `nyara` left over. [#993](https://github.com/TigreGotico/chronologia/issues/993)

- A unit word with no number counts as one. Example (reader `extract_duration`, lang `hu`, anchor 2017-06-27 13:04): `ezen a héten` gives a length of 10080 min and `ezen` left over. [#1004](https://github.com/TigreGotico/chronologia/issues/1004)

- Text that is no date reads as a date, or the wrong reading wins. Example (reader `extract_timespan`, lang `hu`, anchor 2017-06-27 13:04): `április 31 8 órakor` gives 2017-06-27 20:00 to 2017-06-27 20:01 and `április 31` left over. [#1035](https://github.com/TigreGotico/chronologia/issues/1035)

---
[← Hindi](hi.md) · [Home](../index.md) · [Icelandic →](is.md)
