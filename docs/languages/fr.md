# French (`fr`)

<!-- agent-hint
covers: where each construction of the French locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/fr/lang.json, chronologia/locale/fr/*.voc, chronologia/extract/numlayer.py:NUMTAG_LANGS, test/nl_corpus_fr/, test/test_xfail_open_issues_*.py
generated: no
verify: .venv/bin/python -m doctest docs/languages/fr.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/fr.md && .venv/bin/python -c 'exec("import re,sys\nfrom datetime import datetime\nimport chronologia as C\ndef mins(d):\n    return (\"%.6f\" % (d.total_seconds() / 60)).rstrip(\"0\").rstrip(\".\")\ndef rem(r):\n    return \" and \\x60%s\\x60 left over\" % r if r else \"\"\ndef out(rd, tx, lg, an):\n    f = getattr(C, rd)\n    r = f(tx, lg, anchor=an) if rd == \"extract_duration\" else f(tx, lg, an)\n    if rd == \"extract_timespan\":\n        if r is None: return \"no reading\"\n        return \"%s to %s%s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), r.span.end.datetime().strftime(\"%Y-%m-%d %H:%M\"), rem(r.remainder))\n    if rd == \"extract_duration\":\n        if r is None: return \"no length\"\n        return \"a length of %s min%s\" % (mins(r.duration), rem(r.remainder))\n    if rd == \"extract_event\":\n        if r is None: return \"no event\"\n        return \"start %s, length %s, %s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), \"none\" if r.duration is None else mins(r.duration) + \" min\", \"summary \\x60%s\\x60\" % r.summary if r.summary else \"no summary\")\n    if r is None: return \"no rule\"\n    return \"the rule \\x60%s\\x60%s\" % (r.recurrence.to_string(), rem(r.remainder))\n\np=sys.argv[1]\nt=open(p).read()\nm=re.search(r\"\\n## Known limits\\n(.*?)(?=\\n---\\n|\\Z)\",t,re.S)\nbad=0\nn=0\ntot=0\nfor ln in (m[1].split(\"\\n\") if m else []):\n    if \"Example (\" not in ln: continue\n    tot+=1\n    g=re.search(r\"Example \\(reader \\x60(\\w+)\\x60, lang \\x60([\\w-]+)\\x60, anchor (\\d{4}-\\d\\d-\\d\\d \\d\\d:\\d\\d)\\): \\x60([^\\x60]+)\\x60 gives (.+?)\\. \\[#\\d+\\]\",ln)\n    if not g:\n        bad=1\n        print(\"example line does not parse:\",ln[:80])\n        continue\n    n+=1\n    o=out(g[1],g[4],g[2],datetime.strptime(g[3],\"%Y-%m-%d %H:%M\"))\n    if o!=g[5]:\n        bad=1\n        print(\"limit differs\",g[4],\"|\",g[5],\"|\",o)\nprint(\"known limits checked:\",n,\"of\",tot)\nsys.exit(bad)\n")' docs/languages/fr.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the French (`fr`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

One fact decides the most in this locale. French writes its numeric date with slashes and not with dots. `15/06/2020` reads. `15.06.2020` returns nothing at all. The dotted form is the official civil surface of German, Russian, Polish, Czech, Finnish, Turkish and Dutch. The parser reads it in those locales. But it is not French and is not treated as French.

Refusing the run is only half the rule. A numeral inside a date-shaped run is not read as a lone year because the run was rejected. `15.06.2020` answers nothing. It does not answer 2020 with the day and the month quietly gone. A year-first run is different: `2020.06.15` reads, because a four-digit lead is year-first in every language.

The clock is the other thing to know early. French counts toward the coming hour for the quarter to, `neuf heures moins le quart` being 08:45, which is what the subtractive clock order in `lang.json` reads. It counts forward with `et` for the quarter past and the half: `huit heures et quart`, `huit heures et demie`.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('neuf heures moins le quart', "fr", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T08:45:00', '')

## What ships

**Weekdays and months** ship wide and abbreviated. The vocabulary cites Unicode CLDR 47 for them.

**The date line** is little-endian and takes the day as a bare cardinal: `3 octobre 1990`, not an ordinal. `lang.json` sets `ordinal_dot` off. A dot after a numeral is never an ordinal marker in French, which is the same decision that keeps the dotted date out. The slashed numeric form reads, and so does the ISO-shaped year-first form on any separator.

**Relative offsets** run both ways with `dans` and `il y a`. `lang.json` allows the marker before or after the count. An optional article and an optional quantifier can stand in either position. The quantifiers include `quelques` and `plusieurs` for a vague three and `un`/`une` for one.

**The relative determiners** follow the noun in French. For that reason the locale sets `marker_position: post`, as in `la semaine prochaine` and `lundi dernier`. The locale overrides `rel_period` to accept a leading article, so the definite article on the noun does not block the read.

**The clock** carries `heures` as the hour word, `et` and `moins` as the two directions, `quart` and `demi`/`demie` as the fractions, `du matin` and `du soir` as the meridiem phrases, and `midi` and `minuit` as points. The vocabulary cites the half word to TLFi and Larousse under *moitié*. The same file supplies the period sense ("l'une des deux parties égales"). `la première moitié de 2020` reads as the first half-year.

**Day parts** take their boundaries from the Unicode CLDR 47 day-period chart for `fr`, transcribed in `chronologia/dayparts.py`. The vocabulary cites the Trésor de la langue française informatisé at CNRTL for the surfaces. There are four bands and they are not the English four. The `nuit` is the small hours `[00:00, 04:00)`: it is the beginning of the day named, not an English-shaped night that starts the previous evening.

The `matin` then opens at 04:00, two hours before the English morning. The `après-midi` runs `[12:00, 18:00)`, and the `soir` runs `[18:00, 24:00)` with no band between it and the nuit. The hyphenated `après-midi` is canonicalised through the tokenizer, which splits the hyphen into two tokens that the loader re-glues. An ASCII-folded twin ships for the same reason the pm meridiem keeps one.

**Ranges** are `du … au …` and `entre … et …`. `depuis` opens one that runs up to the anchor, and `jusqu'à` closes one that starts there.

**Quarters, ISO weeks, decades and eras.** `le premier trimestre 2020` and `T1 2020` both resolve, as do `semaine 12`, `les années 80`, `les années quatre-vingt`, `44 av. J.-C.` and `1990 ap. J.-C.`. A before-present marker and the Julian, Unix, Anno Mundi and Holocene era prefixes all ship.

**Fuzzy month parts** are `début`, `mi-` and `fin`, which cut the month into thirds: `début juin`, `mi-juin`, `fin juin`.

**The Roman calendar anchors** ship in the Latin classical forms and in the French vernacular ones (`calendes`, `nones` and `ides`). The vocabulary cites the French Wikipedia article *Calendrier romain*. `les ides de mars` resolves.

**Non-Gregorian calendars.** French carries month names for the Hebrew and Islamic civil calendars and for the French Republican calendar. It also carries the Japanese nengō era names. `15 ramadan 1440` resolves to its Gregorian day, and so does `15 nisan 5785`.

**Habitual recurrence** is `les lundis`, and the vocabulary explains the choice. The plural definite article on a weekday noun reads habitually. The singular `le lundi` is ambiguous between "next Monday" and "on Mondays", so the locale excludes it and only the unambiguous plural fires. The cited authorities are Larousse and Grevisse. This is a recurrence rather than a span, so it is the recurrence edge that answers it and the span edge returns nothing.

## Weaker provenance

The Hebrew and Islamic month vocabularies ship one spelling per month and record no source for the French transliteration chosen. Hebrew Tishrei ships as `tishrei` and `tishri`. The common French spelling `tichri` is absent. Nothing in the repository says which transliteration convention was followed.

The French Republican month names ship in ASCII only (`vendemiaire`, not `vendémiaire`) while the Gregorian months and the day parts carry their accents. No source is recorded for the Republican set.

The weekday and month names cite Unicode CLDR 47.

## What refuses

**The dotted date.** `15.06.2020`, `06.15.2020`, `15.6.2020` and `le 15.06.2020` all return nothing, and none of them yields a bare year either.

**A bare duration.** `quinze jours` returns nothing. A quantity without a direction marker is still only a quantity. A fortnight unit does ship, but it needs a marker to become a span.

## Open questions for a native speaker

1. Which transliteration convention should the Hebrew months follow, and should `tichri` and the other common French spellings ship alongside the ones already there?
2. Should the French Republican months carry their accents, and which spellings are standard in French historical writing?
3. Does `nuit` name the small hours of the day for a French reader? Or does `cette nuit`, said in the evening, name the night that is beginning?
4. Does `le lundi` deserve a reading at all, given that it is genuinely ambiguous, and if so which of the two readings should win?
5. Should a Republican-calendar year (`an II`) be readable, and in what surface?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("fr")
    True
    >>> span, rest = extract_timespan('neuf heures moins le quart', "fr", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T08:45:00', '')
    >>> span, rest = extract_timespan('huit heures et quart', "fr", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T08:15:00', '')
    >>> span, rest = extract_timespan('huit heures et demie', "fr", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T08:30:00', '')
    >>> span, rest = extract_timespan('3 octobre 1990', "fr", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('1990-10-03T00:00:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('15.06.2020', "fr", anchor) is None
    True
    >>> extract_timespan('06.15.2020', "fr", anchor) is None
    True
    >>> extract_timespan('15.6.2020', "fr", anchor) is None
    True
    >>> extract_timespan('le 15.06.2020', "fr", anchor) is None
    True
    >>> extract_timespan('quinze jours', "fr", anchor) is None
    True

## Known limits

Each line is an open issue with a strict `xfail` test for this language. The lines are grouped by topic. An example names the reader that produced it, the language and the anchor date, and shows what that reader gives on the test's own phrase.

**Clocks and parts of the day**

- An event with a noun before an evening clock reads a length of nine and a half hours. Example (reader `extract_event`, lang `fr`, anchor 2026-01-30 10:00): `dîner neuf heures et demie le soir demain` gives start 2026-01-31 18:00, length 570 min, summary `dîner`. [#1026](https://github.com/TigreGotico/chronologia/issues/1026)

- A clock with a dot between hour and minute gives no time. Example (reader `extract_timespan`, lang `fr`, anchor 2026-09-25 12:00): `à 8.15` gives no reading. [#1047](https://github.com/TigreGotico/chronologia/issues/1047)

- A clock in `heures` reads as a length. Example (reader `extract_duration`, lang `fr`, anchor 2017-06-27 13:04): `mets une alarme pour 7 heures demain matin` gives a length of 420 min and `mets une alarme demain matin` left over. [#1063](https://github.com/TigreGotico/chronologia/issues/1063)

- A count of hours of travel after `à` reads as a clock and loses the length. Example (reader `extract_timespan`, lang `fr`, anchor 2017-06-27 13:04): `à 8 heures de route` gives 2017-06-27 20:00 to 2017-06-27 20:01 and `de route` left over. [#1379](https://github.com/TigreGotico/chronologia/issues/1379)

- A length before a part of the day reads as a clock. [#1298](https://github.com/TigreGotico/chronologia/issues/1298)

**Dates, ranges and weeks**

- A unit word with no number counts as one. Example (reader `extract_timespan`, lang `fr`, anchor 2017-06-27 13:04): `il reste combien de jours avant le 15 mai` gives 2018-05-14 00:00 to 2018-05-15 00:00 and `il reste combien` left over. [#1004](https://github.com/TigreGotico/chronologia/issues/1004)

- Text that is no date reads as a date, or the wrong reading wins. Example (reader `extract_timespan`, lang `fr`, anchor 2117-09-03 13:30): `elle a 2h de route` gives 2117-09-04 02:00 to 2117-09-04 02:01 and `elle de route` left over. [#1035](https://github.com/TigreGotico/chronologia/issues/1035)

- Bare `fr` does not read the Belgian and Swiss tens. Example (reader `extract_duration`, lang `fr`, anchor 2026-01-30 10:00): `dans septante-et-un jours` gives a length of 1440 min and `dans septante-et` left over. [#1075](https://github.com/TigreGotico/chronologia/issues/1075)

- The last weekday of next month reads as the last weekday of this month. Example (reader `extract_event`, lang `fr`, anchor 2026-10-17 09:00): `le dernier vendredi du mois prochain` gives start 2026-10-30 00:00, length none, summary `prochain`. [#1295](https://github.com/TigreGotico/chronologia/issues/1295)

- A list of two days reads as a clock or as the wrong day. Example (reader `extract_timespan`, lang `fr`, anchor 2026-11-22 09:00): `le 14 et 15 mai` gives 2027-05-01 15:14 to 2027-05-01 15:15. [#1311](https://github.com/TigreGotico/chronologia/issues/1311)

- A range with a shared month or unit drops the unrelated words from the remainder. Example (reader `extract_timespan`, lang `fr`, anchor 2017-06-27 13:04): `xx du 10h au 12h` gives 2017-06-28 10:00 to 2017-06-28 12:01 and `xx du` left over. [#1351](https://github.com/TigreGotico/chronologia/issues/1351)

- A range lead after another word stays in the remainder. [#1355](https://github.com/TigreGotico/chronologia/issues/1355)

**Offsets, lengths and holidays**

- A count of hours or minutes before a holiday gives the day before at 00:00. Example (reader `extract_timespan`, lang `fr`, anchor 2026-09-25 12:00): `un quart d'heure avant noël` gives 2026-12-24 00:00 to 2026-12-25 00:00 and `un quart` left over. [#1087](https://github.com/TigreGotico/chronologia/issues/1087)

- `before christmas` ends after Christmas Day, not when it starts. Example (reader `extract_timespan`, lang `fr`, anchor 2026-09-25 12:00): `avant noël` gives 2026-09-25 12:00 to 2026-12-26 00:00. [#1097](https://github.com/TigreGotico/chronologia/issues/1097)

**Recurrence**

- A repeat count is not read. Example (reader `extract_recurrence`, lang `fr`, anchor 2026-11-22 09:00): `toutes les lundis 10 fois` gives the rule `FREQ=WEEKLY;BYDAY=MO` and `10 fois` left over. [#1322](https://github.com/TigreGotico/chronologia/issues/1322)

**Events, zones, business days and the API**

- A phrase with `moins le quart` leaves those words in the event summary. [#1028](https://github.com/TigreGotico/chronologia/issues/1028)

- The event summary keeps the article and the day word before a day number. Example (reader `extract_event`, lang `fr`, anchor 2025-06-18 10:30): `réunion le jour 5 décembre` gives start 2025-12-05 00:00, length none, summary `réunion le jour`. [#1218](https://github.com/TigreGotico/chronologia/issues/1218)

- The candidate list and the single-span reader read a clock with a length differently. [#1350](https://github.com/TigreGotico/chronologia/issues/1350)

- Input typed in decomposed (NFD) form reads differently from the composed (NFC) form. Example (reader `extract_timespan`, lang `fr`, anchor 2017-06-27 06:04): `le 5 février 2027` gives 2027-01-01 00:00 to 2028-01-01 00:00 and `le 5 février` left over. [#1353](https://github.com/TigreGotico/chronologia/issues/1353)

---
[← Finnish](fi.md) · [Home](../index.md) · [Galician →](gl.md)
