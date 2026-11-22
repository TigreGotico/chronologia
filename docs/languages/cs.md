# Czech (`cs`)

<!-- agent-hint
covers: where each construction of the Czech locale comes from, what it refuses and which questions a native speaker would settle
source: `chronologia/locale/cs/lang.json`, `chronologia/locale/cs/*.voc`, `chronologia/extract/numlayer.py:NUMTAG_LANGS`
generated: no
verify: python -m doctest docs/languages/cs.md && python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/cs.md
see: `docs/languages/index.md`, `docs/extraction.md`
-->

This page records where each construction of the Czech (`cs`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

Czech names the half hour for the hour that has not arrived: `půl deváté` is
08:30, not 09:30, and `půl páté` is half past four. The hour in that phrase is
not a cardinal at all but a genitive-feminine *ordinal* agreeing with an
elided `hodiny` — literally "half of the ninth". numtag reads the ordinal as
9 and `půl` as a fraction, and the fold keeps `půl` a word, so the clock reads
the fraction and the hour apart. The quarter hour runs on a different grammar from the half hour: `čtvrt na devět`
is 08:15 and `tři čtvrtě na devět` is 08:45.

## What ships

**The date line** is little-endian, `DAY MONTH YEAR?`, matching the CLDR 47
`ca-gregorian` chart for `cs` at every level — full `EEEE d. MMMM y`, long
`d. MMMM y`, medium `d. M. y`, short `dd.MM.yy`. `lang.json` adds an
"of"-linked order and a month-led one alongside the plain day-led shape, and
the tokenizer runs with `ordinal_dot` and `dotted_date` on, so both `15. srpna
2020` and the spelled `patnáctého srpna 2020` resolve to the same day.

**Months** ship in three shapes at once, and CLDR 47 accounts for all three.
The standalone nominative (`leden`) is what CLDR's `stand-alone` wide chart
gives; the genitive that follows a day ordinal (`ledna`) is CLDR's `format`
wide chart, which is genitive throughout for Czech; and the three-letter
clippings (`led`, `úno`, `bře`, `dub`, `kvě`, `čvn`, `čvc`, `srp`, `říj`,
`lis`, `pro`) are CLDR's `format` abbreviated chart character for character.
The locative that follows the preposition (`lednu`, `srpnu`) is shipped
alongside them without a recorded source. September is the one month whose
genitive and nominative coincide, `září`.

**Weekdays** ship in the nominative, with the accusative that a
`v <weekday>` phrase takes for the three weekdays whose accusative differs
(`středu`, `sobotu`, `neděli`) and a scattering of genitives; the nominative
set matches CLDR 47's wide weekday chart. No source is recorded for the
choice of oblique forms.

**Day parts** are transcribed from the Unicode CLDR 47 day-period rules for
`cs`, each shipping as the deictic adverb a phrase actually uses rather than a
dictionary citation form: `ráno` (morning, Wiktionary `ráno`, whose Czech
adverb sense is glossed "in the morning"), `odpoledne` (afternoon, Wiktionary
`odpoledne`, adverb, "during the afternoon"), `večer` (evening, whose
Wiktionary entry carries only a noun sense, so the adverbial use the locale
ships rests on the day-period data rather than on that entry). The same words
double as clock meridiem cues on an explicit hour,
`ráno` and `dopoledne` for AM, `odpoledne` and `večer` for PM, so `v 9 hodin
večer` is 21:00.

**Relative offsets** are `před` (ago, governing the instrumental) and `za`
(in/after, governing the accusative), with `v`/`ve` carrying "in" over a
calendar period. That last preposition is cited to its Wiktionary entry for
Czech, whose sense list gives the four temporal uses the locale needs
and glosses each with a worked example — `v šest hodin` ("at six o'clock",
accusative), `v pátek` ("on Friday", accusative), `v roce 2007` ("in the year
2007", locative) and `v lednu` ("in January", locative).

**Determiners.** `minulý` ("last/previous"), `příští` ("next") and `poslední`
("the last one of") each ship a full adjectival paradigm — `minulý` the hard
type across ten forms, `příští` and `poslední` the soft type, whose forms are
largely syncretic so that the base form covers most of the singular and only
`-ího/-ímu/-ím/-ích/-ími` stand apart. Wiktionary carries a complete
declension table for each of the three under its Czech `Adjective` heading.
The first two match the CLDR 47 `cs` `dateFields.json` relative types
directly and across three fields at once, which is unusually clean: week,
month and year all give `minulý ...` for relative-type--1 and `příští ...`
for relative-type-1, with no irregular of the kind Slovenian's `lani` forces.

**"This"** ships in two series, the formal `tento` (`tohoto`, `tomuto`,
`tomto`, `tímto`, `tato`, `této`, `tuto`, `touto`, `toto`, `tyto`, `těchto`,
`těmito`) and the colloquial `tenhle` (`tohohle`, `tomhle`, `tahle`, `tuhle`,
`tohle`). Wiktionary lists both as Czech demonstrative pronouns and gives
each a declension table built on the irregular `ten`.

**Landmarks** are `půlnoc` (midnight) and `poledne` (noon).

**The clock's toward-hour half.** `půl` plus the genitive-feminine ordinal of
the coming hour is the locale's only fractional clock surface, gated by
`bare_half_to: true` in `lang.json` and read
through a `FRACTION HOUR MERIDIEM? ZONE?` order. The hour surfaces —
`první`, `druhé`, `třetí`, `čtvrté`, `páté`, `šesté`, `sedmé`, `osmé`,
`deváté`, `desáté`, `jedenácté`, `dvanácté` — fold to their digits through
numtag, and `půl` stays a word, so the fraction word and the hour never
merge into one number. Two
independent sources fix the direction with worked numeric examples.
Wiktionary's Czech `půl` carries a usage note saying the word means "half to"
when telling the time and glosses `je půl páté` as "half (past) four";
a Czech-for-foreigners grammar table gives `Je čtvrt na osm` for 7:15, `Je půl
osmé` for 7:30 and `Je tři čtvrtě na osm` for 7:45 under the rule that a Czech
speaker "always states the hour being approached". `půl páté` resolves to
04:30 and `půl deváté` to 08:30, and the corpus checks five hours of the
pattern against independent arithmetic, `půl první` among them.

**`půl` stays a word.** numtag reads the Czech numbers in every case form
(`numlayer_slavic.py`), and it reads `půl` as the fraction 0.5. The fold keeps
a clock or period fraction that numtag reads as a fraction as a word, so the
clock reads `půl deváté` and the period reader reads `první polovina 2020`.
The half-hour *duration* reads the same word: `půl hodiny` and `čtvrt hodiny`
reach the duration reader through `lang.json`'s quantifier table and come
back as thirty and fifteen minutes. The spaced `tři čtvrtě` joins into the
clock fraction `třičtvrtě` before the fold.

**Quarters, ISO weeks, decades, centuries and millennia** all resolve, with
`čtvrtletí` and `kvartál` as two live quarter words, `týden` for the ISO week,
`desetiletí` and `dekáda` for the decade, `století` for the century and
`tisíciletí` for the millennium. The millennium file carries the one comment
that explains itself: a neuter noun in `-í` spells its nominative singular and
plural alike, so the singular has to be listed separately or every
`tisíciletí` is read as a plural count.

**Named days** span all five positions around the anchor — `předevčírem`,
`včera`, `dnes`, `zítra`, `pozítří` — and are exactly what the CLDR 47 `cs`
`dateFields.json` day field gives for relative types −2 through +2.

**Era markers** are cited to the Internetová jazyková příručka of the Ústav
pro jazyk český, its page on purely graphic abbreviations
(`prirucka.ujc.cas.cz/?id=780`), which lists both the secular `př. n. l.` and
`n. l.` and the Christian `př. Kr.`. The spaced spelling is the one that page
recommends; the unspaced variants ship because they are widely typed.

**Ranges** run `od A do B` and `A až B`. The range conjunction is cited to the
same institute's dictionary entry for `až`, whose SSČ and SSJČ articles both
give the "up to a limit" sense with numeric examples (`na str. 5 až 10`,
`může přijít pět až deset lidí`).

## Weaker provenance

**The oblique weekday and month forms** carry no citation. The nominatives,
the format genitives and the abbreviations are all traceable to CLDR, but
nothing on file says which case `středu` or `lednu` is meant to serve or
whether the set shipped for each word is complete.

**`čtvrtletí` and `kvartál`** ship as unqualified synonyms for "quarter" with
no source distinguishing register — the same pair, and the same silence,
that the Bulgarian and Slovenian pages record for their own two quarter words.

**The half-period noun.** `marker_half.voc` names the *Slovník spisovného
jazyka českého* as the source for `polovina` and quotes a definition and an
example. The institute's entry for `polovina` does carry the sense, but the
gloss on file is a paraphrase rather than the wording printed there, the
example is not in the entry, and the definition actually belongs to the
shorter *Slovník spisovné češtiny* article on the same page rather than to the
SSJČ one named. The surface is sound; the locator is looser than it reads.

**The determiner and pronoun paradigms** are shipped with locators into the
Internetová jazyková příručka's expository section (`?id=310` for hard
adjectives, `?id=311` for soft, `?id=350` for demonstratives) that do not
lead to the cited articles. The first two lead to the site's "page not
available" notice, and the third leads to an article about female
personal names. The paradigms themselves are correct and are carried by the
Wiktionary declension tables cited above; only the institute locators are
wrong.

**The clock's half-hour citation.** `clock_fraction_30.voc` attributes the
toward-hour reading to the Internetová jazyková příručka. That appliance's
page on time (`?id=820`, *Časové údaje*) covers written notation only — where
the separator goes, when to double-digit the hour — and says nothing about the
spoken `půl <ordinal>` at all. The direction is not in doubt, being carried by
the two sources named above, but it does not come from where the file says it
does.

## What refuses

**Minutes counted to or past the hour.** `pět minut po deváté` does not
resolve. `deset minut před devátou` is read as a minute offset from the anchor
and leaves `devátou` stranded, as does `pět minut před devátou`. There is a
`MINUTE CLOCKDIR HOUR` order in `lang.json`, but the hour-ordinal table it
would need to read (`deváté`) is genitive-feminine and the minute-count phrase
takes different cases on both sides, so the order never binds.
`za pět minut devět` — the ordinary way to say five to nine — is read the same
way, as an offset five minutes ahead with `devět` stranded, which is a
confident answer to a question nobody asked.

**Night.** The CLDR 47 `cs` day-period chart gives `v noci` for the night
band, and no night daypart ships, so `v noci` returns nothing and `dnes v
noci` returns the whole of today with `v noci` stranded. `dopoledne` has the
converse problem: it is a meridiem cue but not a day part, so `dnes
dopoledne` returns the whole day and strands the word. Polish, Slovak and
Welsh are the only other locales with a morning daypart and no night one.
Belarusian ships no day-part vocabulary at all, so the shape is not simply a
Slavic one.

**A leading preposition on the year.** `v roce 2020` returns the whole of 2020 with `v` left in the remainder.

**A missing month abbreviation.** Eleven of the twelve CLDR abbreviated month
names ship. `zář` does not, so `15. zář 2020` returns the whole of 2020 with
`15. zář` stranded where `15. srp 2020` returns the day.

**Mid-period by the other noun.** `polovina` and `prostředek` are the
mid-period words, so `v půlce května` — at least as ordinary in speech —
returns the whole of May with `v půlce` stranded.

## Open questions for a native speaker

1. Is the accusative after `na` the only linking grammar the quarter hour takes? The half hour and the quarter hour disagree about
   case in a way no other locale here has to model.
2. What case do the shipped oblique weekday and month forms mark, and is the
   set complete for each word?
3. Are `čtvrtletí` and `kvartál` interchangeable for a calendar quarter, or
   does one belong to fiscal usage?
4. Is `v noci` the right single surface for the night band, or does colloquial
   Czech need `v noci` alongside a separate `večer`-adjacent form?
5. Does `půlka` compete with `polovina` in date phrases (`v půlce května`)
   strongly enough to ship, or is it too colloquial for a calendar reading?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("cs")
    True
    >>> span, rest = extract_timespan('půl deváté', "cs", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T08:30:00', '')
    >>> span, rest = extract_timespan('čtvrt na devět', "cs", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T08:15:00', '')
    >>> span, rest = extract_timespan('tři čtvrtě na devět', "cs", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T08:45:00', '')
    >>> span, rest = extract_timespan('v 9 hodin večer', "cs", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T21:00:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('pět minut po deváté', "cs", anchor) is None
    True
    >>> extract_timespan('v noci', "cs", anchor) is None
    True

---
[← Croatian](hr.md) · [Home](../index.md) · [Danish →](da.md)
