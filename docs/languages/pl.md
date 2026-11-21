# Polish (`pl`)

<!-- agent-hint
covers: where each construction of the Polish locale comes from, what it refuses and which questions a native speaker would settle
source: `chronologia/locale/pl/lang.json`, `chronologia/locale/pl/*.voc`, `chronologia/extract/numlayer.py:NUMTAG_LANGS`
generated: no
verify: python -m doctest docs/languages/pl.md && python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set()\nfor m in re.finditer(r\"`([^`]+)`[^.`\\n]{0,25}?\\b(?:is|are|reads|gives|=)\\s+(\\d\\d):(\\d\\d)\",pr):\n    ph=m[1]\n    if ph[0]==\"-\" or not re.search(r\"[^\\W\\d_]\",ph): continue\n    r=extract_timespan(ph,c,A)\n    if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2],m[3])\npm=re.sub(r\"`[^`]*`\",lambda m:m[0].replace(\". \",\".\\x01\"),pr)\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(r\"((?:`[^`]+`(?:,| and| or|, and)? ?)+)\\s*(?:both |each |all )?(?:returns?|gives?) (?:nothing|`None`)\",s): cl|=set(x.replace(\"\\x01\",\" \") for x in re.findall(r\"`([^`]+)`\",m[1]))\nex={ast.literal_eval(x) for x in re.findall(r\">>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\",t)}\nif cl!=ex: bad=1;print(\"refusals differ\",cl^ex)\nsys.exit(bad)\n")' docs/languages/pl.md
see: `docs/languages/index.md`, `docs/extraction.md`
-->

This page records where each construction of the Polish (`pl`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

Polish splits its clock system, and the split is deliberate. Only the half hour
counts toward the coming hour — `wpół do dziewiątej` is half toward nine, 08:30
— while the quarter uses the ordinary past-and-to reading: `kwadrans po
dziewiątej` is a quarter past nine, 09:15, and `za kwadrans dziesiąta` is a
quarter to ten, 09:45. `bare_half_to` is therefore set in `lang.json` and
`bare_quarter_to` is deliberately not. The vocabulary cites PWN's Poradnia
Językowa and the Polish Academy of Sciences' *Wielki słownik języka polskiego*
for both halves of that system.

The other decision that shapes the locale is the same one Russian faces: the
ordinary Polish temporal phrase is locative, not nominative. `w zeszłym
tygodniu`, `w ubiegłym miesiącu`, `w tym roku` — listing citation forms alone
would leave the normal register unreadable, so the unit nouns and the
determiners ship their full paradigms, cited to PWN's inflection rules.

## What ships

**Weekdays and months** ship as a nominative and a genitive each, with no
recorded source. That is a narrower listing than the unit nouns get, and it has
consequences noted below.

**The date line** is little-endian, and Polish is one of the languages that
writes the dotted civil date, so `15.06.2020` reads. `ordinal_dot` is on.

**The unit nouns** ship complete, and the vocabulary names the awkward ones.
`tydzień` alternates its stem — `tydzień` against `tygodnia` — and the locative
`tygodniu` carries `w tym / zeszłym / przyszłym tygodniu`. `rok` is suppletive
in the plural, `rok` against `lata`. `miesiąc` ships its locative `miesiącu`
for the same reason. Each cites the PWN dictionary entry for the word.

**The determiners** ship complete too. `zeszły` and `ubiegły` are hard-stem,
`poprzedni` and `ostatni` soft-stem, and all four are listed across the
adjective declension; `przyszły` and `następny` cover "next". `ostatni` doubles
as the ordinal-last determiner behind `ostatni poniedziałek maja`.

The demonstrative `ten` ships across the pronominal paradigm with one form
withheld on purpose. The dative `temu` is deliberately absent, because in
Polish `temu` is the ago-marker — `dwa dni temu` — and admitting it as a "this"
determiner would read a past offset as a present one.

**Relative offsets** are `za` forward and `temu` backward.

**The clock** carries `po` and `za` as the two directions, cited to PWN's
Poradnia Językowa, `kwadrans` as the quarter and `wpół` as the half.
`południe` and `północ` are the landmark points, and the hour is stated as a
feminine ordinal — `o ósmej`.

**The eras** are `p.n.e.` and `n.e.`, each with a dot after every element, and
the vocabulary explains the spelling: the abbreviated elements are followed by
words beginning with vowels. PWN's *Wielki słownik ortograficzny* is cited for
both. The expanded `przed naszą erą` and `naszej ery` read too.

**Ranges** are `od … do …`. `między … a …` reads where the endpoints are
months or bare days.

**Quarters, ISO weeks and month parts.** `pierwszy kwartał 2020`, `tydzień 12`
and the month-third words `początek`, `połowa` and `koniec` all resolve.
`połowa` is also the period noun behind the half-year, cited to PWN's *Słownik
języka polskiego*, so `pierwsza połowa 2020` reads as the first half of that
year.

**Day parts** take their boundaries from the Unicode CLDR 47 day-period chart
for `pl`, transcribed in `chronologia/dayparts.py` as morning `[06:00, 12:00)`,
afternoon `[12:00, 18:00)`, evening `[18:00, 21:00)` and night
`[21:00, 06:00)`. Note the evening: Polish closes it at 21:00, three hours
earlier than the Germanic languages do, and the night wraps across midnight
rather than starting there. Two of the four bands have surfaces, both of them
the deictic adverbs these phrases actually use — `rano` for the morning and
`wieczorem`, the instrumental of `wieczór`, for the evening. Both cite
Wiktionary.

## Weaker provenance

The day-part surfaces rest on Wiktionary entries, weaker than the PWN sources
behind the clock, the eras and the paradigms.

The weekday and month names, the seasons and the holiday vocabulary carry no
recorded source.

## What refuses

**Decades.** `lata 80` returns nothing. The spelled `lata osiemdziesiąte` reads.

**A bare duration.** `dwa tygodnie` returns nothing. A quantity with no
direction marker is still only a quantity.

## Open questions for a native speaker

1. Which instrumental weekday forms should ship so that `między poniedziałkiem
   a piątkiem` reads? The full weekday paradigm is the obvious answer, but only
   the forms Polish actually uses temporally are wanted.
2. What are the ordinary surfaces for the afternoon and the night bands, and
   are they single words or prepositional phrases?
3. Should `lata 80` resolve as a decade?
4. Does the CLDR evening boundary at 21:00 match how a Polish speaker uses
   `wieczorem`?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("pl")
    True
    >>> span, rest = extract_timespan('wpół do dziewiątej', "pl", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T08:30:00', '')
    >>> span, rest = extract_timespan('kwadrans po dziewiątej', "pl", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T09:15:00', '')
    >>> span, rest = extract_timespan('za kwadrans dziesiąta', "pl", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T09:45:00', '')
    >>> span, rest = extract_timespan('w zeszłym tygodniu', "pl", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-19T00:00:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('lata 80', "pl", anchor) is None
    True
    >>> extract_timespan('dwa tygodnie', "pl", anchor) is None
    True

---
[← Persian](fa.md) · [Home](../index.md) · [Portuguese →](pt.md)
