# Indonesian (`id`)

Indonesian is isolating: nouns do not inflect for number, verbs do not
conjugate, and direction is carried entirely by trailing particles.
`lalu` closes a phrase in the past, `lagi` closes one in the future, and both
sit after the counted duration — `3 hari lalu`, `3 hari lagi` — never before
it. The same postposed pattern runs through the whole locale: `depan` (next)
and `lalu` (last) follow the noun they modify (`kuartal depan`, `minggu
lalu`), and the ordinal in a scoped phrase follows its noun too (`abad
ketiga`, `kuartal ketiga`), the reverse of the Romance "third quarter" order.

The clock names the hour **not yet reached**. `setengah tiga` is 02:30, the
half *before* three, not the half past two. This is the German-style
toward-hour reading. *Kamus Besar Bahasa Indonesia* (KBBI) glosses `setengah
jam` as "half an hour," which fixes the fraction but not its clock direction;
the toward-hour reading is corroborated across Indonesian usage sources, but a
KBBI/DBP-canonical clock-reading passage was not obtained, and the locale's
own `clock_fraction_30.voc` records that honestly rather than overstating the
citation.

## What ships

**Day parts** come from the Unicode CLDR 47 day-period rule set for `id`,
transcribed in `chronologia/dayparts.py`: `pagi` (morning) `[00:00, 10:00)`,
`siang` (midday/early afternoon) `[10:00, 15:00)`, `sore` (late
afternoon/evening) `[15:00, 18:00)` and `malam` (night) `[18:00, 00:00)`. Each
surface is the single noun Wiktionary lists for the band — `pagi`, `siang`,
`sore`, `malam` — and each is pinned by a worked test: `pagi` on its own spans
`[00:00, 10:00)`, `kemarin sore` spans the previous day's `[15:00, 18:00)`,
`besok siang` the next day's `[10:00, 15:00)`.

**A clock hour spoken with `malam` is a midnight-crossing band, not a flat
PM shift.** `pukul satu malam` ("one at night") is 01:00, not 13:00; `pukul
sebelas malam` ("eleven at night") is 23:00; twelve is midnight. Hours one
through five stay in the morning half, hours six through eleven go to the
evening half, because `malam` in ordinary speech covers both the tail of one
day and the small hours of the next. The resolver band-splits on this rule,
and the two clock-word markers (`pukul`, `jam`) both carry it. Source:
Wiktionary, `malam`, plus the CLDR night band `[18:00, 00:00)` that fixes
where the evening half of the word begins.

**Named days** are `kemarin lusa` / `kemarin dulu` / `kemarin dahulu`
(day before yesterday), `kemarin` (yesterday), `hari ini` (today), `besok`
(tomorrow) and `lusa` (day after tomorrow) — five distinct words, not a
composed offset, matching the semantic-parity test that resolves each
against its English equivalent.

**Weekdays ship with an optional classifier.** KBBI defines `Senin` as "hari
ke-2 dalam jangka waktu satu minggu" (day 2 of the week) and glosses every
other weekday the same way, with `hari` (day) as part of the entry, so
`hari Senin` ships as a name in its own right beside bare `Senin`. Carrying
the classifier form is what keeps `setiap hari Senin` (every Monday) from
losing the weekday when `setiap hari` (every day) is read first — both
readings are real Indonesian, and the locale needs both surfaces to tell
them apart.

**The date line** is day, month name, optional year — `17 Agustus 1945` — with
month names from CLDR 47's `id` `ca-gregorian.json`. `ordinal_dot` is off:
Indonesian does not write the dotted ordinal day.

**Relative offsets** postpose their direction marker: `NUM UNIT lalu` for the
past, `NUM UNIT lagi` for the future — `3 hari lalu`, `5 tahun lagi`. `depan`
(next) and `lalu` (last, reused from the same past marker) attach after a
scoped noun: `kuartal depan`, `minggu lalu`.

**Eras** are `m` for *masehi* (CE/AD) and `sm` for *sebelum masehi* (BCE/BC),
both trailing the year: `1492 m`, `44 sm`.

**Quarters** postpose the ordinal after `kuartal`: `kuartal ketiga` reads as
Q3 of the anchor year, folding the single-word spelled ordinal through
`ovos-number-parser`'s `numbers_id`. The year form uses the digit instead —
`kuartal 3 2026` — and `Q3 2026` also reads. `kuartal ini` / `depan` / `lalu`
resolve the current, next and previous quarter relative to the anchor.

**Century and decade** follow the same postposed-ordinal shape as the
quarter: `abad ketiga` is the third century, and the digit-plus-hyphen form
`abad ke-20` also resolves, the tokenizer splitting the `ke-` prefix from the
digit. KBBI defines `abad` as a hundred-year span and `dekade` as `masa 10
tahun` (a ten-year span), equating it with the Sanskrit-derived synonym
`dasawarsa` (*dasa* "ten" + *warsa* "year"); both decade words ship. A
relative-offset century or decade — `N abad lalu` — steps the anchor back by
whole calendar months (1200 per century, 120 per decade) rather than by a
fixed year count, so month-length irregularities do not shift the answer.

**ISO weeks** use `minggu N` or `pekan N`, both meaning "week"; `minggu` is
also the ordinary word for the calendar unit "week," while the weekday
Sunday is registered separately as `ahad` precisely so that `minggu` never
has to disambiguate between "week" and "Sunday" in this locale's grammar.

**Ranges** are `antara A dan B` (between, KBBI: "menyatakan hal berada di
tengah dua batas") for a closed interval, and `dari A sampai/hingga B` (from,
KBBI: "menyatakan asal atau titik permulaan") for the same shape with an
explicit lead-in. `sebelum X` (before, KBBI: "lebih dahulu (waktunya)
daripada") opens the range `[now, X's end)` when X is in the future, mirroring
how Spanish `antes de` and English `before` are read elsewhere in this
codebase.

**Fuzzy month parts** are `awal` (early), `pertengahan` (mid) and `akhir`
(late).

**Durations** fold ordinary counted phrases — `2 jam`, `3 minggu` — plus the
two fraction words `setengah jam` (half an hour, 30 minutes) and `seperempat
jam` (a quarter hour, 15 minutes), and chain: `2 hari 4 jam`.

## Weaker provenance

**The seasons** — `musim semi`, `musim panas`, `musim gugur`, `musim dingin`
— ship with no recorded source; they are calques of the four-season Western
vocabulary rather than terms with independent standing in an equatorial
climate, and no dictionary or corpus citation backs any of the four surfaces.

**The clock-direction citation** for `setengah` is honestly incomplete: KBBI
fixes the fraction but not the toward-hour direction, which rests on
cross-checked usage rather than a single canonical grammar passage. The
quarter-hour word (`suku`/`seperempat` on the clock, as opposed to as a
duration) is deliberately left unshipped as a clock fraction because its
direction was not confirmed.

**The weekday and business-day markers** (`kerja` for a business day) and the
weekend noun (`akhir pekan`, `akhir minggu`) carry no cited source beyond
their appearance in the test corpus.

## What refuses

**"After" as a bare open-ended future marker.** `sesudah X` / `setelah X`
never resolves to an open range, because `DateSpan` has no open-ended-future
representation to hand it — the same limit that refuses "after" in every
other locale in this codebase, not an Indonesian-specific gap.

**A duration with no direction marker attached at the wrong construction.**
Plain `2 jam` folds as a duration through `extract_duration`, but the same
phrase inside a relative-offset construction requires the trailing `lalu` or
`lagi`; a bare quantity is a duration, not a point in time.

## Open questions for a native speaker

1. What is the correct KBBI or DBP-cited passage, if one exists, for the
   toward-hour reading of `setengah` on a clock — as opposed to its
   half-an-hour duration sense, which KBBI already covers?
2. Does `suku` or `seperempat` on the clock count minutes toward the coming
   hour or from the hour just past, and is that direction the same as
   `setengah`'s?
3. Are `musim semi/panas/gugur/dingin` in ordinary use for anything beyond
   describing other countries' seasons, or does everyday Indonesian mark the
   wet and dry seasons (`musim hujan`, `musim kemarau`) instead — and if so,
   should those ship as the locale's actual season vocabulary?
4. Is `pekan` fully interchangeable with `minggu` for "week" in a numbered
   ISO-week phrase, or is one of the two markedly more formal?
