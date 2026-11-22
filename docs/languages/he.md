# Hebrew (`he`)

<!-- agent-hint
covers: where each construction of the Hebrew locale comes from, what it refuses and which questions a native speaker would settle
source: `chronologia/locale/he/lang.json`, `chronologia/locale/he/*.voc`, `chronologia/extract/numlayer.py:NUMTAG_LANGS`
generated: no
verify: python -m doctest docs/languages/he.md && python -c 'exec("import ast,re,sys\nfrom datetime import datetime\nfrom chronologia import extract_timespan\np=sys.argv[1];sk=set(sys.argv[2:]);c=re.search(r\"/(\\w+)\\.md$\",p)[1];t=open(p).read()\npr=re.sub(r\"\\s+\",\" \",re.split(r\"-{2}>\",t,maxsplit=1)[1].split(\"\\n## Checked examples\\n\")[0]);A=datetime(2017,6,27,13,4);bad=0;cl=set();R=set();W=[]\ndef mask(m):\n    W.append(m[1].replace(\"\\x01\",\" \")); return \"\\u27e6%d\\u27e7\"%(len(W)-1)\npm=re.sub(r\"`([^`]*)`\",lambda m:mask(re.match(r\"`([^`]*)`\",m[0].replace(\". \",\".\\x01\"))),pr)\nG=r\"((?:\\u27e6\\d+\\u27e7(?:,| and| or|, and)? ?)+)\"\ndef phr(g): return [W[int(i)] for i in re.findall(r\"\\u27e6(\\d+)\\u27e7\",g) if re.search(r\"[^\\W_]\",W[int(i)])]\nfor s in re.split(r\"(?<=[.!?])\\s+\",pm):\n    for m in re.finditer(G+r\"[^\\u27e6\\d]{0,60}?(?<![\\d:\\u2013-])(\\d\\d):(\\d\\d)(?![\\d\\u2013-]|:\\d)\",s):\n        if s[m.end():m.end()+1] in \"\\u2013-\": continue\n        for ph in phr(m[1]):\n            if ph[0]==\"-\" or \"\\u2026\" in ph or \"<\" in ph or ph+\"@\"+m[2]+\":\"+m[3] in sk: continue\n            r=extract_timespan(ph,c,A)\n            if not(r and r[0].start.minute==int(m[3]) and r[0].start.hour%12==int(m[2])%12): bad=1;print(\"clock\",ph,m[2]+\":\"+m[3])\n    if re.search(r\"returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve\",s): R|=set(phr(s))\n    for m in re.finditer(G+r\"\\s*(?:both |each |all |also |still )?(?:returns? nothing|returns? \\u27e6\\d+\\u27e7|refus(?:es|e|ed)\\b|(?:is|are) refused|(?:does|do) not resolve|fails? to resolve)\",s):\n        if \"None\" in m[0] or \"nothing\" in m[0] or \"refus\" in m[0] or \"resolve\" in m[0]: cl|=set(phr(m[1]))\nfor x in cl:\n    if extract_timespan(x,c,A) is not None: bad=1;print(\"refusal not None\",x)\nex={ast.literal_eval(x) for x in re.findall(r\"^\\s*>>> extract_timespan\\((.+?), \\\"\\w+\\\", anchor\\) is None\\n\\s+True$\",t,re.M)}\nif cl-ex: bad=1;print(\"no doctest\",cl-ex)\nif ex-R: bad=1;print(\"doctest without a refusal sentence\",ex-R)\nif sk: print(\"skipped:\",sorted(sk))\nsys.exit(bad)\n")' docs/languages/he.md
see: `docs/languages/index.md`, `docs/extraction.md`
-->

This page records where each construction of the Hebrew (`he`) locale comes from, which ones rest on weaker evidence and which ones it refuses. Numbers are read by numtag (`NUMTAG_LANGS` in `chronologia/extract/numlayer.py`).

Hebrew writes right to left, glues its prepositions onto the word they govern,
and keeps two calendars in everyday use at once. All three facts shape what
this locale can read. The proclitic is the sharpest of them: `ב־` ("in, on,
at"), `מ־` ("from") and `ל־` ("to") are single letters written flush against
the following noun, so `באוגוסט` ("in August") is one token, not two, and any
surface a construction wants to bind has to be listed in the fused spelling or
it will not be seen. The locale's vocabulary is therefore full of pairs —
`אוגוסט` beside `באוגוסט`, `שבת` beside `בשבת` — and the places where only the
bare member of a pair ships are exactly the places where an ordinary phrase
returns nothing.

## What ships

**Gregorian months** ship in two spellings each, the bare noun and the
`ב־`-prefixed one. The bare set is the CLDR 47 `he` `ca-gregorian` wide format
chart character for character, `ינואר` through `דצמבר`, with `מרס` listed
beside `מרץ` for March. The prefixed set is not a second CLDR chart but a
consequence of the first: CLDR's `he` long date pattern is `d בMMMM y`, with
the preposition written into the pattern itself and no space before the month
placeholder, so the form a real date line contains is always the fused one.
`months.voc` repeats the same twenty-six surfaces as a flat list.

**Hebrew-calendar months** ship as their own slot, `month_hebrew_1` through
`month_hebrew_13`, in Hebrew script, in Latin transliteration, and with the
`ב־` prefix — `ניסן`, `nisan`, `בניסן`. The leap month Adar II carries its
three ordinary names, `אדר ב`, `אדר שני` and `אדר בית`, plus Latin variants.
Seven of the locales here ship a Hebrew-calendar month set at all, and this is
the only one that ships it in Hebrew script. Nothing leaks between the two
month sets: the Gregorian surfaces and the Hebrew-calendar surfaces have no
string in common, and the year that follows the month is read on the calendar
the month belongs to, so `15 באוגוסט 2020` is a day in the Common Era while
`15 בניסן 2020` is a day in Anno Mundi 2020 and returns a date before the
Common Era began.

**Weekdays** are the day noun plus an ordinal — `יום ראשון` is literally "first
day", Sunday — and only the seventh has a name of its own, `שבת`. The full
names match CLDR 47's `he` wide weekday chart exactly, and each ships with its
`ב־` prefix as well. The abbreviations are the same construction with the
ordinal reduced to its letter, `יום א׳` through `יום ו׳`, and CLDR's
abbreviated chart gives exactly that, with `שבת` unabbreviated in the seventh
slot. The geresh is typographic and the tokenizer strips it, so the vocabulary
lists the bare letter. The English Wikipedia article on the days of the week in
the Hebrew calendar carries the same table and is the source the vocabulary
comments name.

**Day parts** are `בבוקר`, `בערב` and `בלילה`, each shipped in the deictic
prefixed form a phrase actually uses rather than the dictionary citation form.
The band boundaries are the Unicode CLDR 47 day-period rules for `he`
transcribed in `chronologia/dayparts.py` — morning 06:00–12:00, evening
18:00–22:00, night 22:00–06:00 — and the surfaces are CLDR's own
`morning1` / `evening1` / `night1` labels. Wiktionary carries a Hebrew entry
for each of the three underlying nouns, `בוקר`, `ערב` and `לילה`; all three
give a noun sense only, so the adverbial use rests on the day-period data
rather than on those entries, and the etymology section of `לילה` is the one
place a dictionary states the "at night" reading outright.

**The night band is not a meridiem shift.** `בלילה` doubles as a clock cue,
and the resolver treats it as a band that crosses midnight rather than as a
uniform twelve-hour offset: `אחת בלילה` is 01:00, `אחת עשרה בלילה` is 23:00,
`12 בלילה` is midnight. Small hours stay in the morning, evening hours move to
the afternoon side, and the split follows the CLDR night band's 22:00 opening
and the 06:00 morning boundary.

**Numerals** fold from a curated closed set of masculine and feminine
cardinals, deliberately narrower than what the number model will read.
Ordinals do not fold at all, and the reason is total rather than incidental:
`שני`, `שלישי`, `רביעי`, `חמישי` and `שישי` are the ordinals two through six
*and* the weekday names Monday through Friday, and `ראשון` is both "first" and
Sunday. Folding any of them to a digit would destroy weekday and recurrence
parsing. `שני` alone gets a positional rule, because it is also the construct
form of the cardinal "two": it counts as two only when a noun follows it that
it can count, and never straight after the day noun, so `לפני שני ימים` is two
days ago while `כל יום שני` stays every Monday and comes back as a weekly
recurrence bound to that weekday.

**Dual nouns** are their own slot — `יומיים`, `שעתיים`, `דקתיים`, `שבועיים` —
and are withheld from the numeral fold so they keep their unit meaning. Hebrew
and Arabic are the only two locales here that need this slot, and both have it.

**The clock** binds a spelled or digit hour after `בשעה` / `השעה`, or bare,
with an optional meridiem cue. `בשעה שלוש` is three o'clock, `שמונה בערב` is
20:00, `שלוש אחר הצהריים` is 15:00. `חצות` and `צהריים` are midnight and noon.
CLDR 47 gives `H:mm` as the short time format for `he`, and the colon spelling
is what the numeric path reads.

**Gematria year and day numerals** fold where the typography marks them.
A Hebrew numeral is always set off with a gershayim before its last letter or
a geresh on a lone letter, and that mark is the gate: an unmarked run of
letters is ordinary Hebrew and is left alone, which is what keeps weekday names
and the gershayim-marked abbreviations `סופ״ש` and `לפנה״ס` out of the number
path. A marked numeral directly before a Hebrew-calendar month is the day of
the month at its raw value, so `כ״ה בכסלו` is 25 Kislev; a marked numeral after
a month or a year word is the year in the small count, so `כ״ה בכסלו תשפ״ה`
resolves through the Hebrew calendar. An out-of-range day fails the same way
its numeric spelling does rather than falling back to the bare month.

**Relative offsets** run `לפני` for ago and `בעוד` / `עוד` for hence, with the
unit either counted or dual. Relative periods take the article-bearing
demonstrative pattern CLDR records: `השבוע הבא`, `החודש שעבר`, `השנה הבאה` and
`השנה שעברה` are the CLDR 47 `he` `dateFields` relative types for week, month
and year, and all of them resolve.

**Named days** span the five positions around the anchor — `שלשום`, `אתמול`,
`היום`, `מחר`, `מחרתיים` — and are exactly CLDR 47's `he` day field for
relative types −2 through +2. `אמש` ships as a second surface in the yesterday
slot and resolves to the whole of the previous day, not to its night.

**Ranges** run `מ... עד...` and `בין... ו...`. The upper bound in the
unconditional set is `עד` alone, and Wiktionary's Hebrew entry for it gives
"until, till, up until (a time)" with a worked temporal example. `בין` has a
Hebrew preposition entry glossed "between, among" with a biblical citation.
The directional `ל־` is not in that unconditional set, because as a bare
preposition it is far more common than as a range terminal and registering it
globally would fabricate a range out of any `ל־<noun>`; it is gated in its own
file and licensed only when a `מ־` or `בין` lead sits earlier in the span. No
other locale here ships that file.

**The half of a year** takes the feminine ordinal, because the half noun
`מחצית` is feminine and `ראשונה` / `שנייה` are not weekday names and collide
with nothing. Both spellings of "second" and the definite forms ship, so
`המחצית הראשונה של 2020` and `המחצית השנייה של 2020` resolve. Wiktionary's
Hebrew entry for `מחצית` gives "half, one half: one of two equal parts" and
dates the word to Exodus.

**Quarters, ISO weeks, decades, seasons and eras** all resolve. `רבעון` takes a
digit or a relative marker; `שבוע 33` is the ISO week; the decade has its own
spelled vocabulary, `שנות התשעים` and its siblings, which nine of the locales
here ship and most do not; the four seasons ship bare and with the article; and
the era markers are the secular `לפני הספירה` / `לספירה` alongside the
abbreviated `לפנה״ס`.

**Recurrence** reads `כל` plus a unit or a weekday and the adjectival
frequency words `יומי`, `שבועי`, `חודשי`, `שנתי`.

## Weaker provenance

**The institute citations do not carry locators.** Several marker files name
the Academy of the Hebrew Language as a source with no more than an `s.v.` and
the headword — for `עד`, for `ל־`, and for the vocalisation of `מ־`. No
Academy page can be cited for any of them, and an `s.v.` alone is
not a locator that can be followed even in principle. The surfaces are not in
doubt: Wiktionary's Hebrew entries for `עד` and `בין` carry the senses and the
examples independently, and the grammar the files cite alongside is a standard
reference. It is the Academy locators specifically that are unverifiable as
written.

**The Even-Shoshan quotations** in `marker_half.voc` are given as a Hebrew
gloss without an edition or a page, and the same file's Academy attribution has
the same shape. The gloss is accurate to the sense Wiktionary records for
`מחצית`, so the surface is sound and only the locator is loose.

**The plene spellings are not the ones that ship.** CLDR 47's Hebrew-calendar
chart writes Marcheshvan and Sivan with a double vav, `חשוון` and `סיוון`. The
locale ships the defective `חשון` and `סיון` and no comment records the choice,
so the CLDR spelling of two of the fourteen months resolves to nothing.

## What refuses

**The clock's fractions and directions.** The locale ships the fraction words but no direction word.
`שלוש וחצי`, `חצי שלוש` and `רבע לשלוש` return nothing. They mean half past
three, half toward three and a quarter to three. Arabic ships the fraction and
the direction, and goes further with a dedicated pre-pass that splits the
fused `و`-connector off the fraction word. Nothing equivalent exists here.

**The afternoon.** CLDR 47's `he` day-period chart names six periods —
`בבוקר`, `בצהריים`, `אחר הצהריים`, `בערב`, `בלילה` and `לפנות בוקר` — and
`chronologia/dayparts.py` records the afternoon band 12:00–18:00 for `he` like
the other three. No afternoon day-part vocabulary ships. `אחר הצהריים` is
registered only as a PM clock cue, so `שלוש אחר הצהריים` is 15:00 but
`מחר אחר הצהריים` returns the whole of tomorrow and strands the phrase.
`לפנות בוקר`, the small-hours band, has the same shape as an AM cue and
resolves to nothing on its own.

**The bare article deictics.** `הלילה`, `הערב` and `הבוקר` return nothing. They mean tonight, this evening and
this morning, the definite article doing the work a demonstrative does
elsewhere. Wiktionary lists `הַלַּיְלָה` among the
derived terms of `לילה`, so the construction is not obscure; it simply has no
slot here.

**This week, this month, this year.** CLDR 47's `he` `dateFields` gives
`השבוע`, `החודש` and `השנה` as the relative-type-0 surfaces for those three
fields. `השבוע`, `החודש` and `השנה` return nothing, even though all three strings
are present in the unit vocabulary. The demonstratives that ship — `הזה`,
`הזאת`, `הנוכחי`, `הנוכחית` — are the post-nominal series and none of them is
the bare article the CLDR surface uses. The quarter has the same hole from the
other end: CLDR's this-quarter is `רבעון זה`, and the bare `זה` is not in the
demonstrative set, so that phrase refuses while `הרבעון הקודם` and
`הרבעון הבא` resolve.

**The `ב־` proclitic on a unit or a season.** Months, weekdays and day parts
all ship their prefixed spelling, and units and seasons do not. The result is a
split that shows up in ordinary sentences: `השבוע הבא` resolves and
`בשבוע הבא` does not, `החודש שעבר` resolves and `בחודש שעבר` does not, `הקיץ`
resolves and `בקיץ` does not. Nothing splits the proclitic off a token, so a
form absent from the vocabulary is simply invisible.

**The fused `מ־` in a range.** The vav-fused second endpoint of a range is
handled by a dedicated pre-pass, which splits `ומרץ` back into two tokens when
what follows the vav is a recognised month, weekday or day-part surface. The
`מ־` that opens the range gets no such treatment. `מ ינואר עד אפריל` with a
space resolves to the four-month span; `מינואר עד אפריל` written normally
returns April alone and strands the lead. The consequence reaches the
vocabulary's own documentation: `marker_to.voc` cites its grammar with the
worked example `מיום ראשון עד יום שישי`, and that exact string returns Friday
with `מיום ראשון עד` in the remainder, while the spaced `מ יום ראשון עד יום
שישי` returns the week.

**The fused `ל־` in a range.** `marker_to_after_from.voc` states outright that
the fused form is not split, and the effect is the same: `בין ינואר לאפריל`
returns January alone, where `בין ינואר ל אפריל` returns the four-month span.
This one is a recorded trade-off rather than an oversight — splitting `ל־`
freely would turn every dative into a range boundary — but the ordinary
orthography is the fused one.

**Spelled ordinal quarters.** `רבעון שלישי` cannot resolve, and the reason is
the homograph collision above: the spelled ordinal *is* the weekday name. The
digit and the relative-marker forms cover the same ground. This is recorded as
a deliberate limitation in the numeral module and pinned in the corpus.

**The twelve at noon.** `שתים עשרה בצהריים` and `שתיים עשרה בצהריים` both return noon and leave the numeral in the remainder.

**Deep time.** `לפני מיליון שנים` ("a million years ago") returns nothing. The
construction wants a year word after the scale, and the year-word vocabulary
holds `שנת`, `בשנת`, `שנה` and `השנה` but not the plural `שנים` that the phrase
actually uses. `אלף שנים` is in the millennium vocabulary and reaches nothing
on its own.

**Adar I.** The leap year splits Adar in two, and only the second half has a
surface. `אדר` binds the ordinary Adar and Adar II has its own file, but
`אדר א` — CLDR 47 writes it `אדר א׳` — is in no vocabulary, so a date in the
first Adar of a leap year cannot be expressed.

**Abbreviated Gregorian months.** CLDR 47 gives `ינו׳`, `פבר׳`, `אפר׳`, `אוג׳`,
`ספט׳`, `אוק׳`, `נוב׳` and `דצמ׳` for the eight months whose names are
shortened. None ship, so `15 באוג 2020` returns the whole of 2020 with the day
and month stranded.

## Open questions for a native speaker

1. Should the `ב־` proclitic be split off a unit or a season noun generally, or
   should the prefixed forms be listed one by one the way the months and
   weekdays are? The first risks false positives on every word beginning with
   the letter; the second is exhaustive but finite.
2. Is `השבוע` on its own genuinely ambiguous between "this week" and "the week"
   often enough to justify leaving it unbound, or is the temporal reading
   dominant enough to ship?
3. Which spelling of Marcheshvan and Sivan should a date line use — the
   defective `חשון` / `סיון` that ships, the plene `חשוון` / `סיוון` that CLDR
   gives, or both?
4. Is `שתים עשרה` current enough beside `שתיים עשרה` to be worth admitting to
   the numeral set, given that the defective spelling of a numeral is otherwise
   rarer than the defective spelling of a noun?
5. Does the half-hour need `וחצי` after the clock hour, and if so is the
   connective always written fused to the fraction the way Arabic writes its
   own?

## Checked examples

Each example below runs as a doctest with a fixed anchor, so the output does not depend on the machine. The first one shows which reader handles the numbers of this locale.

    >>> from datetime import datetime
    >>> from chronologia import extract_timespan
    >>> from chronologia.extract.numlayer import reads
    >>> reads("he")
    True
    >>> span, rest = extract_timespan('אחת בלילה', "he", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T01:00:00', '')
    >>> span, rest = extract_timespan('אחת עשרה בלילה', "he", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T23:00:00', '')
    >>> span, rest = extract_timespan('שמונה בערב', "he", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T20:00:00', '')
    >>> span, rest = extract_timespan('שלוש אחר הצהריים', "he", datetime(2017, 6, 27, 0, 5))
    >>> span.start_datetime.isoformat(), rest
    ('2017-06-27T15:00:00', '')
    >>> anchor = datetime(2017, 6, 27, 13, 4)
    >>> extract_timespan('שלוש וחצי', "he", anchor) is None
    True
    >>> extract_timespan('חצי שלוש', "he", anchor) is None
    True
    >>> extract_timespan('רבע לשלוש', "he", anchor) is None
    True
    >>> extract_timespan('הלילה', "he", anchor) is None
    True
    >>> extract_timespan('הערב', "he", anchor) is None
    True
    >>> extract_timespan('הבוקר', "he", anchor) is None
    True
    >>> extract_timespan('השבוע', "he", anchor) is None
    True
    >>> extract_timespan('החודש', "he", anchor) is None
    True
    >>> extract_timespan('השנה', "he", anchor) is None
    True

---
[← Hausa](ha.md) · [Home](../index.md) · [Hindi →](hi.md)
