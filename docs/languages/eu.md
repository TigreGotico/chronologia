# Basque (`eu`)

<!-- agent-hint
covers: where each construction of the Basque locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/eu/lang.json, chronologia/locale/eu/*.voc, chronologia/extract/numlayer.py:NUMTAG_LANGS, test/nl_corpus_eu/, test/test_xfail_open_issues_*.py
generated: no
verify: .venv/bin/python -m doctest docs/languages/eu.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/eu.md afternoon1@12:00 afternoon2@14:00 evening1@19:00 morning1@00:00 morning2@06:00 night1@21:00
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Basque (`eu`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

Basque is a language isolate, and the consequence for a date parser is structural rather than lexical: there are no prepositions to match. Where most locales in this library recognise "from", "until", "during" and "of" as separate words standing before their object, Basque marks all of them as case suffixes glued onto the end of the noun. `ekainaren 5ean` is "of-June 5th-in", two case endings and no function words at all. A tokenizer that splits on whitespace therefore never sees the marker. It sees one long word.

The locale answers this in two places. The vocabulary files list the inflected surfaces themselves (every month ships six forms, every weekday five) and `chronologia/extract/numlayer_agglutinative.py` re-fuses a digit that the tokenizer has sheared from its case ending, so `5ean` comes back as the day number 5 rather than a number followed by a stranded fragment. The marker files that do exist (`marker_from.voc`, `marker_to.voc`, `marker_of.voc`) hold suffixes written with a leading hyphen, not words.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('bostak eta erdi', "eu", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T05:30:00', '')

## What ships

**Months and weekdays** ship as sets of inflected surfaces rather than lemmas. January is `urtarrila`, `urtarrilak`, `urtarrilaren`, `urtarrilean`, `urtarrilan` and `urtarrilko`: absolutive, the `-k` form a date line uses, the genitive that governs a day number, the inessive, and the relational `-ko`. Weekdays follow the same pattern with five forms each. Listing the paradigm is what lets `astelehenean` ("on Monday") and `martxoaren hirugarren astelehena` ("the third Monday of March") both bind without a morphological analyser.

**The date line** is `MONTH-genitive DAY-inessive`, `ekainaren 5ean`, and the year when present leads with its own relational suffix: `2027ko ekaina`, `1999ko urtarrilaren 1ean`. The generic `calendar_date` construction is disabled in `lang.json` in favour of the base grammar's date orders, because the case marking fixes the Basque order, not convention.

**Relative offsets** are two-sided. Backward is the preposed `duela` or `orain dela`, as in `duela hiru egun` (three days ago). Forward is the postposed `barru`, `buru` or `barne`, as in `hiru egun barru` (in three days). The `relative_offset` orders in `lang.json` accordingly list both `MARKER NUM UNIT` and `NUM UNIT MARKER`.

**The clock** names the hour already reached and counts forward from it with `eta` ("and"): `bostak eta erdi` is 05:30, `bostak eta laurden` is 05:15. The plural hour numerals (`bostak`, `hirurak`, `hamabiak`) are the telling-time forms, and the fold maps them to their values. The backward direction uses `gutxi` ("less").

**The inessive telling-time hour** (`hiruretan`, "at three") is one word with no clock marker of any kind in it. The fold splits it into a synthetic `at` marker plus the digit, using `etan` from `marker_at.voc` as the marker surface. Without that split the digit binds nothing at all. `hiruretan` and `goizeko hiruretan` both resolve to 03:00.

**Day parts** come from the Unicode CLDR 47 Day Period Rules chart, which gives `eu` six bands: `morning1` from 00:00, `morning2` (goiza) from 06:00, `afternoon1` (eguerdia) from 12:00, `afternoon2` (arratsaldea) from 14:00, `evening1` (iluntzea) from 19:00 and `night1` (gaua) from 21:00. The implementation in `chronologia/dayparts.py` collapses the two morning bands into one running 00:00-12:00 and the two afternoon bands into one running 12:00-19:00, keeping evening at 19:00-21:00 and night at 21:00-24:00. Basque night therefore does not wrap past midnight. The morning band absorbs the small hours. The shipped surfaces are the inessive forms a phrase actually uses (`goizean`, `arratsaldean`, `iluntzean`, `gauean`) not the CLDR citation forms.

**Ordinals** use the `-garren` series (`bigarren`, `hirugarren`) plus `lehen` and `lehenengo` for one. numtag reads all of them as ordinals.

## Weaker provenance

The vocabulary files carry no source comments except the four day-part files. The months, weekdays, units, seasons and markers are not individually sourced in the repository. This page does not claim provenance for them beyond what the files themselves carry.

`iluntzean` is the shipped evening surface, and its comment header cites the Wiktionary entry for `iluntze`. That entry has a Basque section. It glosses `iluntze` as "dusk". But it carries no declension table.

The inessive `iluntzean` specifically is not attested there. The other three day-part surfaces are on firmer ground. The Wiktionary entries for `goiz`, `arratsalde` and `gau` each carry a declension table that shows `goizean`, `arratsaldean` and `gauean` explicitly.

The comment in `numlayer_agglutinative.py` that documents the inessive-plural hour fold cites `en.wiktionary.org/wiki/-etan#Basque`. That page has no Basque section. Its only section is Old English. The mechanism it describes is nonetheless the one the code implements and the one the hour surfaces show. But the citation does not support it and is unverified. The same comment's second citation, Euskaltzaindia's telling-time forms, names no locator, so that citation is likewise unchecked.

## What refuses

**Bare `asteburuan`.** `special_weekend.voc` holds `asteburua` and `asteburu` but not the inessive `asteburuan`, the most ordinary inflected form of "at the weekend". `asteburuan` returns nothing, and the bare noun resolves.

**The two-word hours.** One and two o'clock are `ordu bata` and `ordu bietan`, two-word forms rather than the single inessive plural the other hours use, and neither resolves.

**`laurden gutxi bostak`.** The quarter-to phrasing binds only in the order `HOUR CLOCKDIR FRACTION` that `lang.json` declares: `bostak gutxi laurden`. Whether that is the order a Basque speaker uses is an open question below, not a settled one.

## Known defects

These are wrong answers rather than refusals, and a wrong answer with a stranded remainder is worse than nothing. Each is stated with the probe that produces it, anchored at 2017-06-27 13:04.

`extract_timespan("2020ko lehen hiruhilekoa", "eu")` returns the first quarter of **2017**, the anchor year, with `2020ko` in the remainder. The relational year form does not bind the `YEAR?` slot of `quarter_ref`.

`extract_timespan("urtarrilaren erdialdean", "eu")` returns the whole of January with `erdialdean` in the remainder, rather than mid-January. `urtarrilaren hasieran` behaves the same way, returning all of January with `hasieran` stranded. The period-part words are listed but the genitive month form does not reach the `month_fuzzy` construction.

`extract_timespan("ekaina eta uztaila artean", "eu")` returns June alone with `eta uztaila artean` in the remainder. The `artean` range is not read, and the narrowed span it returns instead is silently wrong rather than empty.

## Open questions for a native speaker

1. Is `bostak gutxi laurden` or `laurden gutxi bostak` the ordinary order for "quarter to five", and should both be accepted?
2. Should `asteburuan` and the other inessive forms of the weekend, season and unit nouns be listed alongside the absolutive forms already shipped?
3. Are `ordu bata` and `ordu bietan` the living forms for one and two o'clock, and do they take the same `eta` continuation as the plural hours?
4. Which of the three forward-offset markers (`barru`, `buru`, `barne`) are interchangeable, and which are regional?

## Known limits

Each line is an open issue with a strict `xfail` test for this language. The most common cases come first. An example shows what the library gives on the test's own anchor date.

- A length with a suffix and a digit clock with a case suffix are not read. Example: `ezarri hamar minutuko tenporizadore bat` gives no reading. [#1017](https://github.com/TigreGotico/chronologia/issues/1017)

- A part of the day after a clock or a weekday stays in the remainder. Example: `3:00 gauean` gives gauean. [#1200](https://github.com/TigreGotico/chronologia/issues/1200)

- A plural, adverbial or recurring part of the day is not read, so the hour reads in the wrong half. Example: `gogorarazi goizetan medikazioa hartzeko 8etan` gives 2017-06-27 20:00, where the test expects 2017-06-28 08:00. [#1009](https://github.com/TigreGotico/chronologia/issues/1009)

- A day word or a counted offset gives no reading. Example: `duela aste bat` gives 2017-01-02 00:00, where the test expects 2017-06-20. [#992](https://github.com/TigreGotico/chronologia/issues/992)

- Text that is no date reads as a date, or the wrong reading wins. Example: `ordu barru` gives one hour from the anchor, where the test expects no date. [#1035](https://github.com/TigreGotico/chronologia/issues/1035)

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("eu")
    True
    >>> span, rest = extract_timespan('bostak eta erdi', "eu", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T05:30:00', '')
    >>> span, rest = extract_timespan('bostak eta laurden', "eu", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T05:15:00', '')
    >>> span, rest = extract_timespan('ekainaren 5ean', "eu", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2018-06-05T00:00:00', '')
    >>> span, rest = extract_timespan('martxoaren hirugarren astelehena', "eu", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-03-20T00:00:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('asteburuan', "eu", anchor) is None
    True

---
[← Azerbaijani](az.md) · [Home](../index.md) · [Belarusian →](be.md)
