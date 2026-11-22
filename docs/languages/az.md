# Azerbaijani (`az`)

<!-- agent-hint
covers: where each construction of the Azerbaijani locale comes from, what it refuses and which questions a native speaker would settle
source: `chronologia/locale/az/lang.json`, `chronologia/locale/az/*.voc`, `chronologia/extract/numlayer.py:NUMTAG_LANGS`
generated: no
verify: python -m doctest docs/languages/az.md && python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\">>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\",t)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/az.md az@19:00 'saat doqquz yarım@09:30'
see: `docs/languages/index.md`, `docs/extraction.md`
-->

This page records where each construction of the Azerbaijani (`az`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

Azerbaijani is Turkic and agglutinative, and the locale sits next to Turkish in
this library in a way that is more hazard than help. The two languages share a
great deal of temporal vocabulary — `ay`, `gün`, `həftə`, `saat`, `sonra`,
`yarım`, `min` are the same words in both — and they also share strings that
mean different things, which is the more dangerous case. Every Azerbaijani
surface here is checked against an Azerbaijani source rather than inherited
from `tr`.

Two false friends make the point. Turkish `sabah` is "morning" and appears in
`tr/clock_meridiem_am.voc` and `tr/daypart_morning_tr.voc`; Azerbaijani `sabah`
is **tomorrow**, and it is in `az/named_day_1.voc`. Azerbaijani puts `səhər` in
the morning slot instead. Turkish `yaz` is summer and sits in
`tr/season_summer.voc`; Azerbaijani `yaz` is **spring**, and it sits in
`az/season_spring.voc` beside its synonym `bahar`. Both are confirmed by the
Wiktionary entries for `sabah`, `səhər`, `yaz` and `bahar`, each of which
carries an Azerbaijani section that glosses the word exactly this way; the
`sabah` entry adds a usage note recording that the "morning" sense is archaic
or dialectal in Azerbaijani. The library gets both of these right, and the
placement is the evidence.

## What ships

**Months** are the Russian-mediated international series — `yanvar`, `fevral`,
`mart`, `aprel`, `may`, `iyun`, `iyul`, `avqust`, `sentyabr`, `oktyabr`,
`noyabr`, `dekabr` — one surface each, with no inflected alternates.

**Weekdays** are the ordinary Azerbaijani set built around the market day and
the Friday prayer: `bazar` for Sunday, `bazar ertəsi` for Monday, `çərşənbə
axşamı` for Tuesday, `çərşənbə` for Wednesday, `cümə axşamı` for Thursday,
`cümə` for Friday, `şənbə` for Saturday. Four of the seven are multi-word, and
two of those are the "eve of" compounds that name the following day.

**The date line** is day-month-year, and `lang.json` sets `dmy` true and
`dotted_date` true, so both `5 iyun 2027` and the dotted numeric form read.

**Relative offsets** are postposed only. `lang.json` declares exactly one order,
`NUM UNIT MARKER`, because the Azerbaijani marker always follows: `üç gün
əvvəl` for three days ago, `üç gün sonra` for three days on. The backward
marker ships in three variants — `əvvəl`, `qabaq`, `öncə` — and the forward one
is `sonra`. Determiners `keçən`/`ötən` for last and `gələn`/`növbəti` for next
lead their noun, and `bu` is the proximal.

**The clock** puts the hour noun `saat` before the numeral and marks the
numeral itself with the locative case: `saat üçdə`, at three. The suffix
harmonises for backness and for the voicing of the preceding consonant, giving
`-tə`, `-ta`, `-də`, `-da`. numtag reads the inflected numeral as its cardinal,
`üçdə` as 3. A digit hour takes the suffix after an apostrophe, `saat 9'da`;
the fold in `chronologia/extract/numlayer_turkic.py` drops that suffix, but
only inside a clock frame where a `saat` token is present.

**The daypart lead.** Azerbaijani states the part of day before the hour:
`səhər saat doqquzda` is nine in the morning, `axşam saat səkkizdə` eight in
the evening. `gecə` is handled separately because it is not a uniform twelve-
hour shift — it scopes the clock to a band that crosses midnight, so `gecə
saat üçdə` is 03:00 while `gecə saat doqquzda` is 21:00. The resolver splits
the band accordingly, and both readings hold.

**No clock fraction ships.** There is no `clock_fraction_15.voc` and no
`clock_fraction_30.voc` in this locale. Five of the sixty-one locales in the
library are in the same position — `az`, `ha`, `sw`, `ta` and `th` — so it is not unique, but it is a real gap and it has a visible
consequence in the defects section below. `marker_half.voc` holds `yarım`, and
the quantifier table maps `yarım` to 0.5 and `rüb` to 0.25, but neither reaches
the clock.

**Century and decade** are the two vocabulary groups that carry their own
source comments. `əsr` and its plural `əsrlər` come from the Wiktionary entry
for `əsr`, which confirms both the gloss ("century; age, epoch,
era"), the Arabic origin, and the plural in the declension table. `onillik` and
`onilliklər` come from the Wiktionary entry for `il`, which
lists `onillik` glossed "decade" among the derived terms.

**Day-part bands** are transcribed from the Unicode CLDR 47 Day Period Rules
chart, which gives `az` a night running from 19:00, a morning from 04:00, an
afternoon from 12:00 and an evening from 17:00. The bands ship; the surfaces do
not. Ten locales in the library ship no `daypart_*.voc` files at all — an, ast,
az, be, eo, ga, ha, mt, mwl and oc — but nine of those carry no day-part bands
either, so the missing vocabulary costs them nothing. Azerbaijani is the only
one of the ten that has bands with nothing to speak them: the boundaries are
declared and unreachable, and the words are held for a native reader rather
than guessed from the CLDR citation forms.

## Weaker provenance

The meridiem files cite `Azərbaycan dilinin izahlı lüğəti`, the explanatory
dictionary of the Azerbaijani language, without a locator or a URL. That source
could not be reached and is recorded here as unchecked. The claims it is cited
for — that `gecə` scopes a midnight-crossing band and that the daypart word
stands before the hour noun — are independently supported by the Wiktionary
entry for `gecə`, which glosses it "night", and by the parser's own behaviour,
but neither of those is the cited source.

The months, weekdays, seasons, units and markers carry no source comments at
all. Their correctness is asserted by the files, not evidenced by them.

## What refuses

**Bare day-part words.** `axşam`, `gecə` and `səhər` standing alone return
nothing, which follows directly from the locale shipping no day-part surfaces.
They resolve only in their meridiem role, before a clock.

**Half past.** With no clock fraction, `saat doqquz yarım` cannot be read as
09:30.

## Known defects

Anchored at 2017-06-27 13:04.

`extract_timespan("2020-ci ilin birinci rübü", "az")` returns the whole of
2020 with `ci ilin birinci rübü` in the remainder, where the first quarter is
meant. This is the suffixed-ordinal tokenisation gap: the hyphen in `2020-ci`
is sheared, the `ci` fragment is left standing, and nothing re-fuses it the way
the Basque locale re-fuses `5ean`. The plain `2020-ci il` shows the same shear,
returning the year with `ci il` stranded. Written without the suffix,
`1 rüb 2020` returns the correct first quarter.

`extract_timespan("iyunun 5-i", "az")` returns nothing. The genitive month plus
suffixed ordinal day is an ordinary way to write a date, and the same shear
defeats it.

`extract_timespan("saat doqquz yarım", "az")` returns 09:00 with `yarım` in the
remainder. The hour is right, the half hour is lost, and the stranded marker is
the only signal that anything was dropped.

`extract_timespan("bazar ertəsinə qədər", "az")` returns a span up to Monday
2017-07-03, but leaves `ertəsinə` in the remainder — the dative-marked weekday
is not read as one token, and the span is right by luck of the surrounding
words rather than by parse. Written without the case ending, `bazar ertəsi
qədər` resolves cleanly with an empty remainder, but to a different Monday,
2017-07-04: the two phrasings differ in value, not only in whether the
remainder is clean.

`extract_timespan("yazda", "az")` returns nothing. The locative season form is
not listed, so "in spring" fails while bare `yaz` succeeds.

`extract_timespan("yanvarın ortalarında", "az")` returns nothing, as does
`əsrin ortalarında`. `period_part_mid.voc` holds `ortalarında`, but the
genitive-marked noun before it is not read.

## Open questions for a native speaker

1. What are the ordinary spoken surfaces for the four day-part bands, so that
   `axşam` and `gecə` can stand alone and not only before a clock?
2. Is there a half-past construction for the clock, and does `yarım` take part
   in it?
3. Should the case-inflected forms of the seasons, weekdays and month names be
   listed as alternates, or should the tokenizer learn to shear the suffix?
4. Is `qabaq` or `öncə` interchangeable with `əvvəl` in a counted offset, or
   are they stylistically restricted?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("az")
    True
    >>> span, rest = extract_timespan('gecə saat üçdə', "az", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T03:00:00', '')
    >>> span, rest = extract_timespan('gecə saat doqquzda', "az", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T21:00:00', '')
    >>> span, rest = extract_timespan('bazar ertəsi', "az", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-07-03T00:00:00', '')
    >>> span, rest = extract_timespan('çərşənbə axşamı', "az", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T00:00:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('extract_timespan("iyunun 5-i", "az")', "az", anchor) is None
    True
    >>> extract_timespan('extract_timespan("yazda", "az")', "az", anchor) is None
    True
    >>> extract_timespan('extract_timespan("yanvarın ortalarında", "az")', "az", anchor) is None
    True

---
[← Asturian](ast.md) · [Home](../index.md) · [Basque →](eu.md)
