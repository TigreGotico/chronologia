# Greek (`el`)

<!-- agent-hint
covers: where each construction of the Greek locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/el/lang.json, chronologia/locale/el/*.voc, chronologia/extract/numlayer.py:NUMTAG_LANGS, test/nl_corpus_el/
generated: no
verify: .venv/bin/python -m doctest docs/languages/el.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/el.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Greek (`el`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

Greek marks its determiners twice. `marker_position` sets `weekday_ref` and `rel_period` to `post`. The base grammar's `extend`/`override` entries add a second, article-carrying order on top of the plain one: `την Τρίτη που έρχεται` ("the Tuesday that is coming") reads the same offset as a bare postposed marker, because Greek names a relative weekday with a postposed relative clause rather than a prenominal adjective the way English or French do. That construction, not a single determiner word, is the ordinary way to say "next Tuesday" or "last Tuesday" in spoken Greek.

The clock is the second thing to know. It resolves the same direction English and Romanian do: additive past the hour, subtractive toward the next one.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('την Τρίτη που έρχεται', "el", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-07-04T00:00:00', '')

## What ships

**Day parts** are four bands transcribed from the Unicode CLDR 47 day-period rules for `el`: `πρωί` `[04:00, 12:00)`, `απόγευμα` `[12:00, 17:00)`, `βράδυ` `[17:00, 20:00)` and `νύχτα` `[20:00, 04:00)` (crossing midnight). Each noun's gender and its accusative article are confirmed against its own Wiktionary lemma: `πρωί`, `απόγευμα` and `βράδυ` are neuter (`το`), `νύχτα` is feminine (`τη`, since it begins with a consonant outside the vowel/plosive set that forces `την`). The same four nouns double as clock meridiem cues on an explicit hour: `πρωί` is a no-op AM confirmation, `απόγευμα` and `βράδυ` are a uniform +12 PM shift, and `νύχτα` routes through the shared midnight-crossing night-meridiem split (small hours 1-5 stay AM, 6-11 are PM, twelve is midnight).

**Recurrence is unimplemented.** `κάθε μέρα` ("every day") does not resolve. `marker_every.voc` ships the connector word but no construction consumes it yet. A sentence built on `κάθε` binds only the temporal fragment it happens to contain (a daypart, a clock time) and strands `κάθε` in the remainder.

**Weekdays and months** ship bare, in the nominative, with no recorded source in the vocabulary comments.

**The date line** is little-endian (`DAY MONTH YEAR?`), matching the CLDR `el` `ca-gregorian` chart at every level, full `EEEE d MMMM y`, long `d MMMM y`, medium `d MMM y`, short `d/M/yy`.

**Relative offsets** are `πριν`/`πριν από` for the past and `σε`/`μετά` for the future, with the marker able to lead the count (`πριν από τρεις μέρες`) or trail it, and an indefinite-article order for a bare unit (`μια εβδομάδα`).

**The clock** ships two directions off the fixed hour, both cited in the vocabulary to the *Λεξικό της Κοινής Νεοελληνικής* (Triantafyllidis Institute, 1998) and to Triantafyllidis's own *Νεοελληνική Γραμματική* §403 on time expressions, for the meridiem abbreviations, and confirmed independently for the fraction words. `και` ("and") is additive: `τρεις και μισή` is 3:30, `τρεις και τέταρτο` is 3:15. `παρά` ("minus/before") is subtractive from the *next* hour: `τρεις παρά τέταρτο` is 2:45. Two independent sources with worked numeric examples confirm the direction: the project's own test corpus, which checks these exact phrases against independent arithmetic on a fixed anchor and states explicitly that Greek "differs from the Continental-Germanic half" (`και μισή` is half *past*, not half *to*) and a Greek-language learner's guide (Preply), which glosses `Είναι μία και μισή` as "It is half past (one)" and `Είναι δέκα παρά τέταρτο` as "It is quarter to (ten)", with `παρά` explicitly said to work "exactly like the English 'to'". `τέταρτο` ("quarter") is independently confirmed at its Wiktionary lemma entry: "a quarter, a fourth, one of four equal parts", with "quarter of an hour" given as its own clock sense, deriving from the adjective `τέταρτος` ("fourth"). The landmarks are `μεσημέρι` (noon) and `μεσάνυχτα` (midnight).

The meridiem markers `π.μ.`/`π. μ.`/`πμ` (AM, from `προ μεσημβρίας`, "before midday") and `μ.μ.`/`μ. μ.`/`μμ` (PM, from `μετά μεσημβρίαν`, "after midday") ship in their tight-dotted, spaced-dotted and dot-less spellings. The vocabulary comment records that the dot-less forms are the ordinary informal rendering in digital text. The corpus's own regression test documents why the dots matter mechanically: the tokenizer discards dots. An unlisted dot-less variant would silently fall into the remainder and read a p.m. time twelve hours early.

**Determiners.** `περασμένη`/`προηγούμενη` ("last/previous") and `επόμενη` ("next") ship as prenominal adjectives, each with a postposed relative-clause alternative for a weekday (`που πέρασε` ("that has passed") and `που έρχεται` ("that is coming")) both cited to the *Λεξικό της Κοινής Νεοελληνικής*, s.v. `περνώ`/`περασμένος` and `έρχομαι` respectively, as fixed relative-marker surfaces rather than free relative clauses. `τελευταίος` ("last" as an ordinal-last determiner, behind `η τελευταία Δευτέρα του Μαΐου`) is cited to the same dictionary, s.v. `τελευταίος`.

**Ranges** are `μεταξύ`/`ανάμεσα` ("between") and `έως`/`μέχρι`/`ως` ("until"/"to").

**Quarters, ISO weeks, decades, centuries and millennia.** `τρίμηνο` (quarter), `εβδομάδα` (ISO week), `δεκαετία` (decade), `αιώνας` (century) and `χιλιετία` (millennium) all resolve, Greek is among the locales here that ship a dedicated millennium unit rather than folding it into a numeral-plus- scale construction.

**Seconds** ship a unit, `δευτερόλεπτο`/`δευτερόλεπτα`. `πριν 30 δευτερόλεπτα` reads as 30 seconds ago.

**Fuzzy period parts** are `αρχές`/`αρχή` (early), `μέσα`/`μέση` (mid), `τέλη`/`τέλος` (late).

**Eras** are `μ.χ.`/`μ. χ.` (AD, "μετά Χριστόν", after Christ) and `π.χ.`/ `π. χ.` (BC, "προ Χριστού", before Christ), each in tight- and spaced-dotted form.

## Weaker provenance

The weekday and month names carry no recorded source, and neither do the seasons or the holiday vocabulary.

## What refuses

**`bare_half_to`.** The locale's conventions explicitly set `bare_half_to: false`. A bare `μισή` or `μισή ώρα` reading as "half to the hour" with no `παρά`/`και` marker present does not resolve as a clock time. The fraction word only binds inside the full `HOUR CLOCKDIR FRACTION` shape.

## Open questions for a native speaker

1. Does `βράδυ` genuinely extend as a colloquial PM clock cue past its own CLDR band into the 21:00-23:00 hours (`εννιά/δέκα/έντεκα το βράδυ`), the way `tarde` does in Spanish and `abends` does in German, or does ordinary speech switch to `νύχτα` earlier than that?
2. Does the shared 5|6 hour cut used for the `νύχτα` night-meridiem split (small hours 1-5 read AM, 6-11 read PM) match how a Greek speaker actually parses an hour said with `νύχτα`, or does the boundary sit somewhere else in ordinary usage?
3. Is the postposed relative-clause construction (`που πέρασε`/`που έρχεται`) the dominant spoken form for every weekday, or does it compete evenly with the prenominal adjective (`την περασμένη Τρίτη`) in ordinary registers?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("el")
    True
    >>> span, rest = extract_timespan('την Τρίτη που έρχεται', "el", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-07-04T00:00:00', '')
    >>> span, rest = extract_timespan('πριν από τρεις μέρες', "el", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-24T00:05:00', '')
    >>> span, rest = extract_timespan('τρεις και μισή', "el", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T03:30:00', '')
    >>> span, rest = extract_timespan('τρεις και τέταρτο', "el", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T03:15:00', '')

---
[← German](de.md) · [Home](../index.md) · [Hausa →](ha.md)
