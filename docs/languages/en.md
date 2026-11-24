# English (`en`)

<!-- agent-hint
covers: where each construction of the English locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/en/lang.json, chronologia/locale/en/*.voc, chronologia/extract/numlayer.py:NUMTAG_LANGS, test/nl_corpus_en/, test/test_xfail_open_issues_*.py
generated: no
verify: .venv/bin/python -m doctest docs/languages/en.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/en.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the English (`en`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

English is the reference locale, and that is the honest headline. Its vocabulary was written from native competence rather than assembled from cited sources, so almost nothing in `chronologia/locale/en/` carries a provenance comment. Five files out of nearly three hundred, and each of those comments explains a parsing decision rather than attesting a surface. Where the pages for other languages can say which dictionary supplied a word, this one usually cannot. What English has instead is the largest test corpus in the project, and its refusals are argued in the corpus rather than in the vocabulary.

The second thing to know is what English does *not* write. `15.06.2020` returns nothing, and so does `06.15.2020`. The dotted numeric date is the official civil form of German, Russian, Polish, Czech, Finnish, Turkish and Dutch. The parser reads it there, English writes the numeric date with slashes and writes nothing at all with dots in either order. An English caller who types dots has not written a date.

The parser does not invent one. It does not fall back to reading the year either. An answer of `2020` would tell the caller that a whole year was asked for, when a day was.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('6 to 8 pm', "en", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T18:00:00', '')

## What ships

English carries the widest construction set of any locale, and the parts worth naming are the ones that are structurally interesting rather than merely present.

**Both slashed date orders read.** `15/06/2020` and `06/15/2020` both resolve to 15 June 2020, settled by whichever component can only be a day. Where neither can settle it, English reads month first: `06/07/2020` is 7 June.

**The nth-to-last idioms are three separate mechanisms**. The vocabulary keeps them apart on purpose. `next` in `next to last` is deliberately a different table from the relative-marker `next` that shifts a whole scope forward by one: "next to last" is not "next" plus "last" composing an offset. It is one fixed idiom meaning minus two, and sharing a table would let the two collide.

The `to` of `<ordinal> to last` is also a plain grammar literal, besides being one of the range connectives.

The single word `penultimate` is a synonym for the same thing. The vocabulary cites it to Merriam-Webster's gloss "next to the last". The vocabulary records that it is always minus two and never generalises the way the `<ordinal> to last` idiom does. There is no "second-to-penultimate".

**`tonight` is a fused word, not a composition.** It ships in its own today-fused day-part table, because it already names today's night band. The plain band word `night` is different: it composes with the clock's own future-roll rule.

**Non-Gregorian calendars, eras and deep time** all ship: Hebrew and Islamic civil months, French Republican months, Japanese nengō era names, Egyptian and other regnal series and Attic archon years. The Roman Kalends-Nones-Ides counting system ships too. So does the geological period vocabulary from the Archean to the Holocene. The Anno Mundi, Julian, Unix, Holocene and before-present eras ship as well.

**Jurisdiction-aware business days** ship for the United States, Great Britain, Germany, France, Spain, Portugal and Brazil.

## Weaker provenance

Nearly everything. Eight groups ship without a recorded source. They are weekdays and months, clock words, day parts, seasons, range markers, era abbreviations, non-Gregorian month names and geological periods. That does not mean they are doubtful, because they are ordinary English. A reader who wants to know where a surface came from will not find an answer in the vocabulary. The four comments that do exist explain grammar rather than attest words.

The one attested surface is `penultimate`, cited to Merriam-Webster.

## What refuses

English refusals are the most thoroughly argued in the project, because the English corpus is where the residue-veto design is pinned.

**The dotted date, in either order.** `15.06.2020` and `06.15.2020` return nothing and do not degrade to a bare year.

**A duration range dressed as a clock range.** `cook on low for 6 to 8 hours` returns nothing from the span edge. It names a length of time, not two times of day, and the subtractive-clock reading would otherwise hijack it: "6 to 8" as six minutes to eight, a minute-wide span for a sentence about six hours, with the unit stranded in the remainder. The discriminator is a trailing duration unit with no clock cue. A genuine clock range carries a meridiem or an explicit clock, so `6 to 8 pm`, `from 9 to 5` and `3:30 to 4:30` all stay real timespans. The duration itself belongs to the duration edge, not the span edge.

**An ordinal that does not exist inside its scope.** `the 13th month of 2026` and `the 0th week of may` return nothing. There is no overflow projection: the thirteenth month of 2026 is not January 2027. `the 12th month of 2026` resolves normally, so the veto does not over-fire.

**An impossible calendar day.** `the 5th Monday of February` returns nothing when that February has only four Mondays. It returns nothing rather than raising, because the library never raises. `day 32 of February` and `the 366th day of the year 2017` refuse. They do not fall back to the whole month or the whole year. `the 365th day of the year 2017` resolves.

**An ordinal-weekday recurrence with a bounded or week-scoped tail.** `every 3rd tuesday of next year`, `of last month`, `of next week` and their siblings yield no recurrence rule at all. The alternative was worse than nothing. A weaker reading would have folded only the head into an unbounded three-week cadence and stranded the tail. That is a different rule, not a small frequency error.

**A bare duration.** `a fortnight` returns nothing. `in a fortnight` resolves. A quantity with no direction marker is still only a quantity.

## Open questions

1. Should an unscoped `the second-to-last friday` resolve at all? It answers the same date as a plain `the last friday`, with the modifier stranded, where the month-scoped `the second to last friday of may` resolves correctly.
2. Is month-first the right default for an ambiguous slashed date? It is the American convention, and a British caller writing `06/07/2020` means 6 July.
3. Should the vocabulary carry sources at all for a native-competence locale, or is the corpus the right place for that record?

## Known limits

Each line is an open issue with a strict `xfail` test for this language. The most common cases come first. An example shows what the library gives on the test's own anchor date.

**Clocks and parts of the day**

- A date built from two parts loses one of them. Example: `july the fourth` gives 2027-07-01, where the test expects 2027-07-04. [#1034](https://github.com/TigreGotico/chronologia/issues/1034)

- A day number or an offset before a part of the day and a clock loses the day. Example: `in 2 days evening at 8` gives 2026-11-22 20:00, where the test expects 2026-11-24 20:00. [#1325](https://github.com/TigreGotico/chronologia/issues/1325)

- A number with a leading zero before `minutes` reads as a clock. Example: `0030 minutes` gives no reading. [#1331](https://github.com/TigreGotico/chronologia/issues/1331)

- A part of the day in another clause leaves a lone hour as spoken. Example: `at 8 or at 9 pm` gives 2017-06-28 08:00, where the test expects 2017-06-27 20:00. [#1001](https://github.com/TigreGotico/chronologia/issues/1001)

- A clock after `for`, `to` or `per` is not read, and a reschedule phrase reads the old time. Example: `move my alarm to 9` gives no reading. [#1008](https://github.com/TigreGotico/chronologia/issues/1008)

- A range whose end is a movable feast, a weekday date or a clocked date reads a year long. Example: `from early march to easter` gives 2027-03-29 00:00, where the test expects 2026-04-06 00:00. [#1309](https://github.com/TigreGotico/chronologia/issues/1309)

- A part of the day with no day word answers the band that has already passed. Example: `let the upcoming alarm come back each morning` gives 2017-06-27 06:00, where the test expects 2017-06-28. [#997](https://github.com/TigreGotico/chronologia/issues/997)

- Two parts of the day joined by `and` read as the first band and leave the hour behind. Example: `morning and evening at 8` gives 2026-09-25 20:00, where the test expects 2026-09-26 08:00. [#1049](https://github.com/TigreGotico/chronologia/issues/1049)

- A plural part of the day before an alarm loses the hour. Example: `good night, set an alarm at 7` gives 2026-09-25 21:00, where the test expects 2026-09-25 19:00. [#1051](https://github.com/TigreGotico/chronologia/issues/1051)

- `last night` with a clock reads the wrong night. Example: `last night at 11` gives 2026-11-22 23:00, where the test expects 2026-11-21 23:00. [#1333](https://github.com/TigreGotico/chronologia/issues/1333)

- A spoken hour with `tonight` reads the next morning, not this evening. Example: `at 8 tonight` gives 2017-06-28 08:00, where the test expects 2017-06-27 20:00. [#1002](https://github.com/TigreGotico/chronologia/issues/1002)

- An infinitive `to` before `tomorrow morning` opens a range. Example: `remind me to call the bank tomorrow morning` gives 2017-06-27 06:00, where the test expects 2017-06-28 06:00. [#1013](https://github.com/TigreGotico/chronologia/issues/1013)

- The minutes after an alarm hour are dropped. Example: `seven oh five` drops the five. [#1058](https://github.com/TigreGotico/chronologia/issues/1058)

- A list of hours reads the first two numbers as one clock. Example: `alarm at 7, 8 and 9 tonight` gives 2026-11-18 07:08, where the test expects 2026-11-17 19:00. [#1296](https://github.com/TigreGotico/chronologia/issues/1296)

- A list of two days reads as a clock or as the wrong day. Example: `on the 14th and 15th of may` gives 2026-12-14 00:00, where the test expects 2027-05-14 00:00. [#1311](https://github.com/TigreGotico/chronologia/issues/1311)

- The meridiem after an abbreviated hour word is lost. Example: `at 8 hr. pm` gives 2026-11-23 08:00, where the test expects 2026-11-23 20:00. [#1312](https://github.com/TigreGotico/chronologia/issues/1312)

- A range reading crosses a full stop. [#1352](https://github.com/TigreGotico/chronologia/issues/1352)

**Dates, ranges and weeks**

- A common word that is no time word reads as a time word. [#990](https://github.com/TigreGotico/chronologia/issues/990)

- A range with a shared month or unit drops the unrelated words from the remainder. Example: `June 5 to 12 yy` gives , where the test expects 'yy'      - yy. [#1351](https://github.com/TigreGotico/chronologia/issues/1351)

**Offsets, lengths and holidays**

- Text that is no date reads as a date, or the wrong reading wins. Example: `☕ tomorrow` gives , where the test expects '☕'      - ☕. [#1035](https://github.com/TigreGotico/chronologia/issues/1035)

- A count of hours or minutes before a holiday gives the day before at 00:00. Example: `an hour before easter` gives 2027-03-27 00:00, where the test expects 2027-03-27 23:00. [#1087](https://github.com/TigreGotico/chronologia/issues/1087)

- A clock with an offset from a holiday gives the wrong reading or the wrong order. Example: `at 9 one hour before christmas` gives 2026-12-24 00:00, where the test expects 2026-12-24 21:00. [#1196](https://github.com/TigreGotico/chronologia/issues/1196)

- Jurisdiction holidays raise at the bounds, skip the clock and skip the anchor day. Example: `every holiday in Portugal` gives 2027-01-01 00:00, where the test expects 2026-12-25 00:00. [#1255](https://github.com/TigreGotico/chronologia/issues/1255)

- A spelled year before a full stop gives no year when a word starts the next sentence. Example: `two thousand. Then we moved` gives no reading. [#1042](https://github.com/TigreGotico/chronologia/issues/1042)

- A vague count before a holiday gives the whole day before. Example: `a few hours before christmas` gives 2026-12-24 00:00, where the test expects 2026-09-25 12:00. [#1197](https://github.com/TigreGotico/chronologia/issues/1197)

- A unit word with no number counts as one. Example: `how many days before christmas` gives 2017-12-24 00:00, where the test expects 2017-12-25 00:00. [#1004](https://github.com/TigreGotico/chronologia/issues/1004)

- A range of amounts before a range of years gives a year from the first range. [#1040](https://github.com/TigreGotico/chronologia/issues/1040)

- `before christmas` ends after Christmas Day, not when it starts. Example: `before christmas` gives 2026-12-26 00:00, where the test expects 2026-12-25 00:00. [#1097](https://github.com/TigreGotico/chronologia/issues/1097)

- The unit word after `and a quarter` or `and a half` stays in the remainder. Example: `an hour and a quarter of an hour` gives hour. [#1240](https://github.com/TigreGotico/chronologia/issues/1240)

- A clock with `a quarter past` before a date leaves words in the remainder. Example: `at a quarter past ten on the 14th of march` gives at a. [#1301](https://github.com/TigreGotico/chronologia/issues/1301)

**Recurrence**

- An until bound in a recurrence resolves on the anchor day. Example: `every monday at 9 until 5` gives (), where the test expects (9,)      Right contains one more item: 9   Use -v to get more diff. [#1316](https://github.com/TigreGotico/chronologia/issues/1316)

- A part of the day before the clock is lost in a daily rule. Example: `every evening at 8` gives no reading. [#1324](https://github.com/TigreGotico/chronologia/issues/1324)

- A plural part of the day before a clock gives no recurrence. Example: `mornings at 8` gives no reading. [#1052](https://github.com/TigreGotico/chronologia/issues/1052)

- A clock range in a recurrence reads the end hour or a wrong minute. Example: `every monday 9 to 5` gives ((4,), (51,)), where the test expects ((9,), ())      At index 0 diff: (4,) != (9,)   Use -v to get more diff. [#1315](https://github.com/TigreGotico/chronologia/issues/1315)

- A date or an ordinal weekday next to a frequency word is dropped. Example: `the 15th of february every year` gives a yearly rule and drops the date. [#1320](https://github.com/TigreGotico/chronologia/issues/1320)

- A weekday or clock range in a recurrence loses its end. Example: `every monday to friday 9 am` gives ((None, 0),), where the test expects ((None, 0), (None, 1), (None, 2), (None, 3), (None, 4)). [#1321](https://github.com/TigreGotico/chronologia/issues/1321)

- A range after a recurring weekday reads its end as an until bound and leaves the start. Example: `every monday from june to august` gives 2026-11-23 00:00, where the test expects 2027-06-07 00:00. [#1291](https://github.com/TigreGotico/chronologia/issues/1291)

**Events, zones, business days and the API**

- The candidate reader does not raise in raise mode, where the event reader does. [#1276](https://github.com/TigreGotico/chronologia/issues/1276)

- A bare `after X` gives no reading, where ruling 33 says it is an open span. Example: `after monday` gives no reading. [#1098](https://github.com/TigreGotico/chronologia/issues/1098)

- The day of a day word reads as a length. Example: `the day after tomorrow` gives 1440 min with remainder 'after tomorrow', where the test expects nothing. [#1326](https://github.com/TigreGotico/chronologia/issues/1326)

- A year-less range that ends on 29 February spans into the next leap year. Example: `from 1 february to 29 february` gives 2027-02-01 00:00, where the test expects 2028-02-01 00:00. [#1330](https://github.com/TigreGotico/chronologia/issues/1330)

- A bare clock with a zone skips the 12-hour rule. Example: `9:30 utc` gives 2017-06-28 09:30 UTC, where the test expects 2017-06-27 21:30 UTC. [#1254](https://github.com/TigreGotico/chronologia/issues/1254)

- The sixth weekday of every month reads as the next such weekday. Example: `the sixth monday of every month` reads as the next Monday. [#1288](https://github.com/TigreGotico/chronologia/issues/1288)

- The last business day of every month reads as a plain monthly rule. Example: `the last business day of every month` gives FREQ=MONTHLY. [#1289](https://github.com/TigreGotico/chronologia/issues/1289)

- The nth weekday of a month reads as the whole month. Example: `the 3rd weekday of march` reads all of March. [#1290](https://github.com/TigreGotico/chronologia/issues/1290)

- The first few business days of a month read no span. Example: `the last 3 business days of the month` gives no reading. [#1303](https://github.com/TigreGotico/chronologia/issues/1303)

- An impossible day read apart from its month is dropped, and the rest still reads. Example: `in february on the 30th` gives February 2018 with `on the 30th` left over, where the test expects no date. [#1328](https://github.com/TigreGotico/chronologia/issues/1328)

- The candidate list and the single-span reader read a clock with a length differently. Example: `at 9 am for 2 hours` gives 2017-06-27 09:01, where the test expects 2017-06-27 11:00. [#1350](https://github.com/TigreGotico/chronologia/issues/1350)

- The candidate list and the single-span reader disagree on one phrase. [#995](https://github.com/TigreGotico/chronologia/issues/995)

- A night clock with minutes gives the morning hour, where the same clock without minutes gives the evening hour. [#1079](https://github.com/TigreGotico/chronologia/issues/1079)

- The event summary keeps the article and the day word before a day number. Example: `meeting on the day 5 of december` gives meeting on the day, where the test expects 'meeting'      - meeting. [#1218](https://github.com/TigreGotico/chronologia/issues/1218)

- A span that names a zone gives a wrong instant under an aware anchor. [#1253](https://github.com/TigreGotico/chronologia/issues/1253)

- The event summary turns a spelled numeral into a digit. Example: `a second meeting tomorrow` gives 2 meeting, where the test expects 'a second meeting'      - a second meeting. [#1297](https://github.com/TigreGotico/chronologia/issues/1297)

- A cardinal before a singular business-day noun reads nothing. Example: `pay rent on the 3 business day of the month` gives no reading. [#1304](https://github.com/TigreGotico/chronologia/issues/1304)

- A working-day or day-of-month recurrence reads as every day. Example: `every working day at 9` gives no reading. [#1310](https://github.com/TigreGotico/chronologia/issues/1310)

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("en")
    True
    >>> span, rest = extract_timespan('6 to 8 pm', "en", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T18:00:00', '')
    >>> span, rest = extract_timespan('from 9 to 5', "en", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T09:00:00', '')
    >>> span, rest = extract_timespan('3:30 to 4:30', "en", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T03:30:00', '')
    >>> span, rest = extract_timespan('the 12th month of 2026', "en", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2026-12-01T00:00:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('15.06.2020', "en", anchor) is None
    True
    >>> extract_timespan('06.15.2020', "en", anchor) is None
    True
    >>> extract_timespan('cook on low for 6 to 8 hours', "en", anchor) is None
    True
    >>> extract_timespan('the 13th month of 2026', "en", anchor) is None
    True
    >>> extract_timespan('the 0th week of may', "en", anchor) is None
    True
    >>> extract_timespan('the 5th Monday of February', "en", anchor) is None
    True
    >>> extract_timespan('day 32 of February', "en", anchor) is None
    True
    >>> extract_timespan('the 366th day of the year 2017', "en", anchor) is None
    True
    >>> extract_timespan('a fortnight', "en", anchor) is None
    True

---
[← Dutch](nl.md) · [Home](../index.md) · [Esperanto →](eo.md)
