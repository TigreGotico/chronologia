# Arabic (`ar`)

<!-- agent-hint
covers: where each construction of the Arabic locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/ar/lang.json, chronologia/locale/ar/*.voc, chronologia/extract/numlayer.py:NUMTAG_LANGS, test/nl_corpus_ar/, test/test_xfail_open_issues_*.py
generated: no
verify: .venv/bin/python -m doctest docs/languages/ar.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/ar.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Arabic (`ar`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

The week starts on Saturday and the weekend is Friday and Saturday. That is set in `lang.json` as `week_start: saturday` with `weekend_start: 4`. It is the first thing to know because it changes what "next week" and "the weekend" mean before any vocabulary is consulted.

The second is that Arabic is postpositional for its relative determiners (`الأسبوع القادم`, the week the coming) so the locale sets `marker_position: post`, while the offset markers `قبل` and `بعد` lead their counts.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('الأسبوع القادم', "ar", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-07-01T00:00:00', '')

## What ships

**Weekdays and months** ship wide and abbreviated, with no recorded source. Both month naming conventions ship together: the borrowed set (`يناير`, `أكتوبر`) and the Levantine set (`كانون الثاني`, `تشرين الأول`) so a text using either is read.

**The date line** is little-endian: `3 أكتوبر 1990`, with or without a linking `من`.

**The Islamic civil calendar** ships its own month names alongside the Gregorian ones, so `15 رمضان 1440` resolves to its Gregorian day.

**Relative offsets** are `قبل` and `منذ` for the past and `بعد` and `خلال` for the future, in either order relative to the count.

**The dual is present in the vocabulary.** Arabic marks "exactly two" with a distinct dual form rather than the plural. The locale ships dual files for the day, hour, minute and week (`يومان`, `يومين` and their siblings) beside the singular and the plural.

**The clock** ships the hour as a feminine ordinal after `الساعة`, plus quarter and half fractions. The two directions are `و` for the additive form and `إلا` for the subtractive one, the latter in both its hamza spellings. `منتصف الليل` and `نصف الليل` are midnight and `الظهر` is noon. A midnight-crossing night meridiem `ليلا` ships alongside the plain AM and PM ones.

**Day parts** are the one vocabulary in this locale with an explicitly recorded human check: the surfaces are marked as confirmed by a named native speaker in the project's own issue tracker. The band boundaries are cited to the Unicode CLDR 47 day-period rules for `ar`. Four bands ship: `الصباح`, `بعد الظهر`, `المساء` and `الليل`.

`الظهيرة` is *not* listed as an afternoon surface. It names midday, and midday is bound as the noon clock landmark, so as a band surface it would never fire: the noon reading wins. Only `بعد الظهر`, literally "after noon", names the afternoon band.

**Ranges** are `من … إلى …` and `بين … و …`. The from-and-to pair is cited to Wright's *A Grammar of the Arabic Language* and to Badawi, Carter and Gully's *Modern Written Arabic*, both for `من` as the point of origin and `إلى` as the limit reached. `بين` is cited to the same two grammars for governing two coordinated terms joined by `و`. The vocabulary notes that `من` is written as a free word and never a proclitic. It tokenizes on its own. That `إلى` ships in its hamza-less spelling `الى` too, a ubiquitous orthographic variant.

**Quarters, ISO weeks, decades and eras.** `الربع الأول 2020`, `الأسبوع 12`, the spelled decade `الثمانينات`, `44 ق.م` and `1990 م` all resolve, along with a before-present marker. The half-year is `النصف الأول من 2020`, and the vocabulary records that the attested surface carries the definite article, citing *Lisān al-ʿArab* under the root ن‑ص‑ف for `نصف` as one of two equal parts.

**Fuzzy month parts** are `أوائل`, `منتصف` and `أواخر`.

## Weaker provenance

The weekday and month names, the clock words, the seasons and the holiday vocabulary carry no recorded source. The locale sets `hemisphere` to null.

## What refuses

**The half-past clock form.** `الثامنة والنصف` returns nothing, glued or spaced as `الثامنة و النصف`.

**`الليلة` for tonight.** The night band ships as `الليل` and `ليلة`. The definite `الليلة` returns nothing.

## Open questions for a native speaker

1. Which construction should read the dual, and in which positions? `قبل يومين` and `أسبوعين` are the everyday forms and neither resolves.
2. Should the tokenizer split a proclitic `و`, and would splitting it break anything, words that legitimately begin with `و` are the obvious risk.
3. Do the two month-naming conventions ever collide in a way that reads the wrong month, given that both sets ship at once?
4. Is `الثامنة والنصف` the ordinary way to say half past eight, and what should the clock read for it?

## Known limits

Each line is an open issue with a strict `xfail` test for this language. The most common cases come first. An example shows what the library gives on the test's own anchor date.

- A clock form reads wrong or not at all. Example: `الساعة الثالثة والثلث` gives 2026-07-18 03:20, where the test expects 2026-07-17 15:20. [#1032](https://github.com/TigreGotico/chronologia/issues/1032)

- A spelled clock keeps the written hour, where its digit twin takes the next reading. Example: `الساعة السادسة والنصف` gives 2017-06-28 06:30, where the test expects 2017-06-27 18:30. [#1072](https://github.com/TigreGotico/chronologia/issues/1072)

- The dual and a count after the unit give no length. Example: `شهرين` gives no reading. [#1209](https://github.com/TigreGotico/chronologia/issues/1209)

- A spelled count of seconds gives no length, and a fused `و` before a count ends the length early. Example: `ثلاثون ثانية` gives no reading. [#1236](https://github.com/TigreGotico/chronologia/issues/1236)

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("ar")
    True
    >>> span, rest = extract_timespan('الأسبوع القادم', "ar", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-07-01T00:00:00', '')
    >>> span, rest = extract_timespan('كانون الثاني', "ar", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2018-01-01T00:00:00', '')
    >>> span, rest = extract_timespan('تشرين الأول', "ar", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-10-01T00:00:00', '')
    >>> span, rest = extract_timespan('3 أكتوبر 1990', "ar", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('1990-10-03T00:00:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('الثامنة والنصف', "ar", anchor) is None
    True
    >>> extract_timespan('الليلة', "ar", anchor) is None
    True

---
[← Albanian](sq.md) · [Home](../index.md) · [Aragonese →](an.md)
