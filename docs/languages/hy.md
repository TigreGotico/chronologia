# Armenian (`hy`)

Armenian marks almost everything temporal **after** the phrase it governs.
`առաջ` ("ago") is a postposition, `հետո` and `անց` mark a forward offset from
the same position, the year word `թ.` trails the year in a written date, and
the ablative that means "in N days" is a case suffix fused onto the unit noun
itself. Only `մինչև` ("until") leads its object, and only the determiners
`այս`, `նախորդ` and `հաջորդ` stand before their noun.

The clock names the hour **already reached**, not the coming one:
`ութ անց կես` is 08:30, not 07:30.

## What ships

**Months** ship in three shapes from Unicode CLDR 47,
`cldr-dates-full/main/hy/ca-gregorian.json`: the stand-alone wide name is the
nominative, the format wide name is the genitive that a written date uses
(`հունիսի 5`), and the abbreviation is the calendar's own short form.

**Weekdays** come from the same file.

**The date line** is `dd MMMM, y թ.`, with `թ.` the standard abbreviation of
`թվական`, "year", trailing the number.

**Relative offsets** are all postposed, and the forward direction has three
surfaces. `-ից` is the ablative case suffix on the unit noun itself — CLDR's
own future pattern is `{0} օրից`, in N days — and the locale's number fold
splits it off the fused surface. `անց` and `հետո` are free-standing
postpositions after a bare duration; Wiktionary's `անց` entry gives
`հինգ տարի անց`, five years later. Backward is `առաջ`, with the counted noun
unmarked: `{0} օր առաջ`.

**Determiners** are CLDR's relative-type words: `այս` for this, `նախորդ` for
last, `հաջորդ` for next, all prenominal with no case suffix on the noun.
`անցյալ` and `անցած` ship beside `նախորդ` as the two adjectival synonyms
Wiktionary attests in the same slot.

**The clock** opens with `ժամը`, literally "the hour". `անց` counts up from the
hour named, and `ու` ("and") fills the same slot in the standard modern
phrasing `ժամը վեցն ու կեսն է` for 06:30. `կես` and `քառորդ` are the half and
the quarter, each shipped with and without the definite article, since the
`ու կես` phrasing takes the articled form.

**Numerals** are folded by `chronologia/extract/numfold_armenian.py`, which also
handles the fused ablative.

## What refuses

Each refusal is pinned by a test.

**"Since".** A dedicated "since <a point in time>" periphrasis — `-ից ի վեր`,
`-ից սկսած` — has no fetched worked example, so no open-ended backward range is
opened. The bare ablative this locale *does* read is the forward duration
offset, a different construction that happens to share a suffix.

**"For <duration>".** `երեք օր շարունակ` and `երեք օրվա ընթացքում` have no
citation, so a duration phrase must not be read as one.

**"Between A and B".** `միջև` is a postposition governing the genitive on
**both** conjuncts, a shape this library's range grammar has no order for. The
range is refused and the postposition left unread, rather than a half-range
being invented from the first conjunct alone.

**`առաջ` before an event.** The postposition takes two patterns: a bare
duration — `երեք օր առաջ`, which this locale reads — and an ablative-marked
event or reference point, `ուտելուց առաջ`, "before eating". Only the duration
pattern ships; the event one is refused rather than read as a duration, which
would turn "before eating" into a quantity of time.

**The locative `-ում`.** It is reported as a temporal modifier but with no
temporal worked example, and literary usage drops the definite article inside
it, so no locative surface is claimed for any unit or month. `հունիսին` returns
nothing.

**A weekend noun.** No surface was attested, so the two-day span has no name in
this locale.

**`ամեն` in a span parse.** It quantifies a repeating period and is read by the
recurrence path, not the span path, so it must not silently disappear from a
span parse.

## Open questions for a native speaker

1. What is the ordinary "since Monday" construction, with a worked example?
2. How is "for three days" expressed as a duration?
3. Does `միջև` have a form usable for a date range, or is the genitive on both
   conjuncts obligatory?
4. Is the locative `-ում` current for months and units in ordinary writing —
   `հունիսին` for "in June"?
5. Is there a word for the weekend?
