# Malay (`ms`)

Malay is morphologically light — nouns do not inflect for number, and a
weekday, a month and a unit noun all arrive in one shape — so most of this
locale is a short list of words rather than a set of paradigms. Almost all of
the difficulty is concentrated in one place: how a half hour is said, and which
hour it belongs to. That question is open, and the section below states exactly
what is known and exactly what is not.

The reference dictionary throughout is *Kamus Dewan*, published by Dewan Bahasa
dan Pustaka and searchable through the Pusat Rujukan Persuratan Melayu (PRPM).

## What ships

**Months and weekdays** are the standard Malaysian forms: `januari` through
`disember`, with `mac`, `jun`, `julai` and `ogos` where English has March,
June, July and August; `isnin` through `ahad` for the days.

**The weekday classifier.** Malay names a weekday with `hari` in front of it,
and *Kamus Dewan* spells the classifier out in its own definitions — Isnin is
"hari kedua dlm seminggu, selepas hari Ahad". So each weekday ships twice, bare
and with the classifier. That is what stops `setiap hari Isnin` from being read
as `setiap hari`, every day, with the weekday quietly discarded. Bare `setiap
hari` still means daily, because both readings are real. Sunday takes a third
surface, `hari minggu`.

**The date line** is day-first, `15 Januari 2020`, with no linking preposition.

**Relative offsets** are postposed. The past is `lepas`, `lalu` or `yang
lalu`; the future is `lagi` or `dalam`. `3 hari lepas` is three days ago and `2
minggu lagi` is two weeks from now.

**The ordinal prefix.** `ke-` makes a numeral ordinal, hyphenated before a
digit and joined before a spelled numeral. The tokenizer splits the hyphenated
form, so `abad ke-20` reads as the twentieth century.

**Century and decade.** `abad` and `kurun` both gloss to century, and `dekad`
and `dasawarsa` both to a ten-year period; all four come from *Kamus Dewan*.
Because Malay nouns do not inflect, no plural surface is needed.

**The clock.** `pukul` and `jam` introduce a time. *Kamus Dewan* gives `pukul`
a dedicated clock sense — "bahagian drpd sesatu hari spt yg ditunjukkan oleh
jam" — and its own example is `kami sampai di rumah pukul lima petang`, five in
the afternoon. Noon is `tengah hari` and midnight `tengah malam`.

**The night band.** `malam` is not a uniform twelve-hour shift but a band that
crosses midnight. All twelve hours were checked: `pukul satu malam` is 01:00,
`pukul enam malam` is 18:00, `pukul sebelas malam` is 23:00, `pukul dua belas
malam` is 00:00. Hours one through five stay in the small hours, six through
eleven move to the evening. The evening boundary at 19:00 is CLDR's night band
for Malay; the small-hours use of `malam` is the colloquial reading and is
sourced to the Wiktionary entry for `malam`, whose Malay section was checked.

**Dayparts.** `pagi`, `petang` and `malam` also carry band spans of their own,
with the boundaries transcribed from the CLDR 47 day-period rules for `ms` and
the surfaces from the Malay sections of the Wiktionary entries for each word.

**Range and boundary markers.** `sebelum` opens a bare-before range, `dari` and
`daripada` open a bounded one, `antara ... dan ...` frames a closed range,
`sejak` is since, `sehingga`, `hingga` and `sampai` are until, `selama` is a
duration, `setiap` and `tiap` are every. Each is sourced to its *Kamus Dewan*
entry. `selepas` is listed for "after" but is refused, in line with the rule
that a bare "after" has no open-ended-future span to return.

**Habitual recurrence** is `setiap hari isnin`. Answered as a recurrence,
this is the repeating Monday; asked for a span, it comes back as the next
Monday with `setiap` left in the remainder.

**Seasons and the weekend.** The four seasons ship in both the Malaysian and
the Indonesian-flavoured wordings — `musim luruh` beside `musim gugur`, `musim
bunga` beside `musim semi`, `musim sejuk` beside `musim dingin`. The weekend is
`hujung minggu`.

## The half hour — an open question

The locale, and a test that pins it, assert that a bare `setengah` before an
hour names the half *toward* that hour: `setengah tiga` is 02:30, the German
pattern. That reading resolves today, and it does so uniformly. All twelve
hours were checked and every one behaves the same way, `setengah H` giving
(H−1):30.

What the evidence actually supports is a different construction. Attested Malay
puts `setengah` **after** the hour, and reads it additively.

- Malay Wikipedia's article on the Seneca Falls Convention writes that the
  evening session opened `pada pukul tujuh setengah`. The English article it
  translates says "opening it at half-past seven", from the same cited National
  Park Service report. That fixes `pukul tujuh setengah` at 19:30 — hour first,
  half added.
- A Malay time-telling guide from Preply gives `jam tiga setengah` as 3:30, and
  a Malay-language lesson blog gives `pukul lima setengah` as half past five
  and `pukul tiga setengah` as 3:30. Both put the hour first and add the half.
- One further guide, talkpal.ai, gives the same postposed shape the opposite
  value, `pukul tiga setengah` as 2:30. It stands alone against the other
  three, and the site carries no editorial provenance.
- One more Malay Wikipedia sentence, in the article on Calvin Coolidge, has
  `pukul tiga setengah pagi` for the hour at which he learned he had become
  president. The English article gives the oath as 2:47 a.m. That is close to
  02:30 and close to nothing else, but it is a loose translation of a time
  neither reading matches exactly, so it settles nothing.

The preposed construction the locale implements was not found at all. A regular
expression search over Malay Wikipedia for `setengah` followed by an hour word
returns four articles, and every one is a word-boundary accident — `setengah
lapangan` (half the field), `sesetengah empat`, `setengah-setengah dua`. So
there is no corpus attestation in Malay for `setengah tiga` as a clock time.

The dictionary does not decide it either. *Kamus Dewan* defines `setengah` as
`separuh, seperdua` — half — with no clock sense and no example naming an hour.
Its entry for `pukul` has a clock sense but no half-hour example. Neither
`setengah tiga` nor `lapan setengah` is in the dictionary. The Malay section of
the Wiktionary entry for `setengah` gives "a half" and nothing more.

The preposed pattern *is* the Indonesian one, where `setengah tiga` for 02:30
is ordinary, and Indonesian is where a Malay locale would most easily acquire
it by analogy. That is a hypothesis about how the reading got here, not
evidence about Malay.

So today the locale reads a construction that no consulted source attests, and
strands the one that they do. `pukul lapan setengah` returns 08:00 with
`setengah` left in the remainder, and the same happens for every hour: the half
is dropped and a whole hour is returned in its place. If the additive reading
is right, that is a thirty-minute error on every phrase of that shape, with the
word that would have corrected it discarded.

A native speaker settles this by answering two separate questions. Does
`setengah tiga`, hour last, mean anything in Malay, and if so what time? And
does `pukul lapan setengah`, hour first, mean 08:30 or 07:30? Nothing here
should be changed until both are answered, because the sources that speak to
the second question do not agree with each other.

One related setting hangs off the same answer. The locale declares the
toward-the-hour half but not the twelve-hour reckoning that usually accompanies
it, so `setengah satu` resolves to 00:30 rather than 12:30. Whether that is
right depends entirely on whether the toward-hour reading is right at all.

## Weaker provenance

**The quarter hour.** `suku` ships as the business-quarter word only. Its clock
direction is unconfirmed and no clock quarter is implemented, which the locale
file states plainly. One guide offers `pukul dua kuartar` and `pukul tiga
setengah kuartar` for quarter past and quarter to; neither `kuartar` nor that
use of `setengah` appears in *Kamus Dewan*, and the forms are not shipped.

**`kelmarin dulu`** for the day before yesterday is shipped without a
dictionary locator having been checked for it.

## What refuses

**A bare duration.** `setengah jam lagi` — half an hour from now — returns
nothing, although `dua jam lagi` reads. The count-one half does not reach the
offset slot a numeral reaches.

**A decimal clock.** `pukul 2.30` returns nothing.

**"After".** `selepas` is listed but refused, because an open-ended future has
no end to bound a span with.

## Known defects

Beyond the half hour above, each of these is reproducible with
`extract_timespan(text, "ms", anchor=datetime(2017, 6, 27, 13, 4))`.

`pukul dua suku` returns the second quarter of 2017 with `pukul` stranded. A
phrase that names a time of day comes back as a three-month business quarter,
and the word that made it a clock time is discarded. `suku tiga` returns the
third quarter of 2017, which is defensible on its own, but it is the same
collision seen from the other side: `suku` is both the quarter of an hour and
the quarter of a year, and the year always wins.

## Open questions for a native speaker

1. Is `setengah tiga`, with the hour after `setengah`, said in Malay at all,
   and if it is, does it mean 02:30 or 03:30?
2. Does `pukul lapan setengah` mean 08:30 or 07:30?
3. If the half is toward the hour, does the hour before one read as twelve, so
   that the half before one is 12:30 rather than 00:30?
4. What is the ordinary way to say a quarter past and a quarter to, and does
   `suku` appear in it?
5. Is `kelmarin dulu` the usual phrase for the day before yesterday?
