# Basque (`eu`)

Basque is a language isolate, and the consequence for a date parser is
structural rather than lexical: there are no prepositions to match. Where most
locales in this library recognise "from", "until", "during" and "of" as
separate words standing before their object, Basque marks all of them as case
suffixes glued onto the end of the noun. `ekainaren 5ean` is "of-June 5th-in",
two case endings and no function words at all. A tokenizer that splits on
whitespace therefore never sees the marker; it sees one long word.

The locale answers this in two places. The vocabulary files list the inflected
surfaces themselves — every month ships six forms, every weekday five — and
`chronologia/extract/numfold_agglutinative.py` re-fuses a digit that the
tokenizer has sheared from its case ending, so `5ean` comes back as the day
number 5 rather than a number followed by a stranded fragment. The marker files
that do exist (`marker_from.voc`, `marker_to.voc`, `marker_of.voc`) hold
suffixes written with a leading hyphen, not words.

## What ships

**Months and weekdays** ship as sets of inflected surfaces rather than lemmas.
January is `urtarrila`, `urtarrilak`, `urtarrilaren`, `urtarrilean`,
`urtarrilan` and `urtarrilko` — absolutive, the `-k` form a date line uses, the
genitive that governs a day number, the inessive, and the relational `-ko`.
Weekdays follow the same pattern with five forms each. Listing the paradigm is
what lets `astelehenean` ("on Monday") and `martxoaren hirugarren astelehena`
("the third Monday of March") both bind without a morphological analyser.

**The date line** is `MONTH-genitive DAY-inessive`, `ekainaren 5ean`, and the
year when present leads with its own relational suffix: `2027ko ekaina`,
`1999ko urtarrilaren 1ean`. The generic `calendar_date` construction is
disabled in `lang.json` in favour of the base grammar's date orders, because
the Basque order is fixed by the case marking rather than by convention.

**Relative offsets** are two-sided. Backward is the preposed `duela` or
`orain dela` — `duela hiru egun`, three days ago. Forward is the postposed
`barru`, `buru` or `barne` — `hiru egun barru`, in three days. The
`relative_offset` orders in `lang.json` accordingly list both `MARKER NUM UNIT`
and `NUM UNIT MARKER`.

**The clock** names the hour already reached and counts forward from it with
`eta` ("and"): `bostak eta erdi` is 05:30, `bostak eta laurden` is 05:15. The
plural hour numerals (`bostak`, `hirurak`, `hamabiak`) are the telling-time
forms, and the fold maps them to their values. The backward direction uses
`gutxi` ("less").

**The inessive telling-time hour** — `hiruretan`, "at three" — is one word with
no clock marker of any kind in it, so the fold splits it into a synthetic `at`
marker plus the digit, using `etan` from `marker_at.voc` as the marker surface.
Without that split the digit binds nothing at all. `hiruretan` and
`goizeko hiruretan` both resolve to 03:00.

**Day parts** come from the Unicode CLDR 47 Day Period Rules chart, which gives
`eu` six bands: `morning1` from 00:00, `morning2` (goiza) from 06:00,
`afternoon1` (eguerdia) from 12:00, `afternoon2` (arratsaldea) from 14:00,
`evening1` (iluntzea) from 19:00 and `night1` (gaua) from 21:00. The
implementation in `chronologia/dayparts.py` collapses the two morning bands
into one running 00:00–12:00 and the two afternoon bands into one running
12:00–19:00, keeping evening at 19:00–21:00 and night at 21:00–24:00. Basque
night therefore does not wrap past midnight; the morning band absorbs the small
hours. The shipped surfaces are the inessive forms a phrase actually uses —
`goizean`, `arratsaldean`, `iluntzean`, `gauean` — not the CLDR citation forms.

**Ordinals** use the `-garren` series (`bigarren`, `hirugarren`), supplied by
`pronounce_ordinal_eu`, plus `lehen` and `lehenengo` for one, which the
pronouncer does not emit.

## Weaker provenance

The vocabulary files carry no source comments except the four day-part files.
The months, weekdays, units, seasons and markers are not individually sourced
in the repository, and this page does not claim provenance for them beyond
what the files themselves carry.

`iluntzean` is the shipped evening surface, and its comment header cites the
Wiktionary entry for `iluntze`. That entry was fetched: it has a Basque
section, and it glosses `iluntze` as "dusk", but it carries no declension
table, so the inessive `iluntzean` specifically is not attested there. The
other three day-part surfaces are on firmer ground — the Wiktionary entries for
`goiz`, `arratsalde` and `gau` each carry a declension table that shows
`goizean`, `arratsaldean` and `gauean` explicitly.

The comment in `numfold_agglutinative.py` that documents the inessive-plural
hour fold cites `en.wiktionary.org/wiki/-etan#Basque`. That page was fetched
and has no Basque section at all; its only section is Old English. The
mechanism it describes is nonetheless the one the code implements and the one
the hour surfaces show, but the citation does not support it and is recorded
here as unverified. The same comment's second citation, Euskaltzaindia's
telling-time forms, names no locator; the institution's site was reached but
the specific page was not, so that citation is likewise unchecked.

## What refuses

**Bare `asteburuan`.** `special_weekend.voc` holds `asteburua` and `asteburu`
but not the inessive `asteburuan`, so "at the weekend" in its most ordinary
inflected form returns nothing while the bare noun resolves.

**The two-word hours.** One and two o'clock are `ordu bata` and `ordu bietan`,
two-word forms rather than the single inessive plural the other hours use, and
neither resolves.

**`laurden gutxi bostak`.** The quarter-to phrasing binds only in the order
`HOUR CLOCKDIR FRACTION` that `lang.json` declares — `bostak gutxi laurden`.
Whether that is the order a Basque speaker uses is an open question below, not
a settled one.

## Known defects

These are wrong answers rather than refusals, and a wrong answer with a
stranded remainder is worse than nothing. Each is stated with the probe that
produces it, anchored at 2017-06-27 13:04.

`extract_timespan("arratsaldeko bostak eta erdi", "eu")` returns 05:30 with
`arratsaldeko` left in the remainder. The afternoon meridiem does not compose
with the `HOUR eta FRACTION` clock order, so the phrase reads as half past five
in the morning. The same lead composes correctly with the inessive hour:
`arratsaldeko bostetan` returns 17:00.

`extract_timespan("2020ko lehen hiruhilekoa", "eu")` returns the first quarter
of **2017**, the anchor year, with `2020ko` in the remainder. The relational
year form does not bind the `YEAR?` slot of `quarter_ref`.

`extract_timespan("urtarrilaren erdialdean", "eu")` returns the whole of
January with `erdialdean` in the remainder, rather than mid-January.
`urtarrilaren hasieran` behaves the same way, returning all of January with
`hasieran` stranded. The period-part words are listed but the genitive month
form does not reach the `month_fuzzy` construction.

`extract_timespan("ekaina eta uztaila artean", "eu")` returns June alone with
`eta uztaila artean` in the remainder. The `artean` range is not read, and the
narrowed span it returns instead is silently wrong rather than empty.

## Open questions for a native speaker

1. Is `bostak gutxi laurden` or `laurden gutxi bostak` the ordinary order for
   "quarter to five", and should both be accepted?
2. Should `asteburuan` and the other inessive forms of the weekend, season and
   unit nouns be listed alongside the absolutive forms already shipped?
3. Are `ordu bata` and `ordu bietan` the living forms for one and two o'clock,
   and do they take the same `eta` continuation as the plural hours?
4. Which of the three forward-offset markers — `barru`, `buru`, `barne` — are
   interchangeable, and which are regional?
