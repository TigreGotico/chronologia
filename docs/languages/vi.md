# Vietnamese (`vi`)

Vietnamese has no inflection at all, which removes most of the difficulty other
locales spend their vocabulary files on and replaces it with a different one:
several of the most useful temporal words collide exactly with other words, and
the collisions are not resolvable from the string alone. Most of this locale's
refusals are those collisions.

`năm` is the noun "year" and, separately, the numeral five — one spelling, one
tone. Vietnamese itself avoids the clash inside compounds by switching to `lăm`,
which is the language's own admission that the bare word cannot be
disambiguated. The numeral fold therefore never reads a bare `năm` as five.

The clock runs in both directions, and which way depends on the word rather
than on the language. `rưỡi` counts forward from the hour already named, the
English "half past" direction: `ba giờ rưỡi chiều` is 3:30 PM. `kém` names the
hour being approached and subtracts from it: `ba giờ kém mười` is 02:50. Both
are in daily use and neither can be made the locale's default.

## What ships

**Weekdays are ordinal-numbered.** `thứ` means "rank", and the weekdays count
from Sunday — which is not counted but named, `chủ nhật`, "lord's day". Monday
is therefore "rank two". CLDR spells the same construction two ways, the wide
`Thứ Hai` and the abbreviated `Thứ 2`, and both are listed, because they are one
construction in two spellings rather than a name and an abbreviation of it.

**Dates** are introduced by the day noun `ngày` and the month noun `tháng`:
`ngày 5 tháng 3`. `năm` introduces a Gregorian year.

**Relative offsets** work from either side, again as a property of the word.
`trước` means both "before" and "ago" and trails the duration it counts back
over: `ba ngày trước`. `cách đây` is the dedicated "ago" adverb and precedes the
duration: `cách đây ba ngày`. Both orders are declared. `sau` is the mirror for
the future, and the same pair doubles as the last/next period markers postposed
to a unit noun — `tuần trước` is last week, `tuần sau` next week.

**Day parts** come from CLDR's `vi` calendar data. Three of them shift an hour
past midday — `chiều` (12:00–18:00), `tối` (18:00–21:00) and the noon point
`trưa` — and one does not: `đêm` runs from 21:00 round to 04:00 and crosses
midnight, so it is not a flat twelve-hour shift. `một giờ đêm` is 01:00, not
13:00.

**Ordinals** are made by prefixing `thứ` to a numeral. Because the same word
names a weekday when the numeral is a single word, the prefix is optional
wherever the ordinal is already unambiguous: `thế kỷ 20` and `thế kỷ thứ 20`
are the same twentieth century.

**The era** `trước Công Nguyên` ships with its usual abbreviation `tcn`.

**The minimal pair `hôm kia` / `ngày kia`** points in opposite directions.
Both close on `kia`, and only the head noun says which way — `hôm` for the past
family, `ngày` for the future. Matching on `kia` alone would put the answer four
days wrong, so each is a whole surface in its own file.

## What refuses

Every refusal here is pinned by a test.

**`cn`.** CLDR abbreviates `chủ nhật` as `CN`, and bare `cn` is also the era
abbreviation for `Công Nguyên`. Admitting it would let an era marker resolve to
a day of the week, so the abbreviation is withheld.

**Bare `mốt`.** It is the southern short form of `ngày mốt`, the day after
tomorrow, and in a tens compound it is the numeral one — `hai mươi mốt` is
twenty-one. Only the unambiguous `ngày mốt` ships.

**Bare `năm` as a five**, as above. Where no unit noun follows to be counted,
the numeral reading is declined.

**The additive clock without `phút`.** `bốn giờ năm` is four-oh-five with the
minute noun left off, but the same string also reads as four hours and five of
anything, and its last word is the year/five collision besides. The additive
minute is read only when `phút` closes it: `bốn giờ năm phút` is 04:05, while
`bốn giờ năm` returns four o'clock with `năm` in the remainder.

**"Since" and "until".** `kể từ` and `cho đến` surfaced only as aggregate
mentions with no worked example, so neither ships and the range they would open
does not resolve.

**Ranges.** "From A to B" and "between A and B" have no attested marker in the
sources consulted, so a range never binds and at most one endpoint resolves.

**Recurrence.** `hàng` appears only as a bound compounding prefix in the sources
consulted, with no evidence that it stands free, so `hàng ngày`, `hàng tuần` and
`hàng tháng` do not resolve.

**"This <unit>".** No source consulted gave a worked example of a `tuần này` or
`năm nay` deictic, so none is invented; the unit noun alone names no span.

**Scales above the thousand.** `triệu` (million) and `tỷ` (billion) are attested
but sit far outside the range a civil date needs, so the fold stops at the
thousand and a phrase like `một triệu năm trước` is left unread rather than
half-read.

## Open questions for a native speaker

1. What are the ordinary "since" and "until" constructions, with worked
   examples?
2. What marks a from-to range and a between range?
3. Does `hàng` stand free, or only as a bound prefix — and what is the ordinary
   way to say "every week"?
4. What is the "this week" / "this year" deictic, and is `năm nay` it?
5. Is the additive clock ever written without `phút` in a way that could be
   read unambiguously?
