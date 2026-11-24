# Occitan (`oc`)

<!-- agent-hint
covers: where each construction of the Occitan locale comes from, what it refuses and which questions a native speaker would settle
source: chronologia/locale/oc/lang.json, chronologia/locale/oc/*.voc, chronologia/extract/numlayer.py:NUMTAG_LANGS, test/nl_corpus_oc/, test/test_xfail_open_issues_*.py
generated: no
verify: .venv/bin/python -m doctest docs/languages/oc.md && .venv/bin/python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/oc.md
see: docs/languages/index.md, docs/extraction.md
-->

This page records where each construction of the Occitan (`oc`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

Occitan sits next to Catalan and reads like it. The temptation to fill the Occitan locale from the Catalan one is the single largest risk to this page's accuracy. Catalan's date grammar lets the article stand inside the date (`article? DAY of MONTH`) but that order does not carry over, because the two locales disagree about what an article is. Catalan's `marker_article` holds only `el`, `la`, `els`, `les` and `l`.

Occitan's also holds the contracted prepositions `del`, `de la`, `al` and `a la`. An optional leading article in the date grammar would swallow the `del` of `la setmana del 20 de julhet` and the week-of reading would die. Occitan's article vocabulary contains contracted prepositions where Catalan's does not, which is exactly why Catalan can afford a leading article slot in its date orders and Occitan cannot.

The visible cost is small and worth naming: `lo 3 d'octòbre de 1990` gives the right day and leaves `lo` in the remainder, where the Catalan equivalent consumes it.

The other thing to know is that Occitan carries no day-part vocabulary at all. No band table exists for `oc` in `chronologia/dayparts.py` and no `daypart_*.voc` file ships, so `al matin`, `a la vesprada` and `la nuèch` all return nothing as spans. The same words work as clock meridiems (`dètz oras del matin` is 10:00 and `quatre oras del ser` is 16:00) but there is no morning-shaped answer to ask for.

## Try it

To read a phrase, call `extract_timespan` with the phrase, the locale code and an anchor datetime. It returns the span that the phrase names and the text that it left unread.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> span, rest = extract_timespan('dètz oras del matin', "oc", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T10:00:00', '')

## What ships

**Weekdays and months** ship, with abbreviations for most months and none for weekdays. Neither group records a source. `mai`, `junh` and `març` ship without an abbreviation because their full forms are already short.

**The date line** is little-endian: `3 d'octòbre de 1990`, with `de` optional between the parts and no article slot, for the reason above. The slashed numeric form reads. The dotted one does not.

**Contractions** are handled at the number-folding layer rather than the tokenizer. `split_contractions` is off in `lang.json`. The Occitan fold hook instead declares the proclitics `l`, `d`, `un`, `qu`, `n` and `s`, so `d'octòbre` and `l'an` come apart there.

**Relative offsets** are `dins` forward and `fa` backward. The grammar has a quantifier slot Catalan's does not. `un parelh de jorns` counts two, `qualques jorns` and `unes jorns` count three, and `mièja ora` counts half. So `dins una mièja ora` resolves where the Catalan `dins de mitja hora` returns nothing. Seventeen locales carry that quantifier slot, Catalan is not among them.

**The relative determiners** follow the noun (`lo diluns passat`, `la setmana que ven`, `lo diluns prochan`) and `marker_position` is `post`. The "previous" forms come from a native-speaker review filed as [ovos-date-parser issue 300](https://github.com/OpenVoiceOS/ovos-date-parser/issues/300), which supplies `darrèr` and `darrièir` beside `darrièr` and prefers `precedent(s)`. The vocabulary records that `darrèr` and `darrièir` are attested masculine only and that `precedent` is invariable in gender. No feminine spelling was invented for them.

**Ranges** use `de`/`del` as the from-lead and `a`, `au`, `al`, `fins a` or `fins au` as the to-boundary, with `entre … e …` as the other frame and `dempuèi`, `despuèi`, `dempuei` or `dès` opening a since-range. None of these carry a citation in the vocabulary.

**The clock** subtracts with `mens` or `manca` and adds with `e`. `miègjorn` and `mièjanuèch` are points. The `h` clock form is enabled in the fold hook, so `10h30` and `10 h 30` both read.

**The night meridiem** is a midnight-crossing band, as in Catalan and Spanish: small hours one to five stay AM, evening hours six to eleven are PM, twelve is midnight. Occitan's contribution is the surface list rather than the mechanism. Issue 300 supplies `nuèch`, `nuèit`, `nèit`, `nèt`, `nèch` and `nuòch` together with their a-initial twins, all twelve of which ship. The same review supplies the afternoon and evening forms `après miègjorn`, `après merende`, `aprèp merende`, `après dinnar`, `aprèp dinnar` and `vesprada`.

**Eras** run wider than in most locales. Besides `acn` and `apc`, the fold hook recognises the spelled-out `abans jèsus-crist` and `aprèp jèsus-crist` and the secular wording `abans nòstra èra` and `de nòstra èra`, each in both its accented and unaccented spelling, so `44 abans nòstra èra` and `1990 de nòstra èra` resolve. Anno Mundi, Holocene, Julian Day and Unix era prefixes ship as well.

**Non-Gregorian calendars.** Occitan is one of the six locales (with Asturian, English, French, Italian and Romanian) that carry French Republican month names. It also carries Hebrew and Islamic civil months, Japanese era names, the consulship and *pridie* markers of the Roman calendar. The full geological period series. Catalan carries none of it.

**Decades** ship twice over: `los ans 80` reads the digits and `los ans ochanta` reads the spelled tens, which have their own `decade_word_*` files.

**Seasons** are `prima` and `primtemps` for spring, `estiu`, `auton` and `tardor` for autumn. `ivèrn`/`ivern`. `tardor` is the same word Catalan uses. It is not a borrowing from the Catalan locale: the Occitan Wiktionary carries `tardor` in its Occitan section as a feminine noun naming one of the four seasons, alongside `auton` from Latin *autumnus*. The locale pins `hemisphere` to `north`, where Catalan leaves it unset.

**The weekend** is `dimenjada`, built on `dimenge` the way Catalan's `cap de setmana` is not built on anything. The Occitan Wiktionary glosses it as Saturday and Sunday. `weekend` and `week-end` ship beside it.

**Numerals.** numtag reads `uèch`, `uèit` and `uòch` as eight, issue 300 supplies the variants.

## Weaker provenance

Most of this locale carries no citation. Weekdays, months, seasons, units, ranges, the era abbreviations and the Roman anchors all ship without a recorded source, which is a thinner record than the Catalan locale's.

Three sources are named without a fetchable locator. The half-unit noun `mitat` is attributed to the Congrès Permanent de la Lenga Occitana's dicod'Oc under *mitat*, dicod'Oc did not answer at any address that could be constructed for it, so that citation is unchecked. The Occitan Wiktionary corroborates the word independently, glossing `mitat` as "una de las doas parts d'un tot". The locative `en` used with month names is attributed to the *Diccionari general occitan* under *en*, likewise unchecked.

The Occitan Wiktionary confirms `en` as an Occitan preposition but does not confirm the month usage. The vocabulary also declines a form it records as `aprvèspre` on the grounds that it is a typo. The review it comes from writes `après vèspre`. The reason for the exclusion is sound but the spelling quoted for it is not the one in the source.

The Roman anchors ship in Latin (`kalends`, `kalendis`, `calends`, `nones`, `nonis`, `ides`, `idibus`) with no source at all, where Catalan ships vernacular forms with one. That is not obviously wrong, but it is untested: the Occitan Wiktionary's `calendas` means the twelve days before Christmas, not the Roman kalends. The vernacular form Catalan uses would be the wrong word here.

Issue 300 is a native speaker's review on a public tracker, not a published description of the language. It is the strongest evidence this locale has for the surfaces it covers, and it is still one speaker.

## What refuses

**The dotted date.** `15.06.2020` returns nothing.

**Day parts.** `al matin`, `de matin`, `a la vesprada`, `lo ser` and `la nuèch` all return nothing, for want of any band table.

**Holidays.** `Nadal` returns nothing. Thirty-six locales declare a `holiday_ref` construction and Occitan is not one of them.

**The Catalan quarter clock.** `un quart de quatre` and `tres quarts de quatre` return nothing. Catalan's count-toward-the-hour quarters are a Catalan construction, and nothing attests them for Occitan, so the slot is absent rather than borrowed.

**A bare duration.** `quinzena` returns nothing on its own.

**Roman-numeral centuries.** `lo sègle XX` returns nothing.

## Known defects

Reproduced with `extract_timespan(text, "oc", anchor=datetime(2017, 6, 27, 13, 4))`.

`una ora de la nuèch` returns nothing where `1 ora de la nuèch`, `doas oras de la nuèch` and `dotze oras de la nuèch` all resolve. The indefinite-article and quantifier vocabularies claim `una`, so it never reaches the hour slot. The one o'clock hour is the only one with no spelled-out form. Catalan's `la una de la nit` resolves.

`idus de març` comes back as the whole of March with `idus de` stranded. `ides de març` is correct at 15 March. The Latin `idus` that the sibling anchor files otherwise favour is missing from the ides file.

`1r de genièr` comes back as the whole of January with `1r de` stranded, where `primièr de genièr` resolves to 1 January.

`lo primièr de genièr` resolves correctly but leaves `lo` in the remainder, the same article cost as the date line.

## Open questions for a native speaker

1. A native-speaker review says `abans-ièr` is a French borrowing and that `davant-ièr`, `ièr delà`, `ièr delai` and `passat ièr` are the native forms. All five ship, with `abansièr` first. Should the borrowed form be dropped, or kept and demoted?

2. Should the Roman anchors stay Latin, or is there an Occitan vernacular set that does not collide with `calendas` in its Christmas sense?

3. What are the Occitan day-part bands, and do they cut where Catalan's six do or where French's do?

4. Is `dimenjada` the whole weekend or Sunday alone in ordinary use, given it is built on `dimenge`?

5. Does `en genièr` mean "in January" in the temporal sense the locale reads it as, and is there a published source for that beyond the dictionary entry named for it?

## Known limits

Each limit below has an open issue and a strict `xfail` test that fails when the limit is fixed.

- [#990](https://github.com/TigreGotico/chronologia/issues/990): A common word reads as a time word: en "fall", da "går" and "morgen", oc "ora", pl "lata"

- [#992](https://github.com/TigreGotico/chronologia/issues/992): Day words and counted offsets with no reading: en "today's", oc "nuèch", an, eu, kab, fi

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("oc")
    True
    >>> span, rest = extract_timespan('dètz oras del matin', "oc", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T10:00:00', '')
    >>> span, rest = extract_timespan('quatre oras del ser', "oc", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T16:00:00', '')
    >>> span, rest = extract_timespan('la setmana del 20 de julhet', "oc", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-07-17T00:00:00', '')
    >>> span, rest = extract_timespan("3 d'octòbre de 1990", "oc", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('1990-10-03T00:00:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('al matin', "oc", anchor) is None
    True
    >>> extract_timespan('a la vesprada', "oc", anchor) is None
    True
    >>> extract_timespan('la nuèch', "oc", anchor) is None
    True
    >>> extract_timespan('dins de mitja hora', "oc", anchor) is None
    True
    >>> extract_timespan('15.06.2020', "oc", anchor) is None
    True
    >>> extract_timespan('de matin', "oc", anchor) is None
    True
    >>> extract_timespan('lo ser', "oc", anchor) is None
    True
    >>> extract_timespan('Nadal', "oc", anchor) is None
    True
    >>> extract_timespan('un quart de quatre', "oc", anchor) is None
    True
    >>> extract_timespan('tres quarts de quatre', "oc", anchor) is None
    True
    >>> extract_timespan('quinzena', "oc", anchor) is None
    True
    >>> extract_timespan('lo sègle XX', "oc", anchor) is None
    True
    >>> extract_timespan('una ora de la nuèch', "oc", anchor) is None
    True

---
[← Norwegian Nynorsk](nn.md) · [Home](../index.md) · [Persian →](fa.md)
