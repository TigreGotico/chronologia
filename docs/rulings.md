# Rulings

<!-- agent-hint
covers: the decisions that fix how a phrase with two readings is read, with examples and sources
source: chronologia/extract/resolver.py, test/ruling17.py, test/ruling17_pins.txt, test/ruling23_pins.txt, test/ruling1_pins.txt
generated: no
verify: .venv/bin/python -c 'exec("import re,sys\nfrom datetime import datetime as D\nfrom chronologia import extract_timespan as e\nT=re.split(r\"-{2}>\",open(\"docs/rulings.md\").read(),maxsplit=1)[1]\nSEC={}\nfor s in re.split(r\"(?m)^(?=## |\\*\\*\\d+[a-z]?\\. )\",T):\n    m=re.match(r\"(?:## |\\*\\*)(\\w+)\\. \",s)\n    if m: SEC[m[1]]=re.sub(r\"\\s+\",\" \",s)\nMON=\"January February March April May June July August September October November December\".split()\ndef F(d,f): return d.strftime(f.replace(\"%e\",str(d.day)).replace(\"%@\",MON[d.month-1]))\na=D(2017,6,27,13,4);n26=D(2026,11,26,10,0);fri=D(2017,6,30,13,4);p15=D(2017,6,27,15,0);p3=D(2017,6,27,3,0)\nDEF=r\"{p}.{{0,140}}?\\b(?:is|are|answers|reads?|starts on)\\s+{x}\"\nS=[(\"A\",\"en\",\"in two hours\",a,\"%H:%M\",r\"{p}\\\" said at 13:04 is {x}\"),(\"A\",\"an\",\"en 3 días\",a,\"%Y-%m-%d %H:%M\",r\"{p}\\x60.{{0,60}}?said at 13:04 on 2017-06-27 is\\s+{x}\"),(\"B\",\"an\",\"la semana vinient\",a,\"Monday %Y-%m-%d\",r\"{p}\\x60.{{0,80}}?said\\s+on Tuesday 2017-06-27 starts on {x}\"),\n(\"C\",\"ar\",\"الساعة السابعة صباحاً\",a,\"%Y-%m-%d\",r\"{p}\\x60.{{0,60}}?said at 13:04 on 2017-06-27 is {x}\"),(\"C\",\"ar\",\"5 يناير\",a,\"%Y-%m-%d\",DEF),\n(\"D\",\"ro\",\"nouă și zece\",a,\"%I:%M\",DEF),(\"D\",\"ro\",\"nouă fără zece\",a,\"%I:%M\",DEF),(\"D\",\"en\",\"10 past 4\",a,\"%I:%M\",DEF),(\"D\",\"nl\",\"morgen om 10 uur\",a,\"%H:%M\",DEF),(\"D\",\"id\",\"Rapat pukul tiga sore\",a,\"%H:%M\",DEF),\n(\"1\",\"fr\",\"janvier\",D(2017,6,15),\"%@ %Y\",r\"{p}\\\" said in June 2017 is {x}\"),(\"1\",\"fr\",\"juin\",D(2017,6,15),\"%@ %Y\",r\"{p}\\\" said in June 2017 is {x}\"),(\"1\",\"fr\",\"début janvier\",n26,\"%@ %Y\",r\"{p}\\\" said on 26 November 2026 is early {x}\"),(\"1\",\"fr\",\"fin décembre\",n26,\"%@ %Y\",r\"{p}\\\" said on 26 November 2026 is late {x}\"),(\"1\",\"fr\",\"début novembre\",n26,\"%@ %Y\",r\"{p}\\\" said on 26 November 2026 is early {x}\"),(\"1\",\"fr\",\"fin janvier dernier je suis parti\",n26,\"%@ %Y\",r\"{p}\\\" said on 26 November 2026 is late {x}\"),(\"1\",\"fr\",\"fin novembre\",n26,\"%@ %Y\",r\"{p}\\\" said on 26 November 2026 is late {x}\"),(\"1\",\"fr\",\"fin janvier dernier délai\",D(2027,1,15,10,0),\"%@ %Y\",r\"{p}\\\" \\(final deadline\\) said on 15 January 2027 is late {x}\"),(\"1\",\"en\",\"since monday 3 march\",n26,\"%e %@ %Y\",r\"{p}\\\" said on 26 November 2026 starts on {x}\"),(\"1\",\"en\",\"the fourth thursday of november\",n26,\"%e %@ %Y\",r\"{p}\\\" said on Thursday 26 November 2026 is {x}\"),(\"1\",\"fr\",\"début janvier 2026\",n26,\"%@ %Y\",r\"{p}\\\" is early {x}\"),(\"1\",\"fr\",\"fin janvier dernier\",n26,\"%@ %Y\",r\"{p}\\\" said on 26 November 2026 is late {x}\"),(\"1\",\"en\",\"since early october\",n26,\"%e %@ %Y\",r\"{p}\\\" said on 26 November 2026 starts on {x}\"),(\"1\",\"en\",\"the first day of november\",n26,\"%e %@ %Y\",r\"{p}\\\" said on 26 November 2026 is {x}\"),(\"1\",\"en\",\"the first monday of november\",n26,\"%e %@ %Y\",r\"{p}\\\" said on 26 November 2026 is {x}\"),\n(\"2\",\"ast\",\"20h\",a,\"%H:%M\",r\"\\\"{p}\\\" and \\\"21h30\\\" alone read {x}\"),(\"2\",\"ast\",\"21h30\",a,\"%H:%M\",r\"\\\"20h\\\" and \\\"{p}\\\" alone read \\d\\d:\\d\\d and {x}\"),\n(\"8\",\"ru\",\"11 часов ночи\",a,\"%H:%M\",DEF),(\"8\",\"ru\",\"3 часа ночи\",a,\"%H:%M\",DEF),(\"9\",\"ru\",\"в половине третьего дня\",a,\"%H:%M\",DEF),\n(\"10\",\"ru\",\"3 часа ночи\",a,\"%H:%M\",DEF),\n\n(\"13\",\"pt\",\"o dia 30 do mês\",D(2017,1,31,13,4),\"%e March\",r\"{p}\\\" said on 31 January is {x}\"),(\"13\",\"pt\",\"o dia 5 deste mês\",D(2017,10,17,13,4),\"%e October\",r\"{p}\\\" said on 17 October is {x}\"),\n(\"16\",\"en\",\"this tuesday at 10am\",a,\"that Tuesday at %H:%M\",r\"{p}\\\" said on a Tuesday at 13:04 is {x}\"),\n(\"16a\",\"en\",\"a week before friday\",fri,\"%e June\",r\"{p}\\\" said on Friday 30 June 2017 is {x}\"),(\"16a\",\"en\",\"the day before friday\",fri,\"%e June\",r\"{p}\\\" is {x}\"),(\"16a\",\"en\",\"two days from friday\",fri,\"%e July\",r\"{p}\\\" said on that Friday is {x}\"),\n(\"17\",\"en\",\"at 8\",p15,\"%H:%M\",r\"{p}\\\" said at 15:00 is {x}\"),(\"17\",\"pt\",\"às 10 e meia\",a,\"%H:%M\",r\"{p}\\\" said at 13:04 is {x}\"),(\"17\",\"en\",\"tomorrow at 8\",a,\"%H:%M\",DEF),(\"17\",\"pt\",\"às 10 da manhã\",a,\"%H:%M\",DEF),(\"17\",\"fr\",\"à 8h\",p15,\"%H:%M\",r\"{p}\\\" said at 15:00 is {x}\"),\n(\"20\",\"pl\",\"21:30 wieczorem\",a,\"%H:%M\",DEF),(\"20\",\"en\",\"22:30 evening\",a,\"%H:%M\",DEF),(\"20\",\"ko\",\"오후 19:30\",a,\"%H:%M\",DEF),\n(\"23\",\"en\",\"wake me up at 6:30\",a,\"%H:%M\",r\"{p}\\\" said at 13:04 is {x}\"),(\"23\",\"pt\",\"lembra-me às 3:30\",p15,\"%H:%M\",r\"{p}\\\" said at 15:00 is {x}\"),(\"23\",\"en\",\"at 3:30 today\",p15,\"%H:%M\",r\"{p}\\\" said at 15:00 is {x}\"),(\"23\",\"en\",\"tomorrow at 6:30\",a,\"%H:%M\",DEF),\n(\"26\",\"en\",\"remind me today at five\",p15,\"%H:%M\",r\"{p}\\\" said at 15:00 is {x}\"),(\"26\",\"en\",\"today at 5\",p3,\"%H:%M\",r\"said at 03:00 is {x}\"),\n(\"32\",\"en\",\"at 12:30 am\",D(2017,6,27,0,0,30),\"%H:%M\",r\"{p}\\\" said at 00:00:30 is {x}\")]\nR=[(\"20\",\"pt\",\"00:30 da tarde\"),(\"20\",\"pt\",\"15:00 da manhã\"),(\"20\",\"pt\",\"22h da tarde\")]\nSKIP={(\"37\",\"в восьмом часу\"),(\"37\",\"в восьмом часу вечера\"),(\"37\",\"в двенадцатом часу ночи\"),(\"11\",\"The new year\"),(\"10\",\"tonight\"),(\"10a\",\"tonight\"),(\"10a\",\"dnes večer\"),(\"10b\",\"noću\")}\nbad=0;known={(k,p) for k,l,p,*_ in S}|SKIP\nfor k,sec in SEC.items():\n    if \"Not implemented\" in sec: continue\n    for m in re.finditer(r\"(?:\\\"([^\\\"]+)\\\"|\\x60([^\\x60]+)\\x60)[^.\\\"\\x60]{0,70}?\\b(?:is|are|answers|reads?|starts on)\\s+(?:\\d\\d:\\d\\d|\\d{4}-\\d\\d-\\d\\d|\\d{1,2} [A-Z][a-z]+|Monday \\d{4})\",sec):\n        if (k,m[1] or m[2]) not in known: bad=1;print(\"unchecked claim\",k,m[1] or m[2])\nfor k,lg,ph,an,fm,tp in S:\n    r=e(ph,lg,an); x=F(r[0].start_datetime,fm) if r else None\n    if not(x and k in SEC and re.search(tp.format(p=re.escape(ph),x=re.escape(x)),SEC[k])): bad=1;print(\"FAIL\",k,ph,x)\nfor ph,an,s,u,x in [(\"в восьмом часу вечера\",a,19,20,chr(34)+\"в восьмом часу вечера\"+chr(34)+\" is 19:00 to 20:00\"),(\"в восьмом часу\",D(2017,6,27,7,30),19,20,\"said at 07:30, \"+chr(34)+\"в восьмом часу\"+chr(34)+\" is 19:00 to 20:00\"),(\"в двенадцатом часу ночи\",a,23,24,chr(34)+\"в двенадцатом часу ночи\"+chr(34)+\" is 23:00 to 24:00\")]:\n    r=e(ph,\"ru\",an)\n    if not(r and r[0].start_datetime.hour==s and r[0].end_datetime.hour==u%24 and x in SEC[\"37\"]): bad=1;print(\"FAIL 37\",ph)\nfor k,lg,ph in R:\n    if e(ph,lg,a) is not None or ph not in SEC[k]: bad=1;print(\"FAIL refusal\",k,ph)\nif e(\"this tuesday at 10am\",\"en\",a)[0].start_datetime.date()!=a.date(): bad=1;print(\"FAIL date\")\nprint(\"skipped (not checkable):\",sorted(SKIP),\"| rulings marked not implemented:\",sorted(k for k,s in SEC.items() if \"Not implemented\" in s))\nsys.exit(bad)\n")'
see: docs/extraction.md, docs/languages/index.md
-->

These are the decisions that fix how chronologia reads a phrase where two readings are possible. Each ruling gives the reading, an example and, where a dictionary or standard rules on it, the source. A ruling marked "Not implemented" states the reading the engine is to return. The engine does not return that reading. A change to a ruling changes this page.

Rulings A to C are the readings that differ from ovos-date-parser, the reader that chronologia replaces. Ruling D lists settled spelled-clock and day-word readings. The numbered rulings that follow apply to every locale unless a ruling names the locales it covers.

## A. A counted offset carries the clock of the anchor

A counted offset is arithmetic on the anchor. So "in two hours" said at 13:04 is 15:04. And `en 3 días` (Aragonese, in three days) said at 13:04 on 2017-06-27 is 2017-06-30 13:04, not 2017-06-30 00:00. Rounding to the hour is a defect, not a convention. Counted periods follow the same rule.

A counted week, month or year is the anchor plus the count. "In 2 weeks" is the anchor plus 14 days. "3 months ago" is minus 3 calendar months.

## B. A named period is the calendar unit

"Next week" is the calendar week after the anchor's week, starting on the first weekday of the locale. In the same way, "last month" is the previous calendar month. A rolling seven days is not a named period: `la semana vinient` (next week) said on Tuesday 2017-06-27 starts on Monday 2017-07-03, not on 2017-07-04. The engine option `relative_period_mode` takes `calendar` by default and `rolling` for a deployment that wants the rolling reading. The week starts on Monday in 56 locales, on Saturday in ar, sw and fa, and on Sunday in he.

## C. `prefer_future` means the next occurrence

The next occurrence is the first one strictly after the anchor. An instant equal to the anchor is the anchor. `الساعة السابعة صباحاً` (seven in the morning) said at 13:04 on 2017-06-27 is 2017-06-28, and `5 يناير` is 2018-01-05. The weekday "this monday" said on a Tuesday is the coming Monday, never the one that has passed.

## D. Readings settled for spelled clocks and day words

- A spelled clock is read forward from the hour in ro and it: `nouă și zece` (ten past nine) is 09:10. And `nouă fără zece` (ten to nine) is 08:50. A phrase with no marker still reads in that order.
- A spelled clock in es, pt, gl and el reads the same way.
- Arabic `أمس الأول` is the day before yesterday.
- en "10 past 4" is 04:10. nl "morgen om 10 uur" is 10:00. id `Rapat pukul tiga sore` is 15:00. ca `d'aquí a 15 minuts` is 15 minutes from the anchor, not the clock 15:00.

## Numbered rulings

**1. A month named without a day**. A month whose span contains the anchor is this month. A month that ended before the anchor is the month of next year. This is ruling C applied to a span: "janvier" said in June 2017 is January 2018, and "juin" said in June 2017 is June 2017.

A part of a month is a span too, and ruling C reads it the same way. "early january", "the first week of january", "the first monday of january", "the first half of january" and "the last day of january" are parts of a month. A part that holds the anchor or is still ahead is this year's, and a part that has ended is next year's. In a month other than the anchor's, that is the year of the month. So "début janvier" said on 26 November 2026 is early January 2027, as "janvier" and "le 1er janvier" said that day name January 2027. "fin décembre" said on 26 November 2026 is late December 2026.

In the anchor's own month the part decides. "fin novembre" said on 26 November 2026 is late November 2026, because late November holds the anchor. "début novembre" said on 26 November 2026 is early November 2027, because early November 2026 has ended. "the first monday of november" said on 26 November 2026 is 1 November 2027, as "the first day of november" and "le 2 novembre" said that day are next year's.

A year wins: "début janvier 2026" is early January 2026. A year phrase after the month names the month's year as it does for the month alone, and the part takes that year: "fin janvier dernier" said on 26 November 2026 is late January 2026, the January of "janvier dernier". The phrase stops at a comma. A lone marker word ("dernier", "pasado") is also an adjective, so it names the year only at the end of its clause, before a subject or object pronoun that opens the next clause, or before a preposition or a conjunction. Each locale lists its pronouns, from a grammar, in `marker_year_marker_follow.voc`: "fin janvier dernier je suis parti" said on 26 November 2026 is late January 2026. Before any other word, an article or a noun, the marker is left over: "fin janvier dernier délai" (final deadline) said on 15 January 2027 is late January 2027, with "dernier délai" left over. A pronoun that is also an article (fr "le", "la", "les"; es "la"; pt "o", "a"; it "lo", "la") closes the phrase before a noun too. Where the month alone takes no year phrase, its part takes none either, and the phrase is left over: fi "tammikuussa viime vuonna", hu "tavaly januárban", tr "geçen yıl ocak" and it "gennaio dell'anno scorso".

After "since", a part of a month is the one that has begun, as "since january" is: "since early october" said on 26 November 2026 starts on 1 October 2026. A weekday said beside a day of a month names that day on that weekday: "since monday 3 march" said on 26 November 2026 starts on 3 March 2025, the latest 3 March that is a Monday.

This changed on 26 November 2026. A part of a month kept the anchor's year before (ruling 1 as #1066 and #1285 wrote it), so "début janvier" said in November named the January that had passed, while "janvier" and "le 1er janvier" named the next one. A part is now read as a span, as the month and the numbered day are, so that the words never name a span that has ended while "janvier", "le 1er janvier" or "the first day of november" name a later one. `test/ruling1_pins.txt` lists the tests whose expected value this change moved.

A day named by its number is not a part of a month. A year-less "the fifteenth day of march" names the date "15 march" names. So it is the next 15 March, as ruling C reads a day of a month. A day equal to the anchor's day is that day: "the fourth thursday of november" said on Thursday 26 November 2026 is 26 November 2026. "the first day of november" said on 26 November 2026 is 1 November 2027, the next 1 November.

The end of a range may name a day and a month with no year, weekday or clock. Suppose the anchor reads that end later than its first occurrence on or after the start of the range. Then the end is that first occurrence: "from the first week of november to 3 november" said on 5 November 2026 ends with 3 November 2026.

When a start with no year rolls past its end, the range reads from the previous occurrence of the start, if that range holds the anchor and its end does not fall earlier in the month of its start: "from the 1st day of december to 10 january" said on 20 December 2026 runs from 1 December 2026 to 10 January 2027. "from the 1st day of september to 30 june" said on 22 November 2026 runs from 1 September 2026 to 30 June 2027.

A range whose end names the same month as its start, on an earlier day, is not read that way: "from 2 june to 1 june" and "from 12 june to 5 june" said after their start day name no range. A range from a later month into an earlier one is read that way. So "from 1 june to 31 may" said on 1 December 2026 runs from 1 June 2026 to 31 May 2027. The months are compared by name, not by year.

**2. A bare hour or an hour-letter clock**. "20h", "21h30" and "3 heures" read as a clock when they are the whole utterance, as the ruling for a bare hour alone says. Inside a sentence with no clock marker, they refuse. So fr "un film de 2 heures", "2h de route", "il reste 3 heures" and "3 heures de travail" refuse. ast "20h" and "21h30" alone read 20:00 and 21:30. This agrees with chronologia #882.

**3. A bare duration is not a date.** `extract_datetime("pendant 3 heures")` returns None, as "trois jours" already does. A counted offset with a direction word ("dans 3 heures", "daqui a 3 horas") still answers.

**4. pt "antes de ontem" is anteontem**. Priberam lists it as a synonym.

**5. A habitual phrase reads as the next occurrence.** pt "ao sábado", gl "os luns" and fr "le mardi" alone answer the next such day. The function `extract_datetime` has no recurrence type. And a skill wants a date.

**6. A weekday said on that same weekday is today**. "o venres" said on a Friday answers that Friday. A day is a span. Ruling 1 already makes a span that contains the anchor the current one ("juin" said in June is this June). Ruling C agrees: an instant equal to the anchor is the anchor. A phrase that names the next one ("next Friday", "o próximo venres") still moves forward a week.

**7. ru and uk "<ordinal> числа" is a date**. "двадцатого числа" and "двадцятого числа" name the day of the month, because "числа" names it. The bare genitive ordinal ("двадцатого", "двадцятого") and the digit form "20-го" stay unread, because the left-out noun can be any noun. A cardinal before "числа" is a count: "три числа" is "three numbers".

**8. ru "ночи" is a night band that crosses midnight**. "11 часов ночи" is 23:00 and "3 часа ночи" is 03:00, as sl "ponoči" and es "de la noche" read.

**9. ru "в половине третьего" follows the bare-clock rule**. It reads as "половина третьего" reads. A day period fixes the half of the day: "в половине третьего дня" is 14:30.

**10. "Tonight" is the night of the anchor's own day**. Wiktionary "tonight": "During the night following the current day. During the evening of today." CLDR day periods for en start night1 at 21:00 and morning1 at 00:00. So the en night ends at midnight.

A night band that crosses midnight is cut at midnight before its middle hour is taken. With a 21:00 to 06:00 band, "tonight" said at 13:04 answers 22:30 on the anchor day. It does not answer 01:30 the next day. An hour said inside the band keeps its own reading (ruling 8: "3 часа ночи" is 03:00).

**10a. A part of the day that holds the anchor answers the anchor once its middle has passed**. A part of the day named with no day of its own ("tonight", "noću", "dnes večer", "ráno") answers the middle of its band. When the anchor lies inside the band and the middle has passed, the answer is the anchor itself. For a night band, inside the band means inside the kept part between its start and midnight. Before the middle, the middle still answers.

Ruling C decides both: a reading is never before the anchor, and an instant equal to the anchor is the anchor. Said at 23:30 with a 21:00 to 06:00 band, "tonight" answers 23:30. Said at 21:30 it answers 22:30. And cs "dnes večer" said at 21:00, inside the 18:00 to 22:00 evening band, answers 21:00, not 20:00.

**10b. Ruling 10 holds in every locale**. The cut at midnight follows from what "tonight" names (the night of the anchor's own day), not from the en clock. CLDR gives other locales a night that crosses midnight (hr night1 21:00 to 04:00, cs and sk 22:00 to 04:00). A night named with no day of its own is the night of the anchor's day there too. So hr "noću" said at 13:04 answers 22:30 (21:00 plus half of the three hours to midnight). For cs or sk it answers 23:00.

**11. "The new year" is 1 January of the next year**. Wiktionary "New Year": "In particular, January 1 in the Julian and Gregorian calendar (New Year's Day) and the days following." So "how many days until the new year" counts to the next 1 January. The library must not refuse it (TigreGotico/chronologia#933).

**12. "This <weekday>" is the next occurrence**. "esta segunda" said on a Saturday is the coming Monday, as ruling C reads. Said on a Monday it is that Monday (ruling 6). A week-start reading of "this <weekday>" states a design choice and cites no linguistic source, so it is not used.

No pt source rules on "esta <weekday>" for a day already past: Svobodová (2016, Romanistica Pragensia) covers "próxima" and "passada" only, and no Ciberdúvidas answer was found. A command to an assistant names a future time, so the next occurrence is the safer reading.

**13. "Of the month" with no marker rolls. "Of this month" does not**. An nth day, weekday or week "of the month" ("o dia 5 do mês", "a primeira terça-feira do mês") that ended before the anchor is the next month's. Ruling C and ruling 1 read a span that has passed in the same way.

A month that lacks the day is skipped: "o dia 30 do mês" said on 31 January is 30 March.

"Of this month" names the anchor's own month and never rolls. "deste mês" is "Contracção da preposição de com o pronome este" (Priberam s.v. "deste"), and "este" is "Designativo de pessoa ou coisa que está presente, ou mais próxima de quem fala" (Priberam s.v. "este"). So "o dia 5 deste mês" said on 17 October is 5 October.

**14. The first week of a year is ISO 8601 week 01**. "The ISO 8601 definition for calendar week 01 is the week with the first Thursday of the Gregorian year". Equivalently, "It has 4 January in it" (Wikipedia, "ISO week date"). So "a primeira semana de 2026" is Monday 29 December 2025 to Sunday 4 January 2026.

The last week of a year is the one that contains 28 December. ISO defines no weeks of a month. So a week of a month keeps the existing reading: it starts on the first Monday on or after the 1st.

**15. A weekday beside a day word names that day, or no day**. In "amanhã, domingo" the weekday is an apposition: an "aposto" is a "Nome ou locução nominal que se junta a outro nome para melhor o caracterizar" (Priberam s.v. "aposto", 5). When the two agree, the weekday belongs to the date. When they disagree ("amanhã segunda-feira" said on a Saturday), the phrase names no single day, and the reading is refused rather than guessed.

**15a. The apposed weekday follows the day word**. Ruling 15 reads a weekday only after the day word ("amanhã, domingo").

A weekday before a day word is not folded: in de, nl, da and nb, "morgen" after a weekday names the morning ("Dienstagmorgen": "Morgen des Dienstags", Duden s.v. "Dienstagmorgen"), and es, ast and gl "martes mañana" has the same reading. A sentence boundary between the two words also stops the fold: "vou amanhã. segunda-feira trabalho" names tomorrow.

**16. "This <weekday>" fixes the day. A passed clock does not move it**. "this tuesday at 10am" said on a Tuesday at 13:04 is that Tuesday at 10:00 (rulings 6 and 12: "este" is "Designativo de pessoa ou coisa que está presente, ou mais próxima de quem fala", Priberam s.v. "este").

A bare weekday with a clock that has passed is the next one. An example is "tuesday at 10am" said on a Tuesday at 13:04. Ruling C reads an instant before the anchor in the same way. The tense of the sentence is outside the parser.

**16a. A count before or after a weekday counts from the day ruling 6 names**. "a week before friday" said on Friday 30 June 2017 is 23 June. "the day before friday" is 29 June.

The weekday is that same Friday (ruling 6). The count moves from it even when the answer is in the past. "two days from friday" said on that Friday is 2 July, by the same rule.

**17. A lone spoken hour takes the next twelve-hour reading**. An hour 1 to 12 said with no am/pm word and no part of the day takes whichever of its two readings comes next after the anchor. "at 8" said at 15:00 is 20:00. And pt "às 10 e meia" said at 13:04 is 22:30. A named day or part of the day keeps the spoken hour ("tomorrow at 8" is 08:00, "às 10 da manhã" is 10:00).

A digit clock follows ruling 23, and 24-hour hours (13 to 23) are as written. A letter-h clock ("8h", "20h", "6h30") reads as written, because the letter h marks the written 24-hour form. So fr "à 8h" said at 15:00 is 08:00 the next day. Ruling 2 still decides when a bare hour is a clock at all.

**18. pt "quinze dias" is fifteen days**. Priberam s.v. "quinzena", 1: "Período de quinze dias seguidos." No dictionary sense gives "quinze dias" the reading of two weeks, so "daqui a quinze dias" counts fifteen days.

**18a. fr "huit jours" and "quinze jours", said, are one and two weeks**. French counts these days inclusively in everyday use, the first day and the last. Académie française, 9th edition, s.v. "huit": "Huit jours, dans l'usage courant, une semaine entière en comptant le premier jour et le dernier. J'irai vous voir dans huit jours". Same, s.v. "quinze": "Quinze jours, dans l'usage courant, deux semaines complètes". TLFi gives "Huit jours. Une semaine." and "Quinze jours. Deux semaines." So "dans huit jours" is seven days after the anchor, as "dans 7 jours" is, and "dans quinze jours" fourteen. A length ("pendant huit jours") and a recurrence ("tous les quinze jours") read the same.

The sense is that of the spelled numeral in everyday use. A count of days in law is literal: "Lorsqu'un délai est exprimé en jours, celui de l'acte, de l'événement, de la décision ou de la notification qui le fait courir ne compte pas" and "Tout délai expire le dernier jour à vingt-quatre heures" (Code de procédure civile, articles 641 and 642). So the digit forms ("dans 15 jours") count as written, and so does a count after "délai" or before a word that names the kind of day ("jours francs", "calendaires", "pleins", "entiers", "ouvrés", "de travail"). A count added to a larger unit ("dans deux mois et quinze jours") is a literal sum. Ruling 18 still holds for pt, whose dictionaries give no such sense.

**19. A count with a weekday names that weekday in the period the count reaches**. "daqui a uma semana sexta-feira" is the Friday of the calendar week one week on (ruling B: the locale's week start). "daqui a um mês sexta-feira" and "daqui a um ano sexta-feira" are the first Friday on or after the day the count reaches. The weekday belongs to the date (as an apposition does in ruling 15), so it is never left over.

**20. A clock contradicted by its part of the day**. Hour 0 with a pm-side word refuses in every locale ("00:30 da tarde"). A morning word over hour 13 or later refuses in every locale ("15:00 da manhã"). A night word refuses only an hour from 13 to 17, the CLDR afternoon band. From 18 to 23 it keeps its reading where no source rules it out. de cites Duden and DWDS "Nacht" 1. No source was found for ru.

A CLDR day-period band is a formatting label, not a usage limit. So an evening or afternoon word over a 24-hour hour outside its band refuses only in a locale whose resource file cites a usage source for the band. pt cites one, so "22h da tarde" refuses. Every other locale keeps the reading ("21:30 wieczorem" is 21:30, "22:30 evening" is 22:30, ko "오후 19:30" is 19:30). "12:xx" with an evening word stays as read.

**21. A spelled number after a range or since word is a year, unless a unit or currency word follows it**. In en, "since", "until", "till", "from", "between", "before" and "after" mark a spelled number as a year. "Since two thousand and ten I have lived here" is the span from 2010 up to the anchor.

The right end of a range takes the left end's cue ("from two thousand to two thousand and ten" is 2000 to 2010). In pt only "desde" is such a cue. "até", "a partir de" and "entre" mostly introduce an amount ("até dois mil euros", "a partir de três mil euros por mês").

A unit word or a CLDR currency name right after the number makes it a count whatever cue comes before it. The cue does not reach back across sentence or clause punctuation. Known costs: "before three thousand fans arrived" and "after two thousand people left" read a year, as the ovos-date-parser reader does. "até dois mil e trinta vamos poupar" reads no year.

**22. A bare hour before a counted noun is a count. Any other word after it leaves the clock**. In ast, ca, de, en, es, fr, gl, it, nl and pt the preposition of a clock also introduces a counted group: "wave at 5 people", "a las 3 vecinas", "om 3 mensen", "um 3 Euro".

A bare hour behind such a preposition and directly before a noun that counts people or things is not a time of day. With a date it reads the date alone ("a las 3 vecinas mañana" is tomorrow, "look at 5 houses tomorrow" is tomorrow). Alone it reads nothing.

Each locale lists the nouns, each with a cited dictionary entry (`marker_counted_noun.voc`). Any other word after the hour keeps the clock, and this includes a verb, a pronoun or a name: "a las 8 llegamos", "um 8 gehe ich", "om 8 ben ik thuis", "ich rufe dich um 8 an". The count reading stays a candidate at half the confidence. Known cost: a counted noun that is not on the list reads as a clock ("at 5 lions"). A noun that is on the list and names a place or a time reads as a count.

**23. A digit clock from speech follows the lone-hour rule**. Speech recognition writes a spoken "three thirty" as "3:30". So the two forms must read the same.

Consider a digit clock h:mm with an hour from 1 to 11, no leading zero, and no am/pm word or part of the day. It takes the next of its two twelve-hour readings after the anchor, as ruling 17 does for a spoken hour: "wake me up at 6:30" said at 13:04 is 18:30, and "lembra-me às 3:30" said at 15:00 is 15:30.

Other forms read as written. They are a leading zero ("03:30"), the hour 12 ("12:30" is half past noon) and an hour from 13 to 23 ("15:30"). An am/pm word ("6:30 am") or a part of the day ("às 3:30 da manhã") also makes the clock read as written. "Today" names no part of the day, so "at 3:30 today" said at 15:00 is 15:30. A named later day keeps the written hour ("tomorrow at 6:30" is 06:30). Ruling 17 applies to digit clocks through this ruling.

**24. A unit on either end of a closed range measures both ends**. When a closed range ("desde … até", "de … a", "entre … e", "from … to", "between … and") carries a unit or currency word after either number, both numbers are amounts of that unit. Neither is a year. "desde dois mil euros até três mil" reads no date.

A range of bare numbers with no unit and no year cue keeps the reading ruling 21 gives it. Source: NIST SP 811 (2008), section 7.7, on "to" marking a range of values of one quantity. This supports the shared quantity, not a fact about spoken pt.

**25. A comma before the closing connector does not split a range**. A comma directly before the word that closes a range keeps the two numbers one range. Examples are "from two thousand, to two thousand and ten" and "desde dois mil, até dois mil e dez".

Every other clause mark still splits it, as ruling 21 says. No external source. This keeps parity with the ovos-date-parser reader and the purpose of the clause rule.

**26. "Today" names no part of the day for a spoken hour too**. Ruling 23 says "today" beside a digit clock names no half of the day. The same holds for a spoken lone hour under ruling 17: "today at 5" or "remind me today at five" said at 15:00 is 17:00, and said at 03:00 is 05:00.

"Today" limits the choice to the anchor's day, and the hour takes whichever of its two readings comes next within that day. When both readings of the day have passed, the hour reads as written. A part of the day word ("this morning", "hoje à tarde") still decides the half. This keeps the spoken and the digit form of one utterance in step, which is the reason for ruling 23.

**27. A locale's own morning or evening word beside a digit clock decides the half**. Ruling 23 treats a part of the day as reading the clock as written. That covers every word that the locale lists for the half of the day (its `clock_meridiem_am` and `clock_meridiem_pm` words). It holds even when the reader does not join the word to the clock. nl "om 8:00 's ochtends", de "um 6:30 Uhr morgens" and es "madrugada a las 4:30" are morning clocks. The lone-hour rule never moves such a clock to the other half.

**28. A bare part of the day is the anchor day's band unless it has ended**. A part-of-day word said alone ("tarde", "à noite", "in the evening" with no day) names that band on the anchor's day while the band has not ended. Once the band has ended, it names the next day's band.

Ruling C and ruling 1 read a span in the same way. pt "à tarde" said at 10:00 is this afternoon. Said at 21:00 it is tomorrow afternoon. "this evening" and "tonight" always name today's band, even after it has ended, because "this" points at the anchor's day. *Not implemented. Tracked in [#997](https://github.com/TigreGotico/chronologia/issues/997) and [#1103](https://github.com/TigreGotico/chronologia/issues/1103).*

**29. A bare "before X" is the span from the anchor to the start of X**. "before christmas", "avant noël", "antes do natal", "before may 13" and "before friday" all end when X begins (00:00 of X's first day). So X itself is not inside the span.

"Before" means "earlier than" (Wiktionary, "before", preposition). This mirrors ruling 33, where a bare "after X" starts when X ends. *Not implemented. Tracked in [#1097](https://github.com/TigreGotico/chronologia/issues/1097).*

**30. A counted offset before or after a holiday counts from the holiday's start**. The holiday stands for the instant it begins, as "15 minutes after new year" is 00:15 on 1 January. So "en kvart före jul" is 23:45 on 24 December, and "2 hours after christmas" is 02:00 on 25 December. A day count gives the same date both ways: "2 days after christmas" is 27 December and "2 days before christmas" is 23 December.

A count under one day reads as an instant (one minute wide), and a count of a day or more reads as that day. A vague count ("a few hours before christmas") reads as a span. The span ends at the start of the holiday. It begins one upper bound of the vague word before that start.

The number reader gives the vague word its bound. With no bound, it is the span of ruling 29. A bare "after X" with no count is ruling 33. *Not implemented. Exact offsets are tracked in [#1087](https://github.com/TigreGotico/chronologia/issues/1087). No issue tracks vague counts.*

**31. A clock with an offset from a holiday has more than one reading**. "às 9 uma hora antes do natal" names a time. But its words allow several readings. `extract_candidates` returns them ranked, and `extract_timespan` returns the first. First comes the stated clock on the day the offset lands on, in the twelve-hour reading nearer to the offset instant: "às 9 uma hora antes do natal" is 24 December 21:00, and "at 6am 12 hours before easter monday" is Easter Sunday 06:00.

Next comes the offset instant itself (24 December 23:00, Easter Sunday 12:00), then comes the clock's other twelve-hour reading on that day when the clock has no am/pm word. A clock with "am" or "pm" has no other reading. A clock that agrees with the offset gives one reading. *Not implemented. No issue tracks it.*

**32. A clock still ahead today is today**. "at 12:30 am" said at 00:00:30 is 00:30 the same day, as ruling C reads the next occurrence.

**33. A bare "after X" is the open span that starts when X ends**. "after monday", "depois de segunda", "nach Montag" name a time even with no clock. The span runs from the end of the next X onward, with no end. A phrase that names a time never reads no value just because the end is open. Consumers that need an instant take the span's start. *Not implemented. Tracked in [#1098](https://github.com/TigreGotico/chronologia/issues/1098).*

**34. A lone numeral is a candidate, not a reading**. A numeral with no clock marker, no unit and no year cue (da "20", nl "2", "2400") is not a date in `extract_timespan`, as ruling 2 keeps a bare number from being a clock. The function `extract_candidates` lists its readings, ranked low. These are an hour for 0 to 24, a day of the month for 1 to 31, and a year for a four-digit numeral. A consumer that asked "when?" can take them. *Not implemented. Tracked in [#1032](https://github.com/TigreGotico/chronologia/issues/1032) and [#1035](https://github.com/TigreGotico/chronologia/issues/1035).*

**35. A two-digit year takes the century window of the anchor**. "15/06/20" reads the year in the hundred years from 80 years before the anchor to 20 years after it. This is the default two-digit-year start of ICU (ICU SimpleDateFormat, "set2DigitYearStart": the default is 80 years before the current time).

Said in 2117 it is 2120. Said in 2026 it is 2020. *Not implemented. Tracked in [#1035](https://github.com/TigreGotico/chronologia/issues/1035).*

**36. A night word beside a twelve-hour clock picks the half that falls in the night.** de "um elf Uhr nachts", nl "om 11 's nachts" and "om 11:00 's nachts" are 23:00. "um drei Uhr nachts" is 03:00. And "um zwölf Uhr nachts" is 00:00. The night runs on both sides of midnight ("nachts": "in der Nacht", Duden), so the night word does not mark the am half.

It marks the reading inside the locale's night band (ruling 10). When neither half of the hour falls in that band, the clock keeps the am half. A 24-hour clock with a night word follows ruling 20. *Not implemented. Tracked in [#1079](https://github.com/TigreGotico/chronologia/issues/1079).*

**37. ru "в N-ом часу" is the hour from N-1 to N**. "в восьмом часу" is 07:00 to 08:00, the eighth hour of the clock face, counted as "в половине восьмого" (ruling 9) counts it. A day period fixes the half of the day ("в восьмом часу вечера" is 19:00 to 20:00). With none, the hour takes the next twelve-hour reading after the anchor (ruling 17). The start of the hour picks the reading, as ruling 17 does for a cardinal clock: said at 07:30, "в восьмом часу" is 19:00 to 20:00.

The hours run first to twelfth: "в двенадцатом часу ночи" is 23:00 to 24:00. The word "часу" is part of the phrase.

Sources: Ефремова, Современный толковый словарь, s.v. "восьмой", sense III: "Приближающийся к восьми (о единицах исчисления времени)". Ru.wiktionary s.v. "шестой": "шестой час, интервал времени между пятью и шестью часами дня или ночи".

**38. A recurrence that a range bounds runs over the days of the range**. In "every monday from june to august" and de `jeden Montag von Juni bis August`, the rule runs over the same days as the span that `extract_timespan` reads from the range words. The range words are "from june to august", or "from june until august" when the until word stands between the two bounds. `extract_recurrence` sets UNTIL to the end of the right bound, the first instant after August. `extract_event` starts the rule at the later of the anchor and the left bound. Said on 22 November 2026, the first event of "every monday from june to august" falls on Monday 7 June 2027, and UNTIL falls on 1 September 2027 00:00.

A plain until bound has no left bound, so its UNTIL stays at the start of its date: in "every friday until june", UNTIL falls on 1 June. A right bound with a clock (es "desde junio hasta agosto a las 9") also keeps the start of its date and its clock.

**39. A business-day ordinal of a month names the next such day**. "the 3rd business day of march", "the third weekday of the month" and pt "o 3.º dia útil do mês" are the n-th business day of that month. A business day is a day outside the locale's weekend (`weekend_start` and the day after it). With a jurisdiction, a public holiday of that jurisdiction is not a business day. "weekday" as a class noun is a business day.

A named month with no year, and "the month" with no marker, name the next month whose n-th business day is not before the anchor. This is the roll of the weekday ordinal ("the first tuesday of the month"). Said on 22 November 2026, "the third business day of the month" is 3 December 2026, and "the 3rd business day of march" is 3 March 2027. A year or a marker fixes the month: "of next month", "of march 2027". When that month has no n-th business day, no date is read.

---
[← EDTF](edtf.md) · [Home](index.md) · [Calendars →](calendars.md)
