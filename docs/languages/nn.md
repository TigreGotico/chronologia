# Norwegian Nynorsk (`nn`)

<!-- agent-hint
covers: where each construction of the Norwegian Nynorsk locale comes from, what it refuses and which questions a native speaker would settle
source: `chronologia/locale/nn/lang.json`, `chronologia/locale/nn/*.voc`, `chronologia/extract/numlayer.py:NUMTAG_LANGS`
generated: no
verify: python -m doctest docs/languages/nn.md && python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set()\nfor m in re.finditer(r\"`([^`]+)`[^.`\\n]{0,25}?\\b(?:is|are|reads|gives|=)\\s+(\\d\\d):(\\d\\d)\",pr):\n    ph=m[1]\n    if ph[0]==\"-\" or not re.search(r\"[^\\W\\d_]\",ph): continue\n    r=extract_timespan(ph,c,A)\n    if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2],m[3])\npm=re.sub(r\"`[^`]*`\",lambda m:m[0].replace(\". \",\".\\x01\"),pr)\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(r\"((?:`[^`]+`(?:,| and| or|, and)? ?)+)\\s*(?:both |each |all )?(?:returns?|gives?) (?:nothing|`None`)\",s): cl|=set(x.replace(\"\\x01\",\" \") for x in re.findall(r\"`([^`]+)`\",m[1]))\nex={ast.literal_eval(x) for x in re.findall(r\">>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\",t)}\nif cl!=ex: bad=1;print(\"refusals differ\",cl^ex)\nsys.exit(bad)\n")' docs/languages/nn.md
see: `docs/languages/index.md`, `docs/extraction.md`
-->

This page records where each construction of the Norwegian Nynorsk (`nn`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

The half hour names the coming hour: `halv to` is 01:30, not 02:30.
`bare_half_to` is set for that. The quarter takes its direction from the word
beside it, `over` counting up from the named hour and `på` counting down toward
it, so `kvart over to` is 02:15 and `kvart på tre` is 02:45.

The fact that shapes everything else is a pair of collisions in the day
vocabulary. `i morgon` is tomorrow and `morgon` is the morning, and `i går` is
yesterday while `går` is what the verb *å gå* does in the present tense. This
locale ships the bare halves of both pairs as day names, and both collisions
fire.

Nynorsk shares its written month names, most of its clock words and its numeral
system with Bokmål, so a locale assembled carelessly reads as Bokmål with a few
words changed. This one does not: the weekdays are `måndag`, `laurdag` and
`sundag` rather than the Bokmål `mandag`, `lørdag` and `søndag`; the units are
`månad`, `veke` and `time`; the determiners are `førre` and `komande`; the
one-and-a-half quantifier is `halvannan`; the season is `sommar`. The two
Bokmål forms that did get in are named under weaker provenance below.

## What ships

**Weekdays and months** ship wide and abbreviated, with no recorded source.

**The named days** cite CLDR 47 `dateFields.json` for `nn`, and the citation
holds exactly: the day rows there read `i førgår`, `i går`, `i dag`, `i morgon`
and `i overmorgon`, and all five of those surfaces ship and resolve cleanly.
What CLDR does not carry is the nine additional surfaces shipped beside them —
`idag`, `igår`, `går`, `imorgon`, `morgon`, `forgårs`, `iforgårs`, `overmorgon`
and `iovermorgon`. Those are uncited, and two of them cause the defects listed
below.

**The date line** is little-endian and Nynorsk writes the dotted civil date, so
`15.06.2020` reads, as do `15-06-2020` and the ISO `2020-06-15`. `ordinal_dot`
is on and the dotted ordinal day is the ordinary written form: `15. juni 2020`.
Spelled ordinals read too — `fyrste juni`, `andre juni`, `tjueandre juni` — and
the locale supplies its own `calendar_date` orders rather than the shared ones.

**Relative offsets** are `om` forward and `sidan` backward, with `for` optional
in front of a backward count: `om tre dagar`, `for tre dagar sidan`.
`halvannan` works as the one-and-a-half quantifier in both directions.

**The clock** reads `klokka` or `kl` as the "at" marker, with `midnatt` and
`middag` as the landmark points. `kl 14` reads as a bare 24-hour hour.

**Day parts** are `natt` `[00:00, 06:00)`, `føremiddag` `[10:00, 12:00)`,
`ettermiddag` `[12:00, 18:00)` and `kveld` `[18:00, 24:00)`, transcribed in
`chronologia/dayparts.py`, each in the bare and the definite form. The
five-part Nordic day is why `føremiddag` exists: it is the late morning that
English cannot name in one word, and the `morgon` that precedes it is
correspondingly short.

The boundaries come from the CLDR 47 supplemental day-period chart. The chart
does carry an `nn` row, and it gives exactly these boundaries — 00:00, 06:00,
10:00, 12:00, 18:00 — but every surface name in that row is marked missing. The
Bokmål `nb` row is identical in both respects. The names live only in the
generic Norwegian `no` row, and they are Bokmål: `morgen`, `formiddag`,
`ettermiddag`, `kveld`. The boundaries this locale uses are therefore its own
row's whether they are read from `no` or from `nn`; only the names would have
been Bokmål had they been taken from the chart, and they were not. They come
from Nynorskordboka instead.

That citation checks out. The Nynorskordboka entry for `føremiddag` at
`ord.uib.no` glosses it *tid frå morgon til ettermiddag* and *periode frå
frukost til klokka tolv eller middagstid*, which is the 10:00-to-noon band the
locale ships, and it gives `føremiddagen` as the definite singular. The
vocabulary files quote that gloss with the Norwegian vowels transliterated to
ASCII, so `frå` appears there as `fra`; that is the same transliteration the
file headers apply to `Språkrådet`, not a Bokmål reading of the source.

**Ranges** are `frå … til …` and `mellom … og …`, with `sidan` opening one that
runs to the anchor and `til` closing one that starts there.

**Quarters, ISO weeks, decades and eras.** `fyrste kvartal 2020`, `veke 12`,
`80-talet`, `44 f.kr.` and an AD marker all resolve, along with a
before-present marker and the full deep-time period vocabulary.

**Fuzzy month parts** are `byrjinga av`, `midten av` and `slutten av`.

**The ordinal-last determiner** is `siste`, cited to Nynorskordboka, so
`siste måndag i mai` resolves. The dictionary carries `siste` as an inflected
form of the lemma `sist`.

## Weaker provenance

Two Bokmål forms ship. `tallet` sits beside the Nynorsk `talet` in the
decade-marker vocabulary, so `80-tallet` resolves in a Nynorsk locale;
`formiddag` and `formiddagen` sit beside `føremiddag` and `føremiddagen`. Both
are the kind of surface a Nynorsk writer might actually type, and neither does
any harm, but neither is Nynorsk and neither is cited.

Outside the day parts, the named days and `siste`, nothing in this locale
records a source. The weekday and month names, the clock words, the range
markers, the seasons and the numeral vocabulary carry none.

## The half hour toward one

A bare toward-hour phrase for one o'clock names the half hour before one, 00:30 or 12:30. It resolves to whichever of the two comes next after the anchor (ruling 17 in [the rulings](../rulings.md)): `halv eitt` is 00:30 at 13:04 and 12:30 at 06:05. `toward_hour_12h` only renames hour 0 as 12 on that path, so it changes no bare reading. This locale binds no meridiem word, so `halv eitt om ettermiddagen` returns 00:30 and leaves `om ettermiddagen` in the remainder. `kvart på eitt` and `fem på eitt` follow the same rule.

## What refuses

**Any day-part word after a clock time.** `klokka åtte om kvelden` returns
08:00 and leaves `om kvelden`; `halv åtte om kvelden` returns 07:30 and leaves
the same. The band words resolve on their own — `kvelden` alone is 18:00 to
midnight — but nothing binds one to a preceding hour as a meridiem, so every
evening time comes back as its morning twin with the evening word stranded.
This is the locale's largest gap.

**The morning band.** `morgonen` returns nothing. `chronologia/dayparts.py`
declares a `morgon` band at `[06:00, 10:00)` for this locale, but no vocabulary
file supplies its surfaces, so the band is unreachable — the bare `morgon` is
claimed by the tomorrow vocabulary instead.

**A bare duration.** `tre veker` and `14 dagar` return nothing. A quantity with
no direction marker is still only a quantity.

**A recurrence.** `kvar dag` and `dagleg` return nothing. The "every" and
frequency words ship but no construction reads them.

**A spelled half or quarter of an hour.** `om ein halv time` and `om eit
kvarter` return nothing, although `om halvannan time` reads.

**A forward-looking "after".** `etter måndag` returns nothing.

**A four-digit clock.** `14.30` and `klokka 14.30` return nothing; the dotted
form reads as a date, not a time.

## Known defects

Each returns a wrong or partial answer rather than nothing.

`eg går til butikken` ("I walk to the shop") → 26 June, yesterday, with
remainder `eg til butikken`. The bare `går` ships as a yesterday surface, and it
is also the present tense of *å gå*, one of the commonest verbs in the language.
CLDR gives `i går` and only `i går`.

`god morgon` → 28 June, tomorrow, with remainder `god`. `måndag morgon` returns
Monday and strands `morgon`. The bare `morgon` ships as a tomorrow surface; in
Nynorsk it is also, and more basically, the morning. CLDR gives `i morgon`.

`tolv om natta` → the night band 00:00 to 06:00 of the anchor day, with
remainder `tolv om`. The hour is dropped and a six-hour band is returned in
place of a point in time.

`klokka åtte om kvelden` → 08:00 with remainder `om kvelden`. The meridiem gap.

`i forgårs` → 25 June with remainder `i`. The vocabulary ships `forgårs` and
`i førgår` but not `i forgårs`, so the commonest spelling of the phrase parses
with its preposition stranded. `i førgår` parses clean.

`i natt`, `i kveld`, `i helgi`, `i juni` and `i 1990` all return the right span
with `i` in the remainder. `under juni` strands `under`. `frå måndag` returns
the whole of the following Monday and strands `frå`, so an open range starting
at a weekday is silently reduced to that weekday.

`kvar måndag` → the next single Monday with remainder `kvar`.

## Open questions for a native speaker

1. Said in the middle of the afternoon, does `halv eitt` mean 00:30 or 12:30,
   and is one of the two clearly the ordinary reading?
2. What is the connector that binds a day part to a spoken hour, and which
   day-part forms take it?
3. Should the bare `går` and `morgon` be day names at all, given the verb and
   the noun they collide with?
4. What are the ordinary surfaces for the morning band, and does the 10:00
   boundary with `føremiddag` match how the words are used?
5. Is `helgi` current beside `helga`, and is `weekend` written in Nynorsk?
6. Which of `fjerdedel` and `kvart` is the ordinary quarter-of-an-hour word?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("nn")
    True
    >>> span, rest = extract_timespan('halv to', "nn", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T01:30:00', '')
    >>> span, rest = extract_timespan('kvart over to', "nn", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T02:15:00', '')
    >>> span, rest = extract_timespan('kvart på tre', "nn", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T02:45:00', '')
    >>> span, rest = extract_timespan('kvelden', "nn", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T18:00:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('morgonen', "nn", anchor) is None
    True
    >>> extract_timespan('tre veker', "nn", anchor) is None
    True
    >>> extract_timespan('14 dagar', "nn", anchor) is None
    True
    >>> extract_timespan('kvar dag', "nn", anchor) is None
    True
    >>> extract_timespan('dagleg', "nn", anchor) is None
    True
    >>> extract_timespan('om ein halv time', "nn", anchor) is None
    True
    >>> extract_timespan('om eit kvarter', "nn", anchor) is None
    True
    >>> extract_timespan('etter måndag', "nn", anchor) is None
    True
    >>> extract_timespan('14.30', "nn", anchor) is None
    True
    >>> extract_timespan('klokka 14.30', "nn", anchor) is None
    True

---
[← Norwegian Bokmål](nb.md) · [Home](../index.md) · [Occitan →](oc.md)
