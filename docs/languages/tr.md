# Turkish (`tr`)

<!-- agent-hint
covers: where each construction of the Turkish locale comes from, what it refuses and which questions a native speaker would settle
source: `chronologia/locale/tr/lang.json`, `chronologia/locale/tr/*.voc`, `chronologia/extract/numlayer.py:NUMTAG_LANGS`
generated: no
verify: python -m doctest docs/languages/tr.md && python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\">>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\",t)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/tr.md
see: `docs/languages/index.md`, `docs/extraction.md`
-->

This page records where each construction of the Turkish (`tr`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

Turkish is postpositional, and the whole locale is arranged around that. The
marker follows what it scopes — `üç gün sonra` is three days later, `geçen
hafta` is last week but `salı günü` puts the day-word after the weekday — so
`lang.json` sets the marker position to `post` for the weekday and
relative-period constructions and declares the "until" position postfix. The
range frame is postposed too: `pazartesi ile cuma arası`, not a preposition
pair.

The spoken clock is the other thing to know, and it is case-marked. Additive
`geçe` takes the hour in the accusative — `saat dokuzu beş geçe` is 9:05, `üçü
çeyrek geçe` is 3:15 — while subtractive `kala` takes it in the dative, and
counts back from the hour being approached: `saat yediye çeyrek kala` is 6:45
and `dörde yirmi kala` is 3:40. Both markers are cited to the Türk Dil Kurumu's
*Güncel Türkçe Sözlük*, which glosses `geçe` as "after the stated time" and
`kala` as "with a certain time still to go before the stated time".

## What ships

**Weekdays and months** ship with no recorded source. `günü`, the day-word that
trails a weekday, is registered as its own marker so that `salı günü` reads as
Tuesday rather than leaving a stray noun.

**The date line** is little-endian, and Turkish is one of the languages that
writes the dotted civil date, so `15.06.2020` reads. `ordinal_dot` is off.

**Relative offsets** take exactly one shape, count then unit then marker:
`üç gün sonra`, `beş dakika önce`. There is no marker-first order, because
Turkish has none.

**The half hour is a dedicated word, not a fraction.** `buçuk` is additive on
the hour already named — `üç buçuk` is 3:30 — and `bare_half_past` is set
rather than `bare_half_to`. The vocabulary argues the parsing consequence:
TDK lists `buçuk` as an adjective meaning "and a half", joining the preceding
cardinal into a single numeral, so `üç buçuk` is one reading of the clock and
not an hour with a stray word after it. The hour-introducing noun `saat` frames
that whole reading, which is why an `at HOUR FRACTION` order exists and
`saat üç buçuk` is 3:30 rather than 3:00 with `buçuk` left over.

`çeyrek` is the quarter, cited to TDK as a fourth part and as fifteen minutes
of an hour. `öğle` is noon and `gece yarısı` is midnight.

**The day-part adverbial leads the time phrase.** `öğleden sonra saat üç` is
the plain way to say three in the afternoon, and the vocabulary cites TDK's
mirror compound `akşam saati` for the day-part word leading the hour noun. The
postposed order occurs too, so the clock construction reads the marker on
either side of the hour.

**Day parts** take their boundaries from the Unicode CLDR 47 day-period chart
for `tr`, transcribed in `chronologia/dayparts.py` as morning `[06:00, 12:00)`,
afternoon `[12:00, 19:00)`, evening `[19:00, 21:00)` and night
`[21:00, 06:00)`. The evening is a narrow two-hour band and the night wraps
across midnight. Three of the four have surfaces — `sabah`, `akşam` and `gece`
— each cited to Wiktionary, and the first two also ship their
third-person possessive forms `sabahı` and `akşamı`, because that is the form
the `<weekday> sabahı saat …` construction uses: `salı akşamı` is Tuesday
evening, not the evening in general.

**Seasons and half-years are year-first and possessive-marked**, which is the
most distinctively Turkish part of the locale. `season_year_order` is set to
`year_first`, and each season ships both its bare form and its third-person
possessive: `2020 yazı` is 2020's summer, `2020 kışı` its winter, `2020
sonbaharı` its autumn. The vocabulary works the vowel harmony out per word and
cites TDK's possessive-suffix reference — `sonbahar` ends in a back unrounded
vowel and takes `-ı`, `güz` ends in a front rounded one and takes `-ü`.

The half-year works the same way and needs one more piece. `2020'nin ilk
yarısı` puts the year in the genitive, and the tokenizer splits the suffix off
at the apostrophe as a standalone token, so the genitive endings are registered
as their own optional connector across the full vowel-harmony set — `nin`,
`nın`, `nun`, `nün` and the vowel-final variants — cited to TDK's *İmla
Kılavuzu*. `yarı` and `yarısı` are the period nouns and `yarım` is kept
separate for the clock and quantifier path. Naming the year outright works too
— `2020 yılının ilk yarısı` — through the year noun `yıl`, whose possessed and
genitive forms are written as one word and so are registered individually.

**Fuzzy month parts** are postposed too: `haziran başı`, `haziran ortası`,
`haziran sonu`.

**Eras** are `MÖ` and `MS`, readable on either side of the year.

**The century** is `yüzyıl`, cited to TDK. The Arabic loan `asır` is
deliberately left out: the vocabulary records that one attested surface is
enough and that keeping the set small keeps the false-positive risk down.

## Weaker provenance

The day-part surfaces rest on Wiktionary for the bare nouns, with TDK cited
only for the possessive forms.

The weekday and month names, and the holiday vocabulary, carry no recorded
source. The locale sets `hemisphere` to null.

## What refuses

**A from-to range on weekdays.** `pazartesiden cumaya` returns nothing. The
locale ships no "from" or "to" markers at all — the only range frames are the
postposed `arası`/`arasında` and the dash, so `pazartesi ile cuma arası` and
`3 Temmuz - 10 Temmuz` both read.

**An ordinal week number.** `12. hafta` returns nothing; the ISO week order is
week-word first, so `hafta 12` reads.

**A bare duration.** `iki hafta` returns nothing, and so does a bare `yüzyıl`.
A quantity with no marker is still only a quantity.

**A bare `öğleden sonra`.** The phrase reads as a meridiem in front of a clock
time but does not resolve as an afternoon band on its own; the afternoon band
has no day-part surface.

## Open questions for a native speaker

1. Should `2020 birinci çeyrek` read, given that the seasons and the half-year
   are year-first in exactly that shape?
2. What is the ordinary surface for the afternoon band, and should
   `öğleden sonra` do double duty as both meridiem and band?
3. Should `pazartesiden cumaya` — ablative to dative — read as a range, and are
   there other case-marked range frames worth reading?
4. Is `12. hafta` the ordinary way to name an ISO week in Turkish?
5. Does `asır` occur often enough in running text to be worth the
   false-positive risk?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("tr")
    True
    >>> span, rest = extract_timespan('üç gün sonra', "tr", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-30T00:05:00', '')
    >>> span, rest = extract_timespan('geçen hafta', "tr", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-19T00:00:00', '')
    >>> span, rest = extract_timespan('salı günü', "tr", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T00:00:00', '')
    >>> span, rest = extract_timespan('pazartesi ile cuma arası', "tr", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-07-03T00:00:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('pazartesiden cumaya', "tr", anchor) is None
    True
    >>> extract_timespan('12. hafta', "tr", anchor) is None
    True
    >>> extract_timespan('iki hafta', "tr", anchor) is None
    True

---
[← Thai](th.md) · [Home](../index.md) · [Ukrainian →](uk.md)
