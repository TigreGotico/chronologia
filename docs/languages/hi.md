# Hindi (`hi`)

<!-- agent-hint
covers: where each construction of the Hindi locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/hi/lang.json, chronologia/locale/hi/*.voc, chronologia/extract/numfold_indic.py, test/nl_corpus_hi/
generated: no
verify: .venv/bin/python -m doctest docs/languages/hi.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/hi.md && .venv/bin/python -c 'exec("import re,sys\nfrom datetime import datetime\nimport chronologia as C\ndef mins(d):\n    return \"%g\" % (d.total_seconds() / 60)\ndef rem(r):\n    return \" and \\x60%s\\x60 left over\" % r if r else \"\"\ndef out(rd, tx, lg, an):\n    f = getattr(C, rd)\n    r = f(tx, lg, anchor=an) if rd == \"extract_duration\" else f(tx, lg, an)\n    if rd == \"extract_timespan\":\n        if r is None: return \"no reading\"\n        return \"%s to %s%s\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), r.span.end.datetime().strftime(\"%Y-%m-%d %H:%M\"), rem(r.remainder))\n    if rd == \"extract_duration\":\n        if r is None: return \"no length\"\n        return \"a length of %s min%s\" % (mins(r.duration), rem(r.remainder))\n    if rd == \"extract_event\":\n        if r is None: return \"no event\"\n        return \"start %s, length %s, summary \\x60%s\\x60\" % (r.span.start.datetime().strftime(\"%Y-%m-%d %H:%M\"), \"none\" if r.duration is None else mins(r.duration) + \" min\", r.summary)\n    if r is None: return \"no rule\"\n    return \"the rule \\x60%s\\x60%s\" % (r.recurrence.to_string(), rem(r.remainder))\n\np=sys.argv[1]\nt=open(p).read()\nm=re.search(r\"\\n## Known limits\\n(.*?)(?=\\n---\\n|\\Z)\",t,re.S)\nbad=0\nn=0\nfor ln in (m[1].split(\"\\n\") if m else []):\n    g=re.search(r\"Example \\(reader \\x60(\\w+)\\x60, lang \\x60([\\w-]+)\\x60, anchor (\\d{4}-\\d\\d-\\d\\d \\d\\d:\\d\\d)\\): \\x60([^\\x60]+)\\x60 gives (.+?)\\. \\[#\\d+\\]\",ln)\n    if not g: continue\n    n+=1\n    o=out(g[1],g[4],g[2],datetime.strptime(g[3],\"%Y-%m-%d %H:%M\"))\n    if o!=g[5]:\n        bad=1\n        print(\"limit differs\",g[4],\"|\",g[5],\"|\",o)\nprint(\"known limits checked:\",n)\nsys.exit(bad)\n")' docs/languages/hi.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Hindi (`hi`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by its own `numfold_indic` module in `chronologia/extract/`.

The single most important thing about this locale is what it will not answer. कल means both yesterday and tomorrow. परसों means both the day before yesterday and the day after tomorrow. Which one a speaker means is carried entirely by the tense of the verb, and chronologia does not read verb tense. So both words are refused outright: a bare `कल` returns nothing rather than a fifty-fifty guess at a direction. आज (today) is unambiguous and does resolve. There is no other named day in this locale, and its absence is the design.

The other thing worth knowing before reading further is that Hindi's markers are postposed. "Three days ago" is `तीन दिन पहले`: the quantity first, the marker last. That is CLDR's own past relative-time pattern for the language, `{0} दिन पहले`, and the offset construction reads it in that order.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('तीन दिन पहले', "hi", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-24T00:05:00', '')

## What ships

**Months** come from CLDR 47, `cldr-dates-full/main/hi/ca-gregorian.json`, in the wide and abbreviated widths. फ़रवरी is written with the nukta. The nukta-less फरवरी is as common in ordinary Hindi typing and names the same month, so both ship.

**Weekdays** are the Wiktionary Hindi entries.

**Units** carry both the direct and the oblique case, because a noun counted by a numeral stands in the oblique: दिन / दिनों, हफ़्ता / हफ़्ते, सदी / सदियाँ / सदियों. The declension class governs how many surfaces there are. A masculine consonant stem has one direct form, and an ā-stem has a distinct oblique. An invariant loanword like सेकंड has one form for everything. Where a Sanskritic doublet exists and Wiktionary lists it as a synonym of the vernacular word, both registers ship. The doublets are शताब्दी and शती beside सदी, वर्ष and बरस beside साल, and माह and मास beside महीना.

**Relative offsets** postpose their marker. The past marker is पहले, which is CLDR's own pattern word for every unit field. The future marker is में, CLDR's `{0} दिन में`, with बाद as the other everyday word for the same reading, Wiktionary's own usage example there is `एक दिन बाद`.

**The determiners** इस (this), पिछला (last) and अगला (next) are the words CLDR uses for the relative-type-0, -1 and +1 names in this locale. इस is the oblique singular of यह, which is the form a following noun requires. पिछला and अगला are ā-stems and ship in all three declension forms.

**The clock** has four constructions and one asymmetry that is easy to get backwards.

साढ़े and सवा count **forward** from the hour they name: `साढ़े तीन` is 3:30 and `सवा एक` is 1:15. Wiktionary's entries give both, with usage examples: `सवा एक बज गए हैं` glossed as 1:15, and साढ़े's own example running `डेढ़, ढाई, और अब साढ़े तीन बज गए हैं`.

पौने counts **back**. `पौने दस` is 9:45, a quarter short of ten, and never a quarter past it. It is the asymmetric member of the set, which is why it ships in a separate family from the two forward-counting fractions. A fold treating all three alike would place every पौने time an hour late.

डेढ़ and ढाई are fully suppletive literals. डेढ़ is one and a half and, as a clock reading, *is* half past one. ढाई is two and a half and half past two. Neither is ever composed from a half word plus a numeral. They ship as landmarks at minute 90 and minute 150 of the day rather than as fractions.

बजकर frames minutes counted forward from a struck hour: `आठ बजकर बीस मिनट` is 8:20. It is the conjunctive participle of बजना, "to strike the hour". बजे is the adverb that closes an ordinary spoken clock reading.

**Day parts** take their bands from the CLDR 47 supplemental day-period rule set for `hi`, transcribed in `chronologia/dayparts.py`, and their surfaces from the CLDR period names, each confirmed against a Wiktionary gloss: सुबह, दोपहर, शाम, रात.

**Numerals** are a curated native lexicon in `chronologia/extract/numfold_indic.py`. This is not an optimisation but a necessity: Hindi's numerals from one to ninety-nine are suppletive and not compositional (ब्यालीस is forty-two and cannot be derived from the words for four and two) so a compositional folder cannot read them at all.

**Ordinals** ship in the vernacular series पहला / दूसरा / तीसरा and then the -वाँ pattern, gender-inflecting throughout.

**Markers** are Wiktionary postposition entries: के बाद (after), से पहले and के पहले (before, with के पूर्व listed as a synonym), के बीच (between), से (from, since, the ablative), तक (until), हर and प्रत्येक (every), को (the "on" that attaches to a weekday).

## What refuses

**कल and परसों**, as above, the central design decision of this locale.

**The Sanskritic ordinals.** प्रथम, द्वितीय, तृतीय, दशम are a separate learned register from the vernacular series that ships. Mixing them would need that register's own paradigm, so it is left out.

**बृहस्पतिवार**, the formal name for Thursday. Wiktionary carries it only as a Sanskrit entry. The Hindi गुरुवार entry names it a synonym, but the word has no Hindi entry of its own, so it is not attested for this locale.

**The Vikram Samvat months.** चैत्र, वैशाख, फाल्गुन and the rest are not vocabulary but a calendar. The lunisolar system carries a leap month and a year offset that varies by month, and implementing it is a calendar implementation, not a word list. A Vikram Samvat year is never silently converted either: `2081 विक्रम संवत` reads 2081 as the Gregorian year it spells and leaves `विक्रम संवत` in the remainder, rather than quietly applying a +57 shift.

**Closed ranges.** Hindi frames a closed range with both markers postposed: `A से B तक`, the start closed by से and the end by तक. The range grammar reads a leading frame. Only the open reading fires. `छह बजे से दस बजे तक` returns a span that ends at six o'clock, with `से दस बजे` left in the remainder. The open ranges themselves, `शुक्रवार तक` and `सोमवार से`, do resolve. The same applies to के बीच, which is attested as "between" but trails both its bounds.

**The minutes-to frame.** `दस बजने को सात मिनट` counts seven minutes short of ten. Wiring it would need a subtractive clock direction spelled as a two-word verbal frame, which no construction order expresses. It refuses rather than reading the number forward.

**आधी रात**, the everyday phrase for midnight. आधी is the half word the fractional constructions read and रात is the night band, and no compound landmark ships. The phrase returns the night band with आधी left in the remainder, mid-band rather than silently wrong, and visible about it.

**Period parts.** जून की शुरुआत, जून के अंत, जून के मध्य return the whole of June with the qualifier unread. No early/mid/late vocabulary could be attested as a fixed temporal expression.

**Calendar quarters and ISO week references.** पहली तिमाही and तीसरा सप्ताह both refuse. Neither was attested.

**Era vocabulary.** `44 ईसा पूर्व` and `ईसवी सन 1947` either refuse or leave the era word unread. The abbreviations could not be attested.

**लाख and करोड़.** Both are everyday Hindi for 10⁵ and 10⁷, and neither ever names a date. They belong to a deep-time scale vocabulary this locale does not ship, so `एक लाख साल पहले` refuses.

## Open questions for a native speaker

1. Is a real date-of-month written and spoken as a cardinal or as an ordinal?

2. Do the oblique unit paradigms condition on the individual numeral in ways the shipped direct/oblique pair does not capture?

3. How do the numerals compound above one hundred?

4. Is पर attested as a clock "at" marker? It is a plausible analogy and is not shipped on that basis.

5. Is the bare planet-name colloquial form of a weekday, dropping वार, current beyond इतवार?

6. Is there a fixed early/mid/late vocabulary for a month that could be attested?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("hi")
    False
    >>> span, rest = extract_timespan('तीन दिन पहले', "hi", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-24T00:05:00', '')
    >>> span, rest = extract_timespan('{0} दिन पहले', "hi", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T00:05:00', '')
    >>> span, rest = extract_timespan('{0} दिन में', "hi", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T00:05:00', '')
    >>> span, rest = extract_timespan('एक दिन बाद', "hi", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-28T00:05:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('कल', "hi", anchor) is None
    True
    >>> extract_timespan('एक लाख साल पहले', "hi", anchor) is None
    True

---
[← Hebrew](he.md) · [Home](../index.md) · [Hungarian →](hu.md)
