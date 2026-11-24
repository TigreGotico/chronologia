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

**The date line** is little-endian throughout, which `dmy` in `lang.json` declares. Three shapes read. The spelled form is `3. Oktober 1990`, where the ordinal dot is a genuine ordinal marker: `ordinal_dot` is on, capped at two digits so a four-digit year can never be mistaken for one. The dotted civil form is `15.06.2020`.

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

Each limit below has an open issue and a strict `xfail` test that fails when the limit is fixed.

- [#1016](https://github.com/TigreGotico/chronologia/issues/1016): de: "morgen früh um sechs" and "auf fünfzehn Uhr" lose the clock

- [#1033](https://github.com/TigreGotico/chronologia/issues/1033): A day word with an early, late or part-of-day word gives midnight: "mañana temprano", "morgen früh", "freitag morgen"

- [#1034](https://github.com/TigreGotico/chronologia/issues/1034): A date built from two parts loses one: an offset with a clock, a count from a day word, the nth weekday of a relative period

- [#1035](https://github.com/TigreGotico/chronologia/issues/1035): Text that is no date reads as a date, or the wrong reading wins: arithmetic, version numbers, "a third of", a holiday name used as a modifier

- [#1047](https://github.com/TigreGotico/chronologia/issues/1047): A dotted clock gives no time in eight locales: es "a las 8.30", pt "às 8.15", it "alle 8.30"

- [#1071](https://github.com/TigreGotico/chronologia/issues/1071): A morning or evening word the reader does not join lets a lone clock take the other half: de "früh", nb "morgenen", nn "morgonen", de "Uhr abends"

- [#1079](https://github.com/TigreGotico/chronologia/issues/1079): nl "om 11:00 's nachts" gives 11:00 while "om 11 's nachts" gives 23:00, de "elf Uhr nachts" needs a ruling

- [#1204](https://github.com/TigreGotico/chronologia/issues/1204): extract_duration: a decimal count gives no length ("1.5 horas", "7.5 segundos")

- [#1218](https://github.com/TigreGotico/chronologia/issues/1218): Event summary keeps the article and day word before a day number in en, fr, de and nl

- [#1254](https://github.com/TigreGotico/chronologia/issues/1254): A bare clock with a zone skips the 12-hour rule ("9:30 utc" reads tomorrow 09:30)

- [#1276](https://github.com/TigreGotico/chronologia/issues/1276): extract_candidates does not raise in raise mode where extract_event does

- [#1291](https://github.com/TigreGotico/chronologia/issues/1291): de: "jeden Montag von Juni bis August" reads "bis August" as UNTIL and leaves "von Juni"

- [#1306](https://github.com/TigreGotico/chronologia/issues/1306): es, pt, de, nl, ca: the indefinite article in "un día de marzo" reads as "the 1st day of march"

- [#1311](https://github.com/TigreGotico/chronologia/issues/1311): A list of two days reads as a clock or the wrong day: es "el 14 y 15 de mayo" gives 1 May 14:15

- [#1312](https://github.com/TigreGotico/chronologia/issues/1312): Meridiem after an abbreviated hour word is lost: "um 8 Std. abends", "at 8 hr. pm", pt "às 5 pm" read as morning

- [#1316](https://github.com/TigreGotico/chronologia/issues/1316): An until bound in a recurrence resolves on the anchor day: "every monday at 9 until 5 pm" never occurs, de "bis Ende Juni" ends before the anchor

- [#1321](https://github.com/TigreGotico/chronologia/issues/1321): Weekday and clock ranges in a recurrence: nl "tot en met vrijdag" differs from "t/m", "to friday 9 am" loses the range, "until 5/12" loses the date

- [#1322](https://github.com/TigreGotico/chronologia/issues/1322): Only en reads a repeat count: de "jeden Montag 10 mal", es "cada lunes 10 veces" leave the count unread

- [#1328](https://github.com/TigreGotico/chronologia/issues/1328): An impossible day read apart from its month is dropped and the rest still reads: "in february on the 30th", "annually on the 32nd of january"

- [#1350](https://github.com/TigreGotico/chronologia/issues/1350): Candidate list and extract_timespan read a clock with a length differently: de "um 9 Uhr für 2 Stunden"

- [#1351](https://github.com/TigreGotico/chronologia/issues/1351): A range with a shared month or unit drops the unrelated words from the remainder: en "please 5-12 June"

- [#1352](https://github.com/TigreGotico/chronologia/issues/1352): A range reading crosses a full stop: de "am Montag. Der Bericht ist bis Freitag"

- [#1353](https://github.com/TigreGotico/chronologia/issues/1353): Decomposed (NFD) input reads differently from composed (NFC) input: fr "ouvrés", pt "março"

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
