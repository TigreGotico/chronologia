# Croatian (`hr`)

<!-- agent-hint
covers: where each construction of the Croatian locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/hr/lang.json, chronologia/locale/hr/*.voc, chronologia/extract/numlayer.py:NUMTAG_LANGS, test/nl_corpus_hr/, test/test_xfail_open_issues_*.py
generated: no
verify: .venv/bin/python -m doctest docs/languages/hr.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/hr.md && .venv/bin/python -c 'exec("import re,sys\nfrom datetime import datetime\nimport chronologia as C\ndef mins(d):\n    return \"%g\" % (d.total_seconds() / 60)\ndef rem(r):\n    return \" and \\x60%s\\x60 left over\" % r if r else \"\"\ndef out(rd, tx, lg, an):\n    f = getattr(C, rd)\n    r = f(tx, lg, anchor=an) if rd == \"extract_duration\" else f(tx, lg, an)\n    if rd == \"extract_timespan\":\n        if r is None: return \"no reading\"\n        return \"%s to %s%s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), r.span.end.datetime().strftime(\"%Y-%m-%d %H:%M\"), rem(r.remainder))\n    if rd == \"extract_duration\":\n        if r is None: return \"no length\"\n        return \"a length of %s min%s\" % (mins(r.duration), rem(r.remainder))\n    if rd == \"extract_event\":\n        if r is None: return \"no event\"\n        return \"start %s, length %s, summary \\x60%s\\x60\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), \"none\" if r.duration is None else mins(r.duration) + \" min\", r.summary)\n    if r is None: return \"no rule\"\n    return \"the rule \\x60%s\\x60%s\" % (r.recurrence.to_string(), rem(r.remainder))\n\np=sys.argv[1]\nt=open(p).read()\nm=re.search(r\"\\n## Known limits\\n(.*?)(?=\\n---\\n|\\Z)\",t,re.S)\nbad=0\nn=0\nfor ln in (m[1].split(\"\\n\") if m else []):\n    g=re.search(r\"Example \\(reader \\x60(\\w+)\\x60, lang \\x60([\\w-]+)\\x60, anchor (\\d{4}-\\d\\d-\\d\\d \\d\\d:\\d\\d)\\): \\x60([^\\x60]+)\\x60 gives (.+?)\\. \\[#\\d+\\]\",ln)\n    if not g: continue\n    n+=1\n    o=out(g[1],g[4],g[2],datetime.strptime(g[3],\"%Y-%m-%d %H:%M\"))\n    if o!=g[5]:\n        bad=1\n        print(\"limit differs\",g[4],\"|\",g[5],\"|\",o)\nprint(\"known limits checked:\",n)\nsys.exit(bad)\n")' docs/languages/hr.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Croatian (`hr`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

Croatian names the half hour for the hour that has not arrived. It does so with a bare cardinal: `pola devet` is 08:30 and `pola tri` is 02:30. That single fact separates it from most of its Slavic neighbours, where the same construction takes a declined ordinal agreeing with an elided hour noun (`půl deváté`, `pol deviatej`, `полдевятого`). Because the hour is an ordinary cardinal, the clock reads it as numtag reads it. Only the fraction word `pola` has to stay a word, so that it fills the clock's fraction slot. The same wiring serves Serbian, which spells the construction identically.

The second thing to know is that the locale's ordinal-scope grammar is declared as a replacement rather than an addition, and several readings the shared base grammar would have provided are absent because of it. Those are set out under *What refuses*.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('pola devet', "hr", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T08:30:00', '')

## What ships

**The date line** is little-endian, `DAY MONTH YEAR?`, matching the CLDR 47 `ca-gregorian` chart for `hr`: full `EEEE, d. MMMM y.`, long `d. MMMM y.`, medium `d. MMM y.`, short `dd. MM. y.`. The tokenizer runs with `ordinal_dot` and `dotted_date` on, and `lang.json` adds an "of"-linked order and a month-led one beside the plain day-led shape, so `15. siječnja 2020` and the spelled `petnaestog siječnja 2020` both resolve to the fifteenth of January. Compound days compose from a bare cardinal tens element and a declined unit, with or without the linking `i`: `dvadeset trećeg svibnja` and `dvadeset i trećeg svibnja` are both the twenty-third of May.

**Months** ship in three cases. The nominative (`siječanj`, `veljača`) is CLDR 47's `stand-alone` wide chart for `hr` word for word. The genitive that follows a day ordinal (`siječnja`, `veljače`) is the `format` wide chart, which is genitive throughout for Croatian. The locative that follows the preposition (`siječnju`, `veljači`) ships alongside them without a recorded source. November is the one adjectival month, `studeni`, and its oblique forms follow the adjective rather than the noun.

**Weekdays** ship in the nominative, which matches CLDR 47's wide weekday chart, with the accusative that a `u <weekday>` phrase takes for the three whose accusative differs (`srijedu`, `subotu`, `nedjelju`) and a genitive for each. No source is recorded for the choice of oblique forms. The masculine weekdays ship only nominative and genitive because their accusative is syncretic with the nominative.

**Day parts** are transcribed from the Unicode CLDR 47 day-period rules for `hr`, and all four bands ship. Each surface is the deictic adverb a phrase actually uses: `ujutro` (morning), `popodne` (afternoon), `navečer` and `uvečer` (evening), `noću` (night). Wiktionary's Serbo-Croatian entries carry `ujutro` as an adverb glossed "in the morning", `navečer` as an adverb glossed "in the evening, this evening", and `noću` as an adverb glossed "at night, by night, in the night" and derived there as the instrumental of `noć`. So `danas noću` runs from 21:00 to 04:00 and `sutra ujutro` from 04:00 to 12:00. The same words double as clock meridiem cues on an explicit hour (`ujutro` for AM, `popodne`, `poslijepodne` and `navečer` for PM) so `u 9 sati navečer` is 21:00 and `pola devet navečer` is 20:30.

**Relative offsets** are `prije` (ago) and `za` (in/after), with `u` carrying "in" over a calendar period. That last preposition is cited to its Serbo-Croatian Wiktionary entry, whose preposition sense list gives "in, at" with the locative and "to, into" with the accusative, each with a worked example (`biti u školi`, `ići u školu`).

**The emphatic day filler.** A bare genitive plural `dana` trailing a year, month or week count is the idiom `godinu dana`, `tjedan dana` (literally "a year of days", meaning exactly one year) and not a genuine extra day. It is read as filler, so `za godinu dana` is one year ahead and `prije tjedan dana` one week back, both to the minute. Croatian and Serbian are the only locales in the library that ship this surface at all.

**Determiners.** `prošli` and `prethodni` ("last, previous"), `sljedeći` and `idući` ("next"), `posljednji` and `zadnji` ("last of a series") and the demonstrative `ovaj` ("this") each ship a full paradigm rather than a nominative alone. The reason is that Croatian names a past year with the adverbial genitive `prošle godine` and a past week with either the accusative `prošli tjedan` or the genitive `prošlog tjedna`. The masculine genitive and dative carry both the short and the long variant (`-og`/`-oga`, `-om`/`-ome`). The neuter forms are shipped because the season nouns are neuter: `prošlo ljeto` and `prethodno proljeće` both resolve. The Hrvatski jezični portal declension tables for `prošli` and `prethodan` carry every form on file, including the `-omu` dative the locale does not need.

**Unit nouns** ship full paradigms for `godina`, `mjesec` and `tjedan`, the last with its fleeting-vowel stem (`tjedan` / `tjedna`). The genitive `godine` is what carries the adverbial `prošle/ove/sljedeće godine`, all three of which resolve to the whole calendar year.

**Era markers** are cited to two sources that agree. The Hrvatski pravopis of the Institut za hrvatski jezik prescribes the spaced Christian pair under its rule on abbreviations formed from an initial syllable (the rule lists `po. Kr. (poslije Krista)` and `pr. Kr. (prije Krista)` in exactly that wording) and the Hrvatski jezični portal entries for `p. Kr.` and `pr. n. e.` gloss each and name the other as its counterpart, giving the secular pair `pr. n. e.` / `n. e.` alongside. Both pairs ship, spaced and unspaced. `500 pr. Kr.`, `500 pr. n. e.` and `500 prije Krista` all resolve to the same year.

**The clock's toward-hour half.** `pola` plus the bare cardinal of the coming hour is the locale's only fractional clock surface, gated by `bare_half_to` in `lang.json` and read through an `at? FRACTION HOUR MERIDIEM? ZONE?` order. The optional leading preposition means `u pola devet` and `o pola devet` resolve with nothing left over, which the equivalent Czech and Slovenian orders do not manage. Two Wiktionary sources fix the direction with worked numeric examples: the Serbo-Croatian adverb `pola` carries `pola tri — 2:30` in its own sense list. The translation table under the English headword `half past`, whose example is "half past one", gives `pola dva` with the qualifier "used with the following hour". Both name the coming hour, and `pola tri` resolves to 02:30.

**`pola` and `pol` stay words.** numtag reads Croatian numbers in every case form (`numlayer_slavic.py`), and it reads `pola` and `pol` as the fraction 0.5. The fold keeps a fraction that numtag reads as a fraction as a word, so `pola` fills the clock's fraction slot. The duration reader reads the same words through the quantifier table: `pola sata` is thirty minutes, `sat i pol` ninety and `dva i pol sata` 150. `za pola sata` is thirty minutes after the anchor. numtag reads the short ordinal genitive (`trećeg`) and not the long one with the movable `a` (`trećega`). The fold reads the long form through the short one.

**Quarters and ISO weeks** resolve, with `kvartal` and `tromjesečje` as two quarter words and `tjedan` for the ISO week. `prvi kvartal 2020.` is the first quarter and `tjedan 12` the twelfth ISO week.

**Named days** span all five positions around the anchor: `prekjučer`, `jučer`, `danas`, `sutra`, `prekosutra`.

**Ranges** run `od A do B`, and the bare `A do B` shape works as well, so `od ponedjeljka do petka` and `od 1. do 5. svibnja` both resolve.

## Weaker provenance

**The oblique weekday and month forms** carry no citation. The nominatives and the format genitives are traceable to CLDR. But nothing on file says which case `srijedu` or `siječnju` is meant to serve, or whether the set shipped for each word is complete.

**`uvečer`** ships as an evening day part with no source of its own. The Wiktionary entry cited for the file is `navečer`, which lists `uvečer` only in its related-terms line, never as the lemma with a gloss of its own.

**`popodne` as an adverb.** The day-part file describes its surface as the adverb "in the afternoon". The Wiktionary entry it cites carries a noun sense and a noun declension and no adverb sense at all. The adverbial use rests on the CLDR day-period data rather than on that entry. It is the same shape of gap the Czech page records for its own evening word.

**`kvartal` and `tromjesečje`** ship as unqualified synonyms with no source distinguishing register, the same pair and the same silence the Bulgarian, Czech and Slovenian pages record for their own two quarter words.

**The determiner paradigms** are cited to the Hrvatski jezični portal's declension tables. The two locators recorded for `prošli` and `prethodan` resolve to exactly those entries with the full paradigm printed. The locators for `sljedeći`, `idući`, `posljednji`, `zadnji` and the `ovaj` series are generic (they name the portal and its search page rather than an entry) so those paradigms are attributed but not located.

## What refuses

**Several other scoped-ordinal readings, for the same reason.** The base grammar's "Nth weekday of a bare year" and "Nth weekday of this period" orders go with it. `prvi ponedjeljak 2020` does not return the first Monday of 2020. It returns next Monday and drops the year, which is a confident answer to a question nobody asked. `posljednja srijeda u mjesecu` returns next Wednesday, with `posljednja u mjesecu` stranded: the weekday is read. But the ordinal-last scoping is discarded.

**The final day of a month.** `prvi dan svibnja` resolves, because `ORD UNIT MONTH` is declared. `posljednji dan svibnja` does not, because no `ordlast UNIT MONTH` order is. The whole of May comes back instead, with `posljednji dan` stranded.

**The CLDR genitive of November.** `studenoga` is what the CLDR 47 `format` wide chart gives for the eleventh month, and only the shorter `studenog` ships. So `15. studenog 2020` is the fifteenth of November and `15. studenoga 2020` is the whole of 2020 with the day and month stranded.

**The two-word afternoon.** CLDR 47 gives `poslije podne` as the `format` spelling of the afternoon band and `popodne` as the `stand-alone` one. Only the one-word form ships. `danas poslije podne` therefore does not return this afternoon. It decomposes into the noon landmark and returns the single minute at 12:00.

**The singular hour noun on the clock.** `marker_oclock` holds only the plural `sati`. `u 9 sati` resolves cleanly while `u 1 sat` and `u 2 sata` (the counted forms Croatian requires for one and for two through four) resolve to the right hour but strand the noun.

## Open questions for a native speaker

1. Does the quarter take the same toward-hour direction as `pola` or the English one?
2. What case do the shipped oblique weekday and month forms mark, and is the set complete for each word?
3. Are `kvartal` and `tromjesečje` interchangeable for a calendar quarter, or does one belong to fiscal usage?
4. Does `uvečer` compete with `navečer` closely enough to earn a source of its own, and should it also be a PM clock cue? It is an evening day part but not a meridiem word, so `pola dvanaest navečer` binds and `pola dvanaest uvečer` strands.
5. Is `poslije podne` the spelling a speaker would type for the afternoon, or has `popodne` displaced it in ordinary writing?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("hr")
    True
    >>> span, rest = extract_timespan('pola devet', "hr", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T08:30:00', '')
    >>> span, rest = extract_timespan('pola tri', "hr", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T02:30:00', '')
    >>> span, rest = extract_timespan('u 9 sati navečer', "hr", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T21:00:00', '')
    >>> span, rest = extract_timespan('pola devet navečer', "hr", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T20:30:00', '')

## Known limits

Each line is an open issue with a strict `xfail` test for this language. The lines are grouped by topic. An example names the reader that produced it, the language and the anchor date, and shows what that reader gives on the test's own phrase.

- The preposition and the year noun stay in the remainder. Example (reader `extract_timespan`, lang `hr`, anchor 2017-06-27 13:04): `2024. godine` gives 2024-01-01 00:00 to 2025-01-01 00:00 and `godine` left over. [#1190](https://github.com/TigreGotico/chronologia/issues/1190)

---
[← Catalan](ca.md) · [Home](../index.md) · [Czech →](cs.md)
