# Danish (`da`)

<!-- agent-hint
covers: where each construction of the Danish locale comes from, what it refuses and which questions a native speaker would settle
source: `chronologia/locale/da/lang.json`, `chronologia/locale/da/*.voc`, `chronologia/extract/numlayer.py:NUMTAG_LANGS`
generated: no
verify: python -m doctest docs/languages/da.md && python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\">>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\",t)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/da.md 'fem over halv ti@09:35' 'kun op til et halvt døgn@18:49' morgen@05:00
see: `docs/languages/index.md`, `docs/extraction.md`
-->

This page records where each construction of the Danish (`da`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

Danish names the **coming** hour on the half. `halv to` is 01:30, not 02:30,
and `halv tolv` is 11:30. The Danish Wikipedia article *Klokken* states the
rule as a subtraction — `"Halv ...[indsæt timetal]" (en halv time fratrukket)`
— alongside the two quarter forms, `"Kvart i ..."` a quarter subtracted and
`"Kvart over ..."` a quarter added. `bare_half_to` in `lang.json` is what turns
the half on; the quarters take their direction from the preposition beside
them, `over` counting up and `i` counting down.

The same article records the fact that governs everything awkward about this
locale: everyday Danish reckons the clock in two twelve-hour cycles, `"Et" til
"tolv", underforstået 'timer' (2 cykler på en dag)`, and normally speaks it
`kun op til et halvt døgn` — its worked example turns 18:49 into `kvart i syv`.
"The hour before one" below gives the rule for `halv et` and `kvart i et`.

## What ships

**Weekdays and months** ship wide and abbreviated, with no recorded source.

**The named days** come from Unicode CLDR 47,
`cldr-dates-full/main/da/dateFields.json`, whose five day relative-type entries
are `i forgårs`, `i går`, `i dag`, `i morgen` and `i overmorgen`. Each ships
beside a solid-spelled twin — `iforgårs`, `igår`, `idag`, `imorgen`,
`iovermorgen` — and the bare `går`, `morgen`, `forgårs` and `overmorgen` ship
as well. Those extra forms are not in the cited file.

The bare `morgen` is the one that costs something. It is registered as
tomorrow, which is what CLDR's `i morgen` means once the `i` is dropped, but
`morgen` on its own is also the ordinary Danish word for the morning. A bare
`morgen` therefore resolves to tomorrow's whole day.

**The date line** is little-endian with a dotted ordinal day: `den 3. oktober
1990` resolves, so does the bare `3. oktober 1990`. `ordinal_dot` is on and
Danish writes the dotted civil date, so `15.06.2020` reads, as does the ISO
`2020-06-15`.

**The dotted timetable clock.** `14.30` reads the same as the colon form `14:30`. The `dotted_clock` tokenizer mode, which Finnish and Danish declare, reads it. The dotted date stays whole (`3.6.2020` is 3 June 2020), and plain decimals such as `1.000` and `2.5` fall through to the number rule. `klokken 14.30` returns 14:30 with `klokken` left in the remainder.

**Relative offsets** are `om` forward and `siden` backward, with `for` licensed
as a leading before-marker, so both `for tre dage siden` and `tre dage siden`
resolve. Units ship in singular and plural with a separate `unit1_` file each.

**The clock** counts forward with `over` and back with `i`, takes `klokken` or
`kl.` as its at-marker, and reads `midnat` and `middag` as the landmark points.
The o'clock marker binds only in front of a *bare* hour: `klokken otte` reads
08:00 cleanly, but in `klokken halv to` and `klokken kvart over tre` the time
is right and the word `klokken` is left in the remainder, because the locale
declares no order that puts the at-marker in front of a fraction.

A minute count stacked on a half — `fem over halv ti`, ordinary Danish for
09:35 — resolves to 09:30 with `fem over` in the remainder. That is a wrong
time, not a refusal, and it is the sharpest edge in the locale after the two
below.

**A spoken hour binds to a following `om <daypart>` phrase as its meridiem.**
`klokken otte om aftenen` is 20:00, `kvart over tre om eftermiddagen` 15:15,
`klokken ni om formiddagen` 09:00. The definite surfaces `morgenen` and
`formiddagen` hold the hour in the AM half and `eftermiddagen` and `aftenen`
push it into the PM half, a flat twelve-hour move on the spoken 1–11 hour.
`natten` is separate: it is a band that crosses midnight, so `klokken tre om
natten` is 03:00, `klokken elleve om natten` is 23:00 and `klokken tolv om
natten` is midnight, with the AM ceiling following the CLDR `nat` band.

Three things about that binding are worth knowing before relying on it.

The at-marker is optional. Without `klokken`, a spoken hour in front of `om
<daypart>` binds the same way: `tre om eftermiddagen` is 15:00, `otte om aftenen`
is 20:00 and `ni om formiddagen` is 09:00, each with an empty remainder.

The hour word `to` is unusable there even with the at-marker. `klokken to om
eftermiddagen` returns the afternoon band with `klokken om` stranded, and
`klokken to om natten` the night band. The Danish numeral `to` is a homograph
of the English default range connector `to`, which the range splitter consults
in every locale, and the split runs before the clock is read. The collision is
independent of the day-part binding and shows up wherever a Danish `to` sits
between two independently resolvable pieces.

The literal hour twelve reads wrong on the morning side. `klokken tolv om
formiddagen` is midnight rather than noon, and the fractional forms inherit it
one hour lower still: `halv tolv om formiddagen` is 23:30 and `kvart i tolv om
formiddagen` 23:45, where a Danish speaker means 11:30 and 11:45. The meridiem
attaches to the hour *as spoken*, twelve is rewritten to zero on the AM side,
and only then does the fraction roll the hour back. None of these leave a
remainder.

**Day parts** take their band boundaries from the Unicode CLDR 47 day-period
chart, whose Danish rows read `nat` from 00:00, `morgen` from 05:00,
`formiddag` from 10:00, `eftermiddag` from 12:00 and `aften` from 18:00. All
five ship as vocabulary: four in both the bare and the definite form
(`nat`/`natten`, `formiddag`/`formiddagen`, `eftermiddag`/`eftermiddagen`,
`aften`/`aftenen`); `morgen` ships definite-only (see below). The
`formiddag` is the late morning English cannot name in one word.

The `morgen` band is transcribed in `chronologia/dayparts.py`. It ships only under its definite surface `morgenen`, and the bare `morgen` that the sibling day parts (`aften`/`aftenen`, `nat`/`natten`) ship is left out. Bare `morgen` stays reserved for the relative-day "tomorrow" reading, and `morgenen` never appears in that idiom (`i morgen` is always the bare form). `morgenen` alone reads as the 05:00 to 10:00 band, and `klokken ni om morgenen` is 09:00.

**Ranges** are `fra … til …` and `mellem … og …`, with `siden` opening one that
runs to the anchor and `indtil`/`til` closing one that starts there.

**Quarters, ISO weeks and eras.** `første kvartal 2020`, `uge 12`, `44 f.Kr.`
and `1990 e.Kr.` resolve, along with a before-present marker and the full
deep-time period vocabulary.

**Fuzzy month parts** are `begyndelsen af`, `midten af` and `slutningen af`.

**The ordinal-last determiner** is `sidste`, so `sidste mandag i maj` resolves.
The vocabulary file cites Den Danske Ordbog.

**`halvanden`**, the ordinary Danish word for 1.5 (Den Danske Ordbog; from Old
Norse *halfr annarr*), is declared as the `1.5` quantifier. numtag reads it as the fraction 1.5, not as a bare
`0.5`. `halvanden time siden` resolves to 1.5 hours ago rather than half an hour ago.

## The hour before one

A bare toward-hour phrase for one o'clock names the half hour before one, 00:30 or 12:30. It resolves to whichever of the two comes next after the anchor (ruling 17 in [the rulings](../rulings.md)): `halv et` is 00:30 at 13:04 and 12:30 at 06:05. `toward_hour_12h` only renames hour 0 as 12 on that path, so it changes no bare reading. With a day-part word the hour binds: `halv et om eftermiddagen` is 12:30 and `kvart i et om eftermiddagen` is 12:45. `test/nl_corpus_da/test_da_clock.py` pins `halv et` at 12:30 and `kvart i et` at 12:45 through the same next-reading rule.

## Weaker provenance

The named days carry a precise CLDR locator, but the solid spellings and the
bare `går`/`morgen`/`forgårs`/`overmorgen` that ship beside them do not appear
in that file and rest on nothing recorded.

Den Danske Ordbog is the source named in the day-part and `sidste` vocabulary
headers, and `ordnet.dk` cannot be read by an automated client, so those citations are
unchecked. The Danish Wiktionary entries agree with them:
`formiddag` is glossed "Tidspunkt før middag, om morgenen", `eftermiddag`
"Tidspunkt ca. mellem kl. 12 og 18", `middag` the point around twelve when the
sun stands highest, and `sidste` "Modsat første". The day-part *boundaries* do
not depend on the dictionary at all; they are the CLDR chart.

The weekday and month names, the clock words, the range markers, the seasons
and the holiday vocabulary record no source.

## What refuses

**Decades.** `80'erne` and `firserne` return nothing. The locale declares no
decade construction; Bokmål declares one and reads `80-tallet`.

**A bare duration.** `to uger` returns nothing. A quantity with no direction
marker is still only a quantity.

**The deictic day-part adverbs.** `i morges` returns nothing, and `i morgen
tidlig` resolves tomorrow with `tidlig` unread. The framed band words do
resolve, leaving the framing `i` or `om` in the remainder: `i eftermiddag`,
`i aften`, `i nat` and `om eftermiddagen` all return their band.

## Open questions for a native speaker

1. Is `klokken seks om natten` 06:00 or 18:00 in ordinary use? The band split
   puts it at 18:00.

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("da")
    True
    >>> span, rest = extract_timespan('halv to', "da", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T01:30:00', '')
    >>> span, rest = extract_timespan('halv tolv', "da", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T11:30:00', '')
    >>> span, rest = extract_timespan('halv et', "da", datetime(2017, 6, 27, 12, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T12:30:00', '')
    >>> span, rest = extract_timespan('kvart i et', "da", datetime(2017, 6, 27, 12, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T12:45:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan("80'erne", "da", anchor) is None
    True
    >>> extract_timespan('firserne', "da", anchor) is None
    True
    >>> extract_timespan('to uger', "da", anchor) is None
    True
    >>> extract_timespan('i morges', "da", anchor) is None
    True

---
[← Czech](cs.md) · [Home](../index.md) · [Dutch →](nl.md)
