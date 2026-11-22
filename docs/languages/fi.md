# Finnish (`fi`)

<!-- agent-hint
covers: where each construction of the Finnish locale comes from, what it refuses and which questions a native speaker would settle
source: `chronologia/locale/fi/lang.json`, `chronologia/locale/fi/*.voc`, `chronologia/extract/numlayer.py:NUMTAG_LANGS`
generated: no
verify: python -m doctest docs/languages/fi.md && python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\">>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\",t)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/fi.md
see: `docs/languages/index.md`, `docs/extraction.md`
-->

This page records where each construction of the Finnish (`fi`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

Finnish has no prepositions to speak of. Where another language puts a word in
front of a noun to say "at", "from" or "until", Finnish puts a case ending on
the end of it: `maanantaista` is "from Monday", `perjantaihin` is "to Friday",
`kello kolmelta` is "at three o'clock". That is the fact that governs
everything on this page. A vocabulary file for Finnish is not a list of words
but a list of *forms*, and the constructions a locale can read are exactly the
ones whose case it happens to have shipped. Where a case is missing the phrase
does not degrade — it either returns nothing at all, or, more dangerously, it
resolves without the ending and returns a confident answer to a different
question.

## What ships

**Months** ship in four cases each: the nominative `elokuu`, the partitive
`elokuuta` that a day-led date takes, the genitive `elokuun` that leads a
month-led one, and the inessive `elokuussa` for "in August". The nominative set
matches the CLDR 47 `fi` `ca-gregorian` stand-alone wide chart and the
partitive set matches its format wide chart, which is partitive throughout for
Finnish. So `15. elokuuta 2020` and `elokuun 15.` reach the same day and
`elokuussa` reaches the month.

**Weekdays** ship in the nominative and the essive — `maanantai` and
`maanantaina` — and CLDR 47 accounts for both, the stand-alone wide chart
giving the nominative and the format wide chart the essive for six of the
seven. CLDR's format chart has Sunday in the nominative where the other six are
essive; the locale ships both forms for all seven and is the more complete for
it.

**The date line** is little-endian and dotted. CLDR 47 gives `d.M.y` for both
the medium and the short `fi` format, and the tokenizer runs with `dotted_date`
and `ordinal_dot` on, so `3.6.2020` resolves and so does the ordinal spelling
`15. elokuuta 2020`. numtag reads a spelled ordinal such as `viidestoista` as a single
compound word, so `viidestoista huhtikuuta` binds the fifteenth. Iso suomen
kielioppi §770 is the grammar reference the numeral module names for the
ordinal series.

**Relative offsets** are built from postpositions, not prepositions:
`kahden viikon päästä` is in two weeks, `kaksi viikkoa sitten` is two weeks
ago, `kolmen viikon kuluttua` is in three weeks. The numeral in the forward
frame is genitive, a form the number back-end does not read, so the genitives
one through twenty are given to the fold explicitly along with `puolen` and
`puolentoista`. The unit nouns ship in the nominative, partitive and genitive,
and the CLDR-attested oblique case beside them.

**Relative periods** take the case CLDR records for each field, and the
vocabulary comments name the chart and the exact strings. The week is adessive
(`viime viikolla`, `tällä viikolla`, `ensi viikolla`), the year essive
(`viime vuonna`, `tänä vuonna`, `ensi vuonna`), and the month inessive on the
short noun `kuu` rather than on `kuukausi` (`viime kuussa`, `tässä kuussa`,
`ensi kuussa`). Every one of those nine strings is in CLDR 47's `fi`
`dateFields` at the relative type the comment claims, and the demonstrative
ships in all three cases the three fields require — `tänä`, `tässä`, `tällä` —
for exactly that reason.

**The clock** binds a digit hour after `kello` or `klo`, or bare, and reads the
ablative telling-time forms as hours in their own right. `kello kolmelta` and
the bare `kolmelta` both give three o'clock, because the ablative numerals one
through twelve are listed explicitly and a bare one synthesises the missing
`kello`. Wiktionary's entry for the suffix `-lta` identifies the ablative;
Iso suomen kielioppi §1237 is cited alongside it for the telling-time use, and
that section is unchecked. `keskiyöllä` and `keskipäivällä`
are midnight and noon, and both are CLDR 47's `fi` day-period labels for those
two points.

**The half hour runs toward the coming hour.** `puoli kymmenen` is 09:30, not
10:30 — the hour named is the one being approached. The reading is enabled by
`bare_half_to` and read through a `FRACTION HOUR` order, and 25 locales use the
same flag. `puoli yksi` is 00:30 or 12:30, whichever comes next after the
anchor (ruling 17 in [the rulings](../rulings.md)).

**Named days** span the five positions around the anchor and are exactly CLDR
47's `fi` day field for relative types −2 through +2: `toissa päivänä`,
`eilen`, `tänään`, `huomenna`, `ylihuomenna`. The solid spelling
`toissapäivänä` ships beside the spaced one, and the comment's justification
holds up — CLDR's short and narrow charts write the same phrase solid as
`toissap.`

**The quarter** has two names in CLDR 47's `fi` `dateFields`, the long
`neljännesvuonna` and the short `neljänneksenä`, both essive, both attested in
the relative phrases; the vocabulary ships both alongside the nominative and
adessive forms. `Q3 2020` and `viikko 33` resolve through the Latin-letter and
week-number paths.

**Quantifier words** are declared for the approximate counts Finnish uses
instead of a numeral: `pari` for two, `muutama` for three, `puoli` for a half,
`neljännes` and `vartti` for a quarter. They reach the duration reader, where
`pari viikkoa` is fourteen days and `puoli tuntia` is thirty minutes.

**Fuzzy periods** read `alku`, `loppu` and `puoliväli` with their inessive and
adessive forms, so `elokuun alussa` and `elokuun lopussa` return the first and
last thirds of the month.

**Seasons, eras, business days and recurrence** all resolve. The seasons ship
in the nominative and adessive; the eras carry both the secular `eaa.`/`jaa.`
and the Christian `eKr.`/`jKr.`; `arkipäivä` and `työpäivä` drive the
business-day count; and `joka maanantai`, `päivittäin` and `viikoittain` all
come back as recurrences.

## Weaker provenance

**The ablative hour table has one reachable source and one that could not be
checked.** Wiktionary's `-lta` entry resolves and identifies the case, but it
says nothing about telling the time — its usage note only points at the general
appendix on Finnish nominal cases. The telling-time claim rests entirely on the
Iso suomen kielioppi section named beside it, and that site answers a fetch
with a challenge page rather than the text. The forms themselves are ordinary
and uncontroversial; it is the locator that is unconfirmed.

**No source is recorded for the case selection.** The month vocabulary ships
four cases and the weekday vocabulary two, and nothing on file says why those
and not others, or whether the set is complete for the constructions the locale
claims to read. The gaps below suggest it is not.

## What refuses

**Every case-marked range.** This is the largest gap on the page and it follows
directly from the language's own grammar. Finnish opens a range with the
elative and closes it with the illative — `maanantaista perjantaihin`,
`tammikuusta maaliskuuhun`, `yhdeksästä viiteen` — and no vocabulary file in
the locale ships an elative or an illative of a month, a weekday or a unit
noun. The months have nominative, partitive, genitive and inessive; the
weekdays have nominative and essive; the units have nominative, partitive,
genitive and one CLDR-attested oblique. So all three of those phrases return
nothing at all. What does work is the postpositional frame, `tammikuun ja
maaliskuun välillä`, and the two bound words `alkaen` and `asti`/`saakka`
declared as trailing markers.

**The postposition for "after".** `vuoden 2020 jälkeen` resolves the year and
strands `jälkeen`, so the phrase reads as the year itself rather than as
everything past it. The engine allows a locale to declare where a marker sits
for four roles — until, since, for, from — and "after" is not one of them, so
there is no way to declare `jälkeen` as the postposition it is.

**The half hour in the ablative.** `puoli kymmenen` resolves and
`puoli kymmeneltä` does not: the fraction order wants a bare hour, the ablative
hour fold produces a clock token instead, and the two do not compose. The
result is 10:00 with `puoli` stranded, which is thirty minutes and one hour
away from what the phrase says.

**The quantifier words in an offset.** `pari` and `muutama` are declared as two
and three and reach the duration reader correctly, but not the relative-offset
grammar. `pari viikkoa sitten` returns one week ago with `pari` in the
remainder, and `muutama viikko sitten` returns the same. The mechanism exists —
the English locale resolves "a couple of weeks ago" and "a few weeks ago" to
two and three weeks — so this is a wiring gap rather than an engine limit, and
it is the one gap on this page where the same locale answers the same word two
different ways depending on which reader sees it.

**Abbreviations.** CLDR 47 gives clipped month names for `fi` — `tammi`,
`helmi`, `maalis` and the rest — and two-letter weekdays, `su ma ti ke to pe
la`. Neither set ships, so `15. elo 2020` returns the whole of 2020 with the
day and month stranded, and `ma 15.6.2020` returns the day with `ma` left over.
Twenty-five of the locales here ship an abbreviated weekday file.

**The dotted date without a year.** `3.6.2020` resolves. `3.6.` returns nothing, although it is how a
Finnish diary writes a day.

**The decade by its ordinary name.** Finnish names a decade with `-luku`
attached to the year — `1990-luku`, `1990-luvulla`. Neither resolves: the
scope-unit vocabulary has `vuosikymmen` and the year binds on its own, so both
return the single year 1990 and strand the decade word. Nine of the locales
here ship a spelled-decade vocabulary and this is not one of them.

**A bare ip.** `kello 9 ip.` resolves to 21:00, but `9 ip.` alone returns
nothing, because every meridiem-bearing clock order requires the o'clock word
in front.

## Open questions for a native speaker

1. Which cases of a month, a weekday and a unit noun does a date or range
   phrase actually need — is it the full elative and illative pair for each, or
   do the postpositional frames carry enough of the load in practice?
2. Is the period-separated clock (`klo 9.15`) dominant over the colon in
   running text?
3. Does `puoli yksi` mean half past twelve noon, half past midnight, or
   whichever of the two the context makes plausible?
4. Is `1990-luvulla` the ordinary way to name a decade in speech, or does
   `vuosikymmen` carry that weight outside written registers?
5. Are `pari` and `muutama` precise enough in a temporal offset to bind to two
   and three, or is the vagueness part of what a speaker means by them?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("fi")
    True
    >>> span, rest = extract_timespan('puoli kymmenen', "fi", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T09:30:00', '')
    >>> span, rest = extract_timespan('kello kolmelta', "fi", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T03:00:00', '')
    >>> span, rest = extract_timespan('viidestoista huhtikuuta', "fi", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2018-04-15T00:00:00', '')
    >>> span, rest = extract_timespan('kahden viikon päästä', "fi", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-07-11T00:05:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('3.6.', "fi", anchor) is None
    True

---
[← Filipino](fil.md) · [Home](../index.md) · [French →](fr.md)
