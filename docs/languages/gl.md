# Galician (`gl`)

<!-- agent-hint
covers: where each construction of the Galician locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/gl/lang.json, chronologia/locale/gl/*.voc, chronologia/extract/numlayer.py:NUMTAG_LANGS, test/nl_corpus_gl/, test/test_xfail_open_issues_*.py
generated: no
verify: .venv/bin/python -m doctest docs/languages/gl.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/gl.md tarde@12:00
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Galician (`gl`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

Galician sits beside Portuguese and looks like it almost everywhere. That is the standing hazard for this locale. A surface that is right in Portuguese is not thereby right in Galician. Nothing here is admitted on the strength of the Portuguese page.

Every marker that carries a source carries a Galician one, the Dicionario da Real Academia Galega. The day-part bands come from the Galician row of the Unicode day-period table rather than from the Portuguese row next to it. The two rows are not the same row, which is the point.

The clearest place that shows is the clock. Portuguese runs one uninterrupted afternoon from midday to seven in the evening. Galician has a separate hour of noon between morning and afternoon: `mediodía`, from 12:00 to 13:00. The afternoon then runs eight hours to nine at night. `noite` takes only the last three hours of the day. `chronologia/dayparts.py` transcribes bands for fifty locales. Three of them carry an hour-wide noon band of exactly 12:00 to 13:00 (Catalan, German and Galician).

Three close the day with a final band that opens at 21:00 (Catalan, Basque and Galician). Take every band in that table that opens between eleven in the morning and three in the afternoon. None is longer than eight hours, and only two reach it: Galician's `tarde` and the Spanish `tarde`, which is equally eight hours but sits an hour earlier at 12:00 to 20:00.

The second early fact is that `da noite` is a band, not a shift. `dez da noite` is 22:00 but `unha da noite` is 01:00. The small hours one to five stay AM. The evening hours six to eleven are PM. Twelve is midnight. The AM ceiling follows the `madrugada` band, and DRAG's entry for `noite` supports the whole stretch, glossing it as the period from sunset to sunrise.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('dez da noite', "gl", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T22:00:00', '')

## What ships

**Weekdays and months** ship wide and abbreviated. Neither carries a recorded source in the vocabulary.

**The date line** is `o 3 de outubro de 1990`, little-endian, with `de` between the parts and an optional leading article that is consumed with the date rather than left behind. The slashed numeric date reads. The dotted one does not.

**The locative `en`** is a genuine during-word here, so `en xaneiro` binds the month and leaves nothing over. The part-of-day frame `pola`/`polo` lives in its own day-frame vocabulary, separate from the during slot. It does not compete with `en` for it and the marker-prefixed month order comes through clean.

**Relative offsets** are `hai` and `atrás` backward, `en` and `dentro` forward. Relative determiners follow their noun (`a semana pasada`, `o luns que vén`) so the locale sets `marker_position: post`.

**Ranges** are `de … a …`, `do … ao …`, `desde …`, `a partir de …`, `ata …` and `deica …`, with `entre … e …` as the other frame. Each preposition is cited to its own DRAG entry, and the `de`+`o` and `a`+`o` contractions to the RAG/ILG *Normas ortográficas e morfolóxicas do idioma galego*. The from-lead carries structural weight for the same reason it does in Portuguese: `a` is a hyper-common preposition. A bare `A a B` is trusted as a range only when a from-lead is present.

**The clock** has both toward-the-hour shapes and keeps them apart. `catro menos cuarto` subtracts from the hour already named. Forward is `e`: `cinco e media`, `cinco e cuarto`. The indefinite `un`/`unha` sits in the article vocabulary so the `cuarto` fraction can read. `mediodía` and `medianoite` are points.

**Day parts** take their boundaries from the Unicode CLDR 47 day-period chart, locale `gl`, transcribed in `chronologia/dayparts.py`: `madrugada` `[00:00, 06:00)`, `mañá` `[06:00, 12:00)`, `mediodía` `[12:00, 13:00)`, `tarde` `[13:00, 21:00)`, `noite` `[21:00, 24:00)`. The frame is `pola`, `polo` and their plurals, the contractions of `por` with the definite article.

**Fuzzy month parts, quarters, ISO weeks, decades and eras** all resolve: `mediados de xullo`, `o primeiro trimestre de 2020`, `semana 12`, `os anos 80` and `44 ac`. `a primeira metade de 2020` reads as the first half-year, with `metade` cited to DRAG. The singular `ano` names one year and the plural `anos` frames a decade. They are kept in separate vocabularies so that `o ano 1980` cannot reach the decade slot.

**The Roman calendar anchors** ship in their Galician vernacular forms `calendas`, `nonas` and `idos`, cited to the Galician Wikipedia article *Calendario romano*. All three appear in that article with their definitions, which was checked.

## Weaker provenance

**The `mañá` homograph rests on one entry doing two jobs.** DRAG gives `mañá` two senses in one entry. Sense 1 is the day part and sense 3 is the adverbial "day after today". The locale takes both from that single source and separates them by frame: bare `mañá` is tomorrow, framed `pola mañá` or `esta mañá` or `da mañá` is the morning band. Nothing independent corroborates that the frame is what does the separating.

**`deica` ships as a general range terminus.** DRAG says it is not one. The DRAG entry for `deica` states that the idea of the speaker's own place or moment is always present in it. It gives the explicit contrast that one says `Camiñaron desde Pedrafita ata Santiago` and not `deica Santiago`. The locale nevertheless accepts `de xuño deica agosto` as a range because `deica` sits in the same to-marker vocabulary as `ata`. The reading it produces is the natural one, but it is wider than the source licenses.

**`ata` is a homograph the locale does not guard.** DRAG has two `ata` headwords: the preposition, and a feminine noun for the act of tying sheaves. Only the preposition ships and nothing distinguishes the two.

**The Roman anchors rest on a Wikipedia article,** weaker than the DRAG citations the rest of the locale is built on.

**Weekday and month names, and the seasons, carry no recorded source.** The locale sets `hemisphere` to null. A season is never resolved to a southern reading.

## Unchecked and broken citations

The four day-part vocabularies and the night meridiem all cite DRAG through the URL `https://academia.gal/dicionario/-/termo/mana`. That URL leads to the dictionary's search page and no entry. The Galician headword is `mañá`, and the entry is reachable only through the percent-encoded form of the accented word. The glosses quoted in those comments match that entry. Only the link is wrong. The same link appears on the `tarde`, `noite` and `madrugada` files, where it would point at the morning entry even if it resolved.

The during-word vocabulary cites `https://academia.gal/dicionario/en`, which does not resolve. The headword `en` does exist in DRAG under the term path the other entries use.

Every other cited source contains what the vocabulary says it contains. These sources are the DRAG entries for `entre`, `de`, `desde`, `a`, `ata`, `deica`, `metade`, `ano` and `noite`. They also include the Galician Wikipedia *Calendario romano* and the CLDR 47 day-period chart. The `gl` row of that chart gives exactly the five boundaries transcribed.

## What refuses

**Every bare day-part word except `mañá`.** `tarde`, `noite` and `madrugada` return nothing on their own, and `máis tarde` returns nothing. One grammar order binds every day-part surface the locale ships. A bare `tarde` cannot be refused while a bare `mañá` is admitted. `tarde` is equally the adverb *late*. Admitting it would answer an afternoon band for `cheguei tarde`, a sentence that names no time. `mañá` is available bare because bare `mañá` means tomorrow, not the morning.

**The dotted date.** `15.06.2020` returns nothing and does not fall back to reading 2020 as a bare year.

**A bare duration.** `quince días` returns nothing. A fortnight unit ships, but a quantity with no direction marker is still only a quantity.

**Roman-numeral and spelled centuries.** `o século XX` and `o século vinte` both return nothing.

## Known defects

These are wrong answers, not refusals, and each is reproduced against the anchor 2017-06-27 13:04.

`extract_timespan("a década de 1980", "gl", anchor)` returns 1980-01-01 to 1981-01-01 with `a década de` left in the remainder. A decade was asked for and a single year was given. The plural frame `os anos 80` is the one that works. The `década de` frame reaches the year rule instead.

`extract_timespan("até o luns", "gl", anchor)` binds Monday but strands the article `o`. The until-vocabulary carries `ata o` and `ata a` as two-word surfaces precisely so the article is claimed with its marker. The variant spelling `até` has no such pair. The scanner finds the bare `até` first and leaves the article behind. `ata o luns` is clean.

`extract_timespan("a partir do 5 de xuño", "gl", anchor)` binds the date but leaves the whole three-word marker `a partir do` in the remainder, so an open-ended from-range reads as a single day.

`extract_timespan("o mediodía", "gl", anchor)` resolves the noon point and strands the article, and `todos os luns`, `cada martes` and `a próxima fin de semana` each resolve their target while leaving the recurrence or determiner word visible.

## Open questions for a native speaker

1. Does `deica` genuinely accept a from-lead, as `de xuño deica agosto` assumes, or does DRAG's observation rule that reading out?
2. Where does `da noite` stop being AM? The ceiling sits at five, following the `madrugada` band, but DRAG's `mañá` entry gives `ás tres da mañá` for the same hour.
3. Does the hour of `mediodía` behave as a band in speech, or only as the twelve-o'clock point?
4. Is `a década de 1980` an ordinary Galician way to name a decade, and should it therefore resolve to ten years?
5. Are `calendas`, `nonas` and `idos` the forms Galician historical writing uses?

## Known limits

Each line is an open issue with a strict `xfail` test for this language. The most common cases come first. An example shows what the library gives on the test's own anchor date.

**Clocks and parts of the day**

- A count later in the sentence drops the clock. Example: `mañá ás 3 da tarde compra as 3 cousas` gives 2026-09-26 00:00, where the test expects 2026-09-26 15:00. [#1199](https://github.com/TigreGotico/chronologia/issues/1199)

- An approximate clock such as `about nine` is not read. Example: `avísame de luns a venres pola mañá sobre as 7` gives 2017-07-03 00:00, where the test expects 2017-06-28 07:00. [#1011](https://github.com/TigreGotico/chronologia/issues/1011)

- A day-part phrase after a noun reads as the morning, and a week phrase breaks the clock. Example: `amósame as alarmas de mañá` gives 2017-06-27 06:00, where the test expects 2017-06-28 00:00. [#1014](https://github.com/TigreGotico/chronologia/issues/1014)

- A date built from two parts loses one of them. Example: `cada mañá` gives cada. [#1034](https://github.com/TigreGotico/chronologia/issues/1034)

- A clock with a dot between hour and minute gives no time. Example: `ás 8.30` gives no reading. [#1047](https://github.com/TigreGotico/chronologia/issues/1047)

- A day-labelled range start next to a clock with a day part reads as an hour. Example: `desde o día 10 ata as 8 da noite` gives 2026-01-30 22:00, where the test expects 2026-02-10 00:00. [#1229](https://github.com/TigreGotico/chronologia/issues/1229)

**Dates, ranges and weeks**

- A day number with no month reads nothing. Example: `no día 14` gives no reading. [#1302](https://github.com/TigreGotico/chronologia/issues/1302)

- A day range with a relative-month end reads as the whole month. Example: `entre o día 3 e o 5 do mes que vén` gives 2026-02-01 00:00, where the test expects 2026-02-03 00:00. [#1230](https://github.com/TigreGotico/chronologia/issues/1230)

**Offsets, lengths and holidays**

- A weekday mention drops its preposition or article, where a month keeps it. Example: `o venres` gives (2, 8), where the test expects (0, 8)      At index 0 diff: 2 != 0   Use -v to get more diff. [#996](https://github.com/TigreGotico/chronologia/issues/996)

- A unit word with no number counts as one. Example: `a semana pasada` gives 10080 min with remainder 'pasada', where the test expects nothing. [#1004](https://github.com/TigreGotico/chronologia/issues/1004)

- A count of hours or minutes before a holiday gives the day before at 00:00. Example: `un cuarto de hora antes do nadal` gives 2026-12-24 00:00, where the test expects 2026-12-24 23:45. [#1087](https://github.com/TigreGotico/chronologia/issues/1087)

**Recurrence**

- A clock range in a recurrence reads the end hour or a wrong minute. Example: `cada luns das 9 ás 17` gives ((17,), ()), where the test expects ((9,), ())      At index 0 diff: (17,) != (9,)   Use -v to get more diff. [#1315](https://github.com/TigreGotico/chronologia/issues/1315)

**Events, zones, business days and the API**

- `century` and `millennium` give no length. Example: `1 século` gives no reading. [#1203](https://github.com/TigreGotico/chronologia/issues/1203)

- A decimal count gives no length. Example: `1.5 horas` gives no reading. [#1204](https://github.com/TigreGotico/chronologia/issues/1204)

- A bare clock with a zone skips the 12-hour rule. Example: `antes das 9:30 utc` gives 2017-06-28 09:31 UTC, where the test expects 2017-06-27 21:31 UTC. [#1254](https://github.com/TigreGotico/chronologia/issues/1254)

- A working-day or day-of-month recurrence reads as every day. Example: `cada día de traballo ás 9` gives DAILY, where the test expects WEEKLY. [#1310](https://github.com/TigreGotico/chronologia/issues/1310)

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("gl")
    True
    >>> span, rest = extract_timespan('dez da noite', "gl", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T22:00:00', '')
    >>> span, rest = extract_timespan('unha da noite', "gl", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T01:00:00', '')
    >>> span, rest = extract_timespan('da noite', "gl", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T21:00:00', '')
    >>> span, rest = extract_timespan('o 3 de outubro de 1990', "gl", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('1990-10-03T00:00:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('tarde', "gl", anchor) is None
    True
    >>> extract_timespan('noite', "gl", anchor) is None
    True
    >>> extract_timespan('madrugada', "gl", anchor) is None
    True
    >>> extract_timespan('máis tarde', "gl", anchor) is None
    True
    >>> extract_timespan('15.06.2020', "gl", anchor) is None
    True
    >>> extract_timespan('quince días', "gl", anchor) is None
    True
    >>> extract_timespan('o século XX', "gl", anchor) is None
    True
    >>> extract_timespan('o século vinte', "gl", anchor) is None
    True

---
[← French](fr.md) · [Home](../index.md) · [Georgian →](ka.md)
