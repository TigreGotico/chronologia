# Belarusian (`be`)

<!-- agent-hint
covers: where each construction of the Belarusian locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/be/lang.json, chronologia/locale/be/*.voc, chronologia/extract/numfold_be.py, test/nl_corpus_be/
generated: no
verify: .venv/bin/python -m doctest docs/languages/be.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/be.md 'без@19:40' 'пяць хвілін на трэцюю@02:05'
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Belarusian (`be`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by its own `numfold_be` module in `chronologia/extract/`.

Belarusian looks like Russian and is not Russian. The two words this locale would most likely have got wrong by assuming otherwise are the two most load-bearing ones. The minute is `хвіліна`, not the Russian cognate `мінута`. The hour is `гадзіна`, not `час`: in the hour sense `час` is a documented dialectal Russianism, and it is also the ordinary word for "time". Both are confirmed directly from the CLDR display names for the language, not inferred from the family. Nothing in this locale was produced by translating the Russian vocabulary, and a test pins Russian wording as unreadable so it cannot creep back in.

The clock is the other thing worth knowing up front. Belarusian names the *coming* hour throughout, like Russian, but the grammar of it splits at the half hour in a way Russian's does not.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('палова на пятую', "be", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T04:30:00', '')

## What ships

**Weekdays and months** come from Unicode CLDR 47, `cldr-dates-full/main/be/ca-gregorian.json`. Months ship in both widths, because they do different jobs: the stand-alone nominative names a bare month. The format genitive is what follows a day number: `25 сакавіка`. Weekdays ship the wide name plus the genitive a date phrase takes (`у панядзелак`, `да панядзелка`). The date line is `d MMMM y 'г'.`, day then genitive month then year with the standard abbreviation `г.`, which is why the year word accepts `г` alongside `год`, `года` and `годзе`.

**Units** are CLDR display names with the four plural forms CLDR's `relativeTimePattern-count-*` keys give. Those are the real declined forms in context rather than a paradigm reconstructed from a table. Day is `дзень / дні / дзён / дня`, week `тыдзень / тыдні / тыдняў / тыдня`, and so on. The century, decade and the seasons are not in CLDR's field set and come instead from the Тлумачальны слоўнік беларускай мовы, the explanatory dictionary of the Yakub Kolas Institute of Linguistics.

**Relative offsets** are CLDR's own patterns: `{0} X таму` for the past, `праз {0} X` for the future. The deictic days (`пазаўчора`, `учора`, `сёння`, `заўтра`, `паслязаўтра`) are the CLDR relative-type entries for the day field.

Year has two irregular single words rather than a periphrasis: `летась` for last year and `сёлета` for this year, which CLDR gives as the year field's relative-type--1 and relative-type-0. The fold in `chronologia/extract/numfold_be.py` rewrites each into the determiner and noun pair the resolver reads, because Wiktionary's own entries for both gloss them as exactly that. Every other unit uses the periphrastic `у мінулым месяцы`, `на мінулым тыдні` phrasing, so `мінулы`, `гэты` and `наступны` ship in the full adjectival paradigm those phrases put them in rather than in the citation form alone.

**The clock, first half.** From minute zero to thirty, Belarusian uses `на` plus the accusative ordinal of the coming hour: `палова на пятую` is 04:30, `чвэрць на сёмую` is 06:15. This is structurally unlike Russian, which uses a bare genitive ordinal in the same slot with no preposition. The source is Вінцук Вячорка's "Каторая гадзіна?" column for Радыё Свабода, which states the rule explicitly and gives the worked examples.

**The clock, second half.** From thirty to sixty, the minutes are subtracted from the coming hour with `без` (or, with a fraction, `за`): `без дзесяці першая` is 12:50, `за квадранец восьмая` is 07:45, `без чвэрці адзінаццаць` is 10:45. Two independent sources carry worked examples here, Вячорка's column, and the Тлумачальны слоўнік under `чвэрць` ("Гадзіннік паказваў без чвэрці адзінаццаць") and under `без` ("Роўна без дваццаці восем вечара" = 19:40). The genitive minute counts that follow the direction word ship as their own small vocabulary, bound only in that position.

**The half and quarter hour** are dictionary-sourced. `палова` and `палавіна` come from the Тлумачальны слоўнік sense "the moment corresponding to the middle of some hour", with its own worked examples `палову пятай` (04:30) and `палавіна восьмай вечара` (19:30). `чвэрць` is the same dictionary's first sense, "a fourth part of an hour (fifteen minutes)".

**Naming the hour in answer to "when?"** uses `а` or `аб` with the locative ordinal (`а другой`, `аб адзінаццатай`) and switches to `у` before a minute count. That distinction is Вячорка's, including his own explicit note about the exception. `апоўдні` and `апоўначы` come from the dictionary.

**Numerals** are extracted from Wiktionary's `Module:number list/data/be`, the Lua data table its own numeral templates render from, giving matched cardinal and ordinal pairs from zero through one hundred.

**Markers** outside the CLDR relative-time set are dictionary entries throughout: `пасля` (after, governing the genitive), `да` and `перад` (before), `паміж` / `між` (between), `з` / `ад` (from, since), `кожны` (every, with the dictionary's own examples `Аўтобус ходзіць кожныя пяць мінут` and `Кожны дзень`), `апошні` for the last weekday of a month.

## Weaker provenance

**`квадранец`**, the older Latinism for a quarter hour, is thinner than `чвэрць` beside it. `чвэрць` is a numbered dictionary sense with a worked clock example. `квадранец` rests on Вячорка's column, which attests it with a literary citation from Цішка Гартны. It is not a dictionary-only ghost word, but it is one source and one literary attestation rather than a lexicographic entry.

**The first-half `на` construction** has one source. Вячорка states the rule and gives examples. The dictionary corroborates the second-half construction beside it. But nothing independent was found for `на` plus the accusative ordinal specifically.

**`травень` for May** does not ship. Wiktionary lists it and `май` as mutual synonyms with no archaic or dialectal label on either in Belarusian (unlike Russian, where the same dictionary explicitly tags the equivalent as archaic) so it is live vocabulary. But CLDR 47 gives `май` as the sole calendar name in both widths, and only that ships. `25 траўня` returns nothing.

## What refuses

The refusals below are each pinned by a test, so that closing one requires deliberately revisiting the decision.

**Day-part bands.** `раніцай`, `удзень`, `вечарам`, `ноччу` name no time at all, and `сёння раніцай` resolves the day with the day part left unread. This is the finding, not an omission: CLDR has no `dayPeriodRuleSet` entry for Belarusian, so the boundary hours that would turn `раніца` into a clock band were never defined for the language. Inventing them is exactly what the pin prevents.

**A spelled minute count in the first half of the hour.** Вячорка's rule covers `пяць хвілін на трэцюю` (02:05) as well as the fraction forms. But the clock resolver has no additive toward-hour branch for a numeric minute. Its only toward-hour path is the fixed fraction and its only numeric-minute path subtracts. Reading it anyway would return 03:00, an hour and five minutes wrong. The fraction forms of the same idiom, `палова на трэцюю` and `чвэрць на трэцюю`, do ship.

**`да` as a clock direction.** Вячорка lists `да` alongside `без` and `за` for the second half of the hour. It is deliberately absent. `да` is also the ordinary preposition for every range end and deadline in the language (`да пяці гадзін`, `з 5 да 12 ліпеня`) and reading it as a clock direction would turn those into clock times. `чвэрць да шостай` returns nothing, `без чвэрці шостая` and `за чвэрць шостая` both give 05:45.

**The announcement register.** `другая гадзіна пяць хвілін` and `шаснаццатая гадзіна трыццаць хвілін` are real formal Belarusian. But no construction order binds a trailing minute count onto a named hour. The minutes would be silently dropped and the hour returned on the dot. The digit form of the same time is what reads.

**Century and millennium counts.** `5 стагоддзяў таму`, `праз 10 стагоддзяў` and anything with `тысячагоддзе` return nothing: CLDR carries no relative-time patterns for those fields in Belarusian, so their plural forms are unsourced. The ordinal century, sourced as an ordinary neuter noun, does read: `20-е стагоддзе` gives the twentieth century.

**Compound ordinals past a hundred.** The numeral module tabulates them through one hundred. Past that the pattern was not separately verified, so it is not extrapolated.

**`залетась` and `пазалетась`.** Wiktionary lists both as derived from `летась` and glosses both "two years ago": one gloss for two distinct words, which cannot both be right. No source consulted separates them.

**A relative hour period.** CLDR gives `у гэту гадзіну` as the hour field's relative-type-0, but the resolver has no sub-day relative period at all. The same path refuses the English "this hour". Not a gap in this locale.

## Open questions for a native speaker

1. Is `травень` still current for the calendar month, as against the seasonal or poetic sense? If so it could ship as a recognition-only synonym.

2. What distinguishes `залетась` from `пазалетась`? Both are glossed "two years ago" and they cannot name the same year.

3. Does speech still use `квадранец`, or does it survive only in literary writing?

4. Does an independent source corroborate the `на` plus accusative ordinal construction for the first half of the hour?

5. Are there attested boundary hours for `раніца`, `дзень`, `вечар` and `ноч`, or is the absence of a CLDR rule set a genuine reflection of the language?

6. What are the plural forms of `стагоддзе` and `тысячагоддзе` in counted relative-time phrases?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("be")
    False
    >>> span, rest = extract_timespan('палова на пятую', "be", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T04:30:00', '')
    >>> span, rest = extract_timespan('чвэрць на сёмую', "be", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T06:15:00', '')
    >>> span, rest = extract_timespan('без дзесяці першая', "be", datetime(2017, 6, 27, 12, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T12:50:00', '')
    >>> span, rest = extract_timespan('за квадранец восьмая', "be", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T07:45:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('25 траўня', "be", anchor) is None
    True
    >>> extract_timespan('чвэрць да шостай', "be", anchor) is None
    True
    >>> extract_timespan('тысячагоддзе', "be", anchor) is None
    True

---
[← Basque](eu.md) · [Home](../index.md) · [Bulgarian →](bg.md)
