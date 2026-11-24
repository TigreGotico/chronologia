# Spanish (`es`)

<!-- agent-hint
covers: where each construction of the Spanish locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/es/lang.json, chronologia/locale/es/*.voc, chronologia/extract/numlayer.py:NUMTAG_LANGS, test/nl_corpus_es/, test/test_xfail_open_issues_*.py
generated: no
verify: .venv/bin/python -m doctest docs/languages/es.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/es.md
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

**Weekdays and months** ship wide and abbreviated. The vocabulary records no source for them.

**The date line** is `el 3 de octubre de 1990`, little-endian with `de` between each part, and it also reads without the article and without the year. Spanish also has a day-label idiom, `día 3 de octubre`, where `día` heads the date rather than being part of it. The vocabulary cites RAE's *Ortografía* and the *Diccionario panhispánico de dudas* under *día* for `día` as a temporal function word. It registers `día` as its own marker.

A leading `día` joins the consumed text when the date it labels binds, and never when the date fails. A `día` elsewhere in the sentence is left alone. The slashed numeric form reads. The dotted one does not.

**Relative offsets** are `dentro de` forward and `hace` backward, and `lang.json` also accepts the count-first order with a trailing marker.

**The relative determiners** follow the noun (`el lunes pasado`, `la semana que viene`) which is why the locale sets `marker_position: post`.

**Ranges** are the best-documented part of this locale. The `from` lead is `de`, `desde`, `del` or `a partir de`. The `to` boundary is `a`, `al` or `hasta`. The vocabulary cites each one to a specific RAE work.

`de` and `a` are correlative point-of-departure and point-of-arrival prepositions in the *Diccionario panhispánico de dudas*. `desde` and `hasta` come from the *Diccionario de la lengua española*. `a partir de` is a prepositional locution. The obligatory contractions `del` and `al` to RAE-ASALE's *Nueva gramática* and *Ortografía*. The reason the from-lead matters structurally is that `a` is a hyper-common preposition in Spanish. A bare `A a B` is only trusted as a range when a from-lead is present. `entre … y …` is the other frame, cited to RAE's entry for *entre*.

**The clock** has two toward-the-hour constructions and they are not the same shape. `las cuatro menos cuarto` subtracts from the hour already named. `un cuarto para las cuatro` states the fraction first. Then it names the hour it heads for. Both give 03:45, and the vocabulary keeps `menos` and `para` separate for exactly that reason. Forward is `y`: `las ocho y media`, `las ocho y cuarto`. `mediodía` and `medianoche` are points.

**Day parts** take their boundaries from the Unicode CLDR 47 day-period chart for `es`, transcribed in `chronologia/dayparts.py`, with the surfaces cited to RAE's dictionary. There are four bands and two of them have no English equivalent. The `madrugada` is `[00:00, 06:00)`, the small hours, which English has no single word for. The `mañana` runs `[06:00, 12:00)`.

The `tarde` runs `[12:00, 20:00)`. That is one span across what English splits into afternoon and early evening. RAE glosses `tarde` as the part of the day between midday and nightfall. The `noche` then runs `[20:00, 24:00)`. The frame Spanish puts in front of a day part is `por`, cited to RAE's entry for *por*. Unlike Galician `pola` and Portuguese `pela` it does not contract with the article, so the article follows it as its own word.

**Fuzzy month parts** are `principios de`, `mediados de` and `finales de`, cutting the month into thirds.

**Quarters, ISO weeks, decades and eras.** `el primer trimestre de 2020`, `semana 12`, `los años 80`, `44 a. C.` and `1990 d. C.` all resolve. A before-present marker ships. `la primera mitad de 2020` reads as the first half-year, with `mitad` cited to RAE's dictionary.

**The Roman calendar anchors** ship in their Spanish vernacular forms `calendas`, `nonas` and `idus`, cited to the Spanish Wikipedia article *Calendario romano*, so `los idus de marzo` resolves.

**Habitual recurrence** is `los lunes`. The vocabulary holds only the plural articles and says why: RAE's entry for *el* gives the plural article on a weekday noun the habitual reading. The singular `el lunes` names the single next Monday.

The locale excludes `el` and `la`, so the singular reading cannot bind. As a recurrence, the recurrence edge answers it. The span edge reads `los lunes` as the next Monday and leaves the article in the remainder.

## Weaker provenance

The weekday and month names carry no recorded source. Nor do the seasons, and the locale sets `hemisphere` to null, so a season does not resolve to a southern-hemisphere reading for Spanish outside Spain.

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

## Known limits

Each limit below has an open issue and a strict `xfail` test that fails when the limit is fixed.

- [#997](https://github.com/TigreGotico/chronologia/issues/997): A part of the day with no day word answers the band that has passed

- [#1001](https://github.com/TigreGotico/chronologia/issues/1001): Lone spoken hour: a part of the day in another clause keeps the hour as spoken

- [#1004](https://github.com/TigreGotico/chronologia/issues/1004): A unit word with no number counts as one: "how many days before christmas" gives 24 December

- [#1009](https://github.com/TigreGotico/chronologia/issues/1009): A plural, adverbial or recurring part of the day is not read, so the next hour reads in the evening

- [#1010](https://github.com/TigreGotico/chronologia/issues/1010): A weekday range or list followed by a clock drops the clock or picks a past day

- [#1011](https://github.com/TigreGotico/chronologia/issues/1011): An approximate clock (es-CO tipo, gl sobre, ca cap a) is not read

- [#1014](https://github.com/TigreGotico/chronologia/issues/1014): es, gl: "de mañana" after a noun is read as the morning, and "entre semana" breaks the clock

- [#1032](https://github.com/TigreGotico/chronologia/issues/1032): Clock forms read wrong or not at all: "3 30 pm", "07.00 Uhr", "24:00", nl "tien over half drie", it "le tre", ar "الثالثة والثلث"

- [#1033](https://github.com/TigreGotico/chronologia/issues/1033): A day word with an early, late or part-of-day word gives midnight: "mañana temprano", "morgen früh", "freitag morgen"

- [#1034](https://github.com/TigreGotico/chronologia/issues/1034): A date built from two parts loses one: an offset with a clock, a count from a day word, the nth weekday of a relative period

- [#1047](https://github.com/TigreGotico/chronologia/issues/1047): A dotted clock gives no time in eight locales: es "a las 8.30", pt "às 8.15", it "alle 8.30"

- [#1087](https://github.com/TigreGotico/chronologia/issues/1087): A count of hours or minutes before a holiday gives the day before at 00:00 ("an hour before christmas", "um quarto de hora antes do natal")

- [#1199](https://github.com/TigreGotico/chronologia/issues/1199): es, gl, ca: a count later in the sentence drops the clock ("mañana a las 3 de la tarde compra las 3 cosas" gives 00:00)

- [#1200](https://github.com/TigreGotico/chronologia/issues/1200): A part of the day after a clock or a weekday stays in the remainder (an "de la tardi", es "en la mañana", eu "gauean", bg "по обед")

- [#1203](https://github.com/TigreGotico/chronologia/issues/1203): extract_duration: "century" and "millennium" give no length (da "århundrede", es "siglo", gl "século", pt "milénio")

- [#1204](https://github.com/TigreGotico/chronologia/issues/1204): extract_duration: a decimal count gives no length ("1.5 horas", "7.5 segundos")

- [#1229](https://github.com/TigreGotico/chronologia/issues/1229): es, gl, it, ca: a day-labelled range start next to a clock with a day part reads as an hour

- [#1254](https://github.com/TigreGotico/chronologia/issues/1254): A bare clock with a zone skips the 12-hour rule ("9:30 utc" reads tomorrow 09:30)

- [#1295](https://github.com/TigreGotico/chronologia/issues/1295): es/fr: "el último viernes del mes que viene" reads the last Friday of this month

- [#1297](https://github.com/TigreGotico/chronologia/issues/1297): Event summaries turn a spelled numeral into a digit ("a second meeting" gives "2 meeting")

- [#1299](https://github.com/TigreGotico/chronologia/issues/1299): es: "mañana tarde a las 5" reads only the date

- [#1302](https://github.com/TigreGotico/chronologia/issues/1302): es, gl: "el día 14" and "no día 14" without a month read nothing

- [#1306](https://github.com/TigreGotico/chronologia/issues/1306): es, pt, de, nl, ca: the indefinite article in "un día de marzo" reads as "the 1st day of march"

- [#1310](https://github.com/TigreGotico/chronologia/issues/1310): Working-day and day-of-month recurrence heads read as every day: "cada dia útil", "día laborable", "cada dia 15"

- [#1311](https://github.com/TigreGotico/chronologia/issues/1311): A list of two days reads as a clock or the wrong day: es "el 14 y 15 de mayo" gives 1 May 14:15

- [#1312](https://github.com/TigreGotico/chronologia/issues/1312): Meridiem after an abbreviated hour word is lost: "um 8 Std. abends", "at 8 hr. pm", pt "às 5 pm" read as morning

- [#1315](https://github.com/TigreGotico/chronologia/issues/1315): A clock range in a recurrence reads the end hour or a wrong minute: pt "das 9 às 17" gives 17:00, en "9 to 5" gives 04:51

- [#1322](https://github.com/TigreGotico/chronologia/issues/1322): Only en reads a repeat count: de "jeden Montag 10 mal", es "cada lunes 10 veces" leave the count unread

- [#1332](https://github.com/TigreGotico/chronologia/issues/1332): es: a length before "mañana" loses the day: "reunión de dos horas mañana" starts today, "reunión de dos horas esta mañana" reads tomorrow

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

---
[← Slovenian](sl.md) · [Home](../index.md) · [Swahili →](sw.md)
