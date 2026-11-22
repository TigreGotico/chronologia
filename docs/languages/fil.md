# Filipino (`fil`)

<!-- agent-hint
covers: where each construction of the Filipino locale comes from, what it refuses and which questions a native speaker would settle
source: `chronologia/locale/fil/lang.json`, `chronologia/locale/fil/*.voc`, `chronologia/extract/numfold_filipino.py`
generated: no
verify: python -m doctest docs/languages/fil.md && python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\">>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\",t)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/fil.md
see: `docs/languages/index.md`, `docs/extraction.md`
-->

This page records where each construction of the Filipino (`fil`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by its own `numfold_filipino` module in `chronologia/extract/`.

Filipino carries two complete numeral systems side by side — the native
Austronesian one and a Spanish-derived one — and they are split by domain
rather than by register. The clock is where this shows most plainly: it has a
Spanish-lexified form, `alas otso y medya ng gabi` for 20:30, and a native
ordinal form, `limang minuto makalipas ang ika-anim ng umaga` for 06:05. Both
ship, and the fold in `chronologia/extract/numfold_filipino.py` reads each in
its own vocabulary.

The locale code is `fil` rather than `tl` because that is the code CLDR
populates. A lookup for `tl` in CLDR's supplemental day-period table returns
nothing; `fil` is present. For the closed grammatical and temporal vocabulary
this locale covers, Filipino and Tagalog are effectively the same language.

## What ships

**Months and weekdays** come from CLDR 47 in their wide forms. Every weekday
name is a Spanish loan.

**Dates** link the day ordinal to the month with `ng`: `ika-24 ng Agosto`.

**The linker `na`** appears in both its shapes. A Filipino modifier takes the
ligature written onto itself after a vowel — `dalawang araw` — and written as a
separate word after a consonant — `anim na buwan`, `apat na araw`. They are one
morpheme, so the counted-unit orders accept either.

**The Spanish clock.** `alas` leads every hour but one, where `ala` stands
instead: `ala uno`, `alas dose`. `y` optionally joins the hour to what follows.
`medya` is the half and attaches **additively** to the hour already named —
`alas otso y medya` is 20:30, not 19:30 — which is the opposite direction from
the Continental-Germanic bare half, so this locale sets a past-the-hour
convention rather than a toward-the-hour one.

**The native clock** counts minutes off an ordinal-named hour in either
direction. `makalipas` ("after") runs forward from the hour named; `bago`
("before") runs back from the **upcoming** one, and the source states that this
is how Filipino tells a time past the half hour — the additive native frame is
not used there. `ang` introduces the target hour, and `mag` may optionally
stand before it, both `bago ang ika-apat` and `bago mag ika-anim` being
attested.

**Day parts.** `umaga` fixes an hour in the AM half, `hapon` and `gabi` in the
PM half, and `hatinggabi` is the band that crosses midnight — so the twelfth
hour under it is 00:00 rather than noon: `alas dose ng hatinggabi` is midnight.

**Markers** are Wiktionary entries: `pagkatapos` (after), `bago` (before),
`mula` (from), `hanggang` (until), `sa` (the oblique marker used for the future,
glossed for "the time of occurrence" with the worked example
`Sa Lunes kami uuwi`), `tuwing` (every), `susunod` (next), `nakaraan` (last).

`noon` and `noong` deserve their own note. The adverb "indicates past time",
and it is what selects the *preceding* instance of a named day: `noong Lunes` is
the Monday just gone, not the coming one.

The clock constructions and the date order come from Wiktionary entries for the
individual words plus the English Wikipedia article on date and time notation in
the Philippines, which supplies the worked examples.

## Weaker provenance

**`medya`** has no Wiktionary Tagalog entry at all. Its citation is the worked
clock examples in the Wikipedia article and nothing else. The source spells it
`med'ya` as well; the apostrophe form is not shipped, because the tokenizer
would shear it.

## What refuses

Each refusal is pinned by a test.

**`alas una` and `ala una`.** `una` is glossed as the adjective "first", not as
a numeral, and it is far too ordinary a word to read as the digit one on that
basis. The hour one is `ala uno`, whose numeral sense is attested, and that
does resolve.

**`ika-dalawa` and `ika-tatlo`.** The attested second and third ordinals are
the suppletive `ikalawa` and `ikatlo`. The separated forms are made by analogy
and attested nowhere, so the fold leaves the prefix standing. `ikalawa ng Hulyo
2020` reads as the second of July.

**`sesenta` and `nobenta`.** Their dictionary entries carry only a money noun —
"sixty pesos" — and no numeral sense, so neither is folded. Neither is reachable
from the clock anyway: minutes stop at fifty-nine, and `singkuwenta` covers
that.

**`madaling-araw`.** CLDR labels the 06:00–12:00 band `madaling-araw` and the
00:00–06:00 band `umaga`, which is the reverse of the two words' dictionary
senses — `madaling-araw` is glossed as the period between midnight and sunrise.
Which band the word names is therefore unresolved, and no band is bound to it.

**A separate evening band.** CLDR gives `gabi` for both its evening band
(16:00–18:00) and its night band (18:00–24:00). The word is bound to night, the
wider of the two; binding it to both would make the deictic ambiguous, and there
is no second word for the narrower band.

**Every month abbreviation.** Each CLDR abbreviation is either a live Tagalog
word or a rival abbreviation: `may` is the existential "there is", and `mar`
abbreviates both Marso and Martes. Only the wide names ship, so `may 2021` reads
as the bare year 2021 and leaves `may` unconsumed.

**Reduplicated recurrence.** Filipino has two "every X" mechanisms, the particle
`tuwing` and reduplication of the unit noun. Only the particle ships:
`araw-araw`, `buwan-buwan` and `taon-taon` are a closed set of derived adverbs
rather than a marker, `linggo-linggo` has no dictionary entry at all, and
nothing sources whether the two mechanisms are interchangeable.
`linggo-linggo` is two Sunday surfaces to this locale, so one of them is simply
left unconsumed.

**A count before `linggo`.** `linggo` names both Sunday and the week, so
`dalawang linggo` is ambiguous between a span of weeks and a number of Sundays.
The count vetoes the weekday reading — handing back one specific Sunday to a
caller who asked for a duration would be a worse answer than none — and the
duration reading is not asserted in its place. The week unit this locale ships
is `semana`.

**Seasons.** The Philippines has a dry and a wet season, `tag-init` and
`tag-ulan`, which are not the four temperate seasons this library's season slot
models. The four temperate words exist as translations but name no local
period, and mapping one set onto the other would invent a calendar.

**A quarter-hour word.** The half is `medya`; nothing sources a quarter lexeme
beside it, and the worked 3:45 example spells the minutes out —
`kuwarenta singko` — rather than using one. `alas tres y kuwarto` returns three
o'clock with `kuwarto` in the remainder.

## Open questions for a native speaker

1. Which band does `madaling-araw` actually name — CLDR's 06:00–12:00 or the
   dictionary's midnight-to-sunrise?
2. Is there a word for the 16:00–18:00 evening band distinct from `gabi`?
3. Are the reduplicated `araw-araw` forms interchangeable with `tuwing`, and is
   `linggo-linggo` current?
4. Is there a quarter-hour lexeme beside `medya`?
5. Does a real date name its day with a cardinal or an ordinal, and how far does
   the `ika-` series extend?
6. Are `sesenta` and `nobenta` used as numerals outside money?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("fil")
    False
    >>> span, rest = extract_timespan('alas otso y medya', "fil", datetime(2017, 6, 27, 12, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T20:30:00', '')
    >>> span, rest = extract_timespan('alas otso y medya ng gabi', "fil", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T20:30:00', '')
    >>> span, rest = extract_timespan('limang minuto makalipas ang ika-anim ng umaga', "fil", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T06:05:00', '')
    >>> span, rest = extract_timespan('ika-24 ng Agosto', "fil", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-08-24T00:00:00', '')

---
[← Estonian](et.md) · [Home](../index.md) · [Finnish →](fi.md)
