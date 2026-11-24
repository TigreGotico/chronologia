# English (`en`)

<!-- agent-hint
covers: where each construction of the English locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/en/lang.json, chronologia/locale/en/*.voc, chronologia/extract/numlayer.py:NUMTAG_LANGS, test/nl_corpus_en/, test/test_xfail_open_issues_*.py
generated: no
verify: .venv/bin/python -m doctest docs/languages/en.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/en.md && .venv/bin/python -c 'exec("import re,sys\nfrom datetime import datetime\nimport chronologia as C\ndef mins(d):\n    return (\"%.6f\" % (d.total_seconds() / 60)).rstrip(\"0\").rstrip(\".\")\ndef rem(r):\n    return \" and \\x60%s\\x60 left over\" % r if r else \"\"\ndef out(rd, tx, lg, an):\n    f = getattr(C, rd)\n    r = f(tx, lg, anchor=an) if rd == \"extract_duration\" else f(tx, lg, an)\n    if rd == \"extract_timespan\":\n        if r is None: return \"no reading\"\n        return \"%s to %s%s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), r.span.end.datetime().strftime(\"%Y-%m-%d %H:%M\"), rem(r.remainder))\n    if rd == \"extract_duration\":\n        if r is None: return \"no length\"\n        return \"a length of %s min%s\" % (mins(r.duration), rem(r.remainder))\n    if rd == \"extract_event\":\n        if r is None: return \"no event\"\n        return \"start %s, length %s, %s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), \"none\" if r.duration is None else mins(r.duration) + \" min\", \"summary \\x60%s\\x60\" % r.summary if r.summary else \"no summary\")\n    if r is None: return \"no rule\"\n    return \"the rule \\x60%s\\x60%s\" % (r.recurrence.to_string(), rem(r.remainder))\n\np=sys.argv[1]\nt=open(p).read()\nm=re.search(r\"\\n## Known limits\\n(.*?)(?=\\n---\\n|\\Z)\",t,re.S)\nbad=0\nn=0\ntot=0\nfor ln in (m[1].split(\"\\n\") if m else []):\n    if \"Example (\" not in ln: continue\n    tot+=1\n    g=re.search(r\"Example \\(reader \\x60(\\w+)\\x60, lang \\x60([\\w-]+)\\x60, anchor (\\d{4}-\\d\\d-\\d\\d \\d\\d:\\d\\d)\\): \\x60([^\\x60]+)\\x60 gives (.+?)\\. \\[#\\d+\\]\",ln)\n    if not g:\n        bad=1\n        print(\"example line does not parse:\",ln[:80])\n        continue\n    n+=1\n    o=out(g[1],g[4],g[2],datetime.strptime(g[3],\"%Y-%m-%d %H:%M\"))\n    if o!=g[5]:\n        bad=1\n        print(\"limit differs\",g[4],\"|\",g[5],\"|\",o)\nprint(\"known limits checked:\",n,\"of\",tot)\nsys.exit(bad)\n")' docs/languages/en.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the English (`en`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

English is the reference locale, and that is the honest headline. Its vocabulary was written from native competence rather than assembled from cited sources, so most files in `chronologia/locale/en/` carry no provenance comment. The weekday and month names cite Unicode CLDR 47, and a few single words cite Wiktionary or Merriam-Webster. Where the pages for other languages can say which dictionary supplied a word, this one usually cannot. What English has instead is the largest test corpus in the project, and its refusals are argued in the corpus rather than in the vocabulary.

The second thing to know is what English does *not* write. `15.06.2020` returns nothing, and so does `06.15.2020`. The dotted numeric date is the official civil form of German, Russian, Polish, Czech, Finnish, Turkish and Dutch. The parser reads it there. English writes the numeric date with slashes and writes nothing at all with dots in either order. An English caller who types dots has not written a date.

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

Much of the English vocabulary records no source. Clock words, seasons, range markers, era abbreviations, non-Gregorian month names and geological periods ship without a recorded source. Of the day parts, only the plural `mornings` cites a source. That does not mean they are doubtful, because they are ordinary English. A reader who wants to know where a surface came from will not find an answer in the vocabulary.

`penultimate` cites Merriam-Webster.

## What refuses

English refusals are the most thoroughly argued in the project, because the English corpus is where the residue-veto design is pinned.

**The dotted date, in either order.** `15.06.2020` and `06.15.2020` return nothing and do not degrade to a bare year.

**A duration range dressed as a clock range.** `cook on low for 6 to 8 hours` returns nothing from the span edge. It names a length of time, not two times of day, and the subtractive-clock reading would otherwise hijack it: "6 to 8" as six minutes to eight, a minute-wide span for a sentence about six hours, with the unit stranded in the remainder. The discriminator is a trailing duration unit with no clock cue. A genuine clock range carries a meridiem or an explicit clock, so `6 to 8 pm`, `from 9 to 5` and `3:30 to 4:30` all stay real timespans. The duration itself belongs to the duration edge, not the span edge.

**An ordinal that does not exist inside its scope.** `the 13th month of 2026` and `the 0th week of may` return nothing. There is no overflow projection: the thirteenth month of 2026 is not January 2027. `the 12th month of 2026` resolves normally, so the veto does not over-fire.

**An impossible calendar day.** `the 5th Monday of February` returns nothing when that February has only four Mondays. It returns nothing, and it does not raise under `impossible="raise"` either: with no year named, only an ordinal above five raises, such as `the 6th Monday of February`. `the 5th Monday of February 2017` raises, because it names the year. `day 32 of February` and `the 366th day of the year 2017` refuse. They do not fall back to the whole month or the whole year. `the 365th day of the year 2017` resolves.

**An ordinal-weekday recurrence with a bounded or week-scoped tail.** `every 3rd tuesday of next year`, `of last month`, `of next week` and their siblings yield no recurrence rule at all. The alternative was worse than nothing. A weaker reading would have folded only the head into an unbounded three-week cadence and stranded the tail. That is a different rule, not a small frequency error.

**A bare duration.** `a fortnight` returns nothing. `in a fortnight` resolves. A quantity with no direction marker is still only a quantity.

## Open questions

1. Should an unscoped `the second-to-last friday` resolve at all? It answers the same date as a plain `the last friday`, with the modifier stranded, where the month-scoped `the second to last friday of may` resolves correctly.
2. Is month-first the right default for an ambiguous slashed date? It is the American convention, and a British caller writing `06/07/2020` means 6 July.
3. Should the vocabulary carry sources at all for a native-competence locale, or is the corpus the right place for that record?

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

## Known limits

Each line is an open issue with a strict `xfail` test for this language. The lines are grouped by topic. An example names the reader that produced it, the language and the anchor date, and shows what that reader gives on the test's own phrase.

**Clocks and parts of the day**

- A part of the day with no day word answers the band that has already passed. Example (reader `extract_timespan`, lang `en`, anchor 2017-06-27 13:04): `let the upcoming alarm come back each morning` gives 2017-06-27 06:00 to 2017-06-27 12:00 and `let the upcoming alarm come back each` left over. [#997](https://github.com/TigreGotico/chronologia/issues/997)

- A part of the day in another clause leaves a lone hour as spoken. Example (reader `extract_timespan`, lang `en`, anchor 2017-06-27 13:04): `at 8 or at 9 pm` gives 2017-06-28 08:00 to 2017-06-28 08:01 and `or at 9 pm` left over. [#1001](https://github.com/TigreGotico/chronologia/issues/1001)

- A spoken hour with `tonight` reads the next morning, not this evening. Example (reader `extract_timespan`, lang `en`, anchor 2017-06-27 13:04): `at 8 tonight` gives 2017-06-28 08:00 to 2017-06-28 08:01 and `tonight` left over. [#1002](https://github.com/TigreGotico/chronologia/issues/1002)

- A clock after `for`, `to` or `per` is not read, and a reschedule phrase reads the old time. Example (reader `extract_timespan`, lang `en`, anchor 2017-06-27 13:04): `move my alarm to 9` gives no reading. [#1008](https://github.com/TigreGotico/chronologia/issues/1008)

- An infinitive `to` before `tomorrow morning` opens a range. Example (reader `extract_timespan`, lang `en`, anchor 2017-06-27 13:04): `remind me to call the bank tomorrow morning` gives 2017-06-27 06:00 to 2017-06-28 12:00 and `remind me call the bank` left over. [#1013](https://github.com/TigreGotico/chronologia/issues/1013)

- Two parts of the day joined by `and` read as the first band and leave the hour behind. Example (reader `extract_timespan`, lang `en`, anchor 2026-09-25 12:00): `morning and evening at 8` gives 2026-09-25 06:00 to 2026-09-25 12:00 and `and evening at 8` left over. [#1049](https://github.com/TigreGotico/chronologia/issues/1049)

- A plural part of the day before an alarm loses the hour. Example (reader `extract_timespan`, lang `en`, anchor 2026-09-25 12:00): `good night, set an alarm at 7` gives 2026-09-25 21:00 to 2026-09-26 06:00 and `good set an alarm at 7` left over. [#1051](https://github.com/TigreGotico/chronologia/issues/1051)

- The minutes after an alarm hour are dropped. [#1058](https://github.com/TigreGotico/chronologia/issues/1058)

- A night clock with minutes gives the morning hour, where the same clock without minutes gives the evening hour. [#1079](https://github.com/TigreGotico/chronologia/issues/1079)

- The unit word after `and a quarter` or `and a half` stays in the remainder. Example (reader `extract_duration`, lang `en`, anchor 2017-06-27 13:04): `an hour and a quarter of an hour` gives a length of 75 min and `hour` left over. [#1240](https://github.com/TigreGotico/chronologia/issues/1240)

- A list of hours reads the first two numbers as one clock. Example (reader `extract_timespan`, lang `en`, anchor 2026-11-17 08:00): `alarm at 7, 8 and 9 tonight` gives 2026-11-18 07:08 to 2026-11-18 07:09 and `alarm and 9 tonight` left over. [#1296](https://github.com/TigreGotico/chronologia/issues/1296)

- A clock with `a quarter past` before a date leaves words in the remainder. Example (reader `extract_timespan`, lang `en`, anchor 2026-11-22 09:00): `at a quarter past ten on the 14th of march` gives 2027-03-14 10:15 to 2027-03-14 10:16 and `at a` left over. [#1301](https://github.com/TigreGotico/chronologia/issues/1301)

- The meridiem after an abbreviated hour word is lost. Example (reader `extract_timespan`, lang `en`, anchor 2026-11-22 23:00): `at 8 hr. pm` gives 2026-11-23 08:00 to 2026-11-23 08:01 and `hr. pm` left over. [#1312](https://github.com/TigreGotico/chronologia/issues/1312)

- A day number or an offset before a part of the day and a clock loses the day. Example (reader `extract_timespan`, lang `en`, anchor 2026-11-22 09:00): `in 2 days evening at 8` gives 2026-11-22 20:00 to 2026-11-22 20:01 and `in 2 days` left over. [#1325](https://github.com/TigreGotico/chronologia/issues/1325)

- `last night` with a clock reads the wrong night. Example (reader `extract_timespan`, lang `en`, anchor 2026-11-22 09:00): `last night at 11` gives 2026-11-22 23:00 to 2026-11-22 23:01. [#1333](https://github.com/TigreGotico/chronologia/issues/1333)

**Dates, ranges and weeks**

- A common word that is no time word reads as a time word. Example (reader `extract_timespan`, lang `en`, anchor 2026-10-17 12:00): `it may be late` gives 2027-05-01 00:00 to 2027-06-01 00:00 and `it be late` left over. [#990](https://github.com/TigreGotico/chronologia/issues/990)

- A unit word with no number counts as one. Example (reader `extract_timespan`, lang `en`, anchor 2017-06-27 13:04): `how many days before christmas` gives 2017-12-24 00:00 to 2017-12-25 00:00 and `how many` left over. [#1004](https://github.com/TigreGotico/chronologia/issues/1004)

- A date built from two parts loses one of them. Example (reader `extract_timespan`, lang `en`, anchor 2026-09-25 12:00): `half of two weeks before christmas` gives 2026-12-11 00:00 to 2026-12-12 00:00 and `half` left over. [#1034](https://github.com/TigreGotico/chronologia/issues/1034)

- Text that is no date reads as a date, or the wrong reading wins. Example (reader `extract_timespan`, lang `en`, anchor 2117-09-03 13:30): `2400` gives 2400-01-01 00:00 to 2401-01-01 00:00. [#1035](https://github.com/TigreGotico/chronologia/issues/1035)

- A range of amounts before a range of years gives a year from the first range. Example (reader `extract_timespan`, lang `en`, anchor 2017-06-27 13:04): `from two thousand to three thousand dollars, from two thousand to two thousand and ten` gives 2000-01-01 00:00 to 2001-01-01 00:00 and `from two thousand to three thousand dollars, from to two thousand and ten` left over. [#1040](https://github.com/TigreGotico/chronologia/issues/1040)

- A spelled range of units before `ago` gives one point and leaves the first number over. [#1041](https://github.com/TigreGotico/chronologia/issues/1041)

- A spelled year before a full stop gives no year when a word starts the next sentence. Example (reader `extract_timespan`, lang `en`, anchor 2017-06-27 13:04): `two thousand. Then we moved` gives no reading. [#1042](https://github.com/TigreGotico/chronologia/issues/1042)

- A spelled year range with `the year` or `the years` and a word after it gives only the first year. Example (reader `extract_timespan`, lang `en`, anchor 2026-01-30 10:00): `from the year two thousand to two thousand and ten in Europe` gives 2000-01-01 00:00 to 2001-01-01 00:00 and `from to two thousand and ten in Europe` left over. [#1054](https://github.com/TigreGotico/chronologia/issues/1054)

- The nth weekday of a month reads as the whole month. [#1290](https://github.com/TigreGotico/chronologia/issues/1290)

- A range whose end is a movable feast, a weekday date or a clocked date reads a year long. Example (reader `extract_timespan`, lang `en`, anchor 2026-11-22 09:00): `from early march to easter` gives 2026-03-01 00:00 to 2027-03-29 00:00. [#1309](https://github.com/TigreGotico/chronologia/issues/1309)

- A list of two days reads as a clock or as the wrong day. Example (reader `extract_timespan`, lang `en`, anchor 2026-11-22 09:00): `on the 14th and 15th of may` gives 2026-12-14 00:00 to 2026-12-15 00:00 and `and 15th of may` left over. [#1311](https://github.com/TigreGotico/chronologia/issues/1311)

- A year-less range that ends on 29 February spans into the next leap year. Example (reader `extract_timespan`, lang `en`, anchor 2026-11-22 09:00): `from 1 february to 29 february` gives 2027-02-01 00:00 to 2028-03-01 00:00. [#1330](https://github.com/TigreGotico/chronologia/issues/1330)

- A range with a shared month or unit drops the unrelated words from the remainder. Example (reader `extract_timespan`, lang `en`, anchor 2017-06-27 13:04): `June 5 to 12 yy` gives 2018-06-05 00:00 to 2018-06-13 00:00. [#1351](https://github.com/TigreGotico/chronologia/issues/1351)

- A range reading crosses a full stop. [#1352](https://github.com/TigreGotico/chronologia/issues/1352)

**Offsets, lengths and holidays**

- A count of hours or minutes before a holiday gives the day before at 00:00. Example (reader `extract_timespan`, lang `en`, anchor 2026-09-25 12:00): `an hour before easter` gives 2027-03-27 00:00 to 2027-03-28 00:00. [#1087](https://github.com/TigreGotico/chronologia/issues/1087)

- `before christmas` ends after Christmas Day, not when it starts. Example (reader `extract_timespan`, lang `en`, anchor 2026-09-25 12:00): `before christmas` gives 2026-09-25 12:00 to 2026-12-26 00:00. [#1097](https://github.com/TigreGotico/chronologia/issues/1097)

- A bare `after X` gives no reading, where ruling 33 says it is an open span. Example (reader `extract_timespan`, lang `en`, anchor 2026-10-17 12:00): `after monday` gives no reading. [#1098](https://github.com/TigreGotico/chronologia/issues/1098)

- A clock with an offset from a holiday gives the wrong reading or the wrong order. Example (reader `extract_timespan`, lang `en`, anchor 2026-09-25 12:00): `at 9 one hour before christmas` gives 2026-12-24 00:00 to 2026-12-25 00:00 and `at 9` left over. [#1196](https://github.com/TigreGotico/chronologia/issues/1196)

- A vague count before a holiday gives the whole day before. Example (reader `extract_timespan`, lang `en`, anchor 2026-09-25 12:00): `a few hours before christmas` gives 2026-12-24 00:00 to 2026-12-25 00:00. [#1197](https://github.com/TigreGotico/chronologia/issues/1197)

- The day of a day word reads as a length. Example (reader `extract_duration`, lang `en`, anchor 2026-11-22 09:00): `the day after tomorrow` gives a length of 1440 min and `after tomorrow` left over. [#1326](https://github.com/TigreGotico/chronologia/issues/1326)

- A number with a leading zero before `minutes` reads as a clock and gives no length. Example (reader `extract_duration`, lang `en`, anchor 2026-11-22 09:00): `0030 minutes` gives no length. [#1331](https://github.com/TigreGotico/chronologia/issues/1331)

- The hour symbol `h` after `for` gives no length. [#1362](https://github.com/TigreGotico/chronologia/issues/1362)

**Recurrence**

- A plural part of the day before a clock gives no recurrence. Example (reader `extract_recurrence`, lang `en`, anchor 2026-09-25 12:00): `mornings at 8` gives no rule. [#1052](https://github.com/TigreGotico/chronologia/issues/1052)

- The sixth weekday of every month reads as the next such weekday. [#1288](https://github.com/TigreGotico/chronologia/issues/1288)

- A range after a recurring weekday reads its end as an until bound and leaves the start. Example (reader `extract_event`, lang `en`, anchor 2026-11-22 09:00): `every monday from june to august` gives start 2026-11-23 00:00, length none, no summary. [#1291](https://github.com/TigreGotico/chronologia/issues/1291)

- A clock range in a recurrence reads the end hour or a wrong minute. Example (reader `extract_recurrence`, lang `en`, anchor 2026-11-22 09:00): `every monday 9 to 5` gives the rule `FREQ=WEEKLY;BYDAY=MO;BYHOUR=4;BYMINUTE=51`. [#1315](https://github.com/TigreGotico/chronologia/issues/1315)

- An until bound in a recurrence resolves on the anchor day. Example (reader `extract_recurrence`, lang `en`, anchor 2026-11-22 09:00): `every monday at 9 until 5` gives the rule `FREQ=WEEKLY;UNTIL=20261122T090000;BYDAY=MO` and `5` left over. [#1316](https://github.com/TigreGotico/chronologia/issues/1316)

- A date or an ordinal weekday next to a frequency word is dropped. Example (reader `extract_recurrence`, lang `en`, anchor 2026-11-22 09:00): `the 15th of february every year` gives the rule `FREQ=YEARLY` and `the 15th of february` left over. [#1320](https://github.com/TigreGotico/chronologia/issues/1320)

- A weekday or clock range in a recurrence loses its end. Example (reader `extract_recurrence`, lang `en`, anchor 2026-11-22 09:00): `every monday to friday 9 am` gives the rule `FREQ=WEEKLY;BYDAY=MO;BYHOUR=9` and `to friday` left over. [#1321](https://github.com/TigreGotico/chronologia/issues/1321)

- A part of the day before the clock is lost in a daily rule. Example (reader `extract_recurrence`, lang `en`, anchor 2026-11-22 09:00): `every evening at 8` gives no rule. [#1324](https://github.com/TigreGotico/chronologia/issues/1324)

**Events, zones, business days and the API**

- The candidate list and the single-span reader disagree on one phrase. [#995](https://github.com/TigreGotico/chronologia/issues/995)

- The event summary keeps the article and the day word before a day number. Example (reader `extract_event`, lang `en`, anchor 2025-06-18 10:30): `meeting on the day 5 of december` gives start 2025-12-05 00:00, length none, summary `meeting on the day`. [#1218](https://github.com/TigreGotico/chronologia/issues/1218)

- A span that names a zone gives a wrong instant under an aware anchor. [#1253](https://github.com/TigreGotico/chronologia/issues/1253)

- A bare clock with a zone skips the 12-hour rule. Example (reader `extract_timespan`, lang `en`, anchor 2017-06-27 13:04): `9:30 utc` gives 2017-06-28 09:30 to 2017-06-28 09:31. [#1254](https://github.com/TigreGotico/chronologia/issues/1254)

- Jurisdiction holidays raise at the bounds, skip the clock and skip the anchor day. Example (reader `extract_event`, lang `en`, anchor 2026-12-25 10:00): `every holiday in Portugal` gives start 2027-01-01 00:00, length none, no summary. [#1255](https://github.com/TigreGotico/chronologia/issues/1255)

- The candidate reader does not raise in raise mode, where the event reader does. Example (reader `extract_timespan`, lang `en`, anchor 2026-11-22 09:00): `the sixth monday of may 2027` gives no reading. [#1276](https://github.com/TigreGotico/chronologia/issues/1276)

- The last business day of every month reads as a plain monthly rule. Example (reader `extract_recurrence`, lang `en`, anchor 2026-11-22 09:00): `the last business day of every month` gives the rule `FREQ=MONTHLY` and `the last business day of` left over. [#1289](https://github.com/TigreGotico/chronologia/issues/1289)

- The event summary turns a spelled numeral into a digit. Example (reader `extract_event`, lang `en`, anchor 2026-11-22 09:00): `a second meeting tomorrow` gives start 2026-11-23 00:00, length none, summary `2 meeting`. [#1297](https://github.com/TigreGotico/chronologia/issues/1297)

- A count of business days at the start or end of a month reads no span. Example (reader `extract_timespan`, lang `en`, anchor 2026-11-22 09:00): `the last 3 business days of the month` gives no reading. [#1303](https://github.com/TigreGotico/chronologia/issues/1303)

- A cardinal before a singular business-day noun reads nothing. Example (reader `extract_timespan`, lang `en`, anchor 2026-11-22 09:00): `pay rent on the 3 business day of the month` gives no reading. [#1304](https://github.com/TigreGotico/chronologia/issues/1304)

- A working-day or day-of-month recurrence reads as every day. Example (reader `extract_recurrence`, lang `en-US`, anchor 2026-11-22 09:00): `every working day at 9` gives no rule. [#1310](https://github.com/TigreGotico/chronologia/issues/1310)

- An impossible day read apart from its month is dropped, and the rest still reads. Example (reader `extract_timespan`, lang `en`, anchor 2026-11-22 09:00): `in february on the 30th` gives 2027-02-01 00:00 to 2027-03-01 00:00 and `on the 30th` left over. [#1328](https://github.com/TigreGotico/chronologia/issues/1328)

- The candidate list and the single-span reader read a clock with a length differently. [#1350](https://github.com/TigreGotico/chronologia/issues/1350)

---
[← Dutch](nl.md) · [Home](../index.md) · [Esperanto →](eo.md)
