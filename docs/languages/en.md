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

**Non-Gregorian calendars, eras and deep time** all ship: Hebrew and Islamic civil months, French Republican months, Japanese nengō era names, Egyptian and other regnal series and Attic archon years. The Roman Kalends-Nones-Ides counting system ships too, with the geological period vocabulary from the Archean to the Holocene. The Anno Mundi, Julian, Unix, Holocene and before-present eras.

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

Each limit below has an open issue and a strict `xfail` test that fails when the limit is fixed.

- [#990](https://github.com/TigreGotico/chronologia/issues/990): A common word reads as a time word: en "fall", da "går" and "morgen", oc "ora", pl "lata"

- [#995](https://github.com/TigreGotico/chronologia/issues/995): extract_timespans disagrees with extract_timespan: a lost char_span, "jul", and a clock

- [#997](https://github.com/TigreGotico/chronologia/issues/997): A part of the day with no day word answers the band that has passed

- [#1001](https://github.com/TigreGotico/chronologia/issues/1001): Lone spoken hour: a part of the day in another clause keeps the hour as spoken

- [#1002](https://github.com/TigreGotico/chronologia/issues/1002): en "at 8 tonight" gives 08:00 tomorrow, not 20:00 tonight

- [#1004](https://github.com/TigreGotico/chronologia/issues/1004): A unit word with no number counts as one: "how many days before christmas" gives 24 December

- [#1008](https://github.com/TigreGotico/chronologia/issues/1008): A clock after for, to, per or para is not read, and a reschedule phrase reads the old time

- [#1013](https://github.com/TigreGotico/chronologia/issues/1013): en: an infinitive "to" before "tomorrow morning" opens a range

- [#1034](https://github.com/TigreGotico/chronologia/issues/1034): A date built from two parts loses one: an offset with a clock, a count from a day word, the nth weekday of a relative period

- [#1035](https://github.com/TigreGotico/chronologia/issues/1035): Text that is no date reads as a date, or the wrong reading wins: arithmetic, version numbers, "a third of", a holiday name used as a modifier

- [#1040](https://github.com/TigreGotico/chronologia/issues/1040): A range of amounts before a range of years gives a year from the first range

- [#1041](https://github.com/TigreGotico/chronologia/issues/1041): A spelled range of units before "ago" gives one point and leaves the first number over

- [#1042](https://github.com/TigreGotico/chronologia/issues/1042): A spelled year before a full stop gives no year when a word starts the next sentence

- [#1049](https://github.com/TigreGotico/chronologia/issues/1049): en: "mornings and evenings at 8" reads the morning band and leaves the hour behind

- [#1051](https://github.com/TigreGotico/chronologia/issues/1051): en: "good evenings, set an alarm at 7" must keep its hour when "evenings" is a part of the day

- [#1052](https://github.com/TigreGotico/chronologia/issues/1052): en, pt: a plural part of the day before a clock ("mornings at 8", "nas manhãs às 8") gives no recurrence

- [#1054](https://github.com/TigreGotico/chronologia/issues/1054): A spelled year range with "the year(s)" and a word after it gives only the first year ("between the years two thousand and two thousand and ten in Europe")

- [#1058](https://github.com/TigreGotico/chronologia/issues/1058): Minutes after an alarm hour are dropped: seven oh five, 7 and 30, pt and es 7 30

- [#1079](https://github.com/TigreGotico/chronologia/issues/1079): nl "om 11:00 's nachts" gives 11:00 while "om 11 's nachts" gives 23:00, de "elf Uhr nachts" needs a ruling

- [#1087](https://github.com/TigreGotico/chronologia/issues/1087): A count of hours or minutes before a holiday gives the day before at 00:00 ("an hour before christmas", "um quarto de hora antes do natal")

- [#1097](https://github.com/TigreGotico/chronologia/issues/1097): "before christmas" ends after Christmas Day, not when it starts (fr "avant noël", sv "före jul")

- [#1098](https://github.com/TigreGotico/chronologia/issues/1098): A bare "after X" gives no reading since 0.33.5a1, where ruling 33 says it is an open span

- [#1196](https://github.com/TigreGotico/chronologia/issues/1196): A clock with an offset from a holiday: the readings are missing or in the wrong order ("às 9 uma hora antes do natal" gives 09:00)

- [#1197](https://github.com/TigreGotico/chronologia/issues/1197): A vague count before a holiday gives the whole day before ("a few hours before christmas" gives 24 December 00:00 to 25 December)

- [#1218](https://github.com/TigreGotico/chronologia/issues/1218): Event summary keeps the article and day word before a day number in en, fr, de and nl

- [#1240](https://github.com/TigreGotico/chronologia/issues/1240): sv, en: the unit word after "and a quarter" or "and a half" stays in the remainder

- [#1253](https://github.com/TigreGotico/chronologia/issues/1253): extract_timespan with an aware anchor gives a wrong instant for a span that names a zone

- [#1254](https://github.com/TigreGotico/chronologia/issues/1254): A bare clock with a zone skips the 12-hour rule ("9:30 utc" reads tomorrow 09:30)

- [#1255](https://github.com/TigreGotico/chronologia/issues/1255): Jurisdiction holidays: bounds raise, a clock is not applied, the anchor day is skipped

- [#1276](https://github.com/TigreGotico/chronologia/issues/1276): extract_candidates does not raise in raise mode where extract_event does

- [#1288](https://github.com/TigreGotico/chronologia/issues/1288): "the sixth monday of every month" reads next Monday in extract_timespan and extract_candidates

- [#1289](https://github.com/TigreGotico/chronologia/issues/1289): "the last business day of every month" reads as FREQ=MONTHLY with the ordinal left over

- [#1290](https://github.com/TigreGotico/chronologia/issues/1290): "the 3rd weekday of march" reads all of March in extract_timespan

- [#1291](https://github.com/TigreGotico/chronologia/issues/1291): de: "jeden Montag von Juni bis August" reads "bis August" as UNTIL and leaves "von Juni"

- [#1296](https://github.com/TigreGotico/chronologia/issues/1296): en: "alarm at 7, 8 and 9 tonight" reads the list "7, 8" as the clock 7:08

- [#1297](https://github.com/TigreGotico/chronologia/issues/1297): Event summaries turn a spelled numeral into a digit ("a second meeting" gives "2 meeting")

- [#1301](https://github.com/TigreGotico/chronologia/issues/1301): en: "at a quarter past ten on the 14th of march" leaves "at a" in the remainder

- [#1303](https://github.com/TigreGotico/chronologia/issues/1303): "the first 5 business days of the month" reads no span

- [#1304](https://github.com/TigreGotico/chronologia/issues/1304): A cardinal before a singular business-day noun ("the 3 business day of the month") reads nothing

- [#1309](https://github.com/TigreGotico/chronologia/issues/1309): A range whose end is a movable feast, a weekday date or a clocked date reads a year long

- [#1310](https://github.com/TigreGotico/chronologia/issues/1310): Working-day and day-of-month recurrence heads read as every day: "cada dia útil", "día laborable", "cada dia 15"

- [#1311](https://github.com/TigreGotico/chronologia/issues/1311): A list of two days reads as a clock or the wrong day: es "el 14 y 15 de mayo" gives 1 May 14:15

- [#1312](https://github.com/TigreGotico/chronologia/issues/1312): Meridiem after an abbreviated hour word is lost: "um 8 Std. abends", "at 8 hr. pm", pt "às 5 pm" read as morning

- [#1315](https://github.com/TigreGotico/chronologia/issues/1315): A clock range in a recurrence reads the end hour or a wrong minute: pt "das 9 às 17" gives 17:00, en "9 to 5" gives 04:51

- [#1316](https://github.com/TigreGotico/chronologia/issues/1316): An until bound in a recurrence resolves on the anchor day: "every monday at 9 until 5 pm" never occurs, de "bis Ende Juni" ends before the anchor

- [#1320](https://github.com/TigreGotico/chronologia/issues/1320): A date or ordinal weekday next to a frequency word is dropped: "the 15th of february every year" gives FREQ=YEARLY, "every month on the first friday" gives BYMONTHDAY=1

- [#1321](https://github.com/TigreGotico/chronologia/issues/1321): Weekday and clock ranges in a recurrence: nl "tot en met vrijdag" differs from "t/m", "to friday 9 am" loses the range, "until 5/12" loses the date

- [#1324](https://github.com/TigreGotico/chronologia/issues/1324): A part of the day before the clock is lost in a daily rule: en "evening at 8 every day" fires at 08:00

- [#1325](https://github.com/TigreGotico/chronologia/issues/1325): A day number or an offset before a part of the day and a clock loses the day: "the 23rd in the evening at 8", "in 2 days evening at 8"

- [#1326](https://github.com/TigreGotico/chronologia/issues/1326): extract_duration reads the "day" of a day word as a length: "at 9 the day before last" gives 9 days

- [#1328](https://github.com/TigreGotico/chronologia/issues/1328): An impossible day read apart from its month is dropped and the rest still reads: "in february on the 30th", "annually on the 32nd of january"

- [#1330](https://github.com/TigreGotico/chronologia/issues/1330): A year-less range that ends on 29 February spans into the next leap year: "from 1 february to 29 february" gives 2027-02-01 .. 2028-03-01

- [#1331](https://github.com/TigreGotico/chronologia/issues/1331): A leading-zero number before "minutes" reads as a military clock: "0030 minutes" gives 00:30 and no length

- [#1333](https://github.com/TigreGotico/chronologia/issues/1333): en: "last night at 11" reads 23:00 tonight, and "at 11 last night" reads 11:00 today

- [#1350](https://github.com/TigreGotico/chronologia/issues/1350): Candidate list and extract_timespan read a clock with a length differently: de "um 9 Uhr für 2 Stunden"

- [#1351](https://github.com/TigreGotico/chronologia/issues/1351): A range with a shared month or unit drops the unrelated words from the remainder: en "please 5-12 June"

- [#1352](https://github.com/TigreGotico/chronologia/issues/1352): A range reading crosses a full stop: de "am Montag. Der Bericht ist bis Freitag"

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
