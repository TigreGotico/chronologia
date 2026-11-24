# German (`de`)

<!-- agent-hint
covers: where each construction of the German locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/de/lang.json, chronologia/locale/de/*.voc, chronologia/extract/numlayer.py:NUMTAG_LANGS, test/nl_corpus_de/, test/test_xfail_open_issues_*.py
generated: no
verify: .venv/bin/python -m doctest docs/languages/de.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/de.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the German (`de`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

Two decisions shape this locale, and both are about the clock. German names the half hour by the hour it is heading toward. `halb acht` is 07:30 and never 08:30. `bare_half_to` in `lang.json` is what turns that on. And in the south, in the east and in Austria the same forward-looking logic extends to the quarters. A bare `viertel neun` is 08:15 and `dreiviertel neun` is 08:45, three quarters of the way to nine.

Western and northern German has no such bare forms and says `viertel nach acht` and `viertel vor neun` instead. That is a different parse path, so shipping both costs nothing. The bare quarters only add readings for strings that would otherwise stay unparsed. The vocabulary names Bastian Sick's *Zwiebelfisch* column "Von Viertel nach acht bis viertel neun" as the source for the regional forms.

Know one more thing before you read further. German writes its civil date with dots and the day first (`15.06.2020`). The corpus names DIN 5008 as the authority for that surface.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('halb acht', "de", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T07:30:00', '')

## What ships

**Weekdays and months** ship in the wide and abbreviated widths. The vocabulary records no source for them. They are the ordinary CLDR-standard German names, and the abbreviations are written without the trailing dot because the tokenizer strips it.

**The date line** is little-endian throughout, which `dmy` in `lang.json` declares. Three shapes read. The spelled form is `3. Oktober 1990`. Here the ordinal dot is a genuine ordinal marker. The setting `ordinal_dot` is on and capped at two digits, so a four-digit year can never pass for an ordinal. The dotted civil form is `15.06.2020`.

It reads all three components or none. A run like `15.13.2020` or `31.02.2020` names no date. The year inside it is not read on its own either. An answer of `2020` there would hand the caller a whole-year span with the day and month silently gone. The same all-or-nothing rule covers the slash and dash separators. A trailing sentence dot is punctuation, not a fourth component, so `15.06.2020.` still reads.

**Relative offsets** run in both directions with `in` and `vor` (`in drei Tagen`, `vor fünf Minuten`) and `lang.json` allows the marker on either side of the count. Units ship in singular and plural. Each unit has a separate `unit1_` singular file, so "one day" and "two days" pluralise correctly and do not share one lexeme.

**The relative determiners** are where German is unusually generous, and the vocabulary says why. Besides `letzt-`, everyday German uses `vorig-` and `vergangen-` for a past weekday. All three are attributive adjectives taking the full strong, weak and mixed endings. `marker_last.voc` lists every ending rather than a stem. The source named is Duden's inflection tables for *vorig*, *vergangen* and *letzter*. `letzt-` doubles as the ordinal determiner in `der letzte Montag im Mai`, from the same Duden entry.

**The clock** carries the bare regional quarters and the ordinary `viertel nach` and `viertel vor` directional forms. `Uhr` is the o'clock word and `um` is the "at" marker. Midnight and noon are points. Only one timezone offset ships, UTC.

**Day parts** are where German diverges hardest from English, and the vocabulary spells it out. German splits into `Morgen`, `Vormittag`, `Mittag`, `Nachmittag`, `Abend` and `Nacht`, where `Vormittag` is the half English has no word for at all, Duden glosses it as the "Zeit zwischen Morgen und Mittag". All six band boundaries come from the Unicode CLDR 47 day-period chart for `de` and are transcribed in `chronologia/dayparts.py`: Nacht `[00:00, 05:00)`, Morgen `[05:00, 10:00)`, Vormittag `[10:00, 12:00)`, Mittag `[12:00, 13:00)`, Nachmittag `[13:00, 18:00)` and Abend `[18:00, 24:00)`.

Two consequences of that table are worth naming. The Nachmittag opens at 13:00, after an hour-wide Mittag, and not at noon the way the English afternoon does. And the Nacht is the small hours of the day named, not the evening. The Abend holds the evening through to midnight on its own, so `heute Nacht` is 00:00-05:00 of today.

Only four of the six bands have vocabulary. `Mittag` is the noon clock landmark instead. `heute Mittag` resolves to the point 12:00. It does not resolve to the hour-wide band. `Morgen` has no day-part vocabulary, because `morgen` already means "tomorrow". A locale cannot read the same token both ways without guessing. The four that do ship (Vormittag, Nachmittag, Abend, Nacht) each carry both the noun form and the adverbial `-s` form. `abends` reads as well as `Abend`.

**The month framing marker** is `im`, the fusion of `in` and `dem`, which is the standard frame for a calendar month in `im Januar`. The vocabulary cites Wiktionary's German entry for *im*. `während` covers the explicit "during" reading. It ships in the umlauted and the ASCII spelling, as several German surfaces do.

**Ranges** open with `von`, `vom` or `ab` and close with `bis`. The vocabulary cites Duden's entry for *von*. `vom` is the fused form of *von dem*. It is the ordinary temporal range opener, paired with `bis`, as in `vom 3. bis
10. Juli`. `zwischen … und …` reads as a range too, and `seit` opens one that runs up to the anchor.

**Decades** read both spelled and written: `die achtziger Jahre` and `die 80er Jahre` resolve alike.

**Quarters, ISO weeks and eras.** `erstes Quartal 2020` and `Q1 2020` both resolve. ISO weeks read as `Woche 12` and `KW 12`. The eras are `v. Chr.` and `n. Chr.` with their expanded forms, the secular `v. u. z.` beside them, and a before-present marker.

**The Roman calendar anchors** ship in their German vernacular forms `Kalenden`, `Nonen` and `Iden`, cited to the German Wikipedia article *Römischer Kalender*, so `Iden des März` resolves.

## Weaker provenance

The bare toward-the-hour quarters rest on a single named source, and a widely read newspaper column rather than a grammar. The reading is not in doubt (the column exists to explain exactly this split) but it is regional. The locale ships it for all German without a dialect switch. Nothing in the locale distinguishes a southern speaker's `viertel neun` from a northern speaker's. A northern text that happens to contain those two words in that order will be read as a time.

The weekday and month names carry no recorded source at all. They are not in doubt either, but the page cannot point at what was consulted.

## What refuses

**A dotted pair with no year.** `15. 6.` returns nothing, and so does `am 15. 6. kommen wir`. Those are two ordinals. With no four-digit year to anchor the pattern, no date may be fabricated from them.

**Malformed dotted runs.** `1.2.3.4`, `15..06.2020`, `15.06.`, `0.0.0`, `99.99.9999`, `31.02.2020`, `32.06.2020` and `15.13.2020` all refuse, and so does the thousands-grouped number `1.000.000`. A run that continues past the shape (`15.06.20201`) refuses too, on every separator alike.

**A bare two-digit year.** `44`, `99` and `7` return nothing. `lang.json` sets `bare_year_min_digits` to four. A short bare number is never promoted to a year.

**`halb` on its own.** With no hour and no landmark after it, `halb` is not a time.

**The morning as a day part.** `morgens` returns nothing. `heute Morgen` resolves the whole of today with `Morgen` left in the remainder rather than narrowing to 05:00-10:00. The collision with `morgen` "tomorrow" is the reason. The band exists in the CLDR table but has no surface bound to it.

**A bare holiday offset marker.** `nach Ostern` returns nothing on its own. A holiday offset needs a measured distance: `zwei Wochen nach Ostern` and `vierzehn Tage nach Ostern` both resolve to the same day.

**The penultimate weekday of a month.** `der vorletzte Freitag im Mai` resolves the whole of May and leaves `der vorletzte` in the remainder. Only `letzt-` is wired as an ordinal-last determiner. There is no next-to-last vocabulary.

**A bare duration.** `vierzehn Tage` returns nothing. A quantity with no direction marker is still only a quantity, and this is the library's rule rather than anything German.

## Open questions for a native speaker

1. Should the bare toward-the-hour quarters be gated behind a regional variant rather than shipped for all German? The setting reads `viertel neun` as 08:15 in a northern text as readily as in a Bavarian one.
2. How should `Morgen` and `morgens` be told apart from `morgen` "tomorrow"? The distinction is capitalisation in writing and context in speech, and neither is available to a case-folding tokenizer.
3. Does the Nacht band really start at midnight for a German reader, given that `heute Nacht` said in the evening usually means the coming night?
4. Are `Kalenden`, `Nonen` and `Iden` the forms a German text actually uses, or is the Latin left untranslated in most modern writing?

## Known limits

Each line is an open issue with a strict `xfail` test for this language. The most common cases come first. An example shows what the library gives on the test's own anchor date.

**Clocks and parts of the day**

- A date built from two parts loses one of them. Example: `in 3 tagen um 15 uhr` gives 2117-09-06 13:30, where the test expects 2117-09-06 15:00. [#1034](https://github.com/TigreGotico/chronologia/issues/1034)

- A day word with a part of the day loses the clock. Example: `weck mich morgen früh um halb sieben` gives 2017-06-28 00:00, where the test expects 2017-06-28 06:30. [#1016](https://github.com/TigreGotico/chronologia/issues/1016)

- A morning or evening word that the reader does not join lets a lone clock take the other half of the day. Example: `um 6 früh` gives 2017-06-27 18:00, where the test expects 2017-06-28 06:00. [#1071](https://github.com/TigreGotico/chronologia/issues/1071)

- A day word with an early, late or part-of-day word gives midnight. Example: `morgen früh um 6 uhr` gives 2117-09-04 00:00, where the test expects 2117-09-04 06:00. [#1033](https://github.com/TigreGotico/chronologia/issues/1033)

- A clock with a dot between hour and minute gives no time. Example: `um 8.15` gives no reading. [#1047](https://github.com/TigreGotico/chronologia/issues/1047)

- A list of two days reads as a clock or as the wrong day. Example: `am 14. und 15. Mai` gives 2027-05-15 00:00, where the test expects 2027-05-14 00:00. [#1311](https://github.com/TigreGotico/chronologia/issues/1311)

- The meridiem after an abbreviated hour word is lost. Example: `um 8 Std. abends` gives 2026-11-23 08:00, where the test expects 2026-11-23 20:00. [#1312](https://github.com/TigreGotico/chronologia/issues/1312)

- A range reading crosses a full stop. Example: `Wir treffen uns am Montag. Der Bericht ist bis Freitag fällig.` gives 2017-07-08 00:00, where the test expects 2017-07-04 00:00. [#1352](https://github.com/TigreGotico/chronologia/issues/1352)

**Dates, ranges and weeks**

- The indefinite article before a day of a month reads as the first day. Example: `ein Tag im März` gives 2027-03-02 00:00, where the test expects 2027-04-01 00:00. [#1306](https://github.com/TigreGotico/chronologia/issues/1306)

- A range with a shared month or unit drops the unrelated words from the remainder. Example: `xx 3. bis 10. Juli` gives , where the test expects 'xx'      - xx. [#1351](https://github.com/TigreGotico/chronologia/issues/1351)

- Decomposed input reads differently from composed input. Example: `am 5. März 2027 um 15 Uhr` gives 2027-01-01 15:00, where the test expects 2027-03-05 15:00. [#1353](https://github.com/TigreGotico/chronologia/issues/1353)

**Offsets, lengths and holidays**

- Text that is no date reads as a date, or the wrong reading wins. Example: `Installiere Version 1.15.20 morgen` gives 2020-01-15 00:00, where the test expects 2026-09-24 00:00. [#1035](https://github.com/TigreGotico/chronologia/issues/1035)

**Recurrence**

- A weekday or clock range in a recurrence loses its end. Example: `jeden Montag bis Freitag 9 Uhr` gives ((None, 0), (None, 4)), where the test expects ((None, 0), (None, 1), (None, 2), (None, 3), (None, 4)). [#1321](https://github.com/TigreGotico/chronologia/issues/1321)

- A repeat count is not read. Example: `jeden Montag 10 mal` gives None, where the test expects 10. [#1322](https://github.com/TigreGotico/chronologia/issues/1322)

- A range after a recurring weekday reads its end as an until bound and leaves the start. Example: `jeden Montag von Juni bis August` gives juni. [#1291](https://github.com/TigreGotico/chronologia/issues/1291)

- An until bound in a recurrence resolves on the anchor day. Example: `bis Ende Juni` ends before the anchor. [#1316](https://github.com/TigreGotico/chronologia/issues/1316)

**Events, zones, business days and the API**

- A night clock with minutes gives the morning hour, where the same clock without minutes gives the evening hour. Example: `um 11:00 nachts` gives 2017-06-28 11:00, where the test expects 2017-06-27 23:00. [#1079](https://github.com/TigreGotico/chronologia/issues/1079)

- The candidate list and the single-span reader read a clock with a length differently. Example: `um 9 Uhr für 2 Stunden` gives 2017-06-27 09:01, where the test expects 2017-06-27 11:00. [#1350](https://github.com/TigreGotico/chronologia/issues/1350)

- A decimal count gives no length. Example: `weck mich in 3 wochen, 497 tagen und 391.6 sekunden` gives 745920 min, where the test expects datetime.timedelta(days=518, seconds=391, microseconds=600000). [#1204](https://github.com/TigreGotico/chronologia/issues/1204)

- The event summary keeps the article and the day word before a day number. Example: `Treffen am Tag 5 Mai` gives treffen am tag, where the test expects 'treffen'      - treffen. [#1218](https://github.com/TigreGotico/chronologia/issues/1218)

- A bare clock with a zone skips the 12-hour rule. Example: `vor 9:30 utc` gives 2017-06-28 09:31 UTC, where the test expects 2017-06-27 21:31 UTC. [#1254](https://github.com/TigreGotico/chronologia/issues/1254)

- The candidate reader does not raise in raise mode, where the event reader does. [#1276](https://github.com/TigreGotico/chronologia/issues/1276)

- An impossible day read apart from its month is dropped, and the rest still reads. Example: `am 30. Februar um 9 Uhr` gives 21:00 today with `am 30. Februar` left over, where the test expects no date. [#1328](https://github.com/TigreGotico/chronologia/issues/1328)

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("de")
    True
    >>> span, rest = extract_timespan('halb acht', "de", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T07:30:00', '')
    >>> span, rest = extract_timespan('viertel neun', "de", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T08:15:00', '')
    >>> span, rest = extract_timespan('dreiviertel neun', "de", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T08:45:00', '')
    >>> span, rest = extract_timespan('heute Nacht', "de", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T00:00:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('15. 6.', "de", anchor) is None
    True
    >>> extract_timespan('1.2.3.4', "de", anchor) is None
    True
    >>> extract_timespan('15..06.2020', "de", anchor) is None
    True
    >>> extract_timespan('15.06.', "de", anchor) is None
    True
    >>> extract_timespan('0.0.0', "de", anchor) is None
    True
    >>> extract_timespan('99.99.9999', "de", anchor) is None
    True
    >>> extract_timespan('31.02.2020', "de", anchor) is None
    True
    >>> extract_timespan('32.06.2020', "de", anchor) is None
    True
    >>> extract_timespan('15.13.2020', "de", anchor) is None
    True
    >>> extract_timespan('44', "de", anchor) is None
    True
    >>> extract_timespan('99', "de", anchor) is None
    True
    >>> extract_timespan('7', "de", anchor) is None
    True
    >>> extract_timespan('morgens', "de", anchor) is None
    True
    >>> extract_timespan('nach Ostern', "de", anchor) is None
    True
    >>> extract_timespan('vierzehn Tage', "de", anchor) is None
    True

---
[← Georgian](ka.md) · [Home](../index.md) · [Greek →](el.md)
