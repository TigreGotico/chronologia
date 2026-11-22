# Portuguese (`pt`)

<!-- agent-hint
covers: where each construction of the Portuguese locale comes from, what it refuses and which questions a native speaker would settle
source: `chronologia/locale/pt/lang.json`, `chronologia/locale/pt/*.voc`, `chronologia/extract/numlayer.py:NUMTAG_LANGS`
generated: no
verify: python -m doctest docs/languages/pt.md && python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set()\nfor m in re.finditer(r\"`([^`]+)`[^.`\\n]{0,25}?\\b(?:is|are|reads|gives|returns?|resolves? to|comes? back as|=)\\s+(\\d\\d):(\\d\\d)\",pr):\n    ph=m[1]\n    if ph[0]==\"-\": continue\n    r=extract_timespan(ph,c,A)\n    if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2],m[3])\npm=re.sub(r\"`[^`]*`\",lambda m:m[0].replace(\". \",\".\\x01\"),pr)\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(r\"((?:`[^`]+`(?:,| and| or|, and)? ?)+)\\s*(?:both |each |all )?(?:returns?|gives?) (?:nothing|`None`)\",s): cl|=set(x.replace(\"\\x01\",\" \") for x in re.findall(r\"`([^`]+)`\",m[1]))\nex={ast.literal_eval(x) for x in re.findall(r\">>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\",t)}\nif cl!=ex: bad=1;print(\"refusals differ\",cl^ex)\nsys.exit(bad)\n")' docs/languages/pt.md
see: `docs/languages/index.md`, `docs/extraction.md`
-->

This page records where each construction of the Portuguese (`pt`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

No bare day-part word resolves in Portuguese. `manhã` on its own returns
nothing, and so do `tarde`, `noite` and `madrugada`, even though English,
French and Italian all read their bare morning word. The obstacle is not the
word but the slot: one grammar order binds the day-part slot, and that slot
holds every day-part surface the locale ships, so there is no way to admit
`manhã` and refuse its siblings. Admitting the bare form would also admit bare
`tarde`, which is equally the adverb *late* — `mais tarde`, `cheguei tarde`,
`é tarde demais` would each answer a confident afternoon band for a sentence
that names no time. A wrong span is worse than no span, so the bare order stays
off for the whole locale. Nothing is unreachable as a result: `de manhã`,
`pela manhã`, `a manhã` and `esta manhã` all resolve, and that framed form is
what Portuguese actually says.

The other early fact is that `da noite` is a band, not a shift. `dez da noite`
is 22:00 but `uma da noite` is 01:00 — the small hours one to five stay AM, the
evening hours six to eleven are PM, and twelve is midnight. The AM ceiling
follows the `madrugada` band, and the colloquial use of `da noite` for the
small hours is cited to the Dicionário Priberam entry for *noite*.

## What ships

**Weekdays** are the Portuguese ordinal-numbered series, and they ship both
hyphen-glued and spaced — `terça`, `terça feira`, `terças feiras` — because the
tokenizer splits on the hyphen. Months ship wide and abbreviated. Neither
carries a recorded source.

**The date line** is `3 de outubro de 1990`, little-endian with `de` between
the parts, optionally preceded by an article. Portuguese also has the day-label
idiom `dia 3 de outubro`, where `dia` heads the date without being part of it.
The vocabulary cites Cunha e Cintra's *Nova Gramática do Português
Contemporâneo* and Priberam for `dia` being a genuine temporal function word,
and registers it as its own marker so that a leading `dia` is folded into the
consumed text exactly when the date it labels bound — never when the date
fails, so a `dia` elsewhere in the sentence is untouched. That matters most in
range endpoints, where `do dia 3 de março até ao dia 5 de abril` carries two of
them and both must be claimed with their dates. The
slashed numeric date reads; the dotted one does not.

**Relative offsets** are `daqui a` forward and `há` backward. The forward frame
needs an `offsetlink` slot — `a`, `à`, `às`, `ao`, `aos`, `de` — because
Portuguese joins the marker to the count with a preposition that itself
contracts with an article.

**The relative determiners** follow the noun, so the locale sets
`marker_position: post` — `na segunda-feira passada`, `na próxima semana`.

**Ranges** are `de … a …`, `do … ao …`, `desde …`, `a partir de …` and
`até …`, with `entre … e …` as the other frame. Every one of these is cited in
the vocabulary to Priberam, to Ciberdúvidas da Língua Portuguesa, or to Cunha e
Cintra for the obligatory `de`+`o` and `a`+`o` contractions. The from-lead
carries structural weight: `a` is a hyper-common Portuguese preposition, so a
bare `A a B` is only trusted as a range when a from-lead is present.

`até ao` and `até à` are registered as two-word surfaces of their own, tried
before the bare `até`. Without them the scanner found the bare `até` first —
it comes first in the sentence — and left the trailing `ao` an unclaimed token
stranded in the remainder. A bare `até o dia` with no contraction is untouched,
and `até` alone still matches when no contraction follows.

**The clock** has the same two toward-the-hour shapes as Spanish and keeps them
apart for the same reason. `quatro menos um quarto` subtracts from the hour
already named; `um quarto para as quatro` states the fraction first and then
the hour it heads for. Forward is `e` — `oito e meia`, `oito e um quarto`. The
indefinite articles `um` and `uma` are in the article vocabulary specifically
so that the `um quarto` fraction reads, cited to Ciberdúvidas' page on telling
the time. `meio-dia` and `meia-noite` are points.

**Day parts** take their boundaries from the Unicode CLDR 47 day-period chart
for `pt`, transcribed in `chronologia/dayparts.py`: `madrugada`
`[00:00, 06:00)`, `manhã` `[06:00, 12:00)`, `tarde` `[12:00, 19:00)`, `noite`
`[19:00, 24:00)`. The surfaces are cited to Priberam, which glosses `manhã` as
the period between daybreak and midday. The vocabulary records that the entry
marks no European/Brazilian split for these four words and that none is made
here: both varieties say `manhã`, `tarde`, `noite` and `madrugada` alike. The
frame is `pela`/`pelo` and their plurals, the contractions of `por` with the
definite article, cited to Priberam.

**Fuzzy month parts** are `início de`, `meados de` and `fim de`, cutting the
month into thirds.

**Quarters, ISO weeks, decades and eras.** `o primeiro trimestre de 2020`,
`semana 12`, `os anos 80` and `44 a. C.` all resolve, along with an AD marker
and a before-present marker. `a primeira metade de 2020` reads as the first
half-year, with `metade` cited to Priberam.

**The Roman calendar anchors** ship in their Portuguese vernacular forms
`calendas`, `nonas` and `idos`, cited to the Portuguese Wikipedia article
*Calendário romano*.

**Business days** are jurisdiction-aware: the locale carries jurisdiction
vocabularies for Brazil and Portugal alongside Germany, Spain, France, Great
Britain and the United States, so a working-day count can be asked against a
named country's holiday calendar.

## Weaker provenance

The Roman calendar anchors rest on a Wikipedia article, weaker than the
Priberam and Cunha e Cintra citations the rest of the locale is built on.

The weekday and month names, and the seasons, carry no recorded source. The
locale sets `hemisphere` to null, so a season is not resolved to a
southern-hemisphere reading for Brazilian Portuguese.

## What refuses

**Every bare day-part word.** `manhã`, `tarde`, `noite` and `madrugada` return
nothing on their own. This is the locale's defining refusal and the reason is
above.

**The dotted date.** `15.06.2020` returns nothing, and does not fall back to
reading 2020 as a bare year. Portuguese writes the numeric date with slashes.

**A bare duration.** `quinze dias` returns nothing. A fortnight unit ships, but
a quantity with no direction marker is still only a quantity.

## Open questions for a native speaker

1. Where does `da noite` stop being AM? The ceiling sits at five, following
   the `madrugada` band, but `cinco da manhã` and `cinco da madrugada` are both
   ordinary.
2. Should Brazilian Portuguese resolve the seasons to the southern hemisphere,
   and what would select that without a separate locale?
3. Do the day-part bands differ between European and Brazilian usage in ways
   the shared CLDR row hides — in particular where `tarde` ends?
4. Are `calendas`, `nonas` and `idos` the forms Portuguese historical writing
   uses?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("pt")
    True
    >>> span, rest = extract_timespan('dez da noite', "pt", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T22:00:00', '')
    >>> span, rest = extract_timespan('uma da noite', "pt", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T01:00:00', '')
    >>> span, rest = extract_timespan('de manhã', "pt", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T06:00:00', '')
    >>> span, rest = extract_timespan('pela manhã', "pt", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T06:00:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('manhã', "pt", anchor) is None
    True
    >>> extract_timespan('tarde', "pt", anchor) is None
    True
    >>> extract_timespan('noite', "pt", anchor) is None
    True
    >>> extract_timespan('madrugada', "pt", anchor) is None
    True
    >>> extract_timespan('15.06.2020', "pt", anchor) is None
    True
    >>> extract_timespan('quinze dias', "pt", anchor) is None
    True

---
[← Polish](pl.md) · [Home](../index.md) · [Romanian →](ro.md)
