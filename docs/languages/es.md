# Spanish (`es`)

<!-- agent-hint
covers: where each construction of the Spanish locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/es/lang.json, chronologia/locale/es/*.voc, chronologia/extract/numlayer.py:NUMTAG_LANGS, test/nl_corpus_es/, test/test_xfail_open_issues_*.py
generated: no
verify: .venv/bin/python -m doctest docs/languages/es.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/es.md && .venv/bin/python -c 'exec("import re,sys\nfrom datetime import datetime\nimport chronologia as C\ndef mins(d):\n    return (\"%.6f\" % (d.total_seconds() / 60)).rstrip(\"0\").rstrip(\".\")\ndef rem(r):\n    return \" and \\x60%s\\x60 left over\" % r if r else \"\"\ndef out(rd, tx, lg, an):\n    f = getattr(C, rd)\n    r = f(tx, lg, anchor=an) if rd == \"extract_duration\" else f(tx, lg, an)\n    if rd == \"extract_timespan\":\n        if r is None: return \"no reading\"\n        return \"%s to %s%s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), r.span.end.datetime().strftime(\"%Y-%m-%d %H:%M\"), rem(r.remainder))\n    if rd == \"extract_duration\":\n        if r is None: return \"no length\"\n        return \"a length of %s min%s\" % (mins(r.duration), rem(r.remainder))\n    if rd == \"extract_event\":\n        if r is None: return \"no event\"\n        return \"start %s, length %s, %s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), \"none\" if r.duration is None else mins(r.duration) + \" min\", \"summary \\x60%s\\x60\" % r.summary if r.summary else \"no summary\")\n    if r is None: return \"no rule\"\n    return \"the rule \\x60%s\\x60%s\" % (r.recurrence.to_string(), rem(r.remainder))\n\np=sys.argv[1]\nt=open(p).read()\nm=re.search(r\"\\n## Known limits\\n(.*?)(?=\\n---\\n|\\Z)\",t,re.S)\nbad=0\nn=0\ntot=0\nfor ln in (m[1].split(\"\\n\") if m else []):\n    if \"Example (\" not in ln: continue\n    tot+=1\n    g=re.search(r\"Example \\(reader \\x60(\\w+)\\x60, lang \\x60([\\w-]+)\\x60, anchor (\\d{4}-\\d\\d-\\d\\d \\d\\d:\\d\\d)\\): \\x60([^\\x60]+)\\x60 gives (.+?)\\. \\[#\\d+\\]\",ln)\n    if not g:\n        bad=1\n        print(\"example line does not parse:\",ln[:80])\n        continue\n    n+=1\n    o=out(g[1],g[4],g[2],datetime.strptime(g[3],\"%Y-%m-%d %H:%M\"))\n    if o!=g[5]:\n        bad=1\n        print(\"limit differs\",g[4],\"|\",g[5],\"|\",o)\nprint(\"known limits checked:\",n,\"of\",tot)\nsys.exit(bad)\n")' docs/languages/es.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Spanish (`es`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

`de la noche` is not a twelve-hour shift, and getting that wrong is the fastest way to be an hour or twelve out. Spanish uses the phrase across the whole colloquial night, so `las diez de la noche` is 22:00 but `la una de la noche` is 01:00 and `las doce de la noche` is midnight. The vocabulary encodes this as a band, not a uniform PM offset. The small hours one to five stay AM.

The evening hours six to eleven are PM. Twelve is midnight. The AM ceiling follows the `madrugada` band, and the colloquial use of `de la noche` for the small hours is cited to RAE's dictionary entry for *noche*. After a clock, `por la noche` reads the same band: `a las 8 por la noche` is 20:00 and `a la una por la noche` is 01:00.

The second thing to know is that `mañana` is two words in one. It is the morning and it is also tomorrow, and the tomorrow reading wins. The locale does not guess: `daypart_ref` in `lang.json` deliberately omits the bare order. The day-part reading only fires when an article, a demonstrative or `de` licenses it. A bare `mañana` is tomorrow. `por la mañana` is the morning.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('las diez de la noche', "es", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T22:00:00', '')

## What ships

**Weekdays and months** ship wide and abbreviated. The vocabulary cites Unicode CLDR 47 for them, except the Saturday abbreviation `sab`.

**The date line** is `el 3 de octubre de 1990`, little-endian with `de` between each part, and it also reads without the article and without the year. Spanish also has a day-label idiom, `día 3 de octubre`, where `día` heads the date rather than being part of it. The vocabulary cites RAE's *Ortografía* and the *Diccionario panhispánico de dudas* under *día* for `día` as a temporal function word. It registers `día` as its own marker.

A leading `día` joins the consumed text when the date it labels binds, and never when the date fails. A `día` elsewhere in the sentence is left alone. The slashed numeric form reads. The dotted one does not.

**Relative offsets** are `dentro de` forward and `hace` backward, and `lang.json` also accepts the count-first order with a trailing marker.

**The relative determiners** follow the noun (`el lunes pasado`, `la semana que viene`) which is why the locale sets `marker_position: post`.

**Ranges** are the best-documented part of this locale. The `from` lead is `de`, `desde`, `del` or `a partir de`. The `to` boundary is `a`, `al` or `hasta`. The vocabulary cites each one to a specific RAE work.

The *Diccionario panhispánico de dudas* gives `de` and `a` as correlative point-of-departure and point-of-arrival prepositions. The *Diccionario de la lengua española* gives `desde` and `hasta`. `a partir de` is a prepositional locution. RAE-ASALE's *Nueva gramática* and *Ortografía* give the obligatory contractions `del` and `al`. The reason the from-lead matters structurally is that `a` is a hyper-common preposition in Spanish. A bare `A a B` is only trusted as a range when a from-lead is present. `entre … y …` is the other frame, cited to RAE's entry for *entre*.

**The clock** has two toward-the-hour constructions and they are not the same shape. `las cuatro menos cuarto` subtracts from the hour already named. `un cuarto para las cuatro` states the fraction first. Then it names the hour it heads for. Both give 03:45, and the vocabulary keeps `menos` and `para` separate for exactly that reason. Forward is `y`: `las ocho y media`, `las ocho y cuarto`. `mediodía` and `medianoche` are points.

**Day parts** take their boundaries from the Unicode CLDR 47 day-period chart for `es`, transcribed in `chronologia/dayparts.py`, with the surfaces cited to RAE's dictionary. There are four bands and two of them have no English equivalent. The `madrugada` is `[00:00, 06:00)`, the small hours, which English has no single word for. The `mañana` runs `[06:00, 12:00)`.

The `tarde` runs `[12:00, 20:00)`. That is one span across what English splits into afternoon and early evening. RAE glosses `tarde` as the part of the day between midday and nightfall. The `noche` then runs `[20:00, 24:00)`. The frame Spanish puts in front of a day part is `por`, cited to RAE's entry for *por*. Unlike Galician `pola` and Portuguese `pela` it does not contract with the article, so the article follows it as its own word.

**Fuzzy month parts** are `principios de`, `mediados de` and `finales de`, cutting the month into thirds.

**Quarters, ISO weeks, decades and eras.** `el primer trimestre de 2020`, `semana 12`, `los años 80`, `44 a. C.` and `1990 d. C.` all resolve. A before-present marker ships. `la primera mitad de 2020` reads as the first half-year, with `mitad` cited to RAE's dictionary.

**The Roman calendar anchors** ship in their Spanish vernacular forms `calendas`, `nonas` and `idus`, cited to the Spanish Wikipedia article *Calendario romano*, so `los idus de marzo` resolves.

**Habitual recurrence** is `los lunes`. The vocabulary holds only the plural articles and says why: RAE's entry for *el* gives the plural article on a weekday noun the habitual reading. The singular `el lunes` names the single next Monday.

The locale excludes `el` and `la`, so the singular reading cannot bind. As a recurrence, the recurrence edge answers it. The span edge reads `los lunes` as the next Monday and leaves the article in the remainder.

## Weaker provenance

The weekday and month names cite Unicode CLDR 47, except the Saturday abbreviation `sab`. The seasons carry no recorded source, and the locale sets `hemisphere` to null, so a season does not resolve to a southern-hemisphere reading for Spanish outside Spain.

The Roman calendar anchors rest on a Wikipedia article. That source is weaker than the RAE works behind the rest of the locale.

## What refuses

**The dotted date.** `15.06.2020` returns nothing, and it does not fall back to reading 2020 as a bare year either. Spanish writes the numeric date with slashes, and `15/06/2020` reads.

**A bare duration.** `quince días` returns nothing. A fortnight unit ships, but a quantity with no direction marker is still only a quantity.

**A bare `mañana` as the morning.** It resolves, but as tomorrow. The morning reading is not reachable without an article, a demonstrative or `de`. That is a refusal of the ambiguous reading rather than a gap.

## Open questions for a native speaker

1. Where exactly does `de la noche` stop being AM? The vocabulary puts the ceiling at five, following the `madrugada` band, but `las cinco de la mañana` and `las cinco de la madrugada` are both ordinary Spanish.
2. Should the seasons resolve differently for southern-hemisphere Spanish, and if so what would select that?
3. Are `calendas`, `nonas` and `idus` the forms Spanish historical writing uses, or does it keep the Latin?
4. Is `día` ever used in a way that would make folding a leading `día` into a date wrong?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("es")
    True
    >>> span, rest = extract_timespan('las diez de la noche', "es", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T22:00:00', '')
    >>> span, rest = extract_timespan('la una de la noche', "es", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T01:00:00', '')
    >>> span, rest = extract_timespan('de la noche', "es", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T20:00:00', '')
    >>> span, rest = extract_timespan('las doce de la noche', "es", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-28T00:00:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('15.06.2020', "es", anchor) is None
    True
    >>> extract_timespan('quince días', "es", anchor) is None
    True

## Known limits

Each line is an open issue with a strict `xfail` test for this language. The lines are grouped by topic. An example names the reader that produced it, the language and the anchor date, and shows what that reader gives on the test's own phrase.

**Clocks and parts of the day**

- A part of the day with no day word answers the band that has already passed. Example (reader `extract_timespan`, lang `es`, anchor 2017-06-27 13:04): `necesito que suene una alarma por la mañana` gives 2017-06-27 06:00 to 2017-06-27 12:00 and `necesito que suene una alarma` left over. [#997](https://github.com/TigreGotico/chronologia/issues/997)

- A part of the day in another clause leaves a lone hour as spoken. Example (reader `extract_timespan`, lang `es-ES`, anchor 2026-01-05 06:00): `a las 9, esta noche` gives 2026-01-05 09:00 to 2026-01-05 09:01 and `esta noche` left over. [#1001](https://github.com/TigreGotico/chronologia/issues/1001)

- A part of the day before a clock stays in the remainder. Example (reader `extract_timespan`, lang `es-ES`, anchor 2026-10-17 12:00): `tarde a las 4:30` gives 2026-10-17 16:30 to 2026-10-17 16:31 and `tarde` left over. [#1002](https://github.com/TigreGotico/chronologia/issues/1002)

- A plural, adverbial or recurring part of the day is not read, so the hour reads in the wrong half. Example (reader `extract_timespan`, lang `es`, anchor 2017-06-27 13:04): `recuérdame cada mañana tomar mi medicina a las 8` gives 2017-06-28 00:00 to 2017-06-29 00:00 and `recuérdame cada tomar mi medicina a las 8` left over. [#1009](https://github.com/TigreGotico/chronologia/issues/1009)

- A weekday range or list followed by a clock drops the clock or picks a past day. Example (reader `extract_timespan`, lang `es`, anchor 2017-06-27 13:04): `de lunes a viernes a las ocho de la mañana avísame` gives 2017-07-03 00:00 to 2017-07-03 08:01 and `avísame` left over. [#1010](https://github.com/TigreGotico/chronologia/issues/1010)

- An approximate clock such as `about nine` is not read. Example (reader `extract_timespan`, lang `es`, anchor 2017-06-27 13:04): `avíseme de lunes a viernes por la mañana tipo 7` gives 2017-07-03 00:00 to 2017-07-04 00:00 and `avíseme de a viernes por la mañana tipo 7` left over. [#1011](https://github.com/TigreGotico/chronologia/issues/1011)

- A day-part phrase after a noun reads as the morning, and a week phrase breaks the clock. Example (reader `extract_timespan`, lang `es`, anchor 2017-06-27 13:04): `léeme las alarmas de mañana` gives 2017-06-27 06:00 to 2017-06-27 12:00 and `léeme las alarmas` left over. [#1014](https://github.com/TigreGotico/chronologia/issues/1014)

- A clock form reads wrong or not at all. Example (reader `extract_timespan`, lang `es`, anchor 2024-06-15 10:00): `11 55 de la tarde` gives no reading. [#1032](https://github.com/TigreGotico/chronologia/issues/1032)

- A day word with an early, late or part-of-day word gives midnight. Example (reader `extract_timespan`, lang `es`, anchor 1998-01-01 00:00): `ayer noche` gives 1997-12-31 00:00 to 1998-01-01 00:00 and `noche` left over. [#1033](https://github.com/TigreGotico/chronologia/issues/1033)

- A clock with a dot between hour and minute gives no time. Example (reader `extract_timespan`, lang `es`, anchor 2026-09-25 12:00): `a las 8.30` gives no reading. [#1047](https://github.com/TigreGotico/chronologia/issues/1047)

- A count later in the sentence drops the clock. Example (reader `extract_timespan`, lang `es-es`, anchor 2026-09-25 12:00): `mañana a las 3 de la tarde compra las 3 cosas` gives 2026-09-26 00:00 to 2026-09-27 00:00 and `a las 3 de la tarde compra las 3 cosas` left over. [#1199](https://github.com/TigreGotico/chronologia/issues/1199)

- A part of the day after a clock or a weekday stays in the remainder. Example (reader `extract_timespan`, lang `es-ES`, anchor 2026-10-17 12:00): `a las 8 en la mañana` gives 2026-10-18 08:00 to 2026-10-18 08:01 and `en la mañana` left over. [#1200](https://github.com/TigreGotico/chronologia/issues/1200)

- A day-labelled range start next to a clock with a day part reads as an hour. Example (reader `extract_timespan`, lang `es`, anchor 2026-01-30 10:00): `entre el día 3 y las 5 de la tarde` gives 2026-01-30 15:00 to 2026-01-30 17:01. [#1229](https://github.com/TigreGotico/chronologia/issues/1229)

- A part of the day before a clock reads only the date. Example (reader `extract_timespan`, lang `es`, anchor 2026-11-22 09:00): `mañana tarde a las 5` gives 2026-11-23 00:00 to 2026-11-24 00:00 and `tarde a las 5` left over. [#1299](https://github.com/TigreGotico/chronologia/issues/1299)

- The meridiem after an abbreviated hour word is lost. Example (reader `extract_timespan`, lang `es`, anchor 2026-11-22 23:00): `a las 8 hrs. de la noche` gives 2026-11-23 08:00 to 2026-11-23 08:01 and `hrs. de la noche` left over. [#1312](https://github.com/TigreGotico/chronologia/issues/1312)

**Dates, ranges and weeks**

- A unit word with no number counts as one. Example (reader `extract_duration`, lang `es`, anchor 2017-06-27 13:04): `la semana pasada` gives a length of 10080 min and `pasada` left over. [#1004](https://github.com/TigreGotico/chronologia/issues/1004)

- A date built from two parts loses one of them. Example (reader `extract_timespan`, lang `es`, anchor 2026-10-17 12:00): `el 5 de noviembre del año que viene` gives 2026-11-05 00:00 to 2026-11-06 00:00 and `año que viene` left over. [#1034](https://github.com/TigreGotico/chronologia/issues/1034)

- The last weekday of next month reads as the last weekday of this month. Example (reader `extract_event`, lang `es`, anchor 2026-10-17 09:00): `el último viernes del mes que viene` gives start 2026-10-30 00:00, length none, summary `que viene`. [#1295](https://github.com/TigreGotico/chronologia/issues/1295)

- A day number with no month reads nothing. Example (reader `extract_timespan`, lang `es`, anchor 2026-11-22 09:00): `el día 14` gives no reading. [#1302](https://github.com/TigreGotico/chronologia/issues/1302)

- The indefinite article before a day of a month reads as the first day. Example (reader `extract_timespan`, lang `es`, anchor 2026-11-22 09:00): `un día de marzo` gives 2027-03-01 00:00 to 2027-03-02 00:00. [#1306](https://github.com/TigreGotico/chronologia/issues/1306)

- A list of two days reads as a clock or as the wrong day. Example (reader `extract_timespan`, lang `es`, anchor 2026-11-22 09:00): `el 14 y 15 de mayo` gives 2027-05-15 00:00 to 2027-05-16 00:00 and `el 14 y` left over. [#1311](https://github.com/TigreGotico/chronologia/issues/1311)

- A length before a day word loses the day. [#1332](https://github.com/TigreGotico/chronologia/issues/1332)

**Offsets, lengths and holidays**

- A count of hours or minutes before a holiday gives the day before at 00:00. Example (reader `extract_timespan`, lang `es`, anchor 2026-09-25 12:00): `un cuarto de hora antes de navidad` gives 2026-12-24 00:00 to 2026-12-25 00:00 and `un cuarto` left over. [#1087](https://github.com/TigreGotico/chronologia/issues/1087)

- `century` and `millennium` give no length. Example (reader `extract_duration`, lang `es`, anchor 2017-06-27 13:04): `1 siglo` gives no length. [#1203](https://github.com/TigreGotico/chronologia/issues/1203)

- A decimal count is dropped from the length. Example (reader `extract_duration`, lang `es`, anchor 2017-06-27 13:04): `7.5 segundos` gives no length. [#1204](https://github.com/TigreGotico/chronologia/issues/1204)

**Recurrence**

- A clock range in a recurrence reads the end hour or a wrong minute. Example (reader `extract_recurrence`, lang `es`, anchor 2026-11-22 09:00): `cada lunes de 9 a 17 horas` gives the rule `FREQ=WEEKLY;BYDAY=MO;BYHOUR=9` and `horas` left over. [#1315](https://github.com/TigreGotico/chronologia/issues/1315)

- A repeat count is not read. Example (reader `extract_recurrence`, lang `es`, anchor 2026-11-22 09:00): `cada lunes 10 veces` gives the rule `FREQ=WEEKLY;BYDAY=MO` and `10 veces` left over. [#1322](https://github.com/TigreGotico/chronologia/issues/1322)

**Events, zones, business days and the API**

- A bare clock with a zone skips the 12-hour rule. Example (reader `extract_timespan`, lang `es`, anchor 2017-06-27 13:04): `antes de las 9:30 utc` gives 2017-06-27 13:04 to 2017-06-28 09:31. [#1254](https://github.com/TigreGotico/chronologia/issues/1254)

- The event summary turns a spelled numeral into a digit. Example (reader `extract_event`, lang `es`, anchor 2026-11-22 09:00): `una reunión mañana` gives start 2026-11-23 00:00, length none, summary `1 reunión`. [#1297](https://github.com/TigreGotico/chronologia/issues/1297)

- A working-day or day-of-month recurrence reads as every day. Example (reader `extract_recurrence`, lang `es-ES`, anchor 2026-11-22 09:00): `cada día laborable a las 9` gives the rule `FREQ=DAILY;BYHOUR=9` and `laborable` left over. [#1310](https://github.com/TigreGotico/chronologia/issues/1310)

---
[← Slovenian](sl.md) · [Home](../index.md) · [Swahili →](sw.md)
