# Aragonese (`an`)

<!-- agent-hint
covers: where each construction of the Aragonese locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/an/lang.json, chronologia/locale/an/vocab.json, chronologia/extract/numlayer.py:NUMTAG_LANGS, test/nl_corpus_an/, test/test_xfail_open_issues_*.py
generated: no
verify: .venv/bin/python -m doctest docs/languages/an.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/an.md && .venv/bin/python -c 'exec("import re,sys\nfrom datetime import datetime\nimport chronologia as C\ndef mins(d):\n    return (\"%.6f\" % (d.total_seconds() / 60)).rstrip(\"0\").rstrip(\".\")\ndef rem(r):\n    return \" and \\x60%s\\x60 left over\" % r if r else \"\"\ndef out(rd, tx, lg, an):\n    f = getattr(C, rd)\n    r = f(tx, lg, anchor=an) if rd == \"extract_duration\" else f(tx, lg, an)\n    if rd == \"extract_timespan\":\n        if r is None: return \"no reading\"\n        return \"%s to %s%s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), r.span.end.datetime().strftime(\"%Y-%m-%d %H:%M\"), rem(r.remainder))\n    if rd == \"extract_duration\":\n        if r is None: return \"no length\"\n        return \"a length of %s min%s\" % (mins(r.duration), rem(r.remainder))\n    if rd == \"extract_event\":\n        if r is None: return \"no event\"\n        return \"start %s, length %s, %s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), \"none\" if r.duration is None else mins(r.duration) + \" min\", \"summary \\x60%s\\x60\" % r.summary if r.summary else \"no summary\")\n    if r is None: return \"no rule\"\n    return \"the rule \\x60%s\\x60%s\" % (r.recurrence.to_string(), rem(r.remainder))\n\np=sys.argv[1]\nt=open(p).read()\nm=re.search(r\"\\n## Known limits\\n(.*?)(?=\\n---\\n|\\Z)\",t,re.S)\nbad=0\nn=0\ntot=0\nfor ln in (m[1].split(\"\\n\") if m else []):\n    if \"Example (\" not in ln: continue\n    tot+=1\n    g=re.search(r\"Example \\(reader \\x60(\\w+)\\x60, lang \\x60([\\w-]+)\\x60, anchor (\\d{4}-\\d\\d-\\d\\d \\d\\d:\\d\\d)\\): \\x60([^\\x60]+)\\x60 gives (.+?)\\. \\[#\\d+\\]\",ln)\n    if not g:\n        bad=1\n        print(\"example line does not parse:\",ln[:80])\n        continue\n    n+=1\n    o=out(g[1],g[4],g[2],datetime.strptime(g[3],\"%Y-%m-%d %H:%M\"))\n    if o!=g[5]:\n        bad=1\n        print(\"limit differs\",g[4],\"|\",g[5],\"|\",o)\nprint(\"known limits checked:\",n,\"of\",tot)\nsys.exit(bad)\n")' docs/languages/an.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Aragonese (`an`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

Aragonese is a Pyrenean Romance language that sits between Spanish and Catalan and shares a great deal of vocabulary with both. That is the whole difficulty of the locale. A surface that looks Aragonese is very often simply Spanish. A surface that is genuinely Aragonese frequently differs from its Spanish cognate only by a letter or an accent. Every group below was therefore checked against an Aragonese source (the Aragonese Wiktionary, the Aragonese Wikipedia, or a dictionary those two cite) rather than against a Spanish one.

The locale carries Spanish spellings deliberately alongside the Aragonese ones. `día` sits next to `diya`, `año` next to `anyo`, `mediodía` next to `meydia`, `tarde` next to `tardi`. Written Aragonese is not standardised in practice and Castilian spellings appear constantly in real text, so accepting them costs nothing and refusing them would lose ordinary sentences.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('as tres e meya', "an", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T03:30:00', '')

## What ships

**Months.** `chinero`, `chunyo`, `chuliol`, `setiembre`, `aviento` and `deciembre` each have an Aragonese entry on the English Wiktionary. `aviento` is from Latin *adventus*, and Wiktionary's entry compares it with Asturian *avientu*. December ships both `aviento` and `deciembre`. The rest (`febrero`, `marzo`, `abril`, `mayo`, `agosto`, `octubre`, `noviembre`) are identical to their Spanish forms and are shipped as they stand.

**Weekdays.** `luns`, `miercres` and `dominche` are the three that separate Aragonese from Spanish. All three occur in Aragonese Wikipedia running text. `martes`, `chueves`, `viernes` and `sabado` have Aragonese Wiktionary entries. `chueves` is derived there from Latin *Iovis (dies)* with the variant `chuebes`.

**The date line** is `15 de chinero de 2020` (day, `de`, month, `de`, year) with an optional leading article. Day and month order is day-first.

**Relative offsets.** The past marker is `fa`, preposed: `fa tres diyas`, `fa un anyo`. The future is `en` or `dentro`, also preposed: `en tres diyas`, `dentro de tres diyas`. Both take the count-one quantifiers `un`, `una` and `uno`, so `fa un anyo` reads without a digit.

**The clock.** Minutes are added with `e` and subtracted with `menos`, the ordinary Ibero-Romance pattern: `as tres e meya` is 03:30, `as tres menos quarto` is 02:45. The half is `meya` or `meyo`, the quarter `quarto`. Noon is `meydia`, `meydiya` or `mediodía`, midnight is `meyanueyt` or `meyanuei`.

**The night band.** `de nueyt` is not a uniform twelve-hour shift. It is a band that crosses midnight: hours one through five stay in the small hours, hours six through eleven move to the evening, and twelve is midnight: `a la una de nueyt` is 01:00, `a las seis de nueyt` is 18:00, `a las once de nueyt` is 23:00, `a las doce de nueyt` is 00:00. The 5|6 cut is not from an Aragonese source. It is inherited from the sibling Ibero-Romance locales, whose boundary comes from the Spanish, Catalan and Portuguese reference dictionaries, and the locale file says so.

**Century and decade.** `sieglo` has an Aragonese Wiktionary entry, a semi-learned borrowing from Latin *saeculum*, sourced there to Bal Palazios' *Dizionario breu de a luenga aragonesa*. `decada` and `decenio` are not entries there (the Aragonese Wiktionary carries `década`/`decenio` only with Spanish sections) but both have Aragonese sections on the English Wiktionary, `decada` from Latin *decadem*, with the *Diccionario ortografico de l'aragonés* under further reading. That is the source the vocabulary file itself cites.

**The decade frame** is `os anyos 80`, the plural year noun with a two-digit number. Only the plural `anyos` reaches that slot: the singular `anyo` names one year and must not be read as a decade. The plural is sourced through the Wiktionary entry for `anyo`, which cites the *Aragonario, diccionario castellano-aragonés*.

**Markers.** `dimpués` and its variants for "after", `antis` and `denantes` for "before", `dende` for "since", `dica` and `entro a` for "until", `a partir de` for "from", `cada` for "every", `agora` and `ara` for the present. `dica` and `dende` have Aragonese sections on the English Wiktionary deriving them from Latin *de hinc ad* and *deinde*. The locative `en` used with a month name (`en chinero`) is sourced in the locale file to the dictionary of the Academia de l'Aragonés.

**The ordinal last** is `zaguer` and `zaguers`, so `lo zaguer luns d'octubre` is 30 October, read at 13:04 on 27 June 2017. `marker_ordlast` records no source for them.

**Habitual recurrence** is `cada luns`. Answered as a recurrence, this is the repeating Monday. Asked for a span, it comes back as the next Monday with `cada` left in the remainder.

## Weaker provenance

**`ivierno`.** The winter file lists `ivierno` and `hibierno`. Only `hibierno` has an entry on the Aragonese Wiktionary with a full noun paradigm. `ivierno` has no entry on the Aragonese Wiktionary and does not occur in the Aragonese Wikipedia. The English Wiktionary has it only as Old Spanish. It is the weakest surface on the page.

**`meyanueyt`, `pasadoman` and `antesdayere`** likewise returned no hits in Aragonese Wikipedia text and have no Wiktionary entry. They are transparent compounds of parts that are all attested (`meya` plus `nueyt`, `pasado` plus `man`, `antes de ayere`) but the compounds themselves were not found.

**`tardi` as an afternoon word.** It ships as the PM meridiem. Aragonese Wikipedia has it in quantity, but the great majority of those occurrences are the adverb "late", as in `mas tardi`. The afternoon noun reading is the one the locale needs and is the one less visible in the corpus.

**The 5|6 night cut** is transcribed from the sibling locales, not from an Aragonese source, as the locale file states.

**A claim in the locale file that does not check out.** The decade file says the Wiktionary entry for `decada` lists `decenio` as a synonym. That entry carries no synonym line. Both words are real and both have their own Aragonese entries. The cross-reference between them is not where the comment places it.

## What refuses

**Roman-numeral centuries.** `o sieglo XX` returns nothing, although Aragonese Wikipedia writes centuries that way constantly. `20 seclo`-style digit forms are what the century construction accepts.

**A trailing "before" or "after" on an offset.** `tres diyas antis` and `tres diyas dimpués` both return nothing. The offset orders take the marker before the count or after the unit, but the anchorless trailing reading of `antis` is not among them.

**A bare duration.** `meya hora` and `tres horas e meya` return nothing. A duration with no anchor is not a span.

## Known defects

These are wrong or lossy outputs, not refusals, and each is reproducible with `extract_timespan(text, "an", anchor=datetime(2017, 6, 27, 13, 4))`.

A leading bare `a` is stranded whenever `a las` introduces a time. `a las tres e meya` gives the right 03:30 but leaves `a` in the remainder. So do `a las tres e quarto` and `a las 15:30`. The at-marker file lists `las` but not the two-word `a las`, so the preposition orphans. The value is correct. The span does not cover the phrase.

`a las nueu de maitín` gives 09:00 and strands `maitín`. The morning file lists `maitin` unaccented, and the unaccented form parses cleanly, but Aragonese Wikipedia writes `maitín` far more often than `maitin`. The accented spelling is the common one and the locale does not accept it.

`trimestre 3 2020` returns the whole of 2020 with `trimestre 3` stranded. This is the worst shape a result can take: a plausible span over the wrong unit, with the words that named the real unit thrown away.

`a las tres i meya` returns 03:00 with `i meya` stranded. `i` is not an Aragonese conjunction and is not in the locale. The input is arguably not Aragonese. But the engine answers it with a wrong-hour span rather than refusing.

## Open questions for a native speaker

1. Is `ivierno` a real Aragonese spelling of winter, or should the locale ship only `hibierno`?
2. Are `meyanueyt`, `pasadoman` and `antesdayere` the ordinary words, and are there commoner variants?
3. Does the night band really turn at six, or at some other hour in Aragonese?
4. Is `tardi` used as a noun for the afternoon, or is `tardada` the noun and `tardi` only the adverb?
5. Which is the everyday word for today, `hue` or `huei`?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("an")
    True
    >>> span, rest = extract_timespan('as tres e meya', "an", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T03:30:00', '')
    >>> span, rest = extract_timespan('as tres menos quarto', "an", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T02:45:00', '')
    >>> span, rest = extract_timespan('a la una de nueyt', "an", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T01:00:00', '')
    >>> span, rest = extract_timespan('a las seis de nueyt', "an", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T18:00:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('o sieglo XX', "an", anchor) is None
    True
    >>> extract_timespan('tres diyas antis', "an", anchor) is None
    True
    >>> extract_timespan('tres diyas dimpués', "an", anchor) is None
    True
    >>> extract_timespan('meya hora', "an", anchor) is None
    True
    >>> extract_timespan('tres horas e meya', "an", anchor) is None
    True

## Known limits

Each line is an open issue with a strict `xfail` test for this language. The lines are grouped by topic. An example names the reader that produced it, the language and the anchor date, and shows what that reader gives on the test's own phrase.

- A part of the day after a clock or a weekday stays in the remainder. Example (reader `extract_timespan`, lang `an`, anchor 2017-06-27 13:04): `a las 9 d'o maitín` gives 2017-06-27 21:00 to 2017-06-27 21:01 and `maitín` left over. [#1200](https://github.com/TigreGotico/chronologia/issues/1200)

- A day word or a counted offset gives no reading. Example (reader `extract_timespan`, lang `an`, anchor 2017-06-27 13:04): `pasau manyana` gives 2017-06-28 00:00 to 2017-06-29 00:00 and `pasau` left over. [#992](https://github.com/TigreGotico/chronologia/issues/992)

- A word for next or last beside a season, month or week stays in the remainder. Example (reader `extract_timespan`, lang `an`, anchor 2017-06-27 13:04): `mes proximo` gives no reading. [#993](https://github.com/TigreGotico/chronologia/issues/993)

---
[← Arabic](ar.md) · [Home](../index.md) · [Armenian →](hy.md)
