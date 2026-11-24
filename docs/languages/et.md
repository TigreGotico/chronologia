# Estonian (`et`)

<!-- agent-hint
covers: where each construction of the Estonian locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/et/lang.json, chronologia/locale/et/*.voc, chronologia/extract/numlayer.py:NUMTAG_LANGS, test/nl_corpus_et/
generated: no
verify: .venv/bin/python -m doctest docs/languages/et.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/et.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Estonian (`et`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

Estonian's spoken clock counts toward the hour that has not arrived yet. That is the same direction as Slovenian, and the two are unrelated. The phrase `pool üheksa` is 8:30, not 9:30. The same counting-toward logic extends to quarters: `veerand üheksa` is 8:15 and `kolmveerand üheksa` is 8:45. That three-way fraction system rests on a numeral-folding pass that has to read a case system the parser's own cardinal words do not carry.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('pool üheksa', "et", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T08:30:00', '')

## What ships

**The date line** is little-endian. `lang.json` lists `calendar_date` in `base_grammar.disable` and defines its own in its place, It uses the orders `DAY MONTH YEAR?` and `MONTH DAY? YEAR?` (day-led first, month-led as the fallback). They match the CLDR 47 `ca-gregorian` chart for `et` at every level. The formats are full `EEEE, d. MMMM y`, long `d. MMMM y`, medium `d. MMM y` and short `dd.MM.yy`. Estonian spells the day of month with an ordinal (`viieteistkümnes aprill`, "the fifteenth of April"). numtag reads the ordinal words. It reads one word for the days 1-20 and 30. It reads two words for the compound tens 21-29/31 (`kahekümne esimene`). chronologia folds both to the day: `kahekümne esimene aprill` is 21 April.

**Weekdays and months** ship in the nominative plus the adessive case that "on Monday" / "in May" phrases use (`esmaspäev`/`esmaspäeval`, `jaanuar`/`jaanuari`/`jaanuaris`/`jaanuaril`, `mai`/`maikuu`/`mais`/`mail`) with no recorded citation for the case choice. The project's own date-sweep test corpus attests the surfaces (`test_et_full_date_sweep.py`, `test_et_month_year_sweep.py`).

**Day parts** are transcribed from the Unicode CLDR 47 day-period rules for `et`, each shipping as the adessive adverb a phrase actually uses: `hommikul` (morning, Wiktionary `hommik`, adessive `hommikul`), `pärastlõunal` (afternoon, EKI Sõnaveeb `pärastlõuna`), `õhtul` (evening, Wiktionary `õhtu`, adessive `õhtul`), `öösel` (night, Wiktionary `öö`, adessive `öösel`). The same adverbs double as clock meridiem cues on an explicit hour. The abbreviations `e.l.` (AM, "enne lõunat", before noon) and `p.l.` (PM, "pärast lõunat", after noon) serve the same purpose.

**Landmarks** are `kesköö`/`keskööl` (midnight, bare and adessive) and `keskpäev`/`keskpäeval`/`lõuna` (noon, two live surfaces).

**The clock's toward-hour fractions.** All three counting-toward constructions (half, quarter and three-quarter) are cited to Erelt, Mati (ed.), *Estonian Language*, Linguistica Uralica Supplementary Series 1 (Estonian Academy Publishers, 2003), its time-expression section, and to EKI Eesti Keele Instituut's *Sõnaveeb* entries for `pool`, `veerand` and `kolmveerand` in their clock senses. A second, independent source with a worked numeric example (colanguage.com's telling-the-time guide, corroborated by omniglot.com's Estonian time page) confirms the direction: "half an hour is always subtracted from the next hour", glossing `pool üheksa` as 8:30, literally "half nine" naming the hour ahead. The project's own test corpus checks the half-hour reading against independent arithmetic across four hours (`pool üheksa` → 08:30, `pool kaheksa` → 07:30, `pool kaksteist` → 11:30, `pool kümme` → 09:30). It checks the quarter and three-quarter readings the same way. The convention flags `bare_half_to: true` and `bare_quarter_to: true` in `lang.json`, and the `clock_time` construction carries a dedicated `FRACTION HOUR MERIDIEM? ZONE?` order alongside the whole-hour `kell H` shape.

**`pool` survives the number fold intact.** The Estonian hook (`chronologia.extract.numlayer_agglutinative:fold_et`) reads every number through numtag, the genitive numerals of the "N units ago" and "in N units" slots too: `ühe`, `kahe`, `kolme`, ... `kümne`. numtag reads the clock fraction `pool` as one half. The fold keeps it a word when it ends its own mention. The clock grammar sees `pool` before the hour.

**Relative offsets** are `tagasi` (ago, trailing the count) and a leading-marker order, with the deep-time construction (`N SCALE aastat tagasi`, "N thousand/million/billion years ago") reading `aastatuhat`/ `aastatuhande` (millennium).

**Determiners.** `eelmine`/`eelmisel` ("last/previous") and `järgmine`/ `järgmisel`/`tulev`/`tuleval` ("next", two live stems) match CLDR 47 `et` `dateFields.json`'s week-field relative types directly: relative-type--1 is `eelmine nädal`, relative-type-1 is `järgmine nädal`: and the year field gives the same regular pattern, `eelmine aasta`/`järgmine aasta`, unlike Slovenian's irregular `lani`.

**Quarters, ISO weeks, decades, centuries and millennia** resolve: `kvartal`/`kvartali`/`kvartalis` (quarter), `nädal` (ISO week, read via the `week_num` construction), `aastakümme` implied by `scope_unit_decade`, `sajand` implied by `scope_unit_century`, and `aastatuhat` in a dedicated `unit_millennium.voc`: the ordinary arrangement across the locales here, rather than leaving "a thousand years" to a numeral-plus-scale paraphrase.

**Seconds** ship a dedicated unit, `sekund`/`sekundi`/`sekundit`.

**Named days** span all four positions around the anchor: `üleeile` (the day before yesterday), `eile` (yesterday), `homme` (tomorrow), `ülehomme` (the day after tomorrow). All four are exactly what the CLDR 47 `et` `dateFields.json` day field gives for relative types −2, −1, +1 and +2.

## Weaker provenance

**The weekday and month oblique-case choices** (which of the several cases each ships) rest on the project's own test-corpus attestation. No grammar citation names the case.

**`kvartal`** ships without a citation distinguishing it from any native alternative.

## What refuses

**Minutes to or past the hour by count** (`viis minutit üle poole`-style counting) does not resolve. The three counting-toward fractions (half, quarter, three-quarter) are the only fractional clock surfaces sourced, and no arbitrary-minute construction ships.

That is the only refusal. In particular the "Nth weekday of month" construction (`märtsi kolmas esmaspäev`, "the third Monday of March") resolves. The regression test that covers it, `test_et_ordinal_weekday_xfail.py`, carries no `xfail` decorator.

## Open questions for a native speaker

1. What case do the shipped oblique weekday and month forms actually mark, and are the case sets complete for every day and month?
2. Does `kvartal` compete with any native Estonian alternative for "quarter", the way Bulgarian and Slovenian each carry two live quarter words?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("et")
    True
    >>> span, rest = extract_timespan('pool üheksa', "et", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T08:30:00', '')
    >>> span, rest = extract_timespan('veerand üheksa', "et", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T08:15:00', '')
    >>> span, rest = extract_timespan('kolmveerand üheksa', "et", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T08:45:00', '')
    >>> span, rest = extract_timespan('viieteistkümnes aprill', "et", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2018-04-15T00:00:00', '')

---
[← Esperanto](eo.md) · [Home](../index.md) · [Filipino →](fil.md)
