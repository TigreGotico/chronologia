# Russian (`ru`)

<!-- agent-hint
covers: where each construction of the Russian locale comes from, what it refuses and which questions a native speaker would settle
source: `chronologia/locale/ru/lang.json`, `chronologia/locale/ru/*.voc`, `chronologia/extract/numlayer.py:NUMTAG_LANGS`
generated: no
verify: python -m doctest docs/languages/ru.md && python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set()\nfor m in re.finditer(r\"`([^`]+)`[^.`\\n]{0,25}?\\b(?:is|are|reads|gives|returns?|resolves? to|comes? back as|=)\\s+(\\d\\d):(\\d\\d)\",pr):\n    ph=m[1]\n    if ph[0]==\"-\": continue\n    r=extract_timespan(ph,c,A)\n    if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2],m[3])\npm=re.sub(r\"`[^`]*`\",lambda m:m[0].replace(\". \",\".\\x01\"),pr)\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(r\"((?:`[^`]+`(?:,| and| or|, and)? ?)+)\\s*(?:both |each |all )?(?:returns?|gives?) (?:nothing|`None`)\",s): cl|=set(x.replace(\"\\x01\",\" \") for x in re.findall(r\"`([^`]+)`\",m[1]))\nex={ast.literal_eval(x) for x in re.findall(r\">>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\",t)}\nif cl!=ex: bad=1;print(\"refusals differ\",cl^ex)\nsys.exit(bad)\n")' docs/languages/ru.md
see: `docs/languages/index.md`, `docs/extraction.md`
-->

This page records where each construction of the Russian (`ru`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

Almost no Russian temporal phrase stands in the nominative. `на прошлой
неделе` is prepositional, `в прошлом месяце` and `в прошлом году` are
prepositional, `прошлым летом` is instrumental — and none of those is the
dictionary form of the words involved. A locale that shipped citation forms
would leave the ordinary spoken register unreadable, so this one ships full
paradigms: every unit noun in all six cases and both numbers, and every
determiner in its complete adjectival or pronominal paradigm. The vocabulary
cites Грамота.ру's declension tables for each, naming the declension type it
followed.

The clock is the other thing to understand early, because Russian says it in
two directions and neither is the English one. Forward from the previous hour
is the toward-hour form: `четверть десятого` is a quarter *of the tenth*, that
is 09:15, and `половина девятого` — contracted `полдевятого` — is half of the
ninth, 08:30. Backward is `без`, which subtracts from the hour actually named:
`без четверти десять` is a quarter to ten, 09:45. Both are cited to
gramota.ru's guide to telling the time.

## What ships

**Weekdays and months** ship wide and abbreviated, with no recorded source.

**The date line** is little-endian, and the dotted civil form `15.06.2020`
reads — Russian is one of the languages that writes it. `ordinal_dot` is off,
so the dot in a date is a separator and never an ordinal marker.

**The unit nouns** are the heart of the locale, and three of them carry
decisions worth naming.

`час` ships its full paradigm including the locative `в первом часу`, which is
distinct from the prepositional `о часе`. The nominative plural `часы` is
deliberately withheld: it is the ordinary Russian word for a clock or a
wristwatch, and folding it into the duration unit would read a mention of the
object as a span of time.

`год` is suppletive — the plural is built on `лет-` — and both stems ship. But
`лето` is deliberately absent from the year vocabulary even though `лет`
belongs there, because the instrumental `летом` is the season and lives in the
summer vocabulary instead.

`неделя` ships the full first-declension paradigm rather than nominative and
genitive alone, because the prepositional `неделе` carries what is plausibly
the single most common temporal phrase in the language: `на этой / прошлой /
следующей неделе`.

`день` ships both the `ё` spelling `днём` and the `е` spelling `днем`, since
`ё` goes untyped in the majority of running Russian text.

**The determiners** ship complete. `прошлый` is listed across the hard-stem
adjective paradigm and `следующий` across the soft-stem one, `последний` — the
ordinal-last determiner behind `последний понедельник мая` — across the
soft-stem paradigm too, and `этот` across the full pronominal paradigm of
demonstratives. Each cites Грамота.ру and names the paradigm type.

**Relative offsets** are `через` forward and `назад` backward, in either order
relative to the count.

**The clock** ships, beyond the two fraction words, a generalisation of the
subtractive idiom. `без четверти` is the fixed quarter form, but Russian
subtracts any minute count: `без пяти девять` is 08:55, `без десяти девять`
08:50, `без двадцати девять` 08:40, `без пятнадцати девять` 08:45 — numerically
the same as `без четверти девять`. Those genitive cardinals live in their own
map rather than among the fractions, and the vocabulary explains why: unlike
`четверть` and `половина` they name no bare "N of the hour" idiom on their own,
so they are bound only after `без`. `пять девять` alone is not a Russian clock
time and does not read as one. An optional `минут` may follow the count —
`без пяти минут девять` — and reads the same.

`полдень` and `полночь` are the two landmark points, and `час`/`часов` is the
o'clock word.

**Day parts** take their boundaries from the Unicode CLDR 47 day-period chart
for `ru`, transcribed in `chronologia/dayparts.py`: `ночь` `[00:00, 04:00)`,
`утро` `[04:00, 12:00)`, `день` `[12:00, 18:00)`, `вечер` `[18:00, 24:00)`.
The surfaces shipped are not the nouns but the instrumental adverbs — `ночью`,
`утром`, `днём`, `вечером` — because that is the form the deictic phrases
actually use: `сегодня утром`, `вчера ночью`, `завтра днём`. Each is cited to
its Russian Wiktionary adverb entry.

**The eras** are the fullest part of the locale's citation record. The secular
`до нашей эры` abbreviates to `до н. э.` with a space after each letter, which
the vocabulary attributes to Мильчин and Чельцова's *Справочник издателя и
автора* as the typographic norm; the unspaced `до н.э.` is what people
actually type, so it is read too. The religious counterpart `до Р. Х.` — `до
Рождества Христова` — is equally current and names the same span, and its
common-era mirror `по Р. Х.` is recorded from Russian Wiktionary. `н. э.` and
`нашей эры` are the common-era forms.

**Ranges** are `с … по …` and `с … до …`, plus `между … и …`. The choice
between `по` and `до` is not cosmetic and the vocabulary argues it at length:
`по` with the accusative makes the named day *inclusive*, so `с 5 по 12 июня`
ends at the end of 12 June. The authorities cited are Ожегов and Шведова's
*Толковый словарь русского языка* under *по* — glossed there as "вплоть до"
with the examples "прочитать с первой по десятую главу" and "отпуск по
воскресенье" — and Кузнецов's *Большой толковый словарь*, with "проездной
действителен по март месяц" and "оплата с января по апрель".

**Quarters, ISO weeks, decades and seasons.** `первый квартал 2020`,
`неделя 12` and the spelled decade `восьмидесятые годы` all resolve. The
seasons carry adjectival narrowing, so `ранней весны` reads as early spring
rather than the whole of it.

**Fuzzy month parts** are `начало`, `середина` and `конец`.

## Weaker provenance

The weekday and month names carry no recorded source, and neither do the
seasons or the holiday vocabulary.

The `по`-inclusive rule is the best-cited decision in the locale; the
corresponding boundary semantics of `до` are not separately argued in the
vocabulary, and rest on the general contrast with `по`.

## What refuses

**`часы` as a duration.** The nominative plural of `час` returns nothing on its
own, by the deliberate withholding described above — it is a wristwatch, not a
span.

**A bare duration.** `две недели` returns nothing, and so does `полтора часа`
even though `полтора`/`полторы` is registered as a one-and-a-half quantifier.
A quantity with no direction marker is still only a quantity.

## Open questions for a native speaker

1. Should `полтора часа` read as a duration when a marker is present, and what
   surface would carry it?
2. Does `вчера ночью` name the small hours of yesterday, as the band table
   forces, or the night that began yesterday evening?
3. Are the century calque `столетие` and the native `век` interchangeable in
   every construction the locale reads, or does one of them resist some?
4. Should `до` in a range be inclusive or exclusive of the named day? The
   inclusive reading is argued only for `по`.

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("ru")
    True
    >>> span, rest = extract_timespan('без пяти девять', "ru", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T08:55:00', '')
    >>> span, rest = extract_timespan('на прошлой неделе', "ru", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-19T00:00:00', '')
    >>> span, rest = extract_timespan('в прошлом месяце', "ru", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-05-01T00:00:00', '')
    >>> span, rest = extract_timespan('в прошлом году', "ru", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2016-01-01T00:00:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('час', "ru", anchor) is None
    True
    >>> extract_timespan('две недели', "ru", anchor) is None
    True

---
[← Romanian](ro.md) · [Home](../index.md) · [Serbian →](sr.md)
