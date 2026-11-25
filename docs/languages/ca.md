# Catalan (`ca`)

<!-- agent-hint
covers: where each construction of the Catalan locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/ca/lang.json, chronologia/locale/ca/*.voc, chronologia/extract/numlayer.py:NUMTAG_LANGS, test/nl_corpus_ca/, test/test_xfail_open_issues_*.py
generated: no
verify: .venv/bin/python -m doctest docs/languages/ca.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/ca.md 'un quart i mig de nou@08:22' && .venv/bin/python -c 'exec("import re,sys\nfrom datetime import datetime\nimport chronologia as C\ndef mins(d):\n    return (\"%.6f\" % (d.total_seconds() / 60)).rstrip(\"0\").rstrip(\".\")\ndef rem(r):\n    return \" and \\x60%s\\x60 left over\" % r if r else \"\"\ndef out(rd, tx, lg, an):\n    f = getattr(C, rd)\n    r = f(tx, lg, anchor=an) if rd == \"extract_duration\" else f(tx, lg, an)\n    if rd == \"extract_timespan\":\n        if r is None: return \"no reading\"\n        return \"%s to %s%s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), r.span.end.datetime().strftime(\"%Y-%m-%d %H:%M\"), rem(r.remainder))\n    if rd == \"extract_duration\":\n        if r is None: return \"no length\"\n        return \"a length of %s min%s\" % (mins(r.duration), rem(r.remainder))\n    if rd == \"extract_event\":\n        if r is None: return \"no event\"\n        return \"start %s, length %s, %s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), \"none\" if r.duration is None else mins(r.duration) + \" min\", \"summary \\x60%s\\x60\" % r.summary if r.summary else \"no summary\")\n    if r is None: return \"no rule\"\n    return \"the rule \\x60%s\\x60%s\" % (r.recurrence.to_string(), rem(r.remainder))\n\np=sys.argv[1]\nt=open(p).read()\nm=re.search(r\"\\n## Known limits\\n(.*?)(?=\\n---\\n|\\Z)\",t,re.S)\nbad=0\nn=0\ntot=0\nfor ln in (m[1].split(\"\\n\") if m else []):\n    if \"Example (\" not in ln: continue\n    tot+=1\n    g=re.search(r\"Example \\(reader \\x60(\\w+)\\x60, lang \\x60([\\w-]+)\\x60, anchor (\\d{4}-\\d\\d-\\d\\d \\d\\d:\\d\\d)\\): \\x60([^\\x60]+)\\x60 gives (.+?)\\. \\[#\\d+\\]\",ln)\n    if not g:\n        bad=1\n        print(\"example line does not parse:\",ln[:80])\n        continue\n    n+=1\n    o=out(g[1],g[4],g[2],datetime.strptime(g[3],\"%Y-%m-%d %H:%M\"))\n    if o!=g[5]:\n        bad=1\n        print(\"limit differs\",g[4],\"|\",g[5],\"|\",o)\nprint(\"known limits checked:\",n,\"of\",tot)\nsys.exit(bad)\n")' docs/languages/ca.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Catalan (`ca`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

Know this first. Catalan counts quarter hours toward the hour that is coming, not away from the hour that has passed.

`dos quarts de nou` is 08:30, not 09:30 and not 08:15. It is the second of the four quarters leading up to nine. `un quart de nou` is 08:15 and `tres quarts de nou` is 08:45. The vocabulary gives this its own slot, `marker_quarters`, holding `quart` and `quarts`. The clock grammar leads with a dedicated order (`QUARTS quarters of HOUR`) so the count is read before the hour it counts toward. No other locale in the library ships a `marker_quarters` file. The construction has no equivalent to borrow from, and the reading survives a day-part frame, so `dos quarts de nou del vespre` is 20:30.

The second thing is `de la nit`. It is not a uniform twelve-hour shift but a band that crosses midnight: `les deu de la nit` is 22:00, `la una de la nit` is 01:00, and `les dotze de la nit` is midnight. The small hours one to five stay AM, the evening hours six to eleven are PM, and twelve is midnight. The AM ceiling follows the `matinada` band. The colloquial reading is cited in the vocabulary to the Institut d'Estudis Catalans' *Diccionari de la llengua catalana* (DIEC2) under *nit*.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('dos quarts de nou', "ca", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T08:30:00', '')

## What ships

**Weekdays and months** ship wide and abbreviated, and the two-letter weekday abbreviations `dl dt dc dj dv ds dg` ship as their own vocabulary. The vocabulary cites Unicode CLDR 47 for both groups.

**The date line** is `el 3 d'octubre de 1990`, little-endian, with the article optional and `de` between the parts. The article is optional inside the date grammar itself rather than being stripped beforehand, which is what lets `el 3 d'octubre` and `3 d'octubre` both come back clean. The slashed numeric form reads. The dotted one does not.

**Relative offsets** are `dins`, `dintre` and `en` forward and `fa` backward, with `enrere` and `endarrere` as trailing past markers. The grammar takes both the marker-first and the count-first order.

**The relative determiners** follow the noun (`el dilluns passat`, `la setmana que ve`, `el dilluns vinent`) which is why the locale sets `marker_position: post`.

**Ranges** carry the fullest citation record in the locale. The `from` lead is `de`, `des de`, `del` or `a partir de` and the `to` boundary is `a`, `fins a`, `fins` or `al`. The vocabulary attributes each one to a specific IEC work. DIEC2 gives `de` and `a` as correlative point-of-departure and point-of-arrival prepositions. DIEC2 and the *Gramàtica essencial de la llengua catalana* (GEIEC) give `fins` as a limit of time.

Optimot covers `a partir de`. The IEC *Gramàtica de la llengua catalana*, section 16.3, covers the obligatory contractions `del` and `al`. The from-lead matters structurally: `a` is a hyper-common preposition. A bare `A a B` is only trusted as a range when a from-lead is present. `entre … i …` is the other frame, cited to DIEC2 under *entre*.

**The clock** subtracts with `menys` (`les quatre menys quart` is 03:45) and adds with `i`: `les vuit i mitja`, `les vuit i quart`. `migdia` and `mitjanit` are points.

**Day parts** are six bands, more than any locale but Tamil, and German matches that count. The bands come from the Unicode CLDR 47 day-period chart for `ca`, transcribed in `chronologia/dayparts.py`. The `matinada` is `[00:00, 06:00)`, the `matí` `[06:00, 12:00)`, the `migdia` an hour of its own at `[12:00, 13:00)`, the `tarda` `[13:00, 19:00)`, the `vespre` `[19:00, 21:00)` and the `nit` `[21:00, 24:00)`. Two of those cuts are worth naming. Catalan opens the afternoon at 13:00, after an hour-wide noon.

Only German and Galician carve a noon band the same way, and Spanish runs its `tarde` straight from twelve. Catalan holds the evening open until 21:00 before the night starts. Among the locales whose last band runs to midnight, only Galician and Basque start it as late. The `vespre` makes room for that. The *Gran diccionari de la llengua catalana* defines it as the "primeres hores de la nit". That is the early evening, and Spanish has no separate word for it.

The `migdia` band ships no day-part vocabulary of its own, so `al migdia` reaches you as the noon clock landmark, 12:00, rather than as the hour-wide span.

**Fuzzy month parts** are `principis de`, `mitjan` and `finals de`, cutting the month into thirds.

**Quarters, ISO weeks, decades and eras.** `el primer trimestre de 2020`, `setmana 12`, `els anys 80`, `els anys vuitanta`, `44 aC` and `1990 dC` all resolve. A before-present marker ships. `la primera meitat de 2020` reads as the first half-year, with `meitat` cited to DIEC2. The plural year noun `anys` has its own file, apart from the singular `any`, because the *Gran diccionari* glosses `els anys vint` as the decade, while `l'any 1931` names a single year. With two files, the wrong reading cannot bind.

**Holidays** resolve: `Nadal` comes back as 25 December, by way of the Andorran civil-holiday table, Catalan being Andorra's official language.

**The ordinal last** is `últim`, `última`, `ultim`, `ultima`, `darrer`, `darrera`, `darrers` and `darreres`. `el darrer dilluns d'octubre` is 30 October and `l'últim dia de març` is 31 March, both read at 13:04 on 27 June 2017. The `darrer` forms in `marker_ordlast.voc` record no source.

**The Roman calendar anchors** ship in their Catalan vernacular forms `calendes`, `nones` and `ides`, cited to the Catalan Wikipedia article *Calendari romà*.

**Habitual recurrence** is `cada dilluns` or `tots els dilluns`. Answered as a recurrence, these are the repeating Mondays. Asked for a span, they come back as the next Monday with the quantifier left in the remainder.

## Weaker provenance

The seasons carry no recorded source. The weekday and month names cite Unicode CLDR 47. The locale sets `hemisphere` to null, so a season never resolves to a southern-hemisphere reading.

The Roman calendar anchors rest on a Wikipedia article, weaker than the IEC works the rest of the locale is built on.

The DIEC2 citations name entries on a site that serves its dictionary bodies from a script rather than in the page. The entries are not quoted as written text. The *Gran diccionari de la llengua catalana* corroborates them where the same words appear.

It glosses *entre* as "en el temps que separa dos moments, dos esdeveniments". It glosses *meitat* as "cadascuna de les dues parts iguals … en què és dividit un tot". The Optimot and *Gramàtica de la llengua catalana* locators are named on trust and are listed here as unchecked.

## What refuses

**The dotted date.** `15.06.2020` returns nothing and does not fall back to reading 2020 as a lone year. Catalan writes the numeric date with slashes.

**A bare duration.** `quinze dies` returns nothing. A fortnight unit ships, but a quantity with no direction marker is still only a quantity.

**Half a unit.** `fa mitja hora` returns nothing. `mitja` and `mig` are declared as the half quantifier. But the relative-offset grammar has no quantifier slot for them to fill. Only a bare numeral opens an offset.

**Roman-numeral centuries.** `el segle XX` returns nothing.

**Weekday abbreviations on their own.** `dj` returns nothing. The abbreviations are only reachable inside a larger date.

## Known defects

These are wrong answers, not refusals, and each is reproduced with `extract_timespan(text, "ca", anchor=datetime(2017, 6, 27, 13, 4))`.

`idus de març` comes back as the whole of March with `idus de` stranded. The Catalan Wikipedia article that the anchors cite gives the day as "Idus o Ides". Only `ides` ships. `ides de març` is correct at 15 March while its equally attested twin silently widens to the month.

`el 1r de gener` comes back as the whole of January with `el 1r de` stranded, where `el primer de gener` resolves to 1 January. The ordinal suffix `r` is declared, but the abbreviated ordinal does not reach the day slot.

`fins al 12 de juny` and `abans del 5 de juny` push their bound into 2018 while the other end stays at the anchor, producing a span nearly a year long. The future preference is applied to the bound in isolation rather than relative to the open end.

## Open questions for a native speaker

1. Where does `de la nit` stop being AM? The ceiling follows the `matinada` band at five, but `les cinc del matí` and `les cinc de la matinada` are both ordinary Catalan.
2. Should `dos quarts` accept a bare `quarts de nou` without a count, and is the half-quarter (`un quart i mig de nou`, 08:22 or 08:23) worth reading?
3. Is `darrer` in `el darrer dilluns d'octubre` the ordinary written form, or is `últim` the one to prefer once both are accepted?
4. Does the `migdia` band want a day-part surface of its own, so that `al migdia` names the hour rather than the point?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("ca")
    True
    >>> span, rest = extract_timespan('dos quarts de nou', "ca", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T08:30:00', '')
    >>> span, rest = extract_timespan('un quart de nou', "ca", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T08:15:00', '')
    >>> span, rest = extract_timespan('tres quarts de nou', "ca", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T08:45:00', '')
    >>> span, rest = extract_timespan('dos quarts de nou del vespre', "ca", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T20:30:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('15.06.2020', "ca", anchor) is None
    True
    >>> extract_timespan('quinze dies', "ca", anchor) is None
    True
    >>> extract_timespan('fa mitja hora', "ca", anchor) is None
    True
    >>> extract_timespan('el segle XX', "ca", anchor) is None
    True
    >>> extract_timespan('dj', "ca", anchor) is None
    True

## Known limits

Each line is an open issue with a strict `xfail` test for this language. The lines are grouped by topic. An example names the reader that produced it, the language and the anchor date, and shows what that reader gives on the test's own phrase.

**Clocks and parts of the day**

- A plural, adverbial or recurring part of the day is not read, so the hour reads in the wrong half. Example (reader `extract_timespan`, lang `ca`, anchor 2017-06-27 13:04): `recorda'm que vagi a la feina els matins a les 8` gives 2017-06-27 20:00 to 2017-06-27 20:01 and `recorda'm que vagi a la feina els matins` left over. [#1009](https://github.com/TigreGotico/chronologia/issues/1009)

- An approximate clock such as `about nine` is not read. Example (reader `extract_timespan`, lang `ca`, anchor 2017-06-27 13:04): `avisa'm de dilluns a divendres al matí cap a les 7` gives 2017-07-03 00:00 to 2017-07-04 00:00 and `avisa'm de a divendres al matí cap a les 7` left over. [#1011](https://github.com/TigreGotico/chronologia/issues/1011)

- A clock with a dot between hour and minute gives no time. Example (reader `extract_timespan`, lang `ca`, anchor 2026-09-25 12:00): `a les 8.30` gives no reading. [#1047](https://github.com/TigreGotico/chronologia/issues/1047)

- A count later in the sentence drops the clock. Example (reader `extract_timespan`, lang `ca-es`, anchor 2026-09-25 12:00): `demà a les 3 de la tarda compra les 3 coses` gives 2026-09-26 00:00 to 2026-09-27 00:00 and `a les 3 de la tarda compra les 3 coses` left over. [#1199](https://github.com/TigreGotico/chronologia/issues/1199)

- A day-labelled range start next to a clock with a day part reads as an hour. Example (reader `extract_timespan`, lang `ca`, anchor 2026-01-30 10:00): `entre el dia 10 i les 8 del vespre` gives 2026-01-30 22:00 to 2026-01-31 20:01. [#1229](https://github.com/TigreGotico/chronologia/issues/1229)

- A clock with a fraction before a dated day reads only the hour. Example (reader `extract_timespan`, lang `ca`, anchor 2026-11-22 09:00): `a les deu i quart del dia 14 de març` gives 2026-11-22 10:00 to 2026-11-22 10:01 and `i quart del dia 14 de març` left over. [#1300](https://github.com/TigreGotico/chronologia/issues/1300)

**Dates, ranges and weeks**

- A date built from two parts loses one of them. Example (reader `extract_timespan`, lang `ca`, anchor 2017-06-27 00:00): `Toca satanic black metal 2 dies per a aquest divendres` gives 2017-06-30 00:00 to 2017-07-01 00:00 and `Toca satanic black metal 2 dies per a` left over. [#1034](https://github.com/TigreGotico/chronologia/issues/1034)

- The range lead `des del` reads the wrong span. Example (reader `extract_timespan`, lang `ca`, anchor 2026-01-30 10:00): `des del 3 fins al 5 de març` gives 2025-12-01 00:00 to 2026-03-06 00:00 and `3` left over. [#1225](https://github.com/TigreGotico/chronologia/issues/1225)

- A day range with a relative-month end reads as the whole month. Example (reader `extract_timespan`, lang `ca`, anchor 2026-01-30 10:00): `entre el dia 3 i el 5 del mes que ve` gives 2026-02-01 00:00 to 2026-03-01 00:00 and `3 el 5 del` left over. [#1230](https://github.com/TigreGotico/chronologia/issues/1230)

- The indefinite article before a day of a month reads as the first day. Example (reader `extract_timespan`, lang `ca`, anchor 2026-11-22 09:00): `un dia de març` gives 2027-03-01 00:00 to 2027-03-02 00:00. [#1306](https://github.com/TigreGotico/chronologia/issues/1306)

**Offsets, lengths and holidays**

- A count of hours or minutes before a holiday gives the day before at 00:00. Example (reader `extract_timespan`, lang `ca`, anchor 2026-09-25 12:00): `un quart d'hora abans de nadal` gives 2026-12-24 00:00 to 2026-12-25 00:00 and `un quart` left over. [#1087](https://github.com/TigreGotico/chronologia/issues/1087)

**Events, zones, business days and the API**

- A clock preposition, a count of hours or a date word leaves the part of the day in the event summary. Example (reader `extract_timespan`, lang `ca`, anchor 2026-01-30 10:00): `a dues hores a la tarda demà` gives 2026-01-31 02:00 to 2026-01-31 02:01 and `tarda` left over. [#1060](https://github.com/TigreGotico/chronologia/issues/1060)

- A bare clock with a zone skips the 12-hour rule. Example (reader `extract_timespan`, lang `ca`, anchor 2017-06-27 13:04): `abans de les 9:30 utc` gives 2017-06-27 13:04 to 2017-06-28 09:31. [#1254](https://github.com/TigreGotico/chronologia/issues/1254)

- A working-day or day-of-month recurrence reads as every day. Example (reader `extract_recurrence`, lang `ca-ES`, anchor 2026-11-22 09:00): `cada dia laborable a les 9` gives the rule `FREQ=DAILY;BYHOUR=9` and `laborable` left over. [#1310](https://github.com/TigreGotico/chronologia/issues/1310)

---
[← Bulgarian](bg.md) · [Home](../index.md) · [Croatian →](hr.md)
