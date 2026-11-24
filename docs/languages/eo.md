# Esperanto (`eo`)

<!-- agent-hint
covers: where each construction of the Esperanto locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/eo/lang.json, chronologia/locale/eo/*.voc, chronologia/extract/numfold_esperanto.py, test/nl_corpus_eo/
generated: no
verify: .venv/bin/python -m doctest docs/languages/eo.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/eo.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Esperanto (`eo`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by its own `numfold_esperanto` module in `chronologia/extract/`.

Esperanto has no irregular numerals, no gender and no case government on a counted noun, which makes it the simplest number fold in the library. What it does have is a suffix distinction that carries meaning nothing else in this locale carries, and getting it wrong would quietly turn a single appointment into a standing weekly one.

`lundon` (the accusative) names one specific Monday. `lunde` (the adverbial) means "on Mondays", habitually. They are not variants of one another, and they are not folded into one vocabulary slot. The accusative belongs to the date constructions. The adverbial belongs to recurrence, and it gains no recurrence reading from a preceding `ĉiu` either.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('la unua de januaro', "eo", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2018-01-01T00:00:00', '')

## What ships

**Months and weekdays** come from Unicode CLDR 47, `cldr-dates-full/main/eo/ca-gregorian.json`, where the wide format and stand-alone forms are identical. Each ships in the nominative and the accusative, the accusative being what the temporal idiom takes.

**The date** is an ordinal day, `de`, and the month: `la unua de januaro`. `la` is the single invariant definite article, `de` the linking preposition.

**Relative offsets** use `antaŭ` for the past and `post` for the future. Esperanto does not lexically distinguish "before X" from "X ago": the same preposition carries both. The direction is read from context rather than from a separate word. `post` is its attested antonym.

**The clock** has three constructions, and one of them counts the other way.

`kaj` and `post` both count **forward** from the hour named: `la sesa kaj duono` is 6:30, and `duono post la sepa` is 7:30. This is the English past-the-hour convention, not the toward-the-hour convention Icelandic and Lithuanian use. The locale therefore needs none of the toward-hour guards those locales carry. Two independent accounts agree on the direction.

`antaŭ` counts **back** toward the coming hour: `kvarono antaŭ la sepa` is 6:45, a quarter short of seven. It is the asymmetric member of the set.

`je` leads a clock reading (`je la sesa`), and `horo` is the optional formal trailing "o'clock" noun beside the colloquial bare ordinal.

**Recurrence** ships in both attested shapes: the univerbated adverbs `ĉiutage`, `ĉiusemajne`, `ĉiumonate`, `ĉiujare`, and the two-word determiner plus accusative noun `ĉiun tagon`. The univerbated forms are regular `ĉiu-` plus a unit stem plus the adverbial `-e`, the pattern Wiktionary's own `ĉiu` entry lists.

**Named days** are the standard closed-class adverbs `hodiaŭ`, `hieraŭ`, `morgaŭ`, with `antaŭhieraŭ` and `postmorgaŭ` formed by the productive `antaŭ-` and `post-` prefixes.

**Midnight and noon** are `noktomezo` and `tagmezo`. `tagmezo` is attested directly, with a worked example. `noktomezo` is the same productive compound (`nokto` plus `mezo`) formed on the pattern the attested word establishes.

## Weaker provenance

**The clock idioms** rest on a language-learning grammar page, with a second aggregate corroboration for the `post`-linked variant that was treated as secondary rather than independently verified page by page.

**`ĉiun` as the distributive accusative** extends an attested pattern rather than being attested itself. The temporal accusative is attested for single occurrences, and Esperanto adjective-noun case agreement is regular. `ĉiun tagon` follows. But the determiner in the accusative was not separately cited.

**`noktomezo`**, as above, regular compounding on an attested pattern.

**PIV, the *Plena Ilustrita Vortaro*,** the authoritative Esperanto dictionary, was not consulted. Nor was Lernu's dedicated date-format page, which is what would settle the year-inclusive date construction below.

## What refuses

**Day parts.** `matene`, `posttagmeze`, `vespere` and `nokte` all return nothing, and `je la sesa vespere` parses only the clock part, leaving `vespere` visibly stranded. The words exist in the lexicon. What does not exist is any authority for their boundaries. CLDR ships Esperanto only the coarse am/pm pair.

The language is absent from every locale grouping in the supplemental day-period rule set. It falls back to the root am/pm default. Inventing band boundaries is what this refusal prevents. For the same reason no am/pm meridiem marker ships either.

**A year on an absolute date.** `la unua de januaro 2024` resolves the day and month and leaves `2024` unconsumed. Whether the year takes its own connector, sits bare after the month, or uses something like `de la jaro` has no independent source. Only the day-and-month form is wired.

**A two-word relative weekday shift.** `pasinta lundon`, `sekva lundon` and `venonta lundon` resolve the bare weekday and leave the leading word in the remainder. The only attested surfaces for "last Monday" and "next Monday" are the fused compounds `pasintlunde` and `sekvalunde`, which are themselves adverbial `-e` forms whose semantics (one occurrence or a recurring one) the citation listing them does not resolve. Neither the fused nor the two-word form is wired.

## Open questions for a native speaker

1. How is a full date with a year written and said? Does the year take a connector?

2. Does the duration noun in `antaŭ tri tagoj` stand in the nominative or the accusative? The attested example uses an adverb, not a counted noun.

3. Do `pasintlunde` and `sekvalunde` name a single occurrence or a recurring one?

4. Is there an editorially defensible band shape for the four day-part words, given that CLDR defines none?

5. Is a compound ordinal written solid or hyphenated: `dudektria` or `dudek-tria`?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("eo")
    False
    >>> span, rest = extract_timespan('la unua de januaro', "eo", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2018-01-01T00:00:00', '')
    >>> span, rest = extract_timespan('la sesa kaj duono', "eo", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T06:30:00', '')
    >>> span, rest = extract_timespan('duono post la sepa', "eo", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T07:30:00', '')
    >>> span, rest = extract_timespan('kvarono antaŭ la sepa', "eo", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T06:45:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('matene', "eo", anchor) is None
    True
    >>> extract_timespan('posttagmeze', "eo", anchor) is None
    True
    >>> extract_timespan('vespere', "eo", anchor) is None
    True
    >>> extract_timespan('nokte', "eo", anchor) is None
    True

---
[← English](en.md) · [Home](../index.md) · [Estonian →](et.md)
