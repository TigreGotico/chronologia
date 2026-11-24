# Russian (`ru`)

<!-- agent-hint
covers: where each construction of the Russian locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/ru/lang.json, chronologia/locale/ru/*.voc, chronologia/extract/numlayer.py:NUMTAG_LANGS, test/nl_corpus_ru/, test/test_xfail_open_issues_*.py
generated: no
verify: .venv/bin/python -m doctest docs/languages/ru.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/ru.md && .venv/bin/python -c 'exec("import re,sys\nfrom datetime import datetime\nimport chronologia as C\ndef mins(d):\n    return \"%g\" % (d.total_seconds() / 60)\ndef rem(r):\n    return \" and \\x60%s\\x60 left over\" % r if r else \"\"\ndef out(rd, tx, lg, an):\n    f = getattr(C, rd)\n    r = f(tx, lg, anchor=an) if rd == \"extract_duration\" else f(tx, lg, an)\n    if rd == \"extract_timespan\":\n        if r is None: return \"no reading\"\n        return \"%s to %s%s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), r.span.end.datetime().strftime(\"%Y-%m-%d %H:%M\"), rem(r.remainder))\n    if rd == \"extract_duration\":\n        if r is None: return \"no length\"\n        return \"a length of %s min%s\" % (mins(r.duration), rem(r.remainder))\n    if rd == \"extract_event\":\n        if r is None: return \"no event\"\n        return \"start %s, length %s, summary \\x60%s\\x60\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), \"none\" if r.duration is None else mins(r.duration) + \" min\", r.summary)\n    if r is None: return \"no rule\"\n    return \"the rule \\x60%s\\x60%s\" % (r.recurrence.to_string(), rem(r.remainder))\n\np=sys.argv[1]\nt=open(p).read()\nm=re.search(r\"\\n## Known limits\\n(.*?)(?=\\n---\\n|\\Z)\",t,re.S)\nbad=0\nn=0\nfor ln in (m[1].split(\"\\n\") if m else []):\n    g=re.search(r\"Example \\(reader \\x60(\\w+)\\x60, lang \\x60([\\w-]+)\\x60, anchor (\\d{4}-\\d\\d-\\d\\d \\d\\d:\\d\\d)\\): \\x60([^\\x60]+)\\x60 gives (.+?)\\. \\[#\\d+\\]\",ln)\n    if not g: continue\n    n+=1\n    o=out(g[1],g[4],g[2],datetime.strptime(g[3],\"%Y-%m-%d %H:%M\"))\n    if o!=g[5]:\n        bad=1\n        print(\"limit differs\",g[4],\"|\",g[5],\"|\",o)\nprint(\"known limits checked:\",n)\nsys.exit(bad)\n")' docs/languages/ru.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Russian (`ru`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

Almost no Russian temporal phrase stands in the nominative. `на прошлой неделе` is prepositional, `в прошлом месяце` and `в прошлом году` are prepositional, `прошлым летом` is instrumental. None of those is the dictionary form of the words involved. A locale that shipped citation forms would leave the ordinary spoken register unreadable. This one ships full paradigms: every unit noun in all six cases and both numbers, and every determiner in its complete adjectival or pronominal paradigm. The vocabulary cites Грамота.ру's declension tables for each, naming the declension type it followed.

The clock is the other thing to understand early, because Russian says it in two directions and neither is the English one. Forward from the previous hour is the toward-hour form: `четверть десятого` is a quarter *of the tenth*. That is 09:15. `половина девятого` (contracted `полдевятого`) is half of the ninth, 08:30. Backward is `без`, which subtracts from the hour actually named: `без четверти десять` is a quarter to ten, 09:45. Both are cited to gramota.ru's guide to telling the time.

The locative `в восьмом часу` is the hour that begins at seven: the span from 07:00 to 08:00, one hour wide. A day period fixes the half of the day, and the hours run first to twelfth (`marker_hour_span.voc`, ruling 37). The digit form `в 8-м часу` and the inverted order `часу в восьмом` read the same span.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('без пяти девять', "ru", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T08:55:00', '')

## What ships

**Weekdays and months** ship wide and abbreviated, cited to Unicode CLDR 47.

**The date line** is little-endian, and the dotted civil form `15.06.2020` reads. Russian is one of the languages that writes it. `ordinal_dot` is off. The dot in a date is a separator and never an ordinal marker.

**The unit nouns** are the heart of the locale, and three of them carry decisions worth naming.

`час` ships its full paradigm including the locative `в первом часу`, which is distinct from the prepositional `о часе`. The nominative plural `часы` is deliberately withheld. It is the ordinary Russian word for a clock or a wristwatch, and folding it into the duration unit would read a mention of the object as a span of time.

`год` is suppletive (the plural is built on `лет-`) and both stems ship. But `лето` is deliberately absent from the year vocabulary even though `лет` belongs there, because the instrumental `летом` is the season and lives in the summer vocabulary instead.

`неделя` ships the full first-declension paradigm rather than nominative and genitive alone, because the prepositional `неделе` carries what is plausibly the single most common temporal phrase in the language: `на этой / прошлой / следующей неделе`.

`день` ships both the `ё` spelling `днём` and the `е` spelling `днем`, since `ё` goes untyped in the majority of running Russian text.

**The determiners** ship complete. `прошлый` is listed across the hard-stem adjective paradigm and `следующий` across the soft-stem one, `последний` (the ordinal-last determiner behind `последний понедельник мая`) across the soft-stem paradigm too, and `этот` across the full pronominal paradigm of demonstratives. Each cites Грамота.ру and names the paradigm type.

**Relative offsets** are `через` forward and `назад` backward, in either order relative to the count.

**The clock** ships, beyond the two fraction words, a generalisation of the subtractive idiom. `без четверти` is the fixed quarter form, but Russian subtracts a minute count: `без пяти девять` is 08:55, `без десяти девять` 08:50 and `без пятнадцати девять` 08:45, numerically the same as `без четверти девять`. `без двадцати девять` reads 08:40, and so does `без двадцати минут девять`. Those genitive cardinals live in their own map rather than among the fractions. The vocabulary explains why: unlike `четверть` and `половина` they name no bare "N of the hour" idiom on their own. They are bound only after `без`. `пять девять` alone is not a Russian clock time and does not read as one. An optional `минут` may follow the count (`без пяти минут девять`) and reads the same.

`полдень` and `полночь` are the two landmark points, and `час`/`часов` is the o'clock word.

**Day parts** take their boundaries from the Unicode CLDR 47 day-period chart for `ru`, transcribed in `chronologia/dayparts.py`: `ночь` `[00:00, 04:00)`, `утро` `[04:00, 12:00)`, `день` `[12:00, 18:00)`, `вечер` `[18:00, 24:00)`. The surfaces shipped are not the nouns but the instrumental adverbs (`ночью`, `утром`, `днём`, `вечером`) because that is the form the deictic phrases actually use: `сегодня утром`, `вчера ночью`, `завтра днём`. Each is cited to its Russian Wiktionary adverb entry.

**The eras** are the fullest part of the locale's citation record. The secular `до нашей эры` abbreviates to `до н. э.` with a space after each letter, which the vocabulary attributes to Мильчин and Чельцова's *Справочник издателя и автора* as the typographic norm. The unspaced `до н.э.` is what people actually type, so it is read too. The religious counterpart `до Р. Х.` (`до Рождества Христова`) is equally current and names the same span. Its common-era mirror `по Р. Х.` is recorded from Russian Wiktionary. `н. э.` and `нашей эры` are the common-era forms.

**Ranges** are `с … по …` and `с … до …`, plus `между … и …`. The choice between `по` and `до` is not cosmetic and the vocabulary argues it at length: `по` with the accusative makes the named day *inclusive*. `с 5 по 12 июня` ends at the end of 12 June. The authorities cited are Ожегов and Шведова's *Толковый словарь русского языка* under *по* (glossed there as "вплоть до" with the examples "прочитать с первой по десятую главу" and "отпуск по воскресенье") and Кузнецов's *Большой толковый словарь*, with "проездной действителен по март месяц" and "оплата с января по апрель".

**Quarters, ISO weeks, decades and seasons.** `первый квартал 2020`, `неделя 12` and the spelled decade `восьмидесятые годы` all resolve. The seasons carry adjectival narrowing, so `ранней весны` reads as early spring rather than the whole of it.

**Fuzzy month parts** are `начало`, `середина` and `конец`.

## Weaker provenance

The seasons and the holiday vocabulary carry no recorded source. The weekday and month names cite Unicode CLDR 47.

The `по`-inclusive rule is the best-cited decision in the locale. The corresponding boundary semantics of `до` are not separately argued in the vocabulary, and rest on the general contrast with `по`.

## What refuses

**`часы` as a duration.** The nominative plural of `час` returns nothing on its own, by the deliberate withholding described above. It is a wristwatch, not a span.

**A bare duration.** `две недели` returns nothing, and so does `полтора часа` even though `полтора`/`полторы` is registered as a one-and-a-half quantifier. A quantity with no direction marker is still only a quantity.

## Open questions for a native speaker

1. Should `полтора часа` read as a duration when a marker is present, and what surface would carry it?
2. Does `вчера ночью` name the small hours of yesterday, as the band table forces, or the night that began yesterday evening?
3. Are the century calque `столетие` and the native `век` interchangeable in every construction the locale reads, or does one of them resist some?
4. Should `до` in a range be inclusive or exclusive of the named day? The inclusive reading is argued only for `по`.

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("ru")
    True
    >>> span, rest = extract_timespan('без пяти девять', "ru", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T08:55:00', '')
    >>> span, rest = extract_timespan('на прошлой неделе', "ru", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-19T00:00:00', '')
    >>> span, rest = extract_timespan('в прошлом месяце', "ru", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-05-01T00:00:00', '')
    >>> span, rest = extract_timespan('в прошлом году', "ru", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2016-01-01T00:00:00', '')
    >>> span, rest = extract_timespan('без двадцати девять', "ru", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T08:40:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('час', "ru", anchor) is None
    True
    >>> extract_timespan('две недели', "ru", anchor) is None
    True

## Known limits

Each line is an open issue with a strict `xfail` test for this language. The lines are grouped by topic. An example names the reader that produced it, the language and the anchor date, and shows what that reader gives on the test's own phrase.

- An hour after a preposition like `на` is not read as a clock. Example (reader `extract_timespan`, lang `ru`, anchor 2017-06-27 13:04): `поставь напоминание на восемь вечера` gives no reading. [#987](https://github.com/TigreGotico/chronologia/issues/987)

- A spoken hour and minute clock reads only the hour. [#1193](https://github.com/TigreGotico/chronologia/issues/1193)

- The first half of the day reads as 13:00. [#1194](https://github.com/TigreGotico/chronologia/issues/1194)

- A half-hour or quarter clock followed by another word loses its clock. [#1221](https://github.com/TigreGotico/chronologia/issues/1221)

- A half hour written as two words reads no half hour. Example (reader `extract_timespan`, lang `ru`, anchor 2026-11-22 09:00): `пол восьмого` gives no reading. [#1335](https://github.com/TigreGotico/chronologia/issues/1335)

- A preposition or the year noun stays in the remainder. Example (reader `extract_timespan`, lang `ru`, anchor 2017-06-27 13:04): `2022 год` gives 2022-01-01 00:00 to 2023-01-01 00:00 and `год` left over. [#988](https://github.com/TigreGotico/chronologia/issues/988)

- A unit word with no number counts as one. Example (reader `extract_timespan`, lang `ru`, anchor 2017-06-27 13:04): `сколько дней до 31 октября` gives 2017-10-30 00:00 to 2017-10-31 00:00 and `сколько` left over. [#1004](https://github.com/TigreGotico/chronologia/issues/1004)

- A weekday of next week leaves words of the date in the remainder. [#1038](https://github.com/TigreGotico/chronologia/issues/1038)

- A spelled amount of one thousand reads as the year 1000. [#1192](https://github.com/TigreGotico/chronologia/issues/1192)

- A year spoken as an ordinal reads no date. Example (reader `extract_timespan`, lang `ru`, anchor 2026-11-22 09:00): `в две тысячи втором году` gives no reading. [#1336](https://github.com/TigreGotico/chronologia/issues/1336)

- A range reading crosses a full stop. Example (reader `extract_timespan`, lang `ru`, anchor 2017-06-27 06:04): `Мы встретимся в понедельник. Отчёт должен быть готов до пятницы.` gives 2017-07-03 00:00 to 2017-07-08 00:00 and `Мы встретимся Отчёт должен быть готов` left over. [#1352](https://github.com/TigreGotico/chronologia/issues/1352)

- Input typed in decomposed (NFD) form reads differently from the composed (NFC) form. Example (reader `extract_timespan`, lang `ru`, anchor 2017-06-27 06:04): `3 рабочих дней` gives 2017-06-30 00:00 to 2017-07-01 00:00 and `днеи` left over. [#1353](https://github.com/TigreGotico/chronologia/issues/1353)

---
[← Romanian](ro.md) · [Home](../index.md) · [Serbian →](sr.md)
