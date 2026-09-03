# West Frisian (`fy`)

The half hour names the coming hour. `healwei fiven` is 04:30, not 05:30, and
the word itself says so: `healwei` is "halfway", the point halfway toward the
hour that follows. `bare_half_to` is set for that. The quarter word `kertier`
takes its direction from the preposition beside it instead, `oer` counting up
from the named hour and `foar` counting down toward it, so `kertier oer twa` is
02:15 and `kertier foar trije` is 02:45.

The second governing fact is a collision the vocabulary has to work around.
`moarn` is tomorrow and `moarns` is the morning; the two are one word apart, and
only the adverbial `moarns` names the day part. The bare noun is left out of the
morning band on purpose, and `moarn` resolves to the whole of the following day.

## What ships

**Weekdays and months** ship wide and abbreviated, with no recorded source.

**The named days** are `hjoed`, `juster`, `moarn`, `eargister`/`eergister` and
`oaremoarn`/`oarmoarn`, none of them carrying a citation. They cannot come from
CLDR: the CLDR 47 `dateFields.json` for `fy` has Dutch in the day rows —
`gisteren`, `vandaag`, `morgen`, `eergisteren`, `Oermorgen` — so the day names
shipped here are the Frisian ones CLDR does not have. `hjoed`, `juster` and
`moarn` each have a West Frisian entry on the English Wiktionary; `eargister`
and `oaremoarn` have no entry there and rest on nothing that was fetched.

**The date line** is little-endian with a bare cardinal day: `15 juny 2020`
resolves, as does `15-06-2020` and the ISO `2020-06-15`. `ordinal_dot` is off
and the ordinal instead takes a written suffix, so `de 2e juny` reads.

**Relative offsets** are `oer` forward and `lyn` backward — `oer trije dagen`,
`trije dagen lyn` — with the marker allowed on either side of the count and an
optional indefinite `in` between.

**The clock** reads `om` as the "at" marker and `oere` as the o'clock word, with
`middernacht` and `middei` as the landmark points. `middei` is midday, a point;
the afternoon band is `middeis`, and the two are kept apart deliberately.

**The spoken hour takes an inflected form of its own before a fraction.**
`ienen`, `twaen`, `trijen`, `fjouweren`, `fiven`, `seizen`, `sânen`, `achten`,
`njoggenen`, `tsienen`, `alven` and `tolven` are supplied as a fixed word-to-value
map in `chronologia/extract/numfold_germanic.py`, because the number parser this
locale folds through reads only the uninflected cardinals. The map has no cited
source. The uninflected form still reads, so `healwei ien` and `healwei ienen`
both land on 00:30.

**Day parts** are `nachts` `[00:00, 06:00)`, `moarns` `[06:00, 12:00)`,
`middeis` `[12:00, 18:00)` and `jûns` `[18:00, 24:00)`, transcribed in
`chronologia/dayparts.py`. The boundaries are the Dutch ones. CLDR 47 ships no
West Frisian day-period row at all, so the locale borrows the `nl` row on the
grounds that West Frisian is co-official in Fryslân alongside Dutch. The
surfaces are cited to the Frisian dictionary material at `gtb.ivdnt.org`.

**Ranges** are `fan … oant …` and `tusken … en …`, with `sûnt` opening one that
runs to the anchor and `oant` closing one that starts there.

**Quarters, ISO weeks, eras and fuzzy month parts.**
`earste kwartaal fan 2020`, `wike 12`, `44 f.kr.`, `yn 1990`, `begjin juny`,
`midden juny` and `ein juny` all resolve, along with the full deep-time period
vocabulary and a before-present marker.

## Weaker provenance

Only three surfaces in this locale carry a source that can be fetched and read:
`yn` and `foarich` cite West Frisian Wiktionary entries, and both entries do
carry a West Frisian section; `foarich jier` and `folgjend jier` cite the CLDR
47 `fy` year rows, and those rows do read `foarich jier` and `folgjend jier`.
Everything else ships uncited.

The day-part citation is the weakest link that still works. `gtb.ivdnt.org` is
reachable and does host Frisian dictionaries, the *Wurdboek fan de Fryske taal*
among them, but the site is a JavaScript application whose search results cannot
be fetched, so no individual lemma behind that citation was confirmed. The
citation names the source as *Frysk Wurdboek*, which is a different Fryske
Akademy work from the *Wurdboek fan de Fryske taal* the portal actually carries.
Treat the day-part surfaces as attested by an institution, not by a located
entry. `moarns` is the one that can be checked elsewhere: its English Wiktionary
entry glosses it "in the morning" and points at the *Wurdboek fan de Fryske
taal* for the same word.

`healwei` — the word the whole clock turns on — has no citation and no
Wiktionary entry in any language. Frisian Wikipedia carries running-text
attestations of the construction rather than a dictionary one: an article on a
New Year's custom has `Om healwei ienen Aldjiersnacht is de útbarsting fan de
yn de buorren`, which places `healwei ienen` in the small hours and so agrees
with the 00:30 the locale returns; a band name, `Trije Minuten Foar Healwei
Fiven`, attests `foar` combining with `healwei`. Frisian Wikipedia also has an
article titled *Healwei*, and that one is a hamlet on Terschelling and is not
evidence about the clock.

## The half hour toward one, and the flag that would move it

`healwei ienen` resolves to 00:30. Frisian counts the half toward the coming
hour, so the phrase names the half hour before one o'clock, and 00:30 and 12:30
are both that half hour. The locale returns the 24-hour one, and there is no way
to reach the other: a following day-part word does not disambiguate it, because
this locale binds no meridiem at all (see the refusals below). A speaker who
means half past twelve in the middle of the day gets a time twelve hours away.

A convention flag named `toward_hour_12h` exists and would change exactly this.
Eight locales declare `bare_half_to` without it — `da`, `de`, `fy`, `ms`, `nb`,
`nl`, `nn` and `sv` — and all eight return 00:30 for their own version of the
phrase. Sixteen locales declare both, and Icelandic is the only Germanic one
among them; `hálf eitt` returns 12:30 there.

Turning the flag on for West Frisian moves more than the bare half, because the
resolver reads it at three sites and all three are the branch that has just
decremented the hour. Setting it and re-probing every hour from one to twelve
against the bare half, the quarter each way and a five-minute count each way —
five phrase shapes across twelve hours, probed here alongside Nynorsk for a
combined 120 phrases — changes three of the Frisian ones, and all three name
one o'clock: `healwei ienen` becomes 12:30, `kertier foar ienen` becomes
12:45, and `fiif foar ienen` becomes 12:55. Nothing else moves. `kertier foar trije` stays
02:45, every past-side reading stays where it is, and the landmark forms
`kertier foar middernacht` and `healwei middei` are untouched.

So the trade is narrower than a whole-clock shift, but it is still a trade and
not a fix. The flag does not separate the bare half from the explicit-direction
count; it only asks whether the hour that rolls back from one to zero should be
spoken as twelve. Off, `healwei ienen` is 00:30 and `kertier foar ienen` is
00:45, and the daytime readings are unreachable. On, both move to the afternoon
and the small-hours readings are unreachable instead. Either way one of the two
senses is lost, and which loss is worse is a question about how Frisian speakers
actually use the phrase, not about the code. A test pins the current side:
`test/nl_corpus_fy/test_fy_clock.py` asserts `healwei ienen` is 00:30 along with
the other eleven hours.

## What refuses

**Any day-part word after a clock time.** `acht oere jûns` returns 08:00 and
leaves `jûns` in the remainder; `healwei acht jûns` returns 07:30 and leaves
`jûns`. The band words resolve perfectly well on their own — `jûns` alone is
18:00 to midnight — but nothing binds one to a preceding hour as a meridiem, so
every evening time in this locale comes back as its morning twin with the
evening word stranded beside it. This is the locale's largest gap and the reason
the half-hour question above has no workaround.

**The dotted civil date.** `15.06.2020` returns nothing. `dotted_date` is off
for this locale and the hyphenated and ISO forms are what read.

**A bare duration.** `trije wiken` and `fjirtjin dagen` return nothing. A
quantity with no direction marker is still only a quantity.

**A recurrence.** `eltse moandei` returns the next single Monday and leaves
`eltse` in the remainder; `eltse dei` and `deistich` return nothing. The "every"
and frequency words ship but no construction reads them.

**`no` as a present-time word.** It is listed in `marker_present.voc` and
resolves to nothing on its own.

**Fused today-plus-band words.** `fanjûn` and `fannacht` return nothing. Dutch
ships its equivalents as their own surfaces; Frisian does not.

**A four-digit clock.** `14.30` and `om 14.30 oere` return nothing.

## Known defects

Each of these returns a wrong or partial answer rather than nothing, which is
worse than a refusal.

`acht oere jûns` → 08:00 with remainder `jûns`. The meridiem gap, stated above.

`om healwei ienen` → 00:30 with remainder `om`. The "at" marker is read before a
bare or spelled hour but not before a fraction, so the one construction Frisian
Wikipedia attests verbatim does not fully parse.

`fan moandei` → the whole of the following Monday with remainder `fan`. An open
range that starts at a weekday is not read, and the marker is dropped silently.

`de 15e fan juny` → 15 June with remainder `de`. The article is not consumed
before an ordinal day.

`oer healwei twa` → 01:30 with remainder `oer`. The forward-offset marker is
stranded in front of a clock time instead of refusing.

## Open questions for a native speaker

1. Said in the middle of the afternoon, does `healwei ienen` mean 00:30 or
   12:30 — and is one of the two clearly the ordinary reading?
2. What is the connector that binds a day part to a spoken hour, and which
   day-part forms take it?
3. Are `eargister` and `oaremoarn` the ordinary words for the day before
   yesterday and the day after tomorrow, and are there other spellings?
4. Is the inflected hour set (`ienen`, `twaen`, …) complete and correct, and
   does it appear anywhere but before a fraction?
5. Are there fused today-plus-band words on the Dutch model?
6. Does the Dutch day-period table match Frisian use, or do the bands sit
   differently?
