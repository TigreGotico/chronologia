# Albanian (`sq`)

Albanian marks definiteness as a suffix on the noun — `ditë` is "day",
`dita` "the day" — and the form a temporal phrase uses is not a stylistic
choice. It is selected by whatever governs the noun. CLDR's own relative-time
patterns pin down which form each construction takes, and that is what the
vocabulary encodes: bare indefinite after `këtë` and `çdo`, ablative after
`pas`, indefinite plural or ablative after `më parë` and `para`, and the
definite accusative only in the fused `e kaluar` / `e ardhshme` "last" and
"next" phrases on week and month.

The clock splits by construction. Half past and quarter past name the
**current** hour — `7 e gjysmë` is 7:30, `dy e një çerek` is 2:15 — while
quarter to counts back from the **coming** one with `pa`, "minus":
`tre pa çerek` is 2:45. Away from the quarter marks Albanian does not use an
idiom at all; it states the digits, `7 e 25 e mëngjesit` for 7:25 in the
morning.

## What ships

**Weekdays and months** come from CLDR 47,
`cldr-dates-full/main/sq/ca-gregorian.json`. Every weekday name is historically
the article `e` plus an ordinal, already fused in the CLDR citation form, and
each ships in the citation form plus the two forms the relative frames use —
`e hënë`, `të hënë`, `të hënën`.

**Relative offsets** follow CLDR's patterns exactly. The past is `X më parë`
with the indefinite noun (`tre ditë më parë`) or the fronted `para X` with the
ablative (`para dy ditësh`), a pair Wiktionary's `para` entry corroborates with
its own examples — `para një jave`, `para dy vjetësh`. The future is `pas X`
with the ablative, singular for a count of one and the `-sh` plural otherwise:
`pas tre ditësh`.

**This, last and next** are three different shapes. `këtë` takes a bare
indefinite noun. Week and month take the definite accusative plus a fused
adjective: `javën e kaluar`, `muajin e ardhshëm`. Year takes neither — it has
three unrelated lexical words, `vjet` for last year, `sivjet` for this year and
`mot` for next year, and a fold that generalised the week-and-month pattern to
the year would produce an unattested surface.

**`para` and `pas` as general prepositions** cover event-relative "before" and
"after" as well as the offsets, governing the ablative, with Wiktionary's
worked examples `para nisjes`, `para dreke`, `para Vitit të Ri`.

**Ranges** use `nga X deri (në) Y`, with `deri` alone for "until". The worked
example is `Unë punoj nga ora 8 deri në ora 4`.

**Day parts** take their bands from the CLDR 47 supplemental day-period rule
set for `sq` — morning 04:00–09:00 and 09:00–12:00, afternoon 12:00–18:00,
evening 18:00–24:00, night 00:00–04:00 — and their surfaces from the wide
day-period names.

**The hour word licenses a bare hour.** `ora tetë` is eight o'clock; a bare
`tetë` names no time. This is what keeps a stray numeral after any noun from
becoming a clock reading.

## Weaker provenance

Albanian is the locale whose sources are thinnest overall, and the vocabulary
files carry no per-file citation comments the way most locales do.

**The clock idioms** rest on one directly-fetched page — detyra.al's article on
reading analogue and digital clocks, which supplies `7 e gjysëm` glossed as
7:30 and the digital-style minute examples — plus two independent tertiary
aggregates agreeing on `tre pa çerek` for 2:45. That is two lines of evidence,
one of them primary, for a construction that is internally consistent.

**The ±2 day words** `pardje` and `pasnesër` come from tertiary aggregates
only.

**`çdo` with units other than the day** is a pattern generalisation. `çdo ditë`
is attested; `çdo javë`, `çdo muaj` and `çdo vit` follow the same
determiner-plus-bare-noun rule but were not independently sourced per unit.

**Numerals.** One through ten and the ordinals through tenth are sourced. The
tens pattern is implied by an aggregate rather than read from a primary table.
Zero, the hundreds and the thousands were not confirmed from any directly-read
source, and `njëqind` does not resolve.

**The Wiktionary `ditë` declension table** was fetched through a summarising
reader and its ablative row does not match the ablative forms CLDR's own
patterns give. The CLDR-derived forms are what ship; that table is not relied
on.

**Gender for the `tre` / `tri` split.** Albanian marks gender on "three".
`javë` is feminine and `muaj` and `vit` masculine, inferred from the endings
CLDR's definite-accusative and ablative forms show. The genders of `ditë` and
`orë` were not independently cross-checked.

## What refuses

Each refusal is pinned by a test.

**"Since".** `që nga` and `që prej` both appear in word lists as "since", with
nothing fixing which one a temporal phrase takes or what case it governs, so
neither ships and `që nga e hëna` does not resolve.

**"Between … and".** `midis`, `ndërmjet` and `në mes` all surfaced as
"between", none with a two-endpoint example, so no range marker is claimed.

**"For <duration>".** `për` is "for" in every preposition list, but with no
temporal worked example it is not shipped as a duration marker, and
`për tre ditë` does not resolve.

**Decade and millennium.** Neither has a dictionary entry that could be read,
so the units are absent rather than transliterated, and `tre dekada më parë`
refuses.

**The postposed century ordinal.** Albanian writes the century with the ordinal
after the noun, and `shekulli XXI` returns nothing. Reading that order would
also swallow `viti 2027` — a year word plus a year — turning it into a
postposed ordinal, so the construction waits for a mechanism that can tell the
two apart rather than being bought at that price. The failure this pins is
concrete: an earlier fall-through answered `shekulli XXI` with 21:00.

**The feminine ordinal `e para`.** It is homographic with the preposition
`para`, "before" and "ago", and no reading of the bare word tells them apart.
Only the masculine `parë` is in the ordinal fold, which leaves
`para dy ditësh` reading correctly as an offset.

**The abbreviated Tuesday and Saturday.** CLDR abbreviates them `mar` and
`sht`, spelled exactly like abbreviated March and September. The month reading
is the one that carries a year, so those two weekday abbreviations are not
shipped and the abbreviation stays unambiguous: `mar 2020` is March.

**The definite nominative weekday forms.** `e diela`, `e hëna`, `e marta` do
not resolve. The definite nominative is attested for only two of the seven
days, so none of the seven ships it.

**An ordinal day of the month.** Whether an Albanian date names its day with a
cardinal or an ordinal, and where the connective goes, was never attested. The
locale reads only the CLDR pattern, a bare cardinal day: `5 qershor 2027`.

## Open questions for a native speaker

1. What is the ordinary "since" construction, and what case does it govern?
2. What is the "between A and B" frame, with a worked example?
3. Is `për` the duration marker, and how is "for three days" said?
4. Is there a decade word and a millennium word in ordinary use?
5. Does a real Albanian date name its day with a cardinal or an ordinal, and
   where does the connective sit?
6. Are `pardje` and `pasnesër` standard rather than regional?
7. What are zero, the hundreds and the thousands, and what is the tens pattern?
8. Are `ditë` and `orë` feminine, for the `tre` / `tri` agreement?
9. Is a compositional `vitin e kaluar` also current alongside `vjet`?
