# Portuguese (`pt`)

<!-- agent-hint
covers: where each construction of the Portuguese locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/pt/lang.json, chronologia/locale/pt/*.voc, chronologia/extract/numlayer.py:NUMTAG_LANGS, test/nl_corpus_pt/, test/test_xfail_open_issues_*.py
generated: no
verify: .venv/bin/python -m doctest docs/languages/pt.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/pt.md && .venv/bin/python -c 'exec("import re,sys\nfrom datetime import datetime\nimport chronologia as C\ndef mins(d):\n    return \"%g\" % (d.total_seconds() / 60)\ndef rem(r):\n    return \" and \\x60%s\\x60 left over\" % r if r else \"\"\ndef out(rd, tx, lg, an):\n    f = getattr(C, rd)\n    r = f(tx, lg, anchor=an) if rd == \"extract_duration\" else f(tx, lg, an)\n    if rd == \"extract_timespan\":\n        if r is None: return \"no reading\"\n        return \"%s to %s%s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), r.span.end.datetime().strftime(\"%Y-%m-%d %H:%M\"), rem(r.remainder))\n    if rd == \"extract_duration\":\n        if r is None: return \"no length\"\n        return \"a length of %s min%s\" % (mins(r.duration), rem(r.remainder))\n    if rd == \"extract_event\":\n        if r is None: return \"no event\"\n        return \"start %s, length %s, summary \\x60%s\\x60\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), \"none\" if r.duration is None else mins(r.duration) + \" min\", r.summary)\n    if r is None: return \"no rule\"\n    return \"the rule \\x60%s\\x60%s\" % (r.recurrence.to_string(), rem(r.remainder))\n\np=sys.argv[1]\nt=open(p).read()\nm=re.search(r\"\\n## Known limits\\n(.*?)(?=\\n---\\n|\\Z)\",t,re.S)\nbad=0\nn=0\nfor ln in (m[1].split(\"\\n\") if m else []):\n    g=re.search(r\"Example \\(reader \\x60(\\w+)\\x60, lang \\x60([\\w-]+)\\x60, anchor (\\d{4}-\\d\\d-\\d\\d \\d\\d:\\d\\d)\\): \\x60([^\\x60]+)\\x60 gives (.+?)\\. \\[#\\d+\\]\",ln)\n    if not g: continue\n    n+=1\n    o=out(g[1],g[4],g[2],datetime.strptime(g[3],\"%Y-%m-%d %H:%M\"))\n    if o!=g[5]:\n        bad=1\n        print(\"limit differs\",g[4],\"|\",g[5],\"|\",o)\nprint(\"known limits checked:\",n)\nsys.exit(bad)\n")' docs/languages/pt.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Portuguese (`pt`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

No bare day-part word resolves in Portuguese. `manhã` on its own returns nothing. So do `tarde`, `noite` and `madrugada`, even though English, French and Italian all read their bare morning word. The obstacle is not the word but the slot: one grammar order binds the day-part slot. That slot holds every day-part surface the locale ships.

There is no way to admit `manhã` and refuse its siblings. Admitting the bare form would also admit bare `tarde`, which is equally the adverb *late*. Then `mais tarde`, `cheguei tarde` and `é tarde demais` would each answer an afternoon band for a sentence that names no time. A wrong span is worse than no span, so the bare order stays off for the whole locale. Nothing is unreachable as a result: `de manhã`, `pela manhã`, `a manhã` and `esta manhã` all resolve, and that framed form is what Portuguese actually says.

The other early fact is that `da noite` is a band, not a shift. `dez da noite` is 22:00 but `uma da noite` is 01:00. The small hours one to five stay AM, the evening hours six to eleven are PM, and twelve is midnight. The AM ceiling follows the `madrugada` band. The colloquial use of `da noite` for the small hours is cited to the Dicionário Priberam entry for *noite*. After a clock, `à noite` and `pela noite` read the same band as `da noite`: `às 8 à noite` is 20:00 and `às 1 à noite` is 01:00.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('dez da noite', "pt", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T22:00:00', '')

## What ships

**Weekdays** are the Portuguese ordinal-numbered series, and they ship both hyphen-glued and spaced (`terça`, `terça feira`, `terças feiras`) because the tokenizer splits on the hyphen. Months ship wide and abbreviated. Neither carries a recorded source.

**The date line** is `3 de outubro de 1990`, little-endian with `de` between the parts, optionally preceded by an article. Portuguese also has the day-label idiom `dia 3 de outubro`, where `dia` heads the date without being part of it. The vocabulary cites Cunha e Cintra's *Nova Gramática do Português Contemporâneo* and Priberam for `dia` as a temporal function word. It registers `dia` as its own marker. A leading `dia` joins the consumed text when the date it labels binds, and never when the date fails. A `dia` elsewhere in the sentence is untouched.

That matters most in range endpoints, where `do dia 3 de março até ao dia 5 de abril` carries two of them and both must be claimed with their dates. The slashed numeric date reads. The dotted one does not.

**Relative offsets** are `daqui a` forward and `há` backward. The forward frame needs an `offsetlink` slot (`a`, `à`, `às`, `ao`, `aos`, `de`) because Portuguese joins the marker to the count with a preposition that itself contracts with an article.

**The relative determiners** follow the noun, so the locale sets `marker_position: post`: `na segunda-feira passada`, `na próxima semana`.

**Ranges** are `de … a …`, `do … ao …`, `desde …`, `a partir de …` and `até …`, with `entre … e …` as the other frame. The vocabulary cites each of these to Priberam or to Ciberdúvidas da Língua Portuguesa. It cites Cunha e Cintra for the obligatory `de`+`o` and `a`+`o` contractions. The from-lead carries structural weight: `a` is a hyper-common Portuguese preposition. A bare `A a B` is only trusted as a range when a from-lead is present.

`até ao` and `até à` are registered as two-word surfaces of their own, tried before the bare `até`. Without them the scanner found the bare `até` first (it comes first in the sentence) and left the trailing `ao` an unclaimed token stranded in the remainder. A bare `até o dia` with no contraction is untouched, and `até` alone still matches when no contraction follows.

**The clock** has the same two toward-the-hour shapes as Spanish and keeps them apart for the same reason. The phrase `quatro menos um quarto` subtracts from the hour already named. The phrase `um quarto para as quatro` states the fraction first. Then it names the hour it heads for. Forward is `e`: `oito e meia`, `oito e um quarto`. The article vocabulary holds the indefinite articles `um` and `uma` so that the `um quarto` fraction reads. The vocabulary cites Ciberdúvidas' page on telling the time. `meio-dia` and `meia-noite` are points.

**Day parts** take their boundaries from the Unicode CLDR 47 day-period chart for `pt`, transcribed in `chronologia/dayparts.py`: `madrugada` `[00:00, 06:00)`, `manhã` `[06:00, 12:00)`, `tarde` `[12:00, 19:00)`, `noite` `[19:00, 24:00)`. The surfaces are cited to Priberam, which glosses `manhã` as the period between daybreak and midday. The vocabulary records that the entry marks no European/Brazilian split for these four words and that none is made here: both varieties say `manhã`, `tarde`, `noite` and `madrugada` alike. The frame is `pela`/`pelo` and their plurals, the contractions of `por` with the definite article, cited to Priberam.

**Fuzzy month parts** are `início de`, `meados de` and `fim de`, cutting the month into thirds.

**Quarters, ISO weeks, decades and eras.** `o primeiro trimestre de 2020`, `semana 12`, `os anos 80` and `44 a. C.` all resolve. An AD marker and a before-present marker resolve too. The phrase `a primeira metade de 2020` reads as the first half-year, with `metade` cited to Priberam.

**The Roman calendar anchors** ship in their Portuguese vernacular forms `calendas`, `nonas` and `idos`, cited to the Portuguese Wikipedia article *Calendário romano*.

**Business days** are jurisdiction-aware: the locale carries jurisdiction vocabularies for Brazil and Portugal alongside Germany, Spain, France, Great Britain and the United States. A working-day count can be asked against a named country's holiday calendar.

## Weaker provenance

The Roman calendar anchors rest on a Wikipedia article. That source is weaker than the Priberam and Cunha e Cintra citations behind the rest of the locale.

The month names, `sábado`, `domingo` and the weekday abbreviations except `sab` cite Unicode CLDR 47. The weekday names `segunda` to `sexta` and the seasons carry no recorded source. The locale sets `hemisphere` to null, so a season is not resolved to a southern-hemisphere reading for Brazilian Portuguese.

## What refuses

**Every bare day-part word.** `manhã`, `tarde`, `noite` and `madrugada` return nothing on their own. This is the locale's defining refusal and the reason is above.

**The dotted date.** `15.06.2020` returns nothing, and does not fall back to reading 2020 as a bare year. Portuguese writes the numeric date with slashes.

**A bare duration.** `quinze dias` returns nothing. A fortnight unit ships, but a quantity with no direction marker is still only a quantity.

## Open questions for a native speaker

1. Where does `da noite` stop being AM? The ceiling sits at five, following the `madrugada` band, but `cinco da manhã` and `cinco da madrugada` are both ordinary.
2. Should Brazilian Portuguese resolve the seasons to the southern hemisphere, and what would select that without a separate locale?
3. Do the day-part bands differ between European and Brazilian usage in ways that the shared CLDR row hides, in particular where `tarde` ends?
4. Are `calendas`, `nonas` and `idos` the forms Portuguese historical writing uses?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("pt")
    True
    >>> span, rest = extract_timespan('dez da noite', "pt", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T22:00:00', '')
    >>> span, rest = extract_timespan('uma da noite', "pt", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T01:00:00', '')
    >>> span, rest = extract_timespan('de manhã', "pt", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T06:00:00', '')
    >>> span, rest = extract_timespan('pela manhã', "pt", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T06:00:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('manhã', "pt", anchor) is None
    True
    >>> extract_timespan('tarde', "pt", anchor) is None
    True
    >>> extract_timespan('noite', "pt", anchor) is None
    True
    >>> extract_timespan('madrugada', "pt", anchor) is None
    True
    >>> extract_timespan('15.06.2020', "pt", anchor) is None
    True
    >>> extract_timespan('quinze dias', "pt", anchor) is None
    True

## Known limits

Each line is an open issue with a strict `xfail` test for this language. The lines are grouped by topic. An example names the reader that produced it, the language and the anchor date, and shows what that reader gives on the test's own phrase.

**Clocks and parts of the day**

- A part of the day with no day word answers the band that has already passed. Example (reader `extract_timespan`, lang `pt`, anchor 2023-01-15 21:00): `à tarde` gives 2023-01-15 12:00 to 2023-01-15 19:00. [#997](https://github.com/TigreGotico/chronologia/issues/997)

- A clock after `for`, `to` or `per` is not read, and a reschedule phrase reads the old time. Example (reader `extract_timespan`, lang `pt`, anchor 2017-06-27 13:04): `mova o meu alarme das sete para as oito` gives 2017-06-27 19:53 to 2017-06-27 19:54 and `mova o meu alarme das` left over. [#1008](https://github.com/TigreGotico/chronologia/issues/1008)

- A plural, adverbial or recurring part of the day is not read, so the hour reads in the wrong half. Example (reader `extract_timespan`, lang `pt`, anchor 2017-06-27 13:04): `lembra-me todas as manhãs de tomar o medicamento às 8` gives 2017-06-27 06:00 to 2017-06-27 12:00 and `lembra-me todas de tomar o medicamento às 8` left over. [#1009](https://github.com/TigreGotico/chronologia/issues/1009)

- A weekday range or list followed by a clock drops the clock or picks a past day. Example (reader `extract_timespan`, lang `pt`, anchor 2017-06-27 13:04): `me lembre de regar as plantas toda segunda e sexta às 8 da manhã` gives 2017-07-03 00:00 to 2017-07-04 00:00 and `me lembre de regar as plantas toda e sexta às 8 da manhã` left over. [#1010](https://github.com/TigreGotico/chronologia/issues/1010)

- A digit clock written with a space reads only the hour. Example (reader `extract_timespan`, lang `pt`, anchor 2017-06-27 13:04): `às 10 30` gives 2017-06-27 22:00 to 2017-06-27 22:01 and `30` left over. [#1012](https://github.com/TigreGotico/chronologia/issues/1012)

- An event with a noun before an evening clock reads a length of nine and a half hours. Example (reader `extract_event`, lang `pt`, anchor 2026-01-30 10:00): `jantar nove horas e meia de noite amanhã` gives start 2026-01-31 19:00, length 570 min, summary `jantar`. [#1026](https://github.com/TigreGotico/chronologia/issues/1026)

- A spelled clock reads as 14:03 and leaves the word for quarters. Example (reader `extract_timespan`, lang `pt`, anchor 2026-01-30 10:00): `duas horas e três quartos` gives 2026-01-30 14:03 to 2026-01-30 14:04 and `quartos` left over. [#1027](https://github.com/TigreGotico/chronologia/issues/1027)

- A clock with a dot between hour and minute gives no time. Example (reader `extract_timespan`, lang `pt`, anchor 2026-09-25 12:00): `às 8.30` gives no reading. [#1047](https://github.com/TigreGotico/chronologia/issues/1047)

- A part of the day said alone gives no reading. Example (reader `extract_timespan`, lang `pt`, anchor 2023-01-15 12:00): `tarde` gives no reading. [#1103](https://github.com/TigreGotico/chronologia/issues/1103)

- The meridiem after an abbreviated hour word is lost. Example (reader `extract_timespan`, lang `pt`, anchor 2026-11-22 09:00): `às 5 pm` gives 2026-11-22 17:00 to 2026-11-22 17:01 and `pm` left over. [#1312](https://github.com/TigreGotico/chronologia/issues/1312)

**Dates, ranges and weeks**

- A weekday mention drops its preposition or article, where a month keeps it. [#996](https://github.com/TigreGotico/chronologia/issues/996)

- A unit word with no number counts as one. Example (reader `extract_timespan`, lang `pt`, anchor 2017-06-27 13:04): `daqui a uma hora, horas vão ser` gives 2017-06-27 15:04 to 2017-06-27 16:04 and `vão ser` left over. [#1004](https://github.com/TigreGotico/chronologia/issues/1004)

- The late afternoon leaves `ao fim` in the remainder, and `na hora` or `dias de semana` reads as a length. [#1024](https://github.com/TigreGotico/chronologia/issues/1024)

- A date built from two parts loses one of them. [#1034](https://github.com/TigreGotico/chronologia/issues/1034)

- A spelled range of time units reads the first number as the year 2000. Example (reader `extract_event`, lang `pt`, anchor 2026-01-30 10:00): `de dois mil a três mil dias` gives start 2000-01-01 00:00, length 4.32e+06 min, summary ``. [#1053](https://github.com/TigreGotico/chronologia/issues/1053)

- A spelled year range with `the year` or `the years` and a word after it gives only the first year. Example (reader `extract_timespan`, lang `pt`, anchor 2026-01-30 10:00): `desde o ano dois mil até dois mil e dez em Lisboa` gives 2000-01-01 00:00 to 2026-01-30 10:00 and `até dois mil e dez em Lisboa` left over. [#1054](https://github.com/TigreGotico/chronologia/issues/1054)

- A day range with a relative-month end reads as the whole month. Example (reader `extract_timespan`, lang `pt`, anchor 2025-06-18 10:30): `desde o dia 3 até ao 5 do mês que vem` gives 2025-07-01 00:00 to 2025-08-01 00:00 and `3 5 do` left over. [#1230](https://github.com/TigreGotico/chronologia/issues/1230)

- The indefinite article before a day of a month reads as the first day. Example (reader `extract_timespan`, lang `pt`, anchor 2026-11-22 09:00): `um dia de março` gives 2027-03-01 00:00 to 2027-03-02 00:00. [#1306](https://github.com/TigreGotico/chronologia/issues/1306)

- A list of two days reads as a clock or as the wrong day. Example (reader `extract_timespan`, lang `pt`, anchor 2026-11-22 09:00): `no dia 14 e 15 de maio` gives 2026-12-14 00:00 to 2026-12-15 00:00 and `e 15 de maio` left over. [#1311](https://github.com/TigreGotico/chronologia/issues/1311)

- A year range after `o ano de` reads one end. Example (reader `extract_timespan`, lang `pt`, anchor 2026-11-22 09:00): `o ano de 2000 a 2005` gives 2000-01-01 00:00 to 2001-01-01 00:00 and `a 2005` left over. [#1327](https://github.com/TigreGotico/chronologia/issues/1327)

**Offsets, lengths and holidays**

- A count of hours or minutes before a holiday gives the day before at 00:00. Example (reader `extract_timespan`, lang `pt`, anchor 2026-09-25 12:00): `duas horas antes do natal` gives 2026-12-24 00:00 to 2026-12-25 00:00. [#1087](https://github.com/TigreGotico/chronologia/issues/1087)

- A clock with an offset from a holiday gives the wrong reading or the wrong order. Example (reader `extract_timespan`, lang `pt`, anchor 2026-09-25 12:00): `às 9 uma hora antes do natal` gives 2026-12-24 09:00 to 2026-12-24 09:01. [#1196](https://github.com/TigreGotico/chronologia/issues/1196)

- A phrase with `faz três anos` gives next March, not March three years ago. Example (reader `extract_timespan`, lang `pt`, anchor 2017-06-27 13:04): `em março faz três anos` gives 2018-03-01 00:00 to 2018-04-01 00:00 and `faz três anos` left over. [#1201](https://github.com/TigreGotico/chronologia/issues/1201)

- `century` and `millennium` give no length. Example (reader `extract_duration`, lang `pt`, anchor 2017-06-27 13:04): `1 milénio` gives no length. [#1203](https://github.com/TigreGotico/chronologia/issues/1203)

- A decimal count is dropped from the length. Example (reader `extract_duration`, lang `pt`, anchor 2017-06-27 13:04): `2.5 horas` gives no length. [#1204](https://github.com/TigreGotico/chronologia/issues/1204)

- A word `a` before the length leaves the remainder. Example (reader `extract_duration`, lang `pt`, anchor 2017-06-27 13:04): `a duas horas` gives a length of 120 min. [#1205](https://github.com/TigreGotico/chronologia/issues/1205)

**Recurrence**

- A plural part of the day before a clock gives no recurrence. Example (reader `extract_recurrence`, lang `pt`, anchor 2026-09-25 12:00): `nas manhãs às 8` gives no rule. [#1052](https://github.com/TigreGotico/chronologia/issues/1052)

- A clock range in a recurrence reads the end hour or a wrong minute. Example (reader `extract_recurrence`, lang `pt`, anchor 2026-11-22 09:00): `todas as segundas das 9 às 17` gives the rule `FREQ=WEEKLY;BYDAY=MO;BYHOUR=17` and `das 9` left over. [#1315](https://github.com/TigreGotico/chronologia/issues/1315)

- A weekday or clock range in a recurrence loses its end. [#1321](https://github.com/TigreGotico/chronologia/issues/1321)

- A clock before a dated day in a yearly rule becomes the day. Example (reader `extract_timespan`, lang `pt`, anchor 2026-11-22 09:00): `anualmente às 9 a 29 de fevereiro` gives 2028-02-29 09:00 to 2028-02-29 09:01 and `anualmente` left over. [#1329](https://github.com/TigreGotico/chronologia/issues/1329)

**Events, zones, business days and the API**

- The candidate reader does not raise in raise mode, where the event reader does. [#1276](https://github.com/TigreGotico/chronologia/issues/1276)

- A count of business days at the start or end of a month reads no span. Example (reader `extract_timespan`, lang `pt`, anchor 2026-11-22 09:00): `os primeiros 5 dias úteis do mês` gives no reading. [#1303](https://github.com/TigreGotico/chronologia/issues/1303)

- A working-day or day-of-month recurrence reads as every day. Example (reader `extract_recurrence`, lang `pt-PT`, anchor 2026-11-22 09:00): `às dez de cada dia 15` gives the rule `FREQ=DAILY;BYHOUR=10` and `15` left over. [#1310](https://github.com/TigreGotico/chronologia/issues/1310)

- Input typed in decomposed (NFD) form reads differently from the composed (NFC) form. Example (reader `extract_timespan`, lang `pt`, anchor 2017-06-27 06:04): `dia 5 de março de 2027` gives 2017-07-05 00:00 to 2017-07-06 00:00 and `de março de 2027` left over. [#1353](https://github.com/TigreGotico/chronologia/issues/1353)

---
[← Polish](pl.md) · [Home](../index.md) · [Romanian →](ro.md)
