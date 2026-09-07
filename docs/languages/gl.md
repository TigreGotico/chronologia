# Galician (`gl`)

Galician sits beside Portuguese and looks like it almost everywhere, which is
the standing hazard for this locale: a surface that is right in Portuguese is
not thereby right in Galician, and nothing here is admitted on the strength of
the Portuguese page. Every marker that carries a source carries a Galician one,
the Dicionario da Real Academia Galega, and the day-part bands come from the
Galician row of the Unicode day-period table rather than from the Portuguese
row next to it. The two rows are not the same row, which is the point.

The clearest place that shows is the clock. Portuguese runs one uninterrupted
afternoon from midday to seven in the evening. Galician has a separate hour of
noon standing between morning and afternoon, `mediodía` from 12:00 to 13:00,
and then an afternoon running eight hours to nine at night, with `noite`
taking only the last three hours of the day. Among the fifty locales for which
`chronologia/dayparts.py` transcribes bands, three carry an hour-wide noon
band of exactly 12:00 to 13:00 — Catalan, German and Galician — and three
close the day with a final band opening at 21:00 — Catalan, Basque and
Galician. Of every band in that
table that opens between eleven in the morning and three in the afternoon,
none is longer than eight hours, and only two reach it: Galician's `tarde` and
the Spanish `tarde`, which is equally eight hours but sits an hour earlier at
12:00 to 20:00.

The second early fact is that `da noite` is a band, not a shift. `dez da
noite` is 22:00 but `unha da noite` is 01:00: the small hours one to five stay
AM, the evening hours six to eleven are PM, and twelve is midnight. The AM
ceiling follows the `madrugada` band, and DRAG's entry for `noite` supports
the whole stretch, glossing it as the period from sunset to sunrise.

## What ships

**Weekdays and months** ship wide and abbreviated. Neither carries a recorded
source in the vocabulary.

**The date line** is `o 3 de outubro de 1990`, little-endian, with `de`
between the parts and an optional leading article that is consumed with the
date rather than left behind. The slashed numeric date reads; the dotted one
does not.

**The locative `en`** is a genuine during-word here, so `en xaneiro` binds the
month and leaves nothing over. The part-of-day frame `pola`/`polo` lives in
its own day-frame vocabulary, separate from the during slot, so it does not
compete with `en` for it and the marker-prefixed month order comes through
clean.

**Relative offsets** are `hai` and `atrás` backward, `en` and `dentro`
forward. Relative determiners follow their noun — `a semana pasada`, `o luns
que vén` — so the locale sets `marker_position: post`.

**Ranges** are `de … a …`, `do … ao …`, `desde …`, `a partir de …`, `ata …`
and `deica …`, with `entre … e …` as the other frame. Each preposition is
cited to its own DRAG entry, and the `de`+`o` and `a`+`o` contractions to the
RAG/ILG *Normas ortográficas e morfolóxicas do idioma galego*. The from-lead
carries structural weight for the same reason it does in Portuguese: `a` is a
hyper-common preposition, so a bare `A a B` is trusted as a range only when a
from-lead is present.

**The clock** has both toward-the-hour shapes and keeps them apart. `catro
menos cuarto` subtracts from the hour already named. Forward is `e` — `cinco e
media`, `cinco e cuarto`. The indefinite `un`/`unha` sits in the article
vocabulary so the `cuarto` fraction can read. `mediodía` and `medianoite` are
points.

**Day parts** take their boundaries from the Unicode CLDR 47 day-period chart,
locale `gl`, transcribed in `chronologia/dayparts.py`: `madrugada`
`[00:00, 06:00)`, `mañá` `[06:00, 12:00)`, `mediodía` `[12:00, 13:00)`,
`tarde` `[13:00, 21:00)`, `noite` `[21:00, 24:00)`. The frame is `pola`,
`polo` and their plurals, the contractions of `por` with the definite article.

**Fuzzy month parts, quarters, ISO weeks, decades and eras** all resolve:
`mediados de xullo`, `o primeiro trimestre de 2020`, `semana 12`, `os anos 80`
and `44 ac`. `a primeira metade de 2020` reads as the first half-year, with
`metade` cited to DRAG. The singular `ano` names one year and the plural
`anos` frames a decade, and they are kept in separate vocabularies so that
`o ano 1980` cannot reach the decade slot.

**The Roman calendar anchors** ship in their Galician vernacular forms
`calendas`, `nonas` and `idos`, cited to the Galician Wikipedia article
*Calendario romano*. All three appear in that article with their definitions,
which was checked.

## Weaker provenance

**The `mañá` homograph rests on one entry doing two jobs.** DRAG gives `mañá`
the day-part sense and the adverbial "day after today" sense in the same
entry, senses 1 and 3. The locale takes both from that single source and
separates them by frame: bare `mañá` is tomorrow, framed `pola mañá` or `esta
mañá` or `da mañá` is the morning band. Nothing independent corroborates that
the frame is what does the separating.

**`deica` is shipped as a general range terminus, and DRAG says it is not
one.** The DRAG entry for `deica` states that the idea of *here* or *now* is
always present in it, and gives the explicit contrast that one says `Camiñaron
desde Pedrafita ata Santiago` and not `deica Santiago`. The locale
nevertheless accepts `de xuño deica agosto` as a range because `deica` sits in
the same to-marker vocabulary as `ata`. The reading it produces is the natural
one, but it is wider than the source licenses.

**`ata` is a homograph the locale does not guard.** DRAG has two `ata`
headwords: the preposition, and a feminine noun for the act of tying sheaves.
Only the preposition ships and nothing distinguishes the two.

**The Roman anchors rest on a Wikipedia article,** weaker than the DRAG
citations the rest of the locale is built on.

**Weekday and month names, and the seasons, carry no recorded source.** The
locale sets `hemisphere` to null, so a season is never resolved to a southern
reading.

## Unchecked and broken citations

The four day-part vocabularies and the night meridiem all cite DRAG through
the URL `https://academia.gal/dicionario/-/termo/mana`. That URL is a soft
404: it answers HTTP 200 with the dictionary's search shell and no entry. The
Galician headword is `mañá`, and the entry is reachable only through the
percent-encoded form of the accented word. The glosses quoted in those
comments were checked against that entry and are accurate; only the link is
wrong. The same link appears on the `tarde`, `noite` and `madrugada` files,
where it would point at the morning entry even if it resolved.

The during-word vocabulary cites `https://academia.gal/dicionario/en`, which
returns HTTP 404. The headword `en` does exist in DRAG under the term path
the other entries use.

Every other cited source was fetched and confirmed to contain what the
vocabulary says it contains: the DRAG entries for `entre`, `de`, `desde`, `a`,
`ata`, `deica`, `metade`, `ano` and `noite`; the Galician Wikipedia
*Calendario romano*; and the CLDR 47 day-period chart, whose `gl` row gives
exactly the five boundaries transcribed.

## What refuses

**Every bare day-part word except `mañá`.** `tarde`, `noite` and `madrugada`
return nothing on their own, and `máis tarde` returns nothing. One grammar
order binds every day-part surface the locale ships, so a bare `tarde` cannot
be refused while a bare `mañá` is admitted; and `tarde` is equally the adverb
*late*, so admitting it would answer a confident afternoon band for `cheguei
tarde`, a sentence that names no time. `mañá` is available bare because bare
`mañá` is tomorrow, not the morning.

**Seconds.** `hai 30 segundos` returns nothing. No second unit ships.

**The dotted date.** `15.06.2020` returns nothing and does not fall back to
reading 2020 as a bare year.

**A bare duration.** `quince días` returns nothing. A fortnight unit ships,
but a quantity with no direction marker is still only a quantity.

**Roman-numeral and spelled centuries.** `o século XX` and `o século vinte`
both return nothing.

## Known defects

These are wrong answers, not refusals, and each is reproduced against the
anchor 2017-06-27 13:04.

`extract_timespan("a década de 1980", "gl", anchor)` returns 1980-01-01 to
1981-01-01 with `a década de` left in the remainder. A decade was asked for
and a single year was given. The plural frame `os anos 80` is the one that
works; the `década de` frame reaches the year rule instead.

`extract_timespan("até o luns", "gl", anchor)` binds Monday but strands the
article `o`. The until-vocabulary carries `ata o` and `ata a` as two-word
surfaces precisely so the article is claimed with its marker, and the variant
spelling `até` has no such pair, so the scanner finds the bare `até` first and
leaves the article behind. `ata o luns` is clean.

`extract_timespan("a partir do 5 de xuño", "gl", anchor)` binds the date but
leaves the whole three-word marker `a partir do` in the remainder, so an
open-ended from-range reads as a single day.

`extract_timespan("o mediodía", "gl", anchor)` resolves the noon point and
strands the article, and `todos os luns`, `cada martes` and `a próxima fin de
semana` each resolve their target while leaving the recurrence or determiner
word visible.

## Open questions for a native speaker

1. Does `deica` genuinely accept a from-lead, as `de xuño deica agosto`
   assumes, or does DRAG's observation rule that reading out?
2. Where does `da noite` stop being AM? The ceiling sits at five, following
   the `madrugada` band, but DRAG's `mañá` entry gives `ás tres da mañá` for
   the same hour.
3. Does the hour of `mediodía` behave as a band in speech, or only as the
   twelve-o'clock point?
4. Is `a década de 1980` an ordinary Galician way to name a decade, and should
   it therefore resolve to ten years?
5. Are `calendas`, `nonas` and `idos` the forms Galician historical writing
   uses?
