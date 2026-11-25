# Indonesian (`id`)

<!-- agent-hint
covers: where each construction of the Indonesian locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/id/lang.json, chronologia/locale/id/vocab.json, chronologia/extract/numlayer.py:NUMTAG_LANGS, test/nl_corpus_id/, test/test_xfail_open_issues_*.py
generated: no
verify: .venv/bin/python -m doctest docs/languages/id.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/id.md && .venv/bin/python -c 'exec("import re,sys\nfrom datetime import datetime\nimport chronologia as C\ndef mins(d):\n    return (\"%.6f\" % (d.total_seconds() / 60)).rstrip(\"0\").rstrip(\".\")\ndef rem(r):\n    return \" and \\x60%s\\x60 left over\" % r if r else \"\"\ndef out(rd, tx, lg, an):\n    f = getattr(C, rd)\n    r = f(tx, lg, anchor=an) if rd == \"extract_duration\" else f(tx, lg, an)\n    if rd == \"extract_timespan\":\n        if r is None: return \"no reading\"\n        return \"%s to %s%s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), r.span.end.datetime().strftime(\"%Y-%m-%d %H:%M\"), rem(r.remainder))\n    if rd == \"extract_duration\":\n        if r is None: return \"no length\"\n        return \"a length of %s min%s\" % (mins(r.duration), rem(r.remainder))\n    if rd == \"extract_event\":\n        if r is None: return \"no event\"\n        return \"start %s, length %s, %s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), \"none\" if r.duration is None else mins(r.duration) + \" min\", \"summary \\x60%s\\x60\" % r.summary if r.summary else \"no summary\")\n    if r is None: return \"no rule\"\n    return \"the rule \\x60%s\\x60%s\" % (r.recurrence.to_string(), rem(r.remainder))\n\np=sys.argv[1]\nt=open(p).read()\nm=re.search(r\"\\n## Known limits\\n(.*?)(?=\\n---\\n|\\Z)\",t,re.S)\nbad=0\nn=0\ntot=0\nfor ln in (m[1].split(\"\\n\") if m else []):\n    if \"Example (\" not in ln: continue\n    tot+=1\n    g=re.search(r\"Example \\(reader \\x60(\\w+)\\x60, lang \\x60([\\w-]+)\\x60, anchor (\\d{4}-\\d\\d-\\d\\d \\d\\d:\\d\\d)\\): \\x60([^\\x60]+)\\x60 gives (.+?)\\. \\[#\\d+\\]\",ln)\n    if not g:\n        bad=1\n        print(\"example line does not parse:\",ln[:80])\n        continue\n    n+=1\n    o=out(g[1],g[4],g[2],datetime.strptime(g[3],\"%Y-%m-%d %H:%M\"))\n    if o!=g[5]:\n        bad=1\n        print(\"limit differs\",g[4],\"|\",g[5],\"|\",o)\nprint(\"known limits checked:\",n,\"of\",tot)\nsys.exit(bad)\n")' docs/languages/id.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Indonesian (`id`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

Indonesian is isolating: nouns do not inflect for number, verbs do not conjugate, and direction is carried entirely by trailing particles. `lalu` closes a phrase in the past, `lagi` closes one in the future. Both sit after the counted duration (`3 hari lalu`, `3 hari lagi`) never before it. The same postposed pattern runs through the whole locale: `depan` (next) and `lalu` (last) follow the noun they modify (`kuartal depan`, `minggu lalu`). The ordinal in a scoped phrase follows its noun too (`abad ketiga`, `kuartal ketiga`), the reverse of the Romance "third quarter" order.

The clock names the hour **not yet reached**. `setengah tiga` is 02:30, the half *before* three, not the half past two. This is the German-style toward-hour reading. *Kamus Besar Bahasa Indonesia* (KBBI) glosses `setengah jam` as "half an hour," which fixes the fraction but not its clock direction. The toward-hour reading is corroborated across Indonesian usage sources. But a KBBI/DBP-canonical clock-reading passage was not obtained. The locale's own `clock_fraction_30` records that honestly rather than overstating the citation.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('setengah tiga', "id", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T02:30:00', '')

## What ships

**Day parts** come from the Unicode CLDR 47 day-period rule set for `id`, transcribed in `chronologia/dayparts.py`: `pagi` (morning) `[00:00, 10:00)`, `siang` (midday/early afternoon) `[10:00, 15:00)`, `sore` (late afternoon/evening) `[15:00, 18:00)` and `malam` (night) `[18:00, 00:00)`. Each surface is the single noun Wiktionary lists for the band (`pagi`, `siang`, `sore`, `malam`) and a worked test pins each one: `pagi` on its own spans `[00:00, 10:00)`, `kemarin sore` spans the previous day's `[15:00, 18:00)`, `besok siang` the next day's `[10:00, 15:00)`.

**A clock hour spoken with `malam` is a midnight-crossing band, not a flat PM shift.** `pukul satu malam` ("one at night") is 01:00, not 13:00. `pukul sebelas malam` ("eleven at night") is 23:00. Twelve is midnight. Hours one through five stay in the morning half, hours six through eleven go to the evening half, because `malam` in ordinary speech covers both the tail of one day and the small hours of the next. The resolver band-splits on this rule, and the two clock-word markers (`pukul`, `jam`) both carry it. Source: Wiktionary, `malam`, plus the CLDR night band `[18:00, 00:00)` that fixes where the evening half of the word begins.

**Named days** are `kemarin lusa` / `kemarin dulu` / `kemarin dahulu` (day before yesterday), `kemarin` (yesterday), `hari ini` (today), `besok` (tomorrow) and `lusa` (day after tomorrow). Five distinct words, not a composed offset, matching the semantic-parity test that resolves each against its English equivalent.

**Weekdays ship with an optional classifier.** KBBI defines `Senin` as "hari ke-2 dalam jangka waktu satu minggu" (day 2 of the week) and glosses every other weekday the same way, with `hari` (day) as part of the entry. `hari Senin` ships as a name in its own right beside bare `Senin`. Carrying the classifier form is what keeps `setiap hari Senin` (every Monday) from losing the weekday when `setiap hari` (every day) is read first. Both readings are real Indonesian, and the locale needs both surfaces to tell them apart.

**The date line** is day, month name, optional year (`17 Agustus 1945`) with month names from CLDR 47's `id` `ca-gregorian.json`. `ordinal_dot` is off: Indonesian does not write the dotted ordinal day.

**Relative offsets** postpose their direction marker: `NUM UNIT lalu` for the past, `NUM UNIT lagi` for the future: `3 hari lalu`, `5 tahun lagi`. `depan` (next) and `lalu` (last, reused from the same past marker) attach after a scoped noun: `kuartal depan`, `minggu lalu`.

**Eras** are `m` for *masehi* (CE/AD) and `sm` for *sebelum masehi* (BCE/BC), both trailing the year: `1492 m`, `44 sm`.

**Quarters** postpose the ordinal after `kuartal`: `kuartal ketiga` reads as Q3 of the anchor year, numtag reads the spelled ordinal. The year form uses the digit instead (`kuartal 3 2026`) and `Q3 2026` also reads. `kuartal ini` / `depan` / `lalu` resolve the current, next and previous quarter relative to the anchor.

**Century and decade** follow the same postposed-ordinal shape as the quarter: `abad ketiga` is the third century. The digit-plus-hyphen form `abad ke-20` also resolves, the tokenizer splitting the `ke-` prefix from the digit. KBBI defines `abad` as a hundred-year span and `dekade` as `masa 10 tahun` (a ten-year span), equating it with the Sanskrit-derived synonym `dasawarsa` (*dasa* "ten" + *warsa* "year"). Both decade words ship. A relative-offset century or decade (`N abad lalu`) steps the anchor back by whole calendar months (1200 per century, 120 per decade) rather than by a fixed year count, so month-length irregularities do not shift the answer.

**ISO weeks** use `minggu N` or `pekan N`, both meaning "week". `minggu` is also the ordinary word for the calendar unit "week," while the weekday Sunday is registered separately as `ahad` precisely so that `minggu` never has to disambiguate between "week" and "Sunday" in this locale's grammar.

**Ranges** are `antara A dan B` (between, KBBI: "menyatakan hal berada di tengah dua batas") for a closed interval, and `dari A sampai/hingga B` (from, KBBI: "menyatakan asal atau titik permulaan") for the same shape with an explicit lead-in. `sebelum X` (before, KBBI: "lebih dahulu (waktunya) daripada") opens the range from the anchor to the end of X when X is in the future, mirroring how Spanish `antes de` and English `before` are read elsewhere in this codebase.

**Fuzzy month parts** are `awal` (early), `pertengahan` (mid) and `akhir` (late).

**Durations** fold ordinary counted phrases (`2 jam`, `3 minggu`) plus the two fraction words `setengah jam` (half an hour, 30 minutes) and `seperempat jam` (a quarter hour, 15 minutes), and chain: `2 hari 4 jam`.

## Weaker provenance

**The seasons** (`musim semi`, `musim panas`, `musim gugur`, `musim dingin`) ship with no recorded source. They are calques of the four-season Western vocabulary rather than terms with independent standing in an equatorial climate. No dictionary or corpus citation backs any of the four surfaces.

**The clock-direction citation** for `setengah` is honestly incomplete: KBBI fixes the fraction but not the toward-hour direction, which rests on cross-checked usage rather than a single canonical grammar passage. The quarter-hour word (`suku`/`seperempat` on the clock, as opposed to as a duration) is deliberately left unshipped as a clock fraction because its direction was not confirmed.

**The weekday and business-day markers** (`kerja` for a business day) and the weekend noun (`akhir pekan`, `akhir minggu`) carry no cited source beyond their appearance in the test corpus.

## What refuses

**"After" as a bare open-ended future marker.** `sesudah X` / `setelah X` never resolves to an open range, because `DateSpan` has no open-ended-future representation to hand it. The same limit that refuses "after" in every other locale in this codebase, not an Indonesian-specific gap.

**A duration with no direction marker attached at the wrong construction.** Plain `2 jam` folds as a duration through `extract_duration`. But the same phrase inside a relative-offset construction requires the trailing `lalu` or `lagi`. A bare quantity is a duration, not a point in time.

## Open questions for a native speaker

1. What is the correct KBBI or DBP-cited passage, if one exists, for the toward-hour reading of `setengah` on a clock. As opposed to its half-an-hour duration sense, which KBBI already covers?
2. Does `suku` or `seperempat` on the clock count minutes toward the coming hour or from the hour just past, and is that direction the same as `setengah`'s?
3. Are `musim semi/panas/gugur/dingin` in ordinary use for anything beyond describing other countries' seasons, or does everyday Indonesian mark the wet and dry seasons (`musim hujan`, `musim kemarau`) instead, and if so, should those ship as the locale's actual season vocabulary?
4. Is `pekan` fully interchangeable with `minggu` for "week" in a numbered ISO-week phrase, or is one of the two markedly more formal?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("id")
    True
    >>> span, rest = extract_timespan('setengah tiga', "id", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T02:30:00', '')
    >>> span, rest = extract_timespan('pukul satu malam', "id", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T01:00:00', '')
    >>> span, rest = extract_timespan('pukul sebelas malam', "id", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T23:00:00', '')

## Known limits

Each line is an open issue with a strict `xfail` test for this language. The lines are grouped by topic. An example names the reader that produced it, the language and the anchor date, and shows what that reader gives on the test's own phrase.

- A count followed by `setengah` reads half of the count. Example (reader `extract_duration`, lang `id`, anchor 2017-06-27 13:04): `dua setengah jam lagi` gives a length of 60 min and `lagi` left over. [#1231](https://github.com/TigreGotico/chronologia/issues/1231)

---
[← Icelandic](is.md) · [Home](../index.md) · [Irish →](ga.md)
