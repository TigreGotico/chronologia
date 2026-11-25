# Language provenance pages

<!-- agent-hint
covers: which languages have a provenance page, how each page is organised and which reader handles the numbers of each locale
source: chronologia/locale/*/lang.json, chronologia/extract/numlayer.py:NUMTAG_LANGS, chronologia/extract/numfold_*.py
generated: no
verify: .venv/bin/python -c 'exec("import re,glob,os,json\nfrom chronologia.extract.numlayer import NUMTAG_LANGS as N\nT=open(\"docs/languages/index.md\").read()\nrows=re.findall(r\"^\\| \\[[^]]*\\]\\((\\w+)\\.md\\) \\| (\\w+) \\| (\\S+) \\|\",T,re.M)\nc={os.path.basename(os.path.dirname(f)) for f in glob.glob(\"chronologia/locale/*/lang.json\")}\nassert {r[1] for r in rows}==c and len(rows)==len(c)\nfor pg,code,rd in rows:\n    assert pg==code and os.path.exists(\"docs/languages/\"+pg+\".md\")\n    h=json.load(open(\"chronologia/locale/\"+code+\"/lang.json\")).get(\"hook\",\"\")\n    assert (rd==\"numtag\")==(code in N)\n    assert rd==\"numtag\" or h.startswith(\"chronologia.extract.\"+rd+\":\"),(code,rd,h)\nassert \"the \"+str(len(N))+\" locales in\" in T and \"other \"+str(len(c)-len(N))+\" locales\" in T\n")'
see: docs/index.md, docs/extraction.md
-->

This page lists the 61 locales, one page for each, and says which number reader serves each locale. Open the page for your language to see where its words come from, what it refuses and what a native speaker could still settle.

chronologia never guesses a linguistic surface. A construction ships in a locale only where an attested source supports it. Where the sources conflict, or nothing attests the phrase, the locale ships nothing and the phrase returns nothing. That rule makes a wrong answer rare. It also explains why an ordinary phrase in your language can come back empty.

Every locale has a page. The vocabulary files carry their sources in comment headers. Reading `chronologia/locale/<code>/*` answers the same question at a finer grain.

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

numtag reads the spelled numbers of the 40 locales in `NUMTAG_LANGS` in `chronologia/extract/numlayer.py`. chronologia keeps no number words for them. The other 21 locales read numbers with their own `numfold_*` module in `chronologia/extract/`. The table names the reader of each locale.

## Pages

| Language | Code | Numbers |
|:---|:---|:---|
| [Albanian](sq.md) | sq | numfold_albanian |
| [Arabic](ar.md) | ar | numtag |
| [Aragonese](an.md) | an | numtag |
| [Armenian](hy.md) | hy | numfold_armenian |
| [Asturian](ast.md) | ast | numtag |
| [Azerbaijani](az.md) | az | numtag |
| [Basque](eu.md) | eu | numtag |
| [Belarusian](be.md) | be | numfold_be |
| [Bulgarian](bg.md) | bg | numtag |
| [Catalan](ca.md) | ca | numtag |
| [Croatian](hr.md) | hr | numtag |
| [Czech](cs.md) | cs | numtag |
| [Danish](da.md) | da | numtag |
| [Dutch](nl.md) | nl | numtag |
| [English](en.md) | en | numtag |
| [Esperanto](eo.md) | eo | numfold_esperanto |
| [Estonian](et.md) | et | numtag |
| [Filipino](fil.md) | fil | numfold_filipino |
| [Finnish](fi.md) | fi | numtag |
| [French](fr.md) | fr | numtag |
| [Galician](gl.md) | gl | numtag |
| [Georgian](ka.md) | ka | numfold_georgian |
| [German](de.md) | de | numtag |
| [Greek](el.md) | el | numtag |
| [Hausa](ha.md) | ha | numfold_chadic |
| [Hebrew](he.md) | he | numtag |
| [Hindi](hi.md) | hi | numfold_indic |
| [Hungarian](hu.md) | hu | numtag |
| [Icelandic](is.md) | is | numfold_icelandic |
| [Indonesian](id.md) | id | numtag |
| [Irish](ga.md) | ga | numfold_irish |
| [Italian](it.md) | it | numtag |
| [Kabyle](kab.md) | kab | numtag |
| [Korean](ko.md) | ko | numfold_korean |
| [Latvian](lv.md) | lv | numfold_latvian |
| [Lithuanian](lt.md) | lt | numfold_baltic |
| [Macedonian](mk.md) | mk | numfold_macedonian |
| [Malay](ms.md) | ms | numtag |
| [Maltese](mt.md) | mt | numfold_maltese |
| [Mirandese](mwl.md) | mwl | numtag |
| [Norwegian Bokmål](nb.md) | nb | numtag |
| [Norwegian Nynorsk](nn.md) | nn | numtag |
| [Occitan](oc.md) | oc | numtag |
| [Persian](fa.md) | fa | numtag |
| [Polish](pl.md) | pl | numtag |
| [Portuguese](pt.md) | pt | numtag |
| [Romanian](ro.md) | ro | numtag |
| [Russian](ru.md) | ru | numtag |
| [Serbian](sr.md) | sr | numfold_slavic |
| [Slovak](sk.md) | sk | numtag |
| [Slovenian](sl.md) | sl | numtag |
| [Spanish](es.md) | es | numtag |
| [Swahili](sw.md) | sw | numfold_bantu |
| [Swedish](sv.md) | sv | numtag |
| [Tamil](ta.md) | ta | numfold_dravidian |
| [Thai](th.md) | th | numfold_thai |
| [Turkish](tr.md) | tr | numtag |
| [Ukrainian](uk.md) | uk | numtag |
| [Vietnamese](vi.md) | vi | numfold_vietnamese |
| [Welsh](cy.md) | cy | numfold_welsh |
| [West Frisian](fy.md) | fy | numtag |

---
[← Transparency: how correctness is checked](../transparency.md) · [Home](../index.md) · [Albanian →](sq.md)
