# Kabyle (`kab`) and the Amazigh calendar

<!-- agent-hint
covers: where each construction of the Kabyle locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/kab/lang.json, chronologia/locale/kab/*.voc, chronologia/extract/numlayer.py:NUMTAG_LANGS, test/nl_corpus_kab/, test/test_xfail_open_issues_*.py
generated: no
verify: .venv/bin/python -m doctest docs/languages/kab.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/kab.md && .venv/bin/python -c 'exec("import re,sys\nfrom datetime import datetime\nimport chronologia as C\ndef mins(d):\n    return (\"%.6f\" % (d.total_seconds() / 60)).rstrip(\"0\").rstrip(\".\")\ndef rem(r):\n    return \" and \\x60%s\\x60 left over\" % r if r else \"\"\ndef out(rd, tx, lg, an):\n    f = getattr(C, rd)\n    r = f(tx, lg, anchor=an) if rd == \"extract_duration\" else f(tx, lg, an)\n    if rd == \"extract_timespan\":\n        if r is None: return \"no reading\"\n        return \"%s to %s%s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), r.span.end.datetime().strftime(\"%Y-%m-%d %H:%M\"), rem(r.remainder))\n    if rd == \"extract_duration\":\n        if r is None: return \"no length\"\n        return \"a length of %s min%s\" % (mins(r.duration), rem(r.remainder))\n    if rd == \"extract_event\":\n        if r is None: return \"no event\"\n        return \"start %s, length %s, %s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), \"none\" if r.duration is None else mins(r.duration) + \" min\", \"summary \\x60%s\\x60\" % r.summary if r.summary else \"no summary\")\n    if r is None: return \"no rule\"\n    return \"the rule \\x60%s\\x60%s\" % (r.recurrence.to_string(), rem(r.remainder))\n\np=sys.argv[1]\nt=open(p).read()\nm=re.search(r\"\\n## Known limits\\n(.*?)(?=\\n---\\n|\\Z)\",t,re.S)\nbad=0\nn=0\ntot=0\nfor ln in (m[1].split(\"\\n\") if m else []):\n    if \"Example (\" not in ln: continue\n    tot+=1\n    g=re.search(r\"Example \\(reader \\x60(\\w+)\\x60, lang \\x60([\\w-]+)\\x60, anchor (\\d{4}-\\d\\d-\\d\\d \\d\\d:\\d\\d)\\): \\x60([^\\x60]+)\\x60 gives (.+?)\\. \\[#\\d+\\]\",ln)\n    if not g:\n        bad=1\n        print(\"example line does not parse:\",ln[:80])\n        continue\n    n+=1\n    o=out(g[1],g[4],g[2],datetime.strptime(g[3],\"%Y-%m-%d %H:%M\"))\n    if o!=g[5]:\n        bad=1\n        print(\"limit differs\",g[4],\"|\",g[5],\"|\",o)\nprint(\"known limits checked:\",n,\"of\",tot)\nsys.exit(bad)\n")' docs/languages/kab.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Kabyle (`kab`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

The Kabyle locale and the Amazigh calendar are two separate things that share one set of month names, and keeping them separate is the point of this page. `chronologia/locale/kab` reads ordinary civil dates in Kabyle, using the Berber month names as the names of the **Gregorian** months. That is correct, because that is what Kabyle daily speech does. The `berber` calendar in `chronologia/calendars.py` is a different object: the Julian calendar under a shifted era, reachable through the calendar API rather than through the locale.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('duǧembeṛ 2020', "kab", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2020-12-01T00:00:00', '')

## The calendar

The Amazigh calendar in modern use is structurally the Julian calendar (same twelve months, same `year % 4 == 0` leap rule, same 1 January new year) with the months given Berber names and the year counted from a different era. The +950 era offset, which makes the agricultural year 2976 equal to 2026, was fixed in 1968 by the Académie Berbère, who chose it to commemorate the accession of Shoshenq I, the Berber pharaoh of Egypt's twenty-second dynasty, conventionally dated 950 BC. It is a documented twentieth-century symbolic choice, not an ancient reckoning: no earlier era count for this calendar is attested. The implementation says so where a reader will find it.

Because the offset is a pure additive year shift onto the existing Julian arithmetic, 1 Yennayer falls on 1 January Julian every year, which is 14 January Gregorian across the 1900-2099 window. The gold check the implementation states is 1 Yennayer 2976 = Julian 2026-01-01 = Gregorian 2026-01-14.

**The year-end leap day is not encoded.** Popular description often says the intercalary day is appended at the end of the year, after Dujembeṛ, rather than sitting inside February as the Julian layout puts it. That claim traces to a single source with no corroborating primary reference, and moving the leap day within the year changes neither which years are leap nor the total day count. It cannot be checked against any dated event. The plain Julian placement is what ships, and the alternative is recorded as an open question rather than as arithmetic.

**The civil Yennayer holidays are deliberately not calendar output.** Algeria's Yennayer public holiday is a fixed civil date, 12 January Gregorian, set by presidential decree in December 2017 and first observed in 2018. That is two days *earlier* than the 14 January that the Julian-era arithmetic produces for the same era year. Morocco's holiday became a paid national holiday by the May 2023 royal decree, effective from 2024, at a fixed 13 January. Neither is derived from, or reconcilable with, the arithmetic. Both live in the civil-holidays layer, `holiday_data/dz.tab` and `holiday_data/ma.tab`, and never in the calendar function. The popular folk justification for Algeria's 12 January, thirteen days of drift back from 1 January, is arithmetically inconsistent, since thirteen days after 1 January is the fourteenth. It is not encoded in any form.

## The locale

**Month names** follow the glibc `kab_DZ` locale definition: yennayer, fuṛar, meɣres, yebrir, mayyu, yunyu, yulyu, ɣuct, ctembeṛ, tubeṛ, wambeṛ, dujembeṛ. They ship twice. Once as the Gregorian month names Kabyle civil dates use, and once in the `month_berber_*` slots the calendar system reads.

CLDR disagrees with glibc on the last two months, giving `nunembeṛ` and `duǧembeṛ` where glibc has `wambeṛ` and `dujembeṛ`. Months one through ten agree. The glibc spellings are what ship, for consistency across the repository. The CLDR forms are not added as alternates without a native reader's judgement on which are current.

**`Awussu` as an alternate for August** is not shipped. It appears in one calendar reference as "Ghust ou Awussu" and nowhere else consulted, and a single mention is not corroboration.

**No Tifinagh month names ship.** No attestation for them was found, and a transliteration is not an attestation.

**The working week** starts on Monday with a weekend beginning on Friday, which is what `weekend_start` encodes.

## What this page cannot tell you

Most Kabyle vocabulary files carry no source comment. The month files for January to October cite Unicode CLDR 47. Several clock-word files, the three day parts, the hour unit and the weekend noun record a check by a native Kabyle speaker. The weekday names and the other markers are not individually sourced. This page does not claim provenance for them that the files do not carry.

## Open questions for a native speaker

1. Are `wambeṛ` and `dujembeṛ` or `nunembeṛ` and `duǧembeṛ` the living forms, and should both pairs be accepted?
2. Is the leap day placed at the end of the year in practice, or inside February?
3. Is `Awussu` a current alternate for August?
4. Which of the Kabyle temporal words the locale ships are standard, and which are regional?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia import CALENDARS
    >>> from chronologia.extract.numlayer import reads
    >>> reads("kab")
    True
    >>> span, rest = extract_timespan('duǧembeṛ 2020', "kab", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2020-12-01T00:00:00', '')
    >>> span, rest = extract_timespan('wambeṛ 2020', "kab", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2020-11-01T00:00:00', '')
    >>> span, rest = extract_timespan('yennayer 2020', "kab", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2020-01-01T00:00:00', '')
    >>> str(CALENDARS["berber"].date(2976, 1, 1))
    '2026-01-14T00:00:00'

## Known limits

Each line is an open issue with a strict `xfail` test for this language. The lines are grouped by topic. An example names the reader that produced it, the language and the anchor date, and shows what that reader gives on the test's own phrase.

- A weekday range or list followed by a clock drops the clock or picks a past day. Example (reader `extract_timespan`, lang `kab`, anchor 2017-06-27 13:04): `seg letnayen ar lǧemɛa ɣef tesɛa n ṣṣbeḥ, smektay-iyi ad ẓreɣ imaylen-iw` gives 2017-06-26 00:00 to 2017-06-27 13:04 and `ar lǧemɛa ɣef tesɛa n ṣṣbeḥ, smektay-iyi ad ẓreɣ imaylen-iw` left over. [#1010](https://github.com/TigreGotico/chronologia/issues/1010)

- A half past the hour loses the half. [#1021](https://github.com/TigreGotico/chronologia/issues/1021)

- A day word or a counted offset gives no reading. Example (reader `extract_timespan`, lang `kab`, anchor 2017-06-27 13:04): `deg 3 wussan` gives no reading. [#992](https://github.com/TigreGotico/chronologia/issues/992)

- A word for next or last beside a season, month or week stays in the remainder. Example (reader `extract_timespan`, lang `kab`, anchor 2017-06-27 13:04): `tafsut i d-iteddun` gives 2017-03-01 00:00 to 2017-06-01 00:00 and `i d-iteddun` left over. [#993](https://github.com/TigreGotico/chronologia/issues/993)

- The last weekday of a month gives the whole month, or the weekday alone. Example (reader `extract_timespan`, lang `kab`, anchor 2017-06-27 13:04): `letnayen aneggaru n meɣres` gives 2017-07-03 00:00 to 2017-07-04 00:00 and `aneggaru n meɣres` left over. [#1005](https://github.com/TigreGotico/chronologia/issues/1005)

- A compound number loses a part. Example (reader `extract_duration`, lang `kab`, anchor 2017-06-27 13:04): `mraw d sin n tesdidin` gives a length of 2 min and `mraw d` left over. [#1210](https://github.com/TigreGotico/chronologia/issues/1210)

- Some number words give no length. Example (reader `extract_duration`, lang `kab`, anchor 2017-06-27 13:04): `tlatin tasint` gives no length. [#1211](https://github.com/TigreGotico/chronologia/issues/1211)

- The spelled number twelve reads only the tens. Example (reader `extract_duration`, lang `kab`, anchor 2017-06-27 13:04): `sin mraw n tesdidin` gives a length of 10 min and `sin` left over. [#1239](https://github.com/TigreGotico/chronologia/issues/1239)

---
[← Italian](it.md) · [Home](../index.md) · [Korean →](ko.md)
