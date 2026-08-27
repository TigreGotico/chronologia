# Hindi (`hi`)

The single most important thing about this locale is what it will not answer.
कल means both yesterday and tomorrow. परसों means both the day before yesterday
and the day after tomorrow. Which one a speaker means is carried entirely by the
tense of the verb, and chronologia does not read verb tense. So both words are
refused outright: a bare कल returns nothing rather than a fifty-fifty guess at a
direction. आज (today) is unambiguous and does resolve. There is no other named
day in this locale, and its absence is the design.

The other thing worth knowing before reading further is that Hindi's markers
are postposed. "Three days ago" is `तीन दिन पहले` — the quantity first, the
marker last. That is CLDR's own past relative-time pattern for the language,
`{0} दिन पहले`, and the offset construction reads it in that order.

## What ships

**Months** come from CLDR 47, `cldr-dates-full/main/hi/ca-gregorian.json`, in
the wide and abbreviated widths. फ़रवरी is written with the nukta; the
nukta-less फरवरी is as common in ordinary Hindi typing and names the same
month, so both ship.

**Weekdays** are the Wiktionary Hindi entries.

**Units** carry both the direct and the oblique case, because a noun counted by
a numeral stands in the oblique — दिन / दिनों, हफ़्ता / हफ़्ते, सदी / सदियाँ /
सदियों. The declension class governs how many surfaces there are: a masculine
consonant stem has one direct form, an ā-stem has a distinct oblique, and an
invariant loanword like सेकंड has one form for everything. Where a Sanskritic
doublet exists and Wiktionary lists it as a synonym of the vernacular word —
शताब्दी and शती beside सदी, वर्ष and बरस beside साल, माह and मास beside महीना —
both registers ship.

**Relative offsets** postpose their marker. The past marker is पहले, which is
CLDR's own pattern word for every unit field; the future marker is में, CLDR's
`{0} दिन में`, with बाद as the other everyday word for the same reading —
Wiktionary's own usage example there is `एक दिन बाद`.

**The determiners** इस (this), पिछला (last) and अगला (next) are the words CLDR
uses for the relative-type-0, -1 and +1 names in this locale. इस is the oblique
singular of यह, which is the form a following noun requires. पिछला and अगला are
ā-stems and ship in all three declension forms.

**The clock** has four constructions and one asymmetry that is easy to get
backwards.

साढ़े and सवा count **forward** from the hour they name: `साढ़े तीन` is 3:30 and
`सवा एक` is 1:15. Wiktionary's entries give both, with usage examples —
`सवा एक बज गए हैं` glossed as 1:15, and साढ़े's own example running
`डेढ़, ढाई, और अब साढ़े तीन बज गए हैं`.

पौने counts **back**. `पौने दस` is 9:45, a quarter short of ten, and never a
quarter past it. It is the asymmetric member of the set, which is why it ships
in a separate family from the two forward-counting fractions; a fold treating
all three alike would place every पौने time an hour late.

डेढ़ and ढाई are fully suppletive literals. डेढ़ is one and a half and, as a
clock reading, *is* half past one; ढाई is two and a half and half past two.
Neither is ever composed from a half word plus a numeral, so they ship as
landmarks at minute 90 and minute 150 of the day rather than as fractions.

बजकर frames minutes counted forward from a struck hour: `आठ बजकर बीस मिनट` is
8:20. It is the conjunctive participle of बजना, "to strike the hour". बजे is the
adverb that closes an ordinary spoken clock reading.

**Day parts** take their bands from the CLDR 47 supplemental day-period rule
set for `hi`, transcribed in `chronologia/dayparts.py`, and their surfaces from
the CLDR period names, each confirmed against a Wiktionary gloss: सुबह, दोपहर,
शाम, रात.

**Numerals** are a curated native lexicon in
`chronologia/extract/numfold_indic.py`. This is not an optimisation but a
necessity: Hindi's numerals from one to ninety-nine are suppletive and not
compositional — ब्यालीस is forty-two and cannot be derived from the words for
four and two — so a compositional folder cannot read them at all.

**Ordinals** ship in the vernacular series पहला / दूसरा / तीसरा and then the
-वाँ pattern, gender-inflecting throughout.

**Markers** are Wiktionary postposition entries: के बाद (after), से पहले and
के पहले (before, with के पूर्व listed as a synonym), के बीच (between), से (from,
since, the ablative), तक (until), हर and प्रत्येक (every), को (the "on" that
attaches to a weekday).

## What refuses

**कल and परसों**, as above — the central design decision of this locale.

**The Sanskritic ordinals.** प्रथम, द्वितीय, तृतीय, दशम are a separate learned
register from the vernacular series that ships. Mixing them would need that
register's own paradigm, so it is left out.

**बृहस्पतिवार**, the formal name for Thursday. Wiktionary carries it only as a
Sanskrit entry; the Hindi गुरुवार entry names it a synonym, but the word has no
Hindi entry of its own, so it is not attested for this locale.

**The Vikram Samvat months.** चैत्र, वैशाख, फाल्गुन and the rest are not
vocabulary but a calendar — the lunisolar system carries a leap month and a
year offset that varies by month, and implementing it is a calendar
implementation, not a word list. A Vikram Samvat year is never silently
converted either: `2081 विक्रम संवत` reads 2081 as the Gregorian year it spells
and leaves विक्रम unread, rather than quietly applying a +57 shift.

**Closed ranges.** Hindi frames a closed range with both markers postposed —
`A से B तक`, the start closed by से and the end by तक. The range grammar reads a
leading frame, so only the open reading fires and the far bound stays visible in
the remainder. `छह बजे से दस बजे तक` gives six o'clock onward with `तक` unread.
The open ranges themselves, `शुक्रवार तक` and `सोमवार से`, do resolve. The same
applies to के बीच, which is attested as "between" but trails both its bounds.

**The minutes-to frame.** `दस बजने को सात मिनट` counts seven minutes short of
ten. Wiring it would need a subtractive clock direction spelled as a two-word
verbal frame, which no construction order expresses, so it refuses rather than
reading the number forward.

**आधी रात**, the everyday phrase for midnight. आधी is the half word the
fractional constructions read and रात is the night band, and no compound
landmark ships. The phrase returns the night band with आधी left in the
remainder — mid-band rather than silently wrong, and visible about it.

**Period parts.** जून की शुरुआत, जून के अंत, जून के मध्य return the whole of
June with the qualifier unread. No early/mid/late vocabulary could be attested
as a fixed temporal expression.

**Calendar quarters and ISO week references.** पहली तिमाही and तीसरा सप्ताह
both refuse; neither was attested.

**Era vocabulary.** `44 ईसा पूर्व` and `ईसवी सन 1947` either refuse or leave the
era word unread. The abbreviations could not be attested.

**लाख and करोड़.** Both are everyday Hindi for 10⁵ and 10⁷, and neither ever
names a date. They belong to a deep-time scale vocabulary this locale does not
ship, so `एक लाख साल पहले` refuses.

## Open questions for a native speaker

1. Is a real date-of-month written and spoken as a cardinal or as an ordinal?
2. Do the oblique unit paradigms condition on the individual numeral in ways the
   shipped direct/oblique pair does not capture?
3. How do the numerals compound above one hundred?
4. Is पर attested as a clock "at" marker? It is a plausible analogy and is not
   shipped on that basis.
5. Is the bare planet-name colloquial form of a weekday, dropping वार, current
   beyond इतवार?
6. Is there a fixed early/mid/late vocabulary for a month that could be
   attested?
