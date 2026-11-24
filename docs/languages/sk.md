# Slovak (`sk`)

<!-- agent-hint
covers: where each construction of the Slovak locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/sk/lang.json, chronologia/locale/sk/*.voc, chronologia/extract/numlayer.py:NUMTAG_LANGS, test/nl_corpus_sk/, test/test_xfail_open_issues_*.py
generated: no
verify: .venv/bin/python -m doctest docs/languages/sk.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/sk.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Slovak (`sk`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

Slovak names the hour with a declined ordinal agreeing with an elided `hodina`: `o druhej` is two o'clock, `o ôsmej` is eight. The ordinal stands in the feminine locative because the preposition `o` governs it. numtag reads the ordinal in that case (`numlayer_slavic.py`). `druhej` folds to 2 as the digit does. The same ordinal names the coming hour after `pol`: `pol deviatej` is 08:30.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('pol deviatej', "sk", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T08:30:00', '')

## What ships

**The date line** is little-endian, `DAY MONTH YEAR?`, matching the CLDR 47 `ca-gregorian` chart for `sk` at every level, full `EEEE d. MMMM y`, long `d. MMMM y`, medium and short `d. M. y`. The tokenizer runs with `ordinal_dot` and `dotted_date` on, so both the written `15. januára 2020` and the spelled `pätnásteho januára 2020` resolve to the fifteenth of January. The spelled day is a genitive ordinal agreeing with an elided day noun, and Slovak declines both elements of a compound (`dvadsiateho tretieho`), numtag reads the two words as one ordinal, 23.

**Months** ship in four cases at once. The nominative (`január`, `marec`) is CLDR 47's `stand-alone` wide chart. The genitive that follows a day ordinal (`januára`, `marca`) is the `format` wide chart, genitive throughout for Slovak. The locative that follows the preposition (`januári`, `marci`) and the instrumental (`januárom`) ship alongside them without a recorded source. So `v januári` is the whole of January.

**Weekdays** ship in the nominative, matching CLDR 47's wide weekday chart, with the accusative a `v <weekday>` phrase takes for the three whose accusative differs (`stredu`, `sobotu`, `nedeľu`) and a genitive for each of the masculine ones. No source is recorded for the choice of oblique forms.

**Day parts** are transcribed from the Unicode CLDR 47 day-period rules for `sk`, each shipping as the form a phrase actually uses rather than a citation form. `ráno` is the morning band, `popoludní` the afternoon and `večer` the evening, so `dnes ráno` runs from 04:00 to 12:00, `dnes popoludní` from 12:00 to 18:00 and `dnes večer` from 18:00 to 22:00. The afternoon surface is the locative singular of `popoludnie`, which is the spelling CLDR's own `format` chart gives and which the Wiktionary declension table for that noun prints in its locative row. The same words double as clock meridiem cues on an explicit hour (`ráno` and `dopoludnia` for AM, `poobede`, `popoludní`, `podvečer` and `večer` for PM) so `o deviatej večer` is 21:00 and `o deviatej ráno` is 09:00.

**The spoken hour.** The feminine locative ordinal that names the hour (`jednej`, `druhej`, `tretej` ... `dvanástej`) folds to its digit through numtag. It feeds the ordinary `at HOUR` order. `o druhej` and `o druhej hodine` are both two o'clock. This is a literal named hour, not a toward-hour reading: the preposition plus locative simply names the hour it says.

**Relative offsets** are `pred` (ago, governing the instrumental) and `za`, `o` and `cez` (in/after). Direction is a fact of the marker. `pred 5 rokmi` is five years back and `o 5 rokov` five years ahead, both to the minute. `o päť minút` is five minutes ahead of the anchor.

**Determiners.** `minulý` and `posledný` ("last, previous"), `budúci` and `nasledujúci` ("next"). The demonstrative `tento` ("this") each ship a full paradigm rather than a nominative alone, `minulý` and `posledný` on the hard `pekný` pattern and `budúci` and `nasledujúci` on the soft `cudzí` one. The oblique forms are what the ordinary phrasings need: `minulého roka` is the genitive "last year" and `v minulom týždni` the locative "last week". `posledný` also serves as the ordinal-last determiner, in full concord with the weekday it scopes. `posledný piatok v júni` is the last Friday of June.

**Unit nouns** ship full paradigms. `rok` carries both attested genitive singulars, `roka` and `roku`, because the locative phrasings need the second and the counted ones the first.

**Century.** `v 20. storočí` and `20. storočie` both resolve to the years 1900 through 1999. The locative `storočí` is spelled exactly like the genitive plural (the form Slovak counts centuries with from five up) so behind the preposition the century reading and a bare count of centuries are the same two words. The written ordinal dot is what tells them apart. The order that binds the locative requires it: `v 20. storočí` resolves and `v 20 storočí`, `v päť storočí` and `päť storočí` all refuse rather than answering with the twentieth century. The Wikislovník entry for `storočie` carries the declension: whose table gives locative singular `storočí` and genitive plural `storočí` alike.

**Era markers** ship in both the secular and the Christian pair, `pred n. l.` / `n. l.` and `pred Kr.` / `po Kr.`, together with the spelled-out `pred naším letopočtom` and `nášho letopočtu` and the shorter `pr. n. l.` and `p. n. l.` that circulate alongside. All four abbreviations match the CLDR 47 `sk` era chart, which gives `pred Kr.` and `po Kr.` as the primary pair and `pred n. l.` and `n. l.` as the alternates. `500 pr. n. l.` resolves to the right year in the right direction.

**Quarters, ISO weeks and decades** all resolve, with `štvrťrok` and `kvartál` as two quarter words, `týždeň` for the ISO week and `desaťročie` for the decade. `prvý štvrťrok 2020` is the first quarter of 2020, `týždeň 12` the twelfth ISO week and `2. desaťročie` the years 10 through 19.

**Named days** span all five positions around the anchor: `predvčerom`, `včera`, `dnes`, `zajtra`, `pozajtra`.

**Scoped ordinals** are declared as an extension of the shared base grammar rather than a replacement. Every base reading survives beside the locale's own additions. `tretí pondelok v marci 2020` is the third Monday of March 2020, `posledná streda v mesiaci` the last Wednesday of this month, and `prvý pondelok 2020` and `posledný pondelok 2020` the first and last Mondays of that year.

**Ranges** run `od A do B`, so `od pondelka do piatku` and `od 1. mája do 5. mája` both resolve.

## Weaker provenance

**Every citation into the Slovak Academy's dictionary portal is unverified here.** The determiner paradigms, the unit-noun paradigms, the hour-ordinal table, the day-ordinal table and both era files are attributed to `slovnik.juls.savba.sk`: the Jazykovedný ústav Ľ. Štúra collection. The right authority for all of them. None of those locators is checked. Treat the attributions as unchecked rather than as absent evidence. The surfaces themselves are ordinary Slovak and several are corroborated by CLDR.

**The preposition `v`.** Its file cites the English Wiktionary entry for `v`, Slovak section, glossed "in". That section carries an alternative form, an etymology, a pronunciation and a preposition heading with a definition-requested marker in place of any sense. The gloss "in, inside, at" belongs to the Slovene section immediately below it. The Slovak Wikislovník page of the same name is the article for the Latin letter.

Neither supports the citation. The surface is not in doubt. The locator is wrong on both wiktionaries.

**`ráno`.** Its file records that neither Wiktionary carries a Slovak `ráno` (the English entry has a Czech section only, and Wikislovník has no page) and falls back on the CLDR chart, whose `sk` row spells the morning band with this exact surface. Both halves of that hold.

**The oblique weekday and month forms** carry no citation. The nominatives and the format genitives are traceable to CLDR. But nothing on file says which case `stredu` or `januári` is meant to serve, or whether the set shipped for each word is complete.

**`štvrťrok` and `kvartál`** ship as unqualified synonyms with no source distinguishing register, the same pair and the same silence the Bulgarian, Czech and Slovenian pages record for their own two quarter words.

## What refuses

**Part of the fractional clock.** `pol deviatej` is 08:30 and `štvrť na deväť` is 08:15, because `pol` and `štvrť` stay words for the clock. The three-quarter `tri štvrte na deväť` and the minute-counted `päť minút po deviatej` return nothing. `pol hodiny` and `štvrť hodiny` reach the duration reader through the quantifier table and come back as thirty and fifteen minutes.

**A century before the era.** `20. storočie pred n. l.` does not return a span two thousand years before the era. It is read as a twenty-century offset back from the anchor and returns the years 17 to 117, with the era marker stranded. The counted phrasing `20 storočí pred naším letopočtom` refuses outright, which is the safer of the two behaviours. `v 20. storočí pred n. l.` returns the twentieth century of the common era and strands the marker.

**Night.** The CLDR 47 `sk` day-period chart gives `v noci` for the night band. No night day part ships. `v noci` returns nothing and `dnes v noci` returns the whole of today with `v noci` stranded. `dopoludnia` has the converse problem. It is a meridiem cue but not a day part. `dnes dopoludnia` returns the whole day and strands the word. Czech, Polish and Welsh share the shape. A morning day part and no night one.

**A leading preposition on the year and the period.** `v roku 2020`, `v minulom týždni`, `v tomto týždni` and `v minulom roku` return their span with `v` left in the remainder, as do `cez víkend` and `na jar`. `v lete` reads whole.

**The final day of a month.** `prvý deň mája` resolves, because `ORD UNIT MONTH` is declared. `posledný deň mája` does not, because no `ordlast UNIT MONTH` order is. Yesterday comes back instead, with `mája` stranded.

**`až` as a range word.** `od 1. mája do 5. mája` resolves and `1. máj až 5. máj` does not: `až` is in no vocabulary file. The first date is returned alone and the rest of the range is stranded.

## Open questions for a native speaker

1. Is `o 9 hodín` nine o'clock or nine hours ahead? The hour noun's genitive plural is in the clock vocabulary. It reads as the clock, while the two-to-four form takes the offset: `o 2 hodiny` is two hours ahead and `o 9 hodín` is 09:00. The same construction therefore splits on the numeral's grammar alone, and the minute counterpart `o 9 minút` takes the offset reading throughout.

2. Is an ordinal-aware toward-hour construction worth building for `pol deviatej`, and does the quarter (`štvrť na deväť`) take the accusative after `na` as its only linking grammar?

3. What case do the shipped oblique weekday and month forms mark, and is the set complete for each word?

4. Are `štvrťrok` and `kvartál` interchangeable for a calendar quarter, or does one belong to fiscal usage?

5. Is `v noci` the right single surface for the night band, or does the locative phrase need a nominal partner?

## Known limits

Each limit below has an open issue and a strict `xfail` test that fails when the limit is fixed.

- [#1190](https://github.com/TigreGotico/chronologia/issues/1190): pl, cs, sk, bg, hr: the preposition and the year noun stay in the remainder ("w 2024 roku", "2024 година")

- [#1221](https://github.com/TigreGotico/chronologia/issues/1221): ru, cs, sk, pl, uk: a half-hour or quarter clock followed by another word loses its clock

- [#1227](https://github.com/TigreGotico/chronologia/issues/1227): sk: "o prvej" before a noun reads 01:00

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("sk")
    True
    >>> span, rest = extract_timespan('pol deviatej', "sk", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T08:30:00', '')
    >>> span, rest = extract_timespan('o deviatej večer', "sk", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T21:00:00', '')
    >>> span, rest = extract_timespan('o deviatej ráno', "sk", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T09:00:00', '')
    >>> span, rest = extract_timespan('štvrť na deväť', "sk", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T08:15:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('v 20 storočí', "sk", anchor) is None
    True
    >>> extract_timespan('v päť storočí', "sk", anchor) is None
    True
    >>> extract_timespan('päť storočí', "sk", anchor) is None
    True
    >>> extract_timespan('päť minút po deviatej', "sk", anchor) is None
    True
    >>> extract_timespan('20 storočí pred naším letopočtom', "sk", anchor) is None
    True
    >>> extract_timespan('v noci', "sk", anchor) is None
    True

---
[← Serbian](sr.md) · [Home](../index.md) · [Slovenian →](sl.md)
