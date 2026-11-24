# Asturian (`ast`)

<!-- agent-hint
covers: where each construction of the Asturian locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/ast/lang.json, chronologia/locale/ast/*.voc, chronologia/extract/numlayer.py:NUMTAG_LANGS, test/nl_corpus_ast/, test/test_xfail_open_issues_*.py
generated: no
verify: .venv/bin/python -m doctest docs/languages/ast.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/ast.md && .venv/bin/python -c 'exec("import re,sys\nfrom datetime import datetime\nimport chronologia as C\ndef mins(d):\n    return \"%g\" % (d.total_seconds() / 60)\ndef rem(r):\n    return \" and \\x60%s\\x60 left over\" % r if r else \"\"\ndef out(rd, tx, lg, an):\n    f = getattr(C, rd)\n    r = f(tx, lg, anchor=an) if rd == \"extract_duration\" else f(tx, lg, an)\n    if rd == \"extract_timespan\":\n        if r is None: return \"no reading\"\n        return \"%s to %s%s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), r.span.end.datetime().strftime(\"%Y-%m-%d %H:%M\"), rem(r.remainder))\n    if rd == \"extract_duration\":\n        if r is None: return \"no length\"\n        return \"a length of %s min%s\" % (mins(r.duration), rem(r.remainder))\n    if rd == \"extract_event\":\n        if r is None: return \"no event\"\n        return \"start %s, length %s, summary \\x60%s\\x60\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), \"none\" if r.duration is None else mins(r.duration) + \" min\", r.summary)\n    if r is None: return \"no rule\"\n    return \"the rule \\x60%s\\x60%s\" % (r.recurrence.to_string(), rem(r.remainder))\n\np=sys.argv[1]\nt=open(p).read()\nm=re.search(r\"\\n## Known limits\\n(.*?)(?=\\n---\\n|\\Z)\",t,re.S)\nbad=0\nn=0\nfor ln in (m[1].split(\"\\n\") if m else []):\n    g=re.search(r\"Example \\(reader \\x60(\\w+)\\x60, lang \\x60([\\w-]+)\\x60, anchor (\\d{4}-\\d\\d-\\d\\d \\d\\d:\\d\\d)\\): \\x60([^\\x60]+)\\x60 gives (.+?)\\. \\[#\\d+\\]\",ln)\n    if not g: continue\n    n+=1\n    o=out(g[1],g[4],g[2],datetime.strptime(g[3],\"%Y-%m-%d %H:%M\"))\n    if o!=g[5]:\n        bad=1\n        print(\"limit differs\",g[4],\"|\",g[5],\"|\",o)\nprint(\"known limits checked:\",n)\nsys.exit(bad)\n")' docs/languages/ast.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Asturian (`ast`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

Asturian is the thinnest-sourced of the Ibero-Romance locales here. Almost nothing in its vocabulary files carries a citation: the three Roman-calendar anchors name the Asturian Wikipedia, the night meridiem names the Spanish locale it was copied from. Every other file (weekdays, months, seasons, markers, units, eras) carries none at all. That is the fact a reader should hold onto, because the locale's neighbour is Spanish and a great many Asturian surfaces look like Spanish surfaces with the endings changed. Where this page says a word is attested, it means the word is listed in the *Diccionariu de la Llingua Asturiana* published by the Academia de la Llingua Asturiana, not that it resembles its Spanish cognate.

The other governing fact is that the Unicode day-period table has no Asturian row. Its authority for this language stops at the bare meridiem markers. No time-of-day band ships and `pela mañana`, `pela tarde` and `pela nueche` (the frames the Academia's own dictionary uses in its definitions) are not read as parts of the day. What `pela mañana` does instead is a defect, and it is listed below.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('les diez de la nueche', "ast", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T22:00:00', '')

## What ships

**Weekdays and months.** The month names are the Asturian ones (`xineru`, `xunetu`, `ochobre`, `payares`, `avientu`) with the Castilian-shaped `noviembre` and `diciembre` alongside the last two. The Asturian forms were confirmed in the Academia's dictionary, which dates the year as running from `l'un de xineru` to `el trenta y un d'avientu`, glosses October as the `mes de (les) castañes`, and puts All Souls' Day on the `día primeru de payares`. `llunes` and `vienres` are dictionary headwords, glossed as the first and fifth days of the week.

**The date line** is little-endian: `3 de xineru 1990`, `25 d'avientu`. The apostrophe form of `de` before a vowel is in the of-marker vocabulary, so `d'avientu` and `d avientu` both read.

**Relative offsets** run in both directions and in both orders. `hai` and `fai` count backward, `en` and `dientro` forward. `dempués` and `enantes` are dictionary headwords. `dientro` is one too. The dictionary lists `dientro de` as a locution under it.

**Last and next** follow their noun (the locale sets `marker_position: post`) as `pasáu` and `viniente`. `viniente` is not a headword in the dictionary but appears inside the entry for `añu`, in the locution `al otru añu, al añu siguiente o viniente`, which is where it was checked.

**Ranges** are `de … a …`, `del … al …`, `dende …` and `hasta …`, with `ente … y …` as the between-frame. `dende` and `hasta` are both dictionary headwords with the temporal sense the locale uses, `hasta` glossed with the clock example `Tuvimos hasta les cinco`.

**The clock** counts forward with `y` and backward with `menos`, and takes the feminine plural article the language uses for hours: `a les ocho`, `les cinco y media`, `les cinco menos cuartu`. That article is not decoration. The dictionary lemmatises the hour itself as `cinco, les`, glossed as the fifth hour from noon or from midnight.

**`de la nueche` is a band, not a shift.** `les diez de la nueche` is 22:00 and `les doce de la nueche` is midnight. The small hours one to five stay AM and the evening hours six to eleven are PM. The dictionary's `nueche` entry supports the span, glossing it as the stretch of time when there is no sunlight.

**Non-Gregorian calendars.** Asturian is one of six locales that carry French Republican month names (the others are English, French, Italian, Occitan and Romanian) and it also carries the Hebrew and Islamic civil months, the Japanese era names, a consulship marker and a `pridie` marker for Roman dates. What that costs is set out below.

**Eras and geological periods.** `44 adc` resolves, along with the spelled `enantes de Cristu`, an anno mundi marker, a Holocene era marker, a Julian day marker, a Unix time marker, and twenty-eight geological period names from the Archean to the Holocene.

**The Roman calendar anchors** ship in the Asturian vernacular forms `calendes`, `nones` and `idus`, with the Latin forms kept alongside, cited to the Asturian Wikipedia article *Calendariu romanu*. That article does contain all three, in one sentence, which was checked.

## Weaker provenance

**The night band's boundary is Spanish, not Asturian.** The night meridiem file says so in as many words: Asturian inherits the 5-versus-6 cut from the Spanish, Catalan and Portuguese siblings, whose boundary rests on the Spanish academy's dictionary, and native confirmation for Asturian is still open. This is the one place in the locale where a Spanish source is doing the work for an Asturian surface. It is declared rather than hidden.

**`fasta` is not in the Academia's dictionary.** The until-vocabulary ships `fasta` beside `hasta`. A search of the dictionary returns the `hasta` headword and nothing for `fasta`. It may be a regional variant the dictionary does not lemmatise. On the evidence gathered it is unattested.

**`quevien` is not attested as one word.** The next-marker ships the joined `quevien`, which the dictionary does not carry in any form. The two-word `que vien` parses anyway, so nothing is lost by the joined form being wrong, but nothing supports it either.

**The French Republican months are the French spellings, unadapted.** `brumaire`, `nivose`, `ventose` and the rest are exactly the forms the French locale ships, with no Asturian adaptation and no source. They also arrive without the ordinal-and-anchor guard the Latin dates get. A bare `brumaire` resolves to a month-long span in the Gregorian year. See the defects.

**`mediudía` is not the dictionary's noon word.** The noon landmark ships `mediudía` and `mediudia`. The word that appears throughout the Academia's definitions is `meudía`, which the locale does not carry at all, so `el meudía` returns nothing.

**Everything else is uncited.** Weekday names, season names, unit nouns, era spellings, the geological series, the Japanese era names and the Hebrew and Islamic month lists all ship without a recorded source. The seasons in particular are worth a native's eye: `seronda` for autumn and `branu` for summer are the distinctively Asturian words, both confirmed in the dictionary. But they ship beside the Castilian-shaped `otoñu` and `veranu`, which were not.

## Unchecked and broken citations

Both citations the locale carries hold. The Asturian Wikipedia *Calendariu romanu* contains `calendes`, `nones` and `idus`. The Spanish night-meridiem file that the Asturian one defers to does cite the Spanish academy's `noche` entry for the small-hours usage. The inherited boundary has a source, a source about Spanish.

The Academia de la Llingua Asturiana's dictionary is a POST-driven search with no per-word URL, so headwords are cited here by name rather than by link. Each word named above as attested was looked up individually.

## Known defects

Every one of these is reproduced against the anchor 2017-06-27 13:04 with `extract_timespan(text, "ast", anchor)`. They are wrong answers rather than refusals, and a wrong span with a stranded remainder is worse than nothing at all.

**A leading article is never claimed.** `el 3 de xineru` resolves the day and leaves `el` behind. `el 3 de marzu`, `el mediudía`, `la medianueche`, `nel añu 1990` and `en xineru` all do the same with their own leading word. The article vocabulary itself is generous (it folds in the preposition-plus-article fusions `del`, `de la`, `al` and `a la`, the indefinites and the demonstratives) but no calendar-date order offers an article slot for any of it to fill. The during-slot holds only `durante`. A month cannot absorb the locative `en` either.

**A decade frame.** `la década de 1980` returns the single year 1980 with `la década de` left in the remainder.

**Unadapted French Republican months bind unguarded.** `brumaire` alone returns 2017-10-22 to 2017-11-21, and `1 de brumaire` returns 2017-10-22. A Gregorian span for a Republican month name, with the Republican year nowhere in it. `18 de brumaire del añu VIII` returns 2017-11-08 and leaves `del añu VIII` in the remainder, which is the one case where the discarded text is the part that mattered.

**Declared quantifiers do not reach the offset rule.** The locale declares `par` and `pareya` as two and `dellos`, `delles`, `unos`, `unes` as three, but `un par de díes`, `dellos díes` and `un día` all return nothing.

**Two more return nothing where the vocabulary suggests they should.** `dientro de tres díes` and `dempués de xunu` both fail, as do `los años 80`, `el sieglu XX` and `ente selmana`.

## Open questions for a native speaker

1. Where does `de la nueche` stop being AM in Asturian specifically? The boundary in use is the Spanish one, and nothing Asturian has confirmed it.

2. What are the day-part bands? Nothing supplies them, so `pela mañana` and `pela tarde` cannot resolve to a stretch of the day at all.

3. Is `fasta` a real Asturian variant of `hasta`?

4. Is `meudía` or `mediudía` the standard noon word?

5. Are `otoñu` and `veranu` in ordinary use beside `seronda` and `branu`, and should both pairs ship?

6. Do the French Republican months have Asturian forms, and does anything Asturian actually use them?

7. Is `ente` or `entre` the ordinary between-preposition, and does `ente selmana` mean "on a weekday" as the dictionary's locution suggests?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("ast")
    True
    >>> span, rest = extract_timespan('les diez de la nueche', "ast", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T22:00:00', '')
    >>> span, rest = extract_timespan('pela mañana', "ast", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T06:00:00', '')
    >>> span, rest = extract_timespan('3 de xineru 1990', "ast", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('1990-01-03T00:00:00', '')
    >>> span, rest = extract_timespan("25 d'avientu", "ast", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-12-25T00:00:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('el meudía', "ast", anchor) is None
    True
    >>> extract_timespan('un par de díes', "ast", anchor) is None
    True
    >>> extract_timespan('dellos díes', "ast", anchor) is None
    True
    >>> extract_timespan('un día', "ast", anchor) is None
    True

## Known limits

Each line is an open issue with a strict `xfail` test for this language. The lines are grouped by topic. An example names the reader that produced it, the language and the anchor date, and shows what that reader gives on the test's own phrase.

- A clock with a fraction before a dated day reads only the hour. Example (reader `extract_timespan`, lang `ast`, anchor 2026-11-22 09:00): `a les diez y cuartu del día 14 de marzu` gives 2026-11-22 10:00 to 2026-11-22 10:01 and `y cuartu del día 14 de marzu` left over. [#1300](https://github.com/TigreGotico/chronologia/issues/1300)

- A date built from two parts loses one of them. [#1034](https://github.com/TigreGotico/chronologia/issues/1034)

---
[← Armenian](hy.md) · [Home](../index.md) · [Azerbaijani →](az.md)
