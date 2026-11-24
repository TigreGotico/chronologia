# Malay (`ms`)

<!-- agent-hint
covers: where each construction of the Malay locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/ms/lang.json, chronologia/locale/ms/*.voc, chronologia/extract/numlayer.py:NUMTAG_LANGS, test/nl_corpus_ms/, test/test_xfail_open_issues_*.py
generated: no
verify: .venv/bin/python -m doctest docs/languages/ms.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/ms.md 'pukul lapan setengah@08:30' 'pukul tujuh setengah@19:30' setengah@02:30 && .venv/bin/python -c 'exec("import re,sys\nfrom datetime import datetime\nimport chronologia as C\ndef mins(d):\n    return \"%g\" % (d.total_seconds() / 60)\ndef rem(r):\n    return \" and \\x60%s\\x60 left over\" % r if r else \"\"\ndef out(rd, tx, lg, an):\n    f = getattr(C, rd)\n    r = f(tx, lg, anchor=an) if rd == \"extract_duration\" else f(tx, lg, an)\n    if rd == \"extract_timespan\":\n        if r is None: return \"no reading\"\n        return \"%s to %s%s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), r.span.end.datetime().strftime(\"%Y-%m-%d %H:%M\"), rem(r.remainder))\n    if rd == \"extract_duration\":\n        if r is None: return \"no length\"\n        return \"a length of %s min%s\" % (mins(r.duration), rem(r.remainder))\n    if rd == \"extract_event\":\n        if r is None: return \"no event\"\n        return \"start %s, length %s, summary \\x60%s\\x60\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), \"none\" if r.duration is None else mins(r.duration) + \" min\", r.summary)\n    if r is None: return \"no rule\"\n    return \"the rule \\x60%s\\x60%s\" % (r.recurrence.to_string(), rem(r.remainder))\n\np=sys.argv[1]\nt=open(p).read()\nm=re.search(r\"\\n## Known limits\\n(.*?)(?=\\n---\\n|\\Z)\",t,re.S)\nbad=0\nn=0\nfor ln in (m[1].split(\"\\n\") if m else []):\n    g=re.search(r\"Example \\(reader \\x60(\\w+)\\x60, lang \\x60([\\w-]+)\\x60, anchor (\\d{4}-\\d\\d-\\d\\d \\d\\d:\\d\\d)\\): \\x60([^\\x60]+)\\x60 gives (.+?)\\. \\[#\\d+\\]\",ln)\n    if not g: continue\n    n+=1\n    o=out(g[1],g[4],g[2],datetime.strptime(g[3],\"%Y-%m-%d %H:%M\"))\n    if o!=g[5]:\n        bad=1\n        print(\"limit differs\",g[4],\"|\",g[5],\"|\",o)\nprint(\"known limits checked:\",n)\nsys.exit(bad)\n")' docs/languages/ms.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Malay (`ms`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

Malay is morphologically light (nouns do not inflect for number, and a weekday, a month and a unit noun all arrive in one shape) so most of this locale is a short list of words rather than a set of paradigms. Almost all of the difficulty is concentrated in one place: how a half hour is said, and which hour it belongs to. That question is open, and the section below states exactly what is known and exactly what is not.

The reference dictionary throughout is *Kamus Dewan*, published by Dewan Bahasa dan Pustaka and searchable through the Pusat Rujukan Persuratan Melayu (PRPM).

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('pukul satu malam', "ms", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T01:00:00', '')

## What ships

**Months and weekdays** are the standard Malaysian forms: `januari` through `disember`, with `mac`, `jun`, `julai` and `ogos` where English has March, June, July and August, `isnin` through `ahad` for the days.

**The weekday classifier.** Malay names a weekday with `hari` in front of it, and *Kamus Dewan* spells the classifier out in its own definitions. Isnin is "hari kedua dlm seminggu, selepas hari Ahad". So each weekday ships twice, bare and with the classifier. That is what stops `setiap hari Isnin` from being read as `setiap hari`, every day, with the weekday quietly discarded. Bare `setiap hari` still means daily, because both readings are real. Sunday takes a third surface, `hari minggu`.

**The date line** is day-first, `15 Januari 2020`, with no linking preposition.

**Relative offsets** are postposed. The past is `lepas`, `lalu` or `yang lalu`. The future is `lagi` or `dalam`. `3 hari lepas` is three days ago and `2 minggu lagi` is two weeks ahead.

**The ordinal prefix.** `ke-` makes a numeral ordinal, hyphenated before a digit and joined before a spelled numeral. The tokenizer splits the hyphenated form, so `abad ke-20` reads as the twentieth century.

**Century and decade.** `abad` and `kurun` both gloss to century, and `dekad` and `dasawarsa` both to a ten-year period. All four come from *Kamus Dewan*. Because Malay nouns do not inflect, no plural surface is needed.

**The clock.** `pukul` and `jam` introduce a time. *Kamus Dewan* gives `pukul` a dedicated clock sense ("bahagian drpd sesatu hari spt yg ditunjukkan oleh jam") and its own example is `kami sampai di rumah pukul lima petang`, five in the afternoon. Noon is `tengah hari` and midnight `tengah malam`.

**The night band.** `malam` is not a uniform twelve-hour shift but a band that crosses midnight. `pukul satu malam` is 01:00, `pukul enam malam` is 18:00, `pukul sebelas malam` is 23:00, `pukul dua belas malam` is 00:00. Hours one through five stay in the small hours, six through eleven move to the evening. The evening boundary at 19:00 is CLDR's night band for Malay. The small-hours use of `malam` is the colloquial reading and is sourced to the Wiktionary entry for `malam`, whose Malay section was checked.

**Dayparts.** `pagi`, `petang` and `malam` also carry band spans of their own, with the boundaries transcribed from the CLDR 47 day-period rules for `ms` and the surfaces from the Malay sections of the Wiktionary entries for each word.

**Range and boundary markers.** `sebelum` opens a bare-before range, `dari` and `daripada` open a bounded one, `antara ... dan ...` frames a closed range, `sejak` is since, `sehingga`, `hingga` and `sampai` are until, `selama` is a duration, `setiap` and `tiap` are every. Each is sourced to its *Kamus Dewan* entry. `selepas` is listed for "after" but is refused, in line with the rule that a bare "after" has no open-ended-future span to return.

**Habitual recurrence** is `setiap hari isnin`. Answered as a recurrence, this is the repeating Monday. Asked for a span, it comes back as the next Monday with `setiap` left in the remainder.

**Seasons and the weekend.** The four seasons ship in both the Malaysian and the Indonesian-flavoured wordings: `musim luruh` beside `musim gugur`, `musim bunga` beside `musim semi`, `musim sejuk` beside `musim dingin`. The weekend is `hujung minggu`.

## The half hour: an open question

The locale, and a test that pins it, assert that a bare `setengah` before an hour names the half *toward* that hour: `setengah tiga` is 02:30, the German pattern. That reading resolves, and it does so uniformly: `setengah H` gives (H−1):30 for every hour.

What the evidence actually supports is a different construction. Attested Malay puts `setengah` **after** the hour, and reads it additively.

- Malay Wikipedia's article on the Seneca Falls Convention writes that the evening session opened `pada pukul tujuh setengah`. The English article it translates says "opening it at half-past seven", from the same cited National Park Service report. That fixes `pukul tujuh setengah` at 19:30, hour first, half added.

- A Malay time-telling guide from Preply gives `jam tiga setengah` as 3:30. A Malay-language lesson blog gives `pukul lima setengah` as half past five and `pukul tiga setengah` as 3:30. Both put the hour first and add the half.

- One further guide, talkpal.ai, gives the same postposed shape the opposite value, `pukul tiga setengah` as 2:30. It stands alone against the other three, and the site carries no editorial provenance.

- One more Malay Wikipedia sentence, in the article on Calvin Coolidge, has `pukul tiga setengah pagi` for the hour at which he learned he had become president. The English article gives the oath as 2:47 a.m. That is close to 02:30 and close to nothing else. But it is a loose translation of a time neither reading matches exactly, so it settles nothing.

The preposed construction the locale implements was not found at all. A regular expression search over Malay Wikipedia for `setengah` followed by an hour word returns four articles. Every one is a word-boundary accident: `setengah lapangan` (half the field), `sesetengah empat`, `setengah-setengah dua`. So there is no corpus attestation in Malay for `setengah tiga` as a clock time.

The dictionary does not decide it either. *Kamus Dewan* defines `setengah` as `separuh, seperdua` (half) with no clock sense and no example naming an hour. Its entry for `pukul` has a clock sense but no half-hour example. Neither `setengah tiga` nor `lapan setengah` is in the dictionary. The Malay section of the Wiktionary entry for `setengah` gives "a half" and nothing more.

The preposed pattern *is* the Indonesian one, where `setengah tiga` for 02:30 is ordinary, and Indonesian is where a Malay locale would most easily acquire it by analogy. That is a hypothesis about how the reading got here, not evidence about Malay.

So the locale reads a construction that no consulted source attests, and strands the one that they do. `pukul lapan setengah` returns 08:00 with `setengah` left in the remainder. The same happens for every hour: the half is dropped and a whole hour is returned in its place. If the additive reading is right, that is a thirty-minute error on every phrase of that shape, with the word that would have corrected it discarded.

A native speaker settles this by answering two separate questions. Does `setengah tiga`, hour last, mean anything in Malay, and if so what time? And does `pukul lapan setengah`, hour first, mean 08:30 or 07:30? Nothing here should be changed until both are answered, because the sources that speak to the second question do not agree with each other.

`setengah satu` is 00:30 or 12:30, whichever comes next after the anchor (ruling 17 in [the rulings](../rulings.md)).

## Weaker provenance

**The quarter hour.** `suku` ships as the business-quarter word only. Its clock direction is unconfirmed and no clock quarter is implemented, which the locale file states plainly. One guide offers `pukul dua kuartar` and `pukul tiga setengah kuartar` for quarter past and quarter to. Neither `kuartar` nor that use of `setengah` appears in *Kamus Dewan*, and the forms are not shipped.

**`kelmarin dulu`** for the day before yesterday is shipped without a dictionary locator having been checked for it.

## What refuses

**A bare duration.** `setengah jam lagi` (in half an hour) returns nothing, although `dua jam lagi` reads. The count-one half does not reach the offset slot a numeral reaches.

**A decimal clock.** `pukul 2.30` returns nothing.

**"After".** `selepas` is listed but refused, because an open-ended future has no end to bound a span with.

## Known defects

Beyond the half hour above, each of these is reproducible with `extract_timespan(text, "ms", anchor=datetime(2017, 6, 27, 13, 4))`.

`pukul dua suku` returns the second quarter of 2017 with `pukul` stranded. A phrase that names a time of day comes back as a three-month business quarter. The word that made it a clock time is discarded. `suku tiga` returns the third quarter of 2017, which is defensible on its own. But it is the same collision seen from the other side: `suku` is both the quarter of an hour and the quarter of a year, and the year always wins.

## Open questions for a native speaker

1. Is `setengah tiga`, with the hour after `setengah`, said in Malay at all, and if it is, does it mean 02:30 or 03:30?
2. Does `pukul lapan setengah` mean 08:30 or 07:30?
3. If the half is toward the hour, does the hour before one read as twelve, so that the half before one is 12:30 rather than 00:30?
4. What is the ordinary way to say a quarter past and a quarter to, and does `suku` appear in it?
5. Is `kelmarin dulu` the usual phrase for the day before yesterday?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("ms")
    True
    >>> span, rest = extract_timespan('pukul satu malam', "ms", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T01:00:00', '')
    >>> span, rest = extract_timespan('pukul enam malam', "ms", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T18:00:00', '')
    >>> span, rest = extract_timespan('pukul sebelas malam', "ms", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T23:00:00', '')
    >>> span, rest = extract_timespan('pukul dua belas malam', "ms", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-28T00:00:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('pukul 2.30', "ms", anchor) is None
    True

## Known limits

Each line is an open issue with a strict `xfail` test for this language. The lines are grouped by topic. An example names the reader that produced it, the language and the anchor date, and shows what that reader gives on the test's own phrase.

- A count followed by `setengah` reads half of the count. Example (reader `extract_duration`, lang `ms`, anchor 2017-06-27 13:04): `dua setengah jam lagi` gives a length of 60 min and `lagi` left over. [#1231](https://github.com/TigreGotico/chronologia/issues/1231)

---
[← Macedonian](mk.md) · [Home](../index.md) · [Maltese →](mt.md)
