# Romanian (`ro`)

<!-- agent-hint
covers: where each construction of the Romanian locale comes from, what it refuses and which questions a native speaker would settle
source: `chronologia/locale/ro/lang.json`, `chronologia/locale/ro/*.voc`, `chronologia/extract/numlayer.py:NUMTAG_LANGS`
generated: no
verify: python -m doctest docs/languages/ro.md && python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\">>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\",t)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/ro.md noapte@00:00
see: `docs/languages/index.md`, `docs/extraction.md`
-->

This page records where each construction of the Romanian (`ro`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

Romanian is the deepest calendar locale in the project outside the reference
locales: alongside the Gregorian calendar it ships the Roman calendar
(kalends, nones, ides), the French Republican calendar, the Hebrew calendar,
the Islamic civil calendar, and Japanese regnal eras — all through Romanian
vernacular vocabulary or a mix of vernacular and retained Latin/foreign
forms. The scale of that surface is worth stating up front, because it means
most of this page's citation weight sits on the everyday layer — weekdays,
months, the clock, the day parts, ranges — where a Romanian speaker actually
lives, while the calendar layer is mechanically wired rather than richly
sourced.

The second thing to know is the definite article. Romanian attaches it as an
enclitic — `luni` is Monday, `lunea` is "on Monday" in the sense that governs
`lunea trecută`, "last Monday" — and the weekday vocabulary ships both forms
because the articulated one is the ordinary written shape in a relative
phrase.

## What ships

**Weekdays** ship bare and articulated, each cited to dexonline (the
_Dicționarul explicativ al limbii române_) and to DOOM (the Romanian Academy's
orthographic-orthoepic dictionary) for the definite-article form of each day
name — `luni`/`lunea`, `marți`/`marțea`, `miercuri`/`miercurea`,
`joi`/`joia`, `vineri`/`vinerea`, `sâmbătă`/`sâmbăta`. `duminică` is the
exception: its file ships only the two diacritic spellings of the bare noun
(`duminică`/`duminica`) with no dexonline/DOOM citation comment and no
articulated `duminica`-with-enclitic-article form alongside them — the one
weekday in the set without the citation the other six carry.

**Months** ship bare with a three-letter abbreviation (`ianuarie`/`ian`), no
recorded source beyond the abbreviation being the conventional Romanian
month short-form.

**The date line** is little-endian in both the spelled and the dotted civil
form (`dotted_date: true`), matching every level of the CLDR `ro`
`ca-gregorian` chart: full `EEEE, d MMMM y`, long `d MMMM y`, medium `d MMM y`,
short `dd.MM.y` — day first throughout, unlike Persian's short pattern.

**Relative offsets** are `acum` for the past (`acum trei zile`, "three days
ago") and `peste`/`în` for the future, plus a quantifier-led order
(`o săptămână`, `câțiva ani`) that reads `un`/`o` (one), `pereche` (a pair,
two), and `câțiva`/`câteva` (a few, three) as counts in either position
relative to the unit and marker.

**The clock** is additive past the hour and subtractive toward it, the same
direction English uses. `și` ("and") leads the fraction past the hour —
`trei și un sfert` is 3:15, `nouă și jumătate` is 9:30 — and `fără`
("without") subtracts from the *next* hour — `patru fără un sfert` is 3:45.
That direction is confirmed by two independent sources with worked numeric
examples: the project's own test corpus (`trei și un sfert` → 3:15,
`patru fără un sfert` → 3:45, checked against independent arithmetic on a
fixed anchor) and Romania Insider's Romanian-language lesson, which glosses
`Este unu și un sfert` as "It's quarter past one" and `Două fără un sfert` as
"It's quarter to two" — the same hour-relative-to-:30 switch the shipped
vocabulary encodes. `sfert` ("quarter") is independently confirmed at its
Wiktionary lemma entry, glossed "quarter" or "fourth", with `pătrime`/
`pătrar` given as synonyms and a Church Slavic borrowing history that also
produced Ukrainian `чверть` — the same root family, unrelated surface. The
landmarks are `amiază`/`amiaza`/`prânz`/`pranz` (noon) and `miezulnoptii`
(midnight), and the meridiem words `dimineața` (literally "in the morning",
doubling as the AM marker) and `seara` ("in the evening", the PM marker).

**Day parts** take their boundaries from the Unicode CLDR 47 day-period chart
for `ro`, cross-checked directly against the CLDR JSON `dayPeriodRuleSet`:
`dimineață` `[05:00, 12:00)`, `după-amiaza` `[12:00, 18:00)`, `seară`
`[18:00, 22:00)`, `noapte` `[22:00, 05:00)`. The vocabulary comments also cite
dexonline for the surfaces themselves. Two things are worth flagging in how
these were shipped. First, `după-amiaza` is registered as a glued multi-token
surface rather than the bare noun, because the tokenizer splits the hyphen
and, without the glued form, the resulting bare `amiaza` half of
`după-amiaza` collided with `amiaza` the noon landmark and lost to it.
Second, Romanian is the only locale among the ones documented on this site
where the CLDR chart lists `noapte` twice — once at 00:00 and again at
22:00 — because the night band genuinely wraps across midnight, and the
vocabulary comment notes this is a deliberate join rather than a duplicate
entry.

**Ranges** are `între … și …` and `de la … (până) la …`.

**Quarters, ISO weeks, decades, centuries and millennia.** `trimestrul` reads
a numbered or ordinal quarter; `săptămâna` an ISO week; the spelled decades
`douăzeci`, `treizeci` … `nouăzeci` each ship their own file rather than a
shared number grammar; `secol` (century) and `mileniu` (millennium) both
resolve, the latter one of 31 locales that ship a dedicated millennium unit.

**Eras.** `d.hr.`/`după hristos`/`dupa hristos` (AD) and `î.hr.`/`i.hr.`/
`înainte de hristos` (BC) both ship spaced and unspaced abbreviation
variants. `bp`/`ani înainte de prezent` (before present), `anno mundi`, and
an "era holocenă/umană" (Holocene/Human Era) marker also resolve, alongside
Julian day number and Unix time prefixes.

**The Roman calendar** — kalends, nones and ides — ships both the Latin
classical forms (`kalendis`, `nonis`, `idibus`) and Romanian vernacular ones
(`calendele`, `nonele`, `idele`), cited to the Romanian Wikipedia article
"Calendarul roman", which names all three together: "... calendele, idele și
nonele".

**Fuzzy month/period parts** are `început`/`inceput` (early), `mijloc` (mid),
`sfârșit`/`sfarsit`/`final` (late).

## Weaker provenance

The weekday and month names carry stronger provenance than most locales
documented here (dexonline/DOOM citations for the weekdays); the months
themselves do not, and neither do the seasons, the holiday vocabulary, or
the French Republican, Hebrew, Islamic civil, and Japanese-regnal calendar
month lists, all of which ship as bare transliterations without a cited
source.

The clock-direction claim rests on a Romanian-language-learning source
(Romania Insider) rather than a linguistic reference grammar; it is
independent of the project's own tests and gives worked numeric examples, but
a formal grammar citation for the :30 switch point was not located and would
strengthen this page.

## What refuses

**A bare quantifier with no direction.** `câțiva ani` alone, with no `acum`,
`peste` or similar marker, is a count without a direction and is not
expected to resolve to a specific offset — consistent with the general
pattern (also documented for Russian) that a quantity needs a marker to
become a point in time.

## Open questions for a native speaker

1. Is the :30 switch from `și` to `fără` as clean in ordinary speech as the
   Romania Insider source states, or do speakers vary near the boundary
   (`trei și douăzeci și cinci` vs `patru fără douăzeci și cinci`)?
2. Do the French Republican, Hebrew, and Islamic civil month vocabularies
   need a Romanian-specific citation, or is the bare transliteration what
   Romanian sources actually use for these calendars?
3. Should `duminică` carry the same dexonline/DOOM citation and an
   articulated form the way the other six weekdays do, and if the enclitic
   article genuinely does not attach to `duminică` the way it attaches to
   `luni`/`lunea`, is that worth a comment recording the reason?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("ro")
    True
    >>> span, rest = extract_timespan('lunea trecută', "ro", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-26T00:00:00', '')
    >>> span, rest = extract_timespan('acum trei zile', "ro", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-24T00:05:00', '')
    >>> span, rest = extract_timespan('trei și un sfert', "ro", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T03:15:00', '')
    >>> span, rest = extract_timespan('nouă și jumătate', "ro", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T09:30:00', '')

---
[← Portuguese](pt.md) · [Home](../index.md) · [Russian →](ru.md)
