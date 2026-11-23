# Language provenance pages

<!-- agent-hint
covers: which languages have a provenance page, how each page is organised and which reader handles the numbers of each locale
source: `chronologia/locale/*/lang.json`, `chronologia/extract/numlayer.py:NUMTAG_LANGS`, `chronologia/extract/numfold_*.py`
generated: no
verify: python -c 'exec("import re,glob,os,json\nfrom chronologia.extract.numlayer import NUMTAG_LANGS as N\nT=open(\"docs/languages/index.md\").read()\nrows=re.findall(r\"^\\| \\[[^]]*\\]\\((\\w+)\\.md\\) \\| (\\w+) \\| (\\S+) \\|\",T,re.M)\nc={os.path.basename(os.path.dirname(f)) for f in glob.glob(\"chronologia/locale/*/lang.json\")}\nassert {r[1] for r in rows}==c and len(rows)==len(c)\nfor pg,code,rd in rows:\n    assert pg==code and os.path.exists(\"docs/languages/\"+pg+\".md\")\n    h=json.load(open(\"chronologia/locale/\"+code+\"/lang.json\")).get(\"hook\",\"\")\n    assert (rd==\"numtag\")==(code in N)\n    assert rd==\"numtag\" or h.startswith(\"chronologia.extract.\"+rd+\":\"),(code,rd,h)\nassert \"the \"+str(len(N))+\" locales in\" in T and \"other \"+str(len(c)-len(N))+\" locales\" in T\n")'
see: `docs/index.md`, `docs/extraction.md`
-->

chronologia never guesses a linguistic surface. A construction ships in a
locale only where an attested source supports it, and where the sources
conflict or nothing attests the phrase at all, the locale is left without it
and the phrase returns nothing. That rule is what makes a wrong answer rare;
it is also why some perfectly ordinary-looking phrase in your language may
come back empty.

These pages are the record. One page per language explains where each group of
surfaces came from, which ones rest on thinner evidence than the rest, exactly
which constructions were refused and why, and what a native speaker would have
to settle to close the remaining gaps.

Every locale has a page. The vocabulary files themselves carry their sources in comment headers, and reading `chronologia/locale/<code>/*.voc` answers the same question at a finer grain.

## How to read a page

Every page follows the same shape.

**What ships** walks the constructions in the order a reader meets them —
weekdays and months, the date line, relative offsets, the clock, day parts,
numerals, and markers — and names the source for each group precisely enough
to fetch again. Where a group has one source it says so; where two independent
sources agree it says that too, because the difference matters when you are
deciding how far to trust a surface.

**Weaker provenance** collects anything shipped on thinner evidence than the
rest of the page. These surfaces work, and they are not errors, but they are
the first place to look when a locale disagrees with a native speaker.

**What refuses** is the section most readers actually want. It lists the
constructions deliberately left out, each with the reason, so that "why does
this phrase return nothing?" has an answer other than "unknown". A refusal is
a design decision, not a missing feature: it is the library declining to
invent a surface it cannot attest, or declining to pick a reading where the
language itself is genuinely ambiguous.

**Open questions** are the items a native speaker would settle. They are kept
separate from everything above and are never quietly resolved by analogy.

## Citation discipline

A source named on these pages was consulted directly. Author-and-year is used
where a claim is standard; a section or page locator appears only where that
exact locator was checked. Where a source was sought and not reached, the page
says so rather than implying it was read. The output of another date parser is
never cited as evidence about a language.

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
