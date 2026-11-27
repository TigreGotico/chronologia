# Language provenance pages

<!-- agent-hint
covers: which languages and regional tags chronologia supports, per feature, and which reader handles the numbers of each tag
source: tools/language_support.py, docs/languages/support.json, chronologia/locale/*/lang.json, chronologia/extract/numlayer.py:NUMTAG_LANGS
generated: the support table, by tools/language_support.py write
verify: .venv/bin/python -m pytest -q test/test_docs_language_support.py
see: docs/index.md, docs/extraction.md
-->

This page lists the locales, one page for each, and gives the support of each language and leader tag, feature by feature. Open the page for your language to see where its words come from, what it refuses and what a native speaker could still settle.

chronologia never guesses a linguistic surface. A construction ships in a locale only where an attested source supports it. Where the sources conflict, or nothing attests the phrase, the locale ships nothing and the phrase returns nothing. That rule makes a wrong answer rare. It also explains why an ordinary phrase in your language can come back empty.

Every locale has a page. The vocabulary files carry their sources in comment headers. Reading `chronologia/locale/<code>/*.voc` answers the same question at a finer grain.

## How to read a page

Each page opens with a short example you can run, then follows one shape.

**What ships** walks the constructions in the order a reader meets them: weekdays and months, the date line, relative offsets, the clock, day parts, numerals and markers. It names the source for each group, precisely enough to fetch it again. Where two independent sources agree, the page says so, because that agreement tells you how far to trust a surface.

**Weaker provenance** collects the surfaces that ship on thinner evidence than the rest of the page. These surfaces work. They are the first place to look when a locale disagrees with a native speaker.

**What refuses** lists the constructions that the locale deliberately leaves out, each with its reason. A refusal is a design decision, not a missing feature. The library declines to invent a surface it cannot attest, or declines to pick a reading where the language is ambiguous.

**Open questions** are the items that a native speaker would settle. No page resolves them by analogy.

**Checked examples** run as doctests, so the output on the page is the output of the code.

**Known limits** closes the page. Each line is a bug that has an open issue and a strict `xfail` test. An example names its reader, language and anchor date, and the page's verify command runs it again. A limit leaves the page when its issue closes.

## Citation discipline

A source named on these pages was consulted directly. Author and year appear where a claim is standard. A section or page locator appears only where that exact locator was checked. Where a source was sought and not reached, the page says so. The output of another date parser is never evidence about a language.

## How numbers are read

numtag reads the spelled numbers of the locales in `NUMTAG_LANGS` in `chronologia/extract/numlayer.py`. chronologia keeps no number words for them. The other locales read numbers with their own `numfold_*` module in `chronologia/extract/`. The Numbers column of the table names the reader of each tag. The tags `pt-BR`, `fr-BE` and `fr-CH` read numbers with a regional numtag lexicon.

## Support table

The script `tools/language_support.py` writes this table. It reads the locale data in `chronologia/locale/<code>/` and the test results in `docs/languages/support.json`. The test `test/test_docs_language_support.py` writes the table again and fails when this page differs.

Each cell gives a status, then the number of our own test rows that pass and the total of our own test rows, for that locale and feature. These counts come from the regression rows in this repository. They do not measure coverage of the language. A feature can show "yes" with a few rows and still fail most phrases that a speaker uses. For coverage, read the outside date benchmark in [benchmarks.md](../benchmarks.md).

The status follows this rule:

- **yes**: the locale data for the feature exists, and at least one of our test rows passes. "yes" does not mean that the feature is complete.
- **partial**: the data exists and no test row passes, or a test row passes and the locale ships no data for the feature.
- **no**: the data does not exist, and no test row passes.

A test row counts for a feature when its file name in `test/nl_corpus_<code>/` matches the pattern of the feature in `FEATURES` in the script. A strict `xfail` row and a skipped row count as rows that do not pass. The Spoken column counts the rows in `test/test_spoken*_<code>.py`. It reads `chronologia.spoken.writes(tag)`, so a tag with no writer is "no".

The Ready column and the `ready` key of each locale in `support.json` compare chronologia with ovos-date-parser 0.29 on the outside date benchmark. A tag is ready only when chronologia is correct at least as often as ovos-date-parser on every bench class for that tag. One lower class makes the tag "no", also when the total rate of chronologia is higher. A tag with no bench rows shows "not measured". The flag comes from `docs/benchmarks/odp_vs_chronologia.json`, and [benchmarks.md](../benchmarks.md#against-ovos-date-parser) gives the numbers. A consumer can use the flag to select chronologia in place of ovos-date-parser for a tag.

A regional tag reads the data of its base language, named in the Data column. The leader page of each language lists the forms that differ by region. The languages that have a language leader come first, in leader order. The other languages follow by name.

Marwari has no locale. `extract_timespan` raises `NotImplementedError` for `mwr`. Issue [#1484](https://github.com/TigreGotico/chronologia/issues/1484) holds the questions for a native speaker of Bengali and Marwari.

To measure the test rows again and write the table, run these commands:

```bash
python tools/language_support.py measure
python tools/language_support.py write
```

<!-- support-table:start -->
Cells: status, own test rows passed / own test rows.

| Language | Tag | Data | Numbers | Dates | Clock | Durations | Relative days | Ranges | Recurrence | Holidays | Spoken | Ready |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| [Portuguese (Portugal)](pt.md) | pt-PT | pt | numtag | yes 175/175 | yes 321/321 | yes 18/18 | yes 127/127 | yes 112/112 | yes 139/139 | yes 360/361 | yes 1143/1143 | no |
| [Portuguese (Brazil)](pt.md) | pt-BR | pt | numtag (pt-BR lexicon) | yes 175/175 | yes 321/321 | yes 18/18 | yes 127/127 | yes 112/112 | yes 139/139 | yes 360/361 | yes 1143/1143 | no |
| [Spanish (Colombia)](es.md) | es-CO | es | numtag | yes 63/63 | yes 166/166 | yes 31/31 | yes 102/102 | yes 172/172 | yes 42/42 | yes 621/622 | no | not measured |
| [French (France)](fr.md) | fr-FR | fr | numtag | yes 230/230 | yes 199/199 | yes 19/19 | yes 100/100 | yes 340/343 | yes 39/39 | yes 451/452 | no | no |
| [Italian (Italy)](it.md) | it-IT | it | numtag | yes 47/47 | yes 194/194 | yes 8/8 | yes 86/86 | yes 140/140 | yes 18/18 | yes 341/342 | no | no |
| [German (Germany)](de.md) | de-DE | de | numtag | yes 69/69 | yes 102/102 | yes 28/28 | yes 44/44 | yes 413/413 | yes 40/40 | yes 768/769 | no | no |
| [Dutch (Netherlands)](nl.md) | nl-NL | nl | numtag | yes 659/659 | yes 156/156 | yes 19/19 | yes 31/31 | yes 313/313 | yes 11/11 | yes 696/696 | no | no |
| [Danish (Denmark)](da.md) | da-DK | da | numtag | yes 33/33 | yes 116/116 | yes 16/16 | yes 30/30 | yes 345/345 | yes 19/19 | yes 391/391 | no | no |
| [Kabyle](kab.md) | kab | kab | numtag | yes 98/98 | yes 85/85 | yes 13/13 | yes 27/27 | yes 6/6 | yes 8/8 | yes 7/7 | no | no |
| [Hindi (India)](hi.md) | hi-IN | hi | numfold_indic | yes 52/52 | yes 47/47 | partial 0/0 | yes 71/71 | yes 20/20 | yes 27/27 | no 0/0 | no | no |
| [Bengali (India)](bn.md) | bn-IN | bn | numtag | partial 0/0 | partial 0/0 | partial 0/0 | yes 6/10 | partial 0/0 | partial 0/0 | no 0/0 | no | not measured |
| Marwari | mwr | none | not supported, see [#1484](https://github.com/TigreGotico/chronologia/issues/1484) | no | no | no | no | no | no | no | no | no |
| [Albanian](sq.md) | sq | sq | numfold_albanian | partial 0/0 | yes 37/37 | partial 0/0 | yes 66/66 | partial 0/0 | partial 0/0 | no 0/0 | no | no |
| [Arabic](ar.md) | ar | ar | numtag | yes 850/850 | yes 100/100 | yes 25/25 | yes 61/61 | yes 1158/1159 | yes 21/21 | yes 20/20 | no | no |
| [Aragonese](an.md) | an | an | numtag | yes 38/38 | yes 42/42 | yes 14/14 | yes 26/26 | yes 10/10 | yes 19/19 | no 0/0 | no | no |
| [Armenian](hy.md) | hy | hy | numfold_armenian | yes 35/35 | yes 26/26 | partial 0/0 | partial 0/0 | partial 0/0 | partial 0/0 | no 0/0 | no | not measured |
| [Asturian](ast.md) | ast | ast | numtag | yes 278/278 | yes 58/58 | yes 14/14 | yes 61/61 | yes 104/104 | yes 20/20 | no 0/0 | no | no |
| [Azerbaijani](az.md) | az | az | numtag | yes 414/414 | yes 147/147 | yes 13/13 | yes 34/34 | yes 150/150 | yes 10/10 | yes 67/67 | no | no |
| [Basque](eu.md) | eu | eu | numtag | yes 643/643 | yes 29/29 | yes 16/16 | yes 129/129 | yes 4/4 | yes 6/6 | yes 33/33 | no | no |
| [Belarusian](be.md) | be | be | numfold_be | yes 113/113 | yes 104/104 | partial 0/0 | yes 80/80 | partial 0/0 | partial 0/0 | no 0/0 | no | not measured |
| [Bulgarian](bg.md) | bg | bg | numtag | yes 170/170 | yes 20/20 | yes 13/13 | yes 46/46 | yes 238/238 | yes 19/19 | yes 168/168 | no | no |
| [Catalan](ca.md) | ca | ca | numtag | yes 2727/2728 | yes 178/178 | yes 14/14 | yes 96/96 | yes 370/370 | yes 20/20 | yes 226/239 | no | no |
| [Croatian](hr.md) | hr | hr | numtag | yes 70/70 | yes 34/34 | yes 16/16 | yes 41/41 | yes 328/328 | yes 19/19 | yes 282/282 | no | no |
| [Czech](cs.md) | cs | cs | numtag | yes 61/61 | yes 73/73 | yes 13/13 | yes 76/76 | yes 191/191 | yes 20/20 | yes 329/329 | no | no |
| [English](en.md) | en | en | numtag | yes 393/393 | yes 300/300 | yes 92/92 | yes 164/164 | yes 722/727 | yes 242/242 | yes 1081/1082 | no | no |
| [Esperanto](eo.md) | eo | eo | numfold_esperanto | yes 23/23 | yes 32/32 | partial 0/0 | partial 0/0 | no 0/0 | yes 25/25 | no 0/0 | no | no |
| [Estonian](et.md) | et | et | numtag | yes 547/547 | yes 41/41 | yes 13/13 | yes 64/64 | yes 4/4 | yes 19/19 | yes 34/34 | no | no |
| [Filipino](fil.md) | fil | fil | numfold_filipino | yes 60/60 | yes 71/71 | partial 0/0 | yes 54/54 | partial 0/0 | partial 0/0 | no 0/0 | no | not measured |
| [Finnish](fi.md) | fi | fi | numtag | yes 471/471 | yes 95/96 | yes 13/13 | yes 29/29 | yes 16/16 | yes 10/10 | yes 188/188 | no | no |
| [Galician](gl.md) | gl | gl | numtag | yes 1328/1328 | yes 118/118 | yes 14/14 | yes 95/95 | yes 144/144 | yes 20/20 | yes 225/226 | no | no |
| [Georgian](ka.md) | ka | ka | numfold_georgian | yes 42/42 | yes 38/38 | partial 0/0 | yes 42/42 | no 0/0 | no 0/0 | no 0/0 | no | not measured |
| [Greek](el.md) | el | el | numtag | yes 578/578 | yes 223/223 | yes 16/16 | yes 54/54 | yes 103/103 | yes 21/21 | yes 193/193 | no | no |
| [Hausa](ha.md) | ha | ha | numfold_chadic | yes 64/64 | yes 35/35 | yes 2/2 | yes 44/44 | yes 17/17 | partial 0/0 | no 0/0 | no | not measured |
| [Hebrew](he.md) | he | he | numtag | yes 327/327 | yes 45/45 | yes 19/19 | yes 92/92 | yes 81/82 | yes 49/49 | yes 16/16 | no | no |
| [Hungarian](hu.md) | hu | hu | numtag | yes 568/568 | yes 57/57 | yes 15/15 | yes 34/34 | yes 18/18 | yes 10/10 | yes 326/326 | no | no |
| [Icelandic](is.md) | is | is | numfold_icelandic | yes 42/42 | yes 50/50 | partial 0/0 | yes 66/66 | no 0/0 | no 0/0 | no 0/0 | no | not measured |
| [Indonesian](id.md) | id | id | numtag | yes 769/769 | yes 40/40 | yes 18/18 | yes 33/33 | yes 213/213 | yes 38/38 | yes 106/106 | no | no |
| [Irish](ga.md) | ga | ga | numfold_irish | yes 60/60 | yes 70/70 | partial 0/0 | yes 74/74 | yes 2/2 | partial 0/0 | no 0/0 | no | not measured |
| [Korean](ko.md) | ko | ko | numfold_korean | yes 34/34 | yes 42/42 | yes 11/11 | yes 38/38 | no 0/0 | no 0/0 | no 0/0 | no | not measured |
| [Latvian](lv.md) | lv | lv | numfold_latvian | yes 57/57 | yes 37/37 | partial 0/0 | yes 56/56 | partial 0/0 | partial 0/0 | no 0/0 | no | not measured |
| [Lithuanian](lt.md) | lt | lt | numfold_baltic | yes 34/34 | yes 28/28 | partial 0/0 | yes 68/68 | yes 23/23 | partial 0/0 | no 0/0 | no | no |
| [Macedonian](mk.md) | mk | mk | numfold_macedonian | yes 59/59 | yes 64/64 | partial 0/0 | yes 55/55 | partial 0/0 | partial 0/0 | no 0/0 | no | not measured |
| [Malay](ms.md) | ms | ms | numtag | yes 38/38 | yes 36/36 | yes 14/14 | yes 29/29 | yes 15/15 | yes 36/36 | yes 22/22 | no | no |
| [Maltese](mt.md) | mt | mt | numfold_maltese | yes 34/34 | yes 33/33 | partial 0/0 | partial 0/0 | partial 0/0 | partial 0/0 | no 0/0 | no | no |
| [Mirandese](mwl.md) | mwl | mwl | numtag | yes 43/43 | yes 18/18 | yes 14/14 | yes 18/18 | yes 19/19 | yes 19/19 | no 0/0 | no | no |
| [Norwegian Bokmål](nb.md) | nb | nb | numtag | yes 311/311 | yes 55/55 | yes 13/13 | yes 30/30 | yes 269/269 | yes 19/19 | yes 441/441 | no | no |
| [Norwegian Nynorsk](nn.md) | nn | nn | numtag | yes 770/770 | yes 53/53 | yes 13/13 | yes 27/27 | yes 29/29 | yes 19/19 | yes 71/71 | no | no |
| [Occitan](oc.md) | oc | oc | numtag | yes 29/29 | yes 67/67 | yes 14/14 | yes 54/54 | yes 16/16 | yes 20/20 | no 0/0 | no | no |
| [Persian](fa.md) | fa | fa | numtag | yes 30/30 | yes 54/57 | yes 13/13 | yes 59/59 | yes 147/147 | yes 18/18 | yes 25/25 | no | no |
| [Polish](pl.md) | pl | pl | numtag | yes 50/50 | yes 20/20 | yes 18/18 | yes 53/53 | yes 319/319 | yes 20/20 | yes 261/261 | no | no |
| [Romanian](ro.md) | ro | ro | numtag | yes 19/19 | yes 45/45 | yes 14/14 | yes 85/85 | yes 332/332 | yes 19/19 | yes 306/306 | no | no |
| [Russian](ru.md) | ru | ru | numtag | yes 122/122 | yes 94/94 | yes 20/20 | yes 72/72 | yes 695/695 | yes 19/19 | yes 219/219 | no | yes |
| [Serbian](sr.md) | sr | sr | numfold_slavic | yes 42/42 | yes 42/48 | partial 0/0 | partial 0/0 | partial 0/0 | partial 0/0 | no 0/0 | no | no |
| [Slovak](sk.md) | sk | sk | numtag | yes 37/37 | yes 59/59 | yes 13/13 | yes 55/55 | yes 144/144 | yes 19/19 | yes 256/256 | no | no |
| [Slovenian](sl.md) | sl | sl | numtag | yes 69/69 | yes 25/25 | yes 13/13 | yes 42/42 | yes 295/295 | yes 19/19 | yes 256/256 | no | no |
| [Swahili](sw.md) | sw | sw | numfold_bantu | yes 41/41 | yes 81/81 | yes 34/34 | yes 50/50 | partial 0/0 | partial 0/0 | no 0/0 | no | not measured |
| [Swedish](sv.md) | sv | sv | numtag | yes 275/275 | yes 64/64 | yes 13/13 | yes 27/27 | yes 811/811 | yes 19/19 | yes 410/410 | no | no |
| [Tamil](ta.md) | ta | ta | numfold_dravidian | yes 28/28 | yes 21/21 | partial 0/0 | yes 53/53 | no 0/0 | partial 0/0 | no 0/0 | no | not measured |
| [Thai](th.md) | th | th | numfold_thai | yes 30/30 | yes 33/33 | partial 0/0 | yes 63/63 | partial 0/0 | partial 0/0 | no 0/0 | no | not measured |
| [Turkish](tr.md) | tr | tr | numtag | yes 1293/1293 | yes 278/278 | yes 13/13 | yes 36/36 | yes 135/135 | yes 19/19 | yes 201/201 | no | no |
| [Ukrainian](uk.md) | uk | uk | numtag | yes 1294/1294 | yes 91/91 | yes 13/13 | yes 46/46 | yes 199/199 | yes 19/19 | yes 244/244 | no | no |
| [Vietnamese](vi.md) | vi | vi | numfold_vietnamese | yes 54/54 | yes 46/46 | partial 0/0 | yes 51/51 | no 0/0 | no 0/0 | no 0/0 | no | not measured |
| [Welsh](cy.md) | cy | cy | numfold_welsh | yes 45/45 | yes 59/59 | partial 0/0 | yes 73/73 | no 0/0 | yes 30/30 | no 0/0 | no | not measured |
| [West Frisian](fy.md) | fy | fy | numtag | yes 29/29 | yes 54/54 | yes 13/13 | yes 27/27 | yes 29/29 | yes 18/18 | yes 17/17 | no | no |
<!-- support-table:end -->

---
[← Transparency: how correctness is checked](../transparency.md) · [Home](../index.md) · [Albanian →](sq.md)
