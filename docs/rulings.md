# Rulings

These are the decisions that fix how chronologia reads a phrase where two
readings are possible. Each ruling gives the reading, an example and, where a
dictionary or standard rules on it, the source. A ruling marked "Not yet
implemented" states the reading the engine is to return. The engine does not
return that reading yet. A change to a ruling changes this page.

Rulings A to C are the readings that differ from ovos-date-parser, the reader
that chronologia replaces. Ruling D lists settled spelled-clock and day-word
readings. The numbered rulings that follow apply
to every locale unless a ruling names the locales it covers.

## A. A counted offset carries the clock of the anchor

A counted offset is arithmetic on the anchor, so "in two hours" said at 13:04 is
15:04, and `en 3 días` (Aragonese, in three days) said at 13:04 on 2017-06-27 is
2017-06-30 13:04, not 2017-06-30 00:00. Rounding to the hour is a defect, not a
convention. Counted periods follow the same rule: a counted week, month or year
is the anchor plus the count ("in 2 weeks" is the anchor plus 14 days, "3 months
ago" is minus 3 calendar months).

## B. A named period is the calendar unit

"Next week" is the calendar week after the anchor's week, starting on the first
weekday of the locale, and "last month" is the previous calendar month. A
rolling seven days is not a named period: `la semana vinient` (next week) said
on Tuesday 2017-06-27 starts on Monday 2017-07-03, not on 2017-07-04. The engine
option `relative_period_mode` takes `calendar` by default and `rolling` for a
deployment that wants the rolling reading. The week starts on Monday in 56
locales, on Saturday in ar, sw and fa, and on Sunday in he.

## C. `prefer_future` means the next occurrence

The next occurrence is the first one strictly after the anchor, and an instant
equal to the anchor is the anchor. `الساعة السابعة صباحاً` (seven in the
morning) said at 13:04 on 2017-06-27 is 2017-06-28, and `5 يناير` is 2018-01-05.
The weekday "this monday" said on a Tuesday is the coming Monday, never the one
that has passed.

## D. Readings settled for spelled clocks and day words

- A spelled clock is read forward from the hour in ro and it: `nouă și zece`
  (ten past nine) is 09:10, and `nouă fără zece` (ten to nine) is 08:50. A phrase
  with no marker still reads in that order.
- A spelled clock in es, pt, gl and el reads the same way.
- Arabic `أمس الأول` is the day before yesterday.
- en "10 past 4" is 04:10, nl "morgen om 10 uur" is 10:00, id
  `Rapat pukul tiga sore` is 15:00, and ca `d'aquí a 15 minuts` is 15 minutes
  from the anchor, not the clock 15:00.

## Numbered rulings

**1. A month named without a day.** A month whose span contains the anchor is this month. A month that ended before the anchor is the month of next year. This is ruling C applied to a span: "janvier" said in June 2017 is January 2018, and "juin" said in June 2017 is June 2017. A part of a month ("early march", "first week of march") still keeps the anchor's year.

**2. A bare hour or an hour-letter clock.** "20h", "21h30" and "3 heures" read as a clock when they are the whole utterance, as the ruling for a bare hour alone says. Inside a sentence with no clock marker, they refuse. So fr "un film de 2 heures", "2h de route", "il reste 3 heures" and "3 heures de travail" refuse. ast "20h" and "21h30" alone read 20:00 and 21:30. This agrees with chronologia #882.

**3. A bare duration is not a date.** `extract_datetime("pendant 3 heures")` returns None, as "trois jours" already does. A counted offset with a direction word ("dans 3 heures", "daqui a 3 horas") still answers.

**4. pt "antes de ontem" is anteontem.** Priberam lists it as a synonym.

**5. A habitual phrase reads as the next occurrence.** pt "ao sábado", gl "os luns" and fr "le mardi" alone answer the next such day. `extract_datetime` has no recurrence type, and a skill wants a date.

**6. A weekday said on that same weekday is today.** "o venres" said on a Friday answers that Friday. A day is a span, and ruling 1 already makes a span that contains the anchor the current one ("juin" said in June is this June). Ruling C agrees: an instant equal to the anchor is the anchor. A phrase that names the next one ("next Friday", "o próximo venres") still moves forward a week.

**7. ru and uk "<ordinal> числа" is a date.** "двадцатого числа" and "двадцятого числа" name the day of the month, because "числа" names it. The bare genitive ordinal ("двадцатого", "двадцятого") and the digit form "20-го" stay unread, because the left-out noun can be any noun. A cardinal before "числа" is a count: "три числа" is "three numbers".

**8. ru "ночи" is a night band that crosses midnight.** "11 часов ночи" is 23:00 and "3 часа ночи" is 03:00, as sl "ponoči" and es "de la noche" read.

**9. ru "в половине третьего" follows the bare-clock rule.** It reads as "половина третьего" reads. A day period fixes the half of the day: "в половине третьего дня" is 14:30.

**10. "Tonight" is the night of the anchor's own day.** Wiktionary "tonight": "During the night following the current day; during the evening of today." CLDR day periods for en start night1 at 21:00 and morning1 at 00:00, so the en night ends at midnight. A night band that crosses midnight is cut at midnight before its middle hour is taken: with a 21:00 to 06:00 band, "tonight" said at 13:04 answers 22:30 on the anchor day, not 01:30 the next day. An hour said inside the band keeps its own reading (ruling 8: "3 часа ночи" is 03:00).

**10a. A part of the day that holds the anchor answers the anchor once its middle has passed.** A part of the day named with no day of its own ("tonight", "noću", "dnes večer", "ráno") answers the middle of its band. When the anchor lies inside the band (for a night band, inside the kept part between its start and midnight) and the middle has passed, the answer is the anchor itself. Before the middle, the middle still answers. Ruling C decides both: a reading is never before the anchor, and an instant equal to the anchor is the anchor. Said at 23:30 with a 21:00 to 06:00 band, "tonight" answers 23:30. Said at 21:30 it answers 22:30. cs "dnes večer" said at 21:00, inside the 18:00 to 22:00 evening band, answers 21:00 and not 20:00.

**10b. Ruling 10 holds in every locale.** The cut at midnight follows from what "tonight" names (the night of the anchor's own day), not from the en clock. CLDR gives other locales a night that crosses midnight (hr night1 21:00 to 04:00, cs and sk 22:00 to 04:00), and a night named with no day of its own is the night of the anchor's day there too. So hr "noću" said at 13:04 answers 22:30 (21:00 plus half of the three hours to midnight), and cs or sk 23:00.

**11. "The new year" is 1 January of the next year.** Wiktionary "New Year": "In particular, January 1 in the Julian and Gregorian calendar (New Year's Day) and the days following." So "how many days until the new year" counts to the next 1 January. The library must not refuse it (TigreGotico/chronologia#933).

**12. "This <weekday>" is the next occurrence.** "esta segunda" said on a Saturday is the coming Monday, as ruling C reads. Said on a Monday it is that Monday (ruling 6). A week-start reading of "this <weekday>" states a design choice and cites no linguistic source, so it is not used. No pt source rules on "esta <weekday>" for a day already past: Svobodová (2016, Romanistica Pragensia) covers "próxima" and "passada" only, and no Ciberdúvidas answer was found. A command to an assistant names a future time, so the next occurrence is the safer reading.

**13. "Of the month" with no marker rolls; "of this month" does not.** An nth day, weekday or week "of the month" ("o dia 5 do mês", "a primeira terça-feira do mês") that ended before the anchor is the next month's, as ruling C and ruling 1 read a span that has passed. A month that lacks the day is skipped: "o dia 30 do mês" said on 31 January is 30 March. "Of this month" names the anchor's own month and never rolls. "deste mês" is "Contracção da preposição de com o pronome este" (Priberam s.v. "deste"), and "este" is "Designativo de pessoa ou coisa que está presente, ou mais próxima de quem fala" (Priberam s.v. "este"). So "o dia 5 deste mês" said on 17 October is 5 October.

**14. The first week of a year is ISO 8601 week 01.** "The ISO 8601 definition for calendar week 01 is the week with the first Thursday of the Gregorian year"; equivalently, "It has 4 January in it" (Wikipedia, "ISO week date"). So "a primeira semana de 2026" is Monday 29 December 2025 to Sunday 4 January 2026, and the last week of a year is the one that contains 28 December. ISO defines no weeks of a month, so a week of a month keeps the existing reading: it starts on the first Monday on or after the 1st.

**15. A weekday beside a day word names that day, or no day.** In "amanhã, domingo" the weekday is an apposition: an "aposto" is a "Nome ou locução nominal que se junta a outro nome para melhor o caracterizar" (Priberam s.v. "aposto", 5). When the two agree, the weekday belongs to the date. When they disagree ("amanhã segunda-feira" said on a Saturday), the phrase names no single day, and the reading is refused rather than guessed.

**15a. The apposed weekday follows the day word.** Ruling 15 reads a weekday only after the day word ("amanhã, domingo"). A weekday before a day word is not folded: in de, nl, da and nb, "morgen" after a weekday names the morning ("Dienstagmorgen": "Morgen des Dienstags", Duden s.v. "Dienstagmorgen"), and es, ast and gl "martes mañana" has the same reading. A sentence boundary between the two words also stops the fold: "vou amanhã. segunda-feira trabalho" names tomorrow.

**16. "This <weekday>" fixes the day; a passed clock does not move it.** "this tuesday at 10am" said on a Tuesday at 13:04 is that Tuesday at 10:00 (rulings 6 and 12: "este" is "Designativo de pessoa ou coisa que está presente, ou mais próxima de quem fala", Priberam s.v. "este"). A bare weekday with a clock that has passed ("tuesday at 10am" said on a Tuesday at 13:04) is the next one, as ruling C reads an instant before the anchor. The tense of the sentence is outside the parser.

**16a. A count before or after a weekday counts from the day ruling 6 names.** "a week before friday" said on Friday 30 June 2017 is 23 June, and "the day before friday" is 29 June. The weekday is that same Friday (ruling 6). The count moves from it even when the answer is in the past. "two days from friday" said on that Friday is 2 July, by the same rule.

**17. A lone spoken hour takes the next twelve-hour reading.** An hour 1 to 12 said with no am/pm word and no part of the day takes whichever of its two readings comes next after the anchor: "at 8" said at 15:00 is 20:00, and pt "às 10 e meia" said at 13:04 is 22:30. A named day or part of the day keeps the spoken hour ("tomorrow at 8" is 08:00, "às 10 da manhã" is 10:00). A digit clock follows ruling 23, and 24-hour hours (13 to 23) are as written. A letter-h clock ("8h", "20h", "6h30") reads as written, because the letter h marks the written 24-hour form: fr "à 8h" said at 15:00 is 08:00 the next day. Ruling 2 still decides when a bare hour is a clock at all.

**18. pt "quinze dias" is fifteen days.** Priberam s.v. "quinzena", 1: "Período de quinze dias seguidos." No dictionary sense gives "quinze dias" the reading of two weeks, so "daqui a quinze dias" counts fifteen days.

**19. A count with a weekday names that weekday in the period the count reaches.** "daqui a uma semana sexta-feira" is the Friday of the calendar week one week on (ruling B: the locale's week start). "daqui a um mês sexta-feira" and "daqui a um ano sexta-feira" are the first Friday on or after the day the count reaches. The weekday belongs to the date (as an apposition does in ruling 15), so it is never left over.

**20. A clock contradicted by its part of the day.** Hour 0 with a pm-side word refuses in every locale ("00:30 da tarde"). A morning word over hour 13 or later refuses in every locale ("15:00 da manhã"). A night word refuses only an hour from 13 to 17, the CLDR afternoon band. From 18 to 23 it keeps its reading where no source rules it out (de cites Duden and DWDS "Nacht" 1, and no source was found for ru). A CLDR day-period band is a formatting label, not a usage limit, so an evening or afternoon word over a 24-hour hour outside its band refuses only in a locale whose resource file cites a usage source for the band. pt cites one ("22h da tarde" refuses). Every other locale keeps the reading ("21:30 wieczorem" is 21:30, "22:30 evening" is 22:30, ko "오후 19:30" is 19:30). "12:xx" with an evening word stays as read.

**21. A spelled number after a range or since word is a year, unless a unit or currency word follows it.** In en, "since", "until", "till", "from", "between", "before" and "after" mark a spelled number as a year ("since two thousand and ten I have lived here" is the span from 2010 up to the anchor). The right end of a range takes the left end's cue ("from two thousand to two thousand and ten" is 2000 to 2010). In pt only "desde" is such a cue. "até", "a partir de" and "entre" mostly introduce an amount ("até dois mil euros", "a partir de três mil euros por mês"). A unit word or a CLDR currency name right after the number makes it a count whatever cue comes before it. The cue does not reach back across sentence or clause punctuation. Known costs: "before three thousand fans arrived" and "after two thousand people left" read a year, as the ovos-date-parser reader does. "até dois mil e trinta vamos poupar" reads no year.

**22. A bare hour before a counted noun is a count, and any other word after it leaves the clock.** In ast, ca, de, en, es, fr, gl, it, nl and pt the preposition of a clock also introduces a counted group ("wave at 5 people", "a las 3 vecinas", "om 3 mensen", "um 3 Euro"). A bare hour behind such a preposition and directly before a noun that counts people or things is not a time of day. With a date it reads the date alone ("a las 3 vecinas mañana" is tomorrow, "look at 5 houses tomorrow" is tomorrow), and alone it reads nothing. Each locale lists the nouns, each with a cited dictionary entry (`marker_counted_noun.voc`). Any other word after the hour keeps the clock, a verb, a pronoun or a name included ("a las 8 llegamos", "um 8 gehe ich", "om 8 ben ik thuis", "ich rufe dich um 8 an"). The count reading stays a candidate at half the confidence. Known cost: a counted noun that is not on the list reads as a clock ("at 5 lions"). A noun that is on the list and names a place or a time reads as a count.

**23. A digit clock from speech follows the lone-hour rule.** Speech recognition writes a spoken "three thirty" as "3:30", so the two forms must read the same. A digit clock h:mm with an hour from 1 to 11, no leading zero, and no am/pm word or part of the day takes whichever of its two twelve-hour readings comes next after the anchor, as ruling 17 does for a spoken hour: "wake me up at 6:30" said at 13:04 is 18:30, and "lembra-me às 3:30" said at 15:00 is 15:30. A leading zero ("03:30"), the hour 12 ("12:30" is half past noon), an hour from 13 to 23 ("15:30"), an am/pm word ("6:30 am") or a part of the day ("às 3:30 da manhã") reads as written. "Today" names no part of the day, so "at 3:30 today" said at 15:00 is 15:30. A named later day keeps the written hour ("tomorrow at 6:30" is 06:30). Ruling 17 applies to digit clocks through this ruling.

**24. A unit on either end of a closed range measures both ends.** When a closed range ("desde … até", "de … a", "entre … e", "from … to", "between … and") carries a unit or currency word after either number, both numbers are amounts of that unit. Neither is a year: "desde dois mil euros até três mil" reads no date. A range of bare numbers with no unit and no year cue keeps the reading ruling 21 gives it. Source: NIST SP 811 (2008), section 7.7, on "to" marking a range of values of one quantity. This supports the shared quantity, not a fact about spoken pt.

**25. A comma before the closing connector does not split a range.** A comma directly before the word that closes a range ("from two thousand, to two thousand and ten", "desde dois mil, até dois mil e dez") keeps the two numbers one range. Every other clause mark still splits it, as ruling 21 says. No external source. This keeps parity with the ovos-date-parser reader and the purpose of the clause rule.

**26. "Today" names no part of the day for a spoken hour too.** Ruling 23 says "today" beside a digit clock names no half of the day. The same holds for a spoken lone hour under ruling 17: "today at 5" or "remind me today at five" said at 15:00 is 17:00, and said at 03:00 is 05:00. "Today" limits the choice to the anchor's day, and the hour takes whichever of its two readings comes next within that day. When both readings of the day have passed, the hour reads as written. A part of the day word ("this morning", "hoje à tarde") still decides the half. This keeps the spoken and the digit form of one utterance in step, which is the reason for ruling 23.

**27. A locale's own morning or evening word beside a digit clock decides the half.** Ruling 23 treats a part of the day as reading the clock as written. That covers every word the locale lists for the half of the day (its `clock_meridiem_am` and `clock_meridiem_pm` words), even when the reader does not join the word to the clock: nl "om 8:00 's ochtends", de "um 6:30 Uhr morgens" and es "madrugada a las 4:30" are morning clocks. The lone-hour rule never moves such a clock to the other half.

**28. A bare part of the day is the anchor day's band unless it has ended.** A part-of-day word said alone ("tarde", "à noite", "in the evening" with no day) names that band on the anchor's day while the band has not ended, and the next day's band once it has, as ruling C and ruling 1 read a span: pt "à tarde" said at 10:00 is this afternoon, said at 21:00 is tomorrow afternoon. "this evening" and "tonight" always name today's band, even after it has ended, because "this" points at the anchor's day. *Implemented for a band word that is the whole text in pt (`tarde`, `noite`, `manhã`, `madrugada`) and for it `stasera`, on the anchor's day. The roll to the next day once the band has ended is not yet implemented. Tracked in [#997](https://github.com/TigreGotico/chronologia/issues/997).*

**29. A bare "before X" is the span from the anchor to the start of X.** "before christmas", "avant noël", "antes do natal", "before may 13" and "before friday" all end when X begins (00:00 of X's first day), so X itself is not inside the span. "Before" means "earlier than" (Wiktionary, "before", preposition). This mirrors ruling 33, where a bare "after X" starts when X ends. *Not yet implemented. Tracked in [#1097](https://github.com/TigreGotico/chronologia/issues/1097).*

**30. A counted offset before or after a holiday counts from the holiday's start.** The holiday stands for the instant it begins, as "15 minutes after new year" is 00:15 on 1 January. So "en kvart före jul" is 23:45 on 24 December, and "2 hours after christmas" is 02:00 on 25 December. A day count gives the same date both ways: "2 days after christmas" is 27 December and "2 days before christmas" is 23 December. A count under one day reads as an instant (one minute wide), and a count of a day or more reads as that day. A vague count ("a few hours before christmas") reads as a span that ends at the holiday's start and begins the vague word's upper bound before it, taking the bound that the number reader gives the vague word; with no bound, it is the span of ruling 29. A bare "after X" with no count is ruling 33. *Not yet implemented. Exact offsets are tracked in [#1087](https://github.com/TigreGotico/chronologia/issues/1087). Vague counts have no issue yet.*

**31. A clock with an offset from a holiday has more than one reading.** "às 9 uma hora antes do natal" names a time, but its words allow several readings. `extract_candidates` returns them ranked, and `extract_timespan` returns the first. First comes the stated clock on the day the offset lands on, in the twelve-hour reading nearer to the offset instant: "às 9 uma hora antes do natal" is 24 December 21:00, and "at 6am 12 hours before easter monday" is Easter Sunday 06:00. Next comes the offset instant itself (24 December 23:00, Easter Sunday 12:00), then the clock's other twelve-hour reading on that day when the clock has no am/pm word; a clock with "am" or "pm" has no other reading. A clock that agrees with the offset gives one reading. *Not yet implemented. No issue yet.*

**32. A clock still ahead today is today.** "at 12:30 am" said at 00:00:30 is 00:30 the same day, as ruling C reads the next occurrence.

**33. A bare "after X" is the open span that starts when X ends.** "after monday", "depois de segunda", "nach Montag" name a time even with no clock: the span from the end of the next X onward, with no end. A phrase that names a time never reads no value just because the end is open; consumers that need an instant take the span's start. *Not yet implemented. Tracked in [#1098](https://github.com/TigreGotico/chronologia/issues/1098).*

**34. A lone numeral is a candidate, not a reading.** A numeral with no clock marker, no unit and no year cue (da "20", nl "2", "2400") is not a date in `extract_timespan`, as ruling 2 keeps a bare number from being a clock. `extract_candidates` lists its readings ranked low: an hour for 0 to 24, a day of the month for 1 to 31, and a year for a four-digit numeral. A consumer that asked "when?" can take them. *Not yet implemented. Tracked in [#1032](https://github.com/TigreGotico/chronologia/issues/1032) and [#1035](https://github.com/TigreGotico/chronologia/issues/1035).*

**35. A two-digit year takes the century window of the anchor.** "15/06/20" reads the year in the hundred years from 80 years before the anchor to 20 years after it, as ICU's default two-digit-year start does (ICU SimpleDateFormat, "set2DigitYearStart": the default is 80 years before the current time). Said in 2117 it is 2120; said in 2026 it is 2020. *Not yet implemented. Tracked in [#1035](https://github.com/TigreGotico/chronologia/issues/1035).*

**36. A night word beside a twelve-hour clock picks the half that falls in the night.** de "um elf Uhr nachts", nl "om 11 's nachts" and "om 11:00 's nachts" are 23:00. "um drei Uhr nachts" is 03:00, and "um zwölf Uhr nachts" is 00:00. The night runs on both sides of midnight ("nachts": "in der Nacht", Duden), so the night word does not mark the am half. It marks the reading inside the locale's night band (ruling 10). When neither half of the hour falls in that band, the clock keeps the am half. A 24-hour clock with a night word follows ruling 20. *Not yet implemented. Tracked in [#1079](https://github.com/TigreGotico/chronologia/issues/1079).*
