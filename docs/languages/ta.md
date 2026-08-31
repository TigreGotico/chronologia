# Tamil (`ta`)

Tamil is the library's first Dravidian language. It is agglutinative and
case-suffixing, and two of its habits decide what this locale reads: an offset
carries its direction on the counted noun rather than in a separate word, and
the clock runs **forward** from the hour it names.

`ஒன்பதரை` is 9:30 — "nine-and-a-half", the fraction `அரை` fused onto the
numeral for nine — and `ஒன்பதே கால்` is 9:15. A reader who carries over the
European "half nine" habit and subtracts gets 8:30 for both, and every reading
in the language is then an hour out with nothing in the output to show it. The
one construction that genuinely counts backwards says so: `ஆறு மணிக்கு
பதினைந்து நிமிடம் குறைவு` is 5:45, because `குறைவு` means "less" and the hour
the phrase names is the upcoming one.

## The direction lives in the suffix

"Three days ago" is `மூன்று நாட்களுக்கு முன்` — the dative on the noun and a
trailing `முன்`. "In three days" is `மூன்று நாட்களில்` — the locative on the
noun and no preposition whatsoever. The two readings are six days apart and the
only thing separating them is a suffix.

The matching engine reads a direction from a marker token, and the forward
phrase has none to read. The locale's numeral fold therefore cuts the fused
surface in two: the unit in its citation form, and the locative suffix as the
separate forward marker `marker_future.voc` ships. The pairs are transcribed
from CLDR's own in-N patterns one at a time rather than stripped by rule,
because the oblique stem the suffix attaches to differs from noun to noun —
`மாதம்` becomes `மாதத்தில்` and `நாள்` becomes `நாளில்` — and a rule would have
to invent those stems. A bare `இல்` is never written detached in Tamil, so the
marker surface is unreachable from ordinary text.

## The script needed the tokenizer opened up

Tamil is an abugida: a syllable is a base consonant carrying combining vowel
signs, and the virama that cancels the inherent vowel is a combining mark too.
Those marks are Unicode categories Mn and Mc, which the regex `\w` class does
not match. Before the tokenizer's letter class carried them, `ஒன்பதரை` arrived
as the two fragments `ஒன` and `பதர` and not one Tamil word in the locale could
bind a slot. The class now carries the Tamil block's mark subranges — `U+0B82`,
`U+0BBE`–`U+0BCD` and `U+0BD7` — which are Tamil-block codepoints and therefore
inert for every other script. The digits `௦`–`௯` are excluded because the
numeric rule already reads them, and the day, month, year and rupee signs
because a bookkeeping symbol is not a letter.

Tamil digits need no locale pass of their own: they are ordinary Unicode
decimal digits, so `௨௦௨௬` reads as 2026 and `௧௫:௩௦` matches the clock literal
exactly as its ASCII spelling does.

## What ships

**Weekdays** are the CLDR wide and abbreviated forms from
`cldr-dates-full/main/ta/ca-gregorian.json`. Saturday's two forms are the same
word, so no separate abbreviation ships for it.

**Months** are the wide and abbreviated Gregorian names from the same file.
They are transliterations of the Latin ones.

**Relative offsets** come from `dateFields.json`, with both counts of every
pattern. Tamil has singular/plural agreement, the plural stem for "day" is
suppletive in shape (`நாள்` → `நாட்கள்`), and `மணிநேரம்` does not inflect for
count in either direction — CLDR gives the same wording for one hour and for N.

**Day parts** are the CLDR supplemental day-period rules for `ta`, and there
are nine of them, at the high end of what the standard carries for any locale.
They are kept under their own names rather than folded into an English-shaped
four, because the extra cuts are real words with narrow senses: `அதிகாலை` is
03:00 to 05:00 and a band of its own, not a synonym for `காலை`; `மதியம்` and
`பிற்பகல்` split the afternoon at 14:00; `மாலை` and `அந்தி மாலை` split the
evening at 18:00. `நண்பகல்` falls on a band boundary and draws no stretch of
its own, so it ships as a clock landmark instead.

**Numerals** are transcribed surface by surface from Wiktionary's
`Module:number_list/data/ta`, and nothing in the table is generated. Tamil
compounds are not concatenations: a compound is built on a distinct adjectival
stem — `ஒரு`, `இரு`, `மு`, `நால்`, `ஐ`, `அறு`, `ஏழ்`, `எண்`, `பதின்` — and the
join triggers sandhi at the seam, so 11 is `பதினொன்று` rather than `பத்து
ஒன்று` and 21 is `இருபத்தொன்று`. The hundreds are suppletive words in their own
right: `முந்நூறு` is 300 and `நானூறு` is 400, and neither follows from `மூன்று`
or `நான்கு` by any rule. That the source module spells each compound out
instead of generating it is itself the evidence that the seam is not
mechanical. The colloquial doublets the same module carries — `ஒண்ணு`,
`ரெண்டு`, `மூணு`, `நாலு`, `அஞ்சு` — are a real spoken register and are read.

**A day-period word in front of a clock phrase** picks the half-day, and it
does so from the band it names rather than by adding twelve. `மாலை ஆறு மணி` is
18:00 and `இரவு இரண்டு மணி` is 02:00; a blanket "afternoon word means add
twelve" would answer 14:00 for the second, because `இரவு` wraps midnight. The
spoken hour is placed at whichever of its two twelve-hour readings falls inside
the CLDR band, and where neither does the phrase refuses — `காலை ஒரு மணி` names
an hour outside the morning band, nobody says it, and answering either 01:00 or
13:00 would be a guess.

## Weaker provenance

The clock rests on three language-teaching pages rather than a reference
grammar. One of them glosses `பத்து நிமிடம்` ("ten minutes") as "quarter past",
which is simply wrong, and treats `பிற்பகல்` as a PM marker while CLDR uses it
as the label of the 14:00–16:00 band. That page is taken as corroboration for
the 9:30 example only, and every band label comes from CLDR.

The band's closing hour is admitted as well as its opening one, so 18:00 reads
under both `மாலை` and `அந்தி மாலை`. The CLDR band is half-open on instants, but
an hour *name* sitting exactly on a boundary belongs to neither half-open
interval, and 18:00 is spoken as `மாலை ஆறு மணி` readily enough that refusing it
would be the wrong answer. It can never make a phrase ambiguous: no band here
is twelve hours wide, so at most one of an hour's two readings ever lands
inside one.

## What refuses

**A count in front of `திங்கள்`.** The word is Monday, the moon, "month" and an
obsolete word for the week, all at once, and it lands on the most frequent
weekday token in the language. CLDR uses `மாதம்` for the month field, so this
locale reads that as the month unit and ships no month sense for `திங்கள்` at
all. A count in front of it can then only be a span of months — nobody counts
Mondays that way — so the count vetoes the weekday reading and `இரண்டு திங்கள்`
returns nothing. Declining the false weekday reading is not the same as
asserting the unshipped month one, which stays unavailable. Bare `திங்கள்`
carries no count and is still Monday.

**`முக்கால்` on the clock.** Three quarters is a fraction word of the language,
but no source consulted works it out as a clock reading. Reading it as three
quarters past the named hour is an analogy from `அரை` and `கால்`, and an
analogy is not evidence. The whole phrase is withdrawn, numeral included, so
the hour cannot survive as a bare day of the month either.

**The fused fractions on any hour but nine.** Both fusions elide the numeral's
final vowel before the following one, and the sources work that elision out for
nine and no other hour. Applying it to the remaining eleven would be generated
spelling, not attested spelling — the same line the numeral table draws. The
general shapes `N மணி`, `N மணி M நிமிடம்` and the two marked constructions
carry every other reading and need no fused surface.

**The Tamil solar months.** `சித்திரை`, `வைகாசி` and the other ten are a full
second register and entirely live. They are not the month-1-to-12 equivalents
of the Gregorian list: each straddles a Gregorian month boundary, and turning
one into a date needs calendar arithmetic no source consulted closes.
Recognising them without that arithmetic would mean answering a date a month
wide and a fortnight off.

**A compound numeral whose surface was not transcribed.** `பதினான்கு` (14) and
`இருபத்திரண்டு` (22) fold to no value. The digits still read, and inventing the
missing spelling would be a guess dressed up as coverage.

**`மணி` and `கால்` on their own.** `மணி` is "bell" before it is "o'clock", and
`கால்` is the ordinary word for a leg. Both read as clock words only beside a
numeral, and the hour duration noun the locale ships is `மணிநேரம்` instead.

**Ordinals, seasons, decades, centuries, and "before", "from", "until" and
"between" as free-standing markers.** No source consulted attests them. `முன்`
ships only in the trailing role CLDR's ago-pattern gives it.

**Midnight as a landmark.** No source consulted for this locale gave its label,
so none is invented.

## Open questions for a native speaker

- The full `-கிழமை` weekday register (`ஞாயிற்றுக்கிழமை` and its siblings) and
  whether it is the preferred form in writing. CLDR does not carry it.
- Whether the fused fraction forms are the ordinary written surface or a spoken
  shortening of `ஒன்பது மணி முப்பது நிமிடம்`. The answer decides whether the
  fused table is worth extending past the one attested hour.
- Whether `முக்கால்` in a clock phrase is read as three quarters past the named
  hour, by analogy with `அரை` and `கால்`.
- Whether the colloquial numeral doublets appear in written dates and times or
  only in speech.
- Free-standing "before", "from … until" and "between", with the case each
  governs. `முதல்` … `வரை` is the expected pair for the second but neither was
  confirmed.
- Whether an unmarked minute tail (`ஏழு மணி இருபது நிமிடம்`, with neither
  `மேல்` nor `குறைவு`) is genuinely read forward, as the fused fractions
  suggest, or whether it is simply not written that way.
