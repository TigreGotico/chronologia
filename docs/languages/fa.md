# Persian (`fa`)

<!-- agent-hint
covers: where each construction of the Persian locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/fa/lang.json, chronologia/locale/fa/*.voc, chronologia/extract/numlayer.py:NUMTAG_LANGS, test/nl_corpus_fa/, test/test_xfail_open_issues_*.py
generated: no
verify: .venv/bin/python -m doctest docs/languages/fa.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/fa.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Persian (`fa`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

Persian ships two independent calendars for the same vocabulary of markers, ranges and offsets. The split between them is the first thing to understand. `year_ref` defaults to the Solar Hijri (Jalali) calendar for a bare four-digit year in the range 1200-1500 (the ordinary range of a contemporary Persian date, such as `۱۴۰۳`) and falls through to Gregorian outside that window or when the explicit `میلادی` ("Gregorian/AD") marker is present. `calendar_date` reads Gregorian month names. `nongregorian_date` reads the Solar Hijri month names against the same day/month/year orders. So `۱۵ اسفند ۱۴۰۲` and `15 مارس 2024` both resolve, through two different grammars sharing one vocabulary shape.

The second thing to know is the direction of the postpositional markers. `marker_position` is set to `post`. A determiner such as `آینده` ("next") or `گذشته` ("last/past") follows the noun it modifies rather than leading it, matching ordinary Persian word order: `هفتهٔ آینده`, the week the coming, not a leading "next week".

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('۱۵ اسفند ۱۴۰۲', "fa", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2024-03-05T00:00:00', '')

## What ships

**Weekdays and months** ship without a recorded source. The Gregorian month names are French-derived transliterations (`ژانویه`, `فوریه` …), the ordinary form in Persian print and broadcast for a Gregorian date. The Solar Hijri months (`فروردین` through `اسفند`) are a separate twelve-entry vocabulary keyed `month_solar_hijri_arithmetic_N`, read only through the `nongregorian_date` construction.

**The date line** is little-endian for both calendars: `DAY MONTH YEAR?` or `MONTH DAY? YEAR?`, with the year optional in either order.

**Relative offsets** are `قبل از`/`پیش از`/`قبل` for the past and `بعد از`/ `پس از`/`بعد` for the future, trailing the count in the single fixed order `NUM UNIT MARKER`.

**Ranges** are `از … تا …` for the bounded interval and `بین …` / `میان …` for the coordinated pair. `از` is cited to the Dehkhoda Dictionary and the Sokhan Comprehensive Dictionary, s.v. `از`, as the marker of the origin point in time or place, correlative with `تا` for the terminal point. The vocabulary's own comment gives `از ۵ ژوئن تا ۱۲ ژوئن` as the worked example. `بین` and `میان` are cited to the same two dictionaries as governing two coordinated terms joined by `و`, the same shape as Arabic `بين … و …`. `از` is also the `since`-marker, the open reading of the same starting point. The vocabulary notes both roles trace to one entry.

**The locative prepositions** `در` ("in", governing a month) and `در` again as `marker_of` are both cited to the Persian Wiktionary entry for `در`.

**Half and quarter quantifiers** ship as general-purpose fractions (`نیم` for one half, `ربع` for one quarter) and resolve `نیم ساعت` to a thirty-minute duration and `ربع ساعت` to a fifteen-minute one. Wiktionary's entry for `ربع` glosses it "quarter, one-fourth" and gives `دو و ربع` ("two and a quarter") as its own worked example for quarter-past-two on a clock, confirming the fraction is the same word Persian speakers use for a spoken clock time, not only a duration word.

**The clock**, despite that, ships only two shapes: a bare digit clock (`۱۵:۳۰`, `15:30`) and the marked hour `ساعت N` / `راس ساعت N`, plus the two landmarks `ظهر` (noon) and `نیمه‌شب` (midnight). There is no `دو و ربع`-style spelled fractional clock construction wired into `clock_time`: see Weaker provenance.

**Day parts** take their boundaries from the Unicode CLDR 47 day-period chart for `fa`: `night2` `[00:00, 01:00)`, `morning1` `[01:00, 04:00)`, `morning2` `[04:00, 12:00)`, `afternoon1` `[12:00, 13:00)`, `afternoon2` `[13:00, 19:00)`, `night1` `[19:00, 24:00)`. Three surfaces ship, each merging adjacent CLDR bands into the single vocabulary a Persian speaker actually reaches for: `صبح` (morning) for `morning2`, cited to CLDR `fa` `morning2` and to the Persian Wiktionary entry for `صبح`, `بعدازظهر`/`عصر` (afternoon) for the combined `afternoon1`+`afternoon2` span, cited to CLDR `fa` `afternoon1`/`afternoon2`, and `شب` (night) for `night1`, cited to CLDR `fa` `night1` and Wiktionary's entry for `شب`. The CLDR `morning1` (01:00-04:00) and `night2` (00:00-01:00) bands have no shipped surface at all. No Persian word in this vocabulary names the small hours between midnight and four as their own band.

**Fuzzy period parts** are `اوایل`/`ابتدای`/`ابتدا` (early), `اواسط`/`وسط`/ `میانه` (mid), and `اواخر`/`آخر`/`پایان` (late).

**Quarters, ISO weeks, century and decade** resolve through `سه‌ماهه`/`فصل` (quarter word), `هفته` (week number), `قرن` (century) and `دهه` (decade). `قرن` and `دهه` both carry their own vocabulary comments: `قرن` as the standard dictionary word for "century", and `دهه` as derived from `ده` ("ten") and the standard word for a ten-year span.

**Seasons** are cited to the Dehkhoda Dictionary and the Sokhan Comprehensive Dictionary, one entry each: `بهار` (spring), `تابستان` (summer), `پاییز`/ `پائیز` (fall, both hamza spellings listed since the tokenizer performs no normalisation), and `زمستان` (winter).

**The weekend** is `آخر هفته`/`آخرهفته`, and `week_start` is set to Saturday with `weekend_start: 3`: Thursday and Friday, the ordinary Iranian weekend, rather than the Friday-Saturday weekend some other Persian-speaking regions keep.

## Weaker provenance

The weekday names and the Gregorian month names carry no recorded source. `hemisphere` is set to null in the locale's conventions, so seasonal resolution does not lean on a fixed hemisphere assumption.

The short numeric CLDR date pattern for `fa` (`y/M/d`) orders year first, while the long and full CLDR patterns (`d MMMM y`) order day first, matching `dmy: true` in the locale's conventions. The two CLDR patterns disagree with each other. This page follows the spelled-date pattern, which is what the locale's `calendar_date` construction actually reads, and does not extend the claim to bare numeric input.

## What refuses

**The Solar Hijri year outside its window.** A bare four-digit year below 1200 or above 1500 is read as Gregorian rather than Jalali, by the `calendar_year_range` guard in `lang.json`. A Jalali year outside that window (a distant historical or far-future Persian date) is not reachable through a bare year and needs the explicit calendar's own construction path.

**The small hours as a day part.** `صبح زود` ("early in the morning", literally combining the `morning` surface with `early`) reaches the fuzzy grammar. But nothing names the CLDR `night2`/`morning1` span (00:00-04:00) as its own band. A phrase meaning specifically "the small hours" has no dedicated surface.

## Open questions for a native speaker

1. Should `دو و ربع` / `ساعت سه و نیم`-style spelled fractional clock times be wired into `clock_time`, and does the "count past the hour" reading (Wiktionary's `دو و ربع` = quarter past two) hold for the half-hour form too, or does Persian switch direction the way Russian does?
2. Is Thursday-Friday the weekend to assume for every Persian-speaking region this locale serves, or should the Friday-Saturday convention be configurable?
3. Is there an ordinary Persian surface for the 00:00-04:00 span that the CLDR chart splits into `night2`/`morning1` but this vocabulary does not name at all?
4. Does the Solar Hijri calendar window (1200-1500) need widening for historical or far-future Jalali dates, and if so, by what guard?

## Known limits

Each line is an open issue with a strict `xfail` test for this language. The most common cases come first. An example shows what the library gives on the test's own anchor date.

- Compound numbers lose the tens, and a clock loses the hour or the night. Example: `یک تایمر ده دقیقه‌ای بگذار` gives no reading. [#1018](https://github.com/TigreGotico/chronologia/issues/1018)

- A digit clock written with a space reads only the hour. Example: `در ساعت 10 30` gives 2017-06-27 22:00, where the test expects 2017-06-27 22:30. [#1012](https://github.com/TigreGotico/chronologia/issues/1012)

- A verb prefix reads as a month name, or a weekday reads as another day. Example: `دمای هوا صبح دوشنبه چند درجه می شود` gives 2017-06-27 01:00, where the test expects 2017-07-03. [#989](https://github.com/TigreGotico/chronologia/issues/989)

- The last weekday of a month gives the whole month, or the weekday alone. Example: `آخرین دوشنبه مارس` gives 2018-03-01 00:00, where the test expects 2017-03-27 00:00. [#1005](https://github.com/TigreGotico/chronologia/issues/1005)

- Text that is no date reads as a date, or the wrong reading wins. Example: `یک ساعت و پنجاه و هفت و نیم دقیقه طول می` gives May 2018 with the length words left over, where the test expects no date. [#1035](https://github.com/TigreGotico/chronologia/issues/1035)

- A day word or a counted offset gives no reading. Example: `هفته اول ژوئیه` gives 2017-01-02 00:00, where the test expects 2017-07-03. [#992](https://github.com/TigreGotico/chronologia/issues/992)

- A decimal count gives no length. Example: `7.5 ثانیه` gives no reading. [#1204](https://github.com/TigreGotico/chronologia/issues/1204)

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("fa")
    True
    >>> span, rest = extract_timespan('۱۵ اسفند ۱۴۰۲', "fa", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2024-03-05T00:00:00', '')
    >>> span, rest = extract_timespan('15 مارس 2024', "fa", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2024-03-15T00:00:00', '')
    >>> span, rest = extract_timespan('هفتهٔ آینده', "fa", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-07-01T00:00:00', '')
    >>> span, rest = extract_timespan('از ۵ ژوئن تا ۱۲ ژوئن', "fa", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2018-06-05T00:00:00', '')

---
[← Occitan](oc.md) · [Home](../index.md) · [Polish →](pl.md)
