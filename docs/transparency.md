# Transparency: how this library was built

This library was written by AI, orchestrated by AI, and directed by a
human — most of it in one very long working session. You deserve to know
that, and to know how it worked. This page is the honest account.

## Who did what

**The human maintainer designed this architecture.** Years before this
library existed, they prototyped its core ideas in a lingua-franca pull
request: date extraction split from time extraction, resolution-aware
results (day, week, month, century…), calendar-scoped ordinals and
seasons, and named eras and epochs with out-of-range dates as an open
problem. That design — including the `ranges` module and the
`DateTimeResolution` concept that still anchor the resolver — sat
largely dormant in the predecessor parser until this library grew
around it. The maintainer also made every decision that shaped the
result: that results must be *spans* with honest widths rather than
fake-precise instants; that `AstroDate` must speak `datetime`'s
language; that extraction belongs in the reckoning library; that
holiday data must be built clean-room from primary sources, that every
holiday needs its own "when is X" test, and that holiday names belong
to the countries that own them; that ugly APIs get rewritten ("anyone
who reads this will close the tab" — they were right). They contributed
data directly too — the Portuguese municipal holiday tables began as
their hand-curated research.

**An orchestrating AI** (Anthropic's Claude) worked the gaps in that
design: filled in the unresolved parts (the out-of-range representation
became `AstroDate`; the resolution concept became span width), extended
the architecture to domains the original didn't reach (calendars,
timelines, deep time, the sky, Mars), planned the work, split it into
missions, reviewed every result, and merged nothing it had not
independently re-verified. **Dozens of subordinate AI agents** each
executed one mission — one language, one calendar family, one country
batch, one documentation pass — in isolated git worktrees, under
written rules, with their work gated by tests before merging.

## The method

Three rules did most of the heavy lifting:

1. **Cite or refuse.** Every algorithm is transcribed from a downloaded,
   named source; every holiday rule cites a law, gazette, or official
   listing; every gold test value is derived by hand or from an
   independent source — never from the code under test. When no
   citable source existed (the Javanese calendar's contested leap
   pattern, Bennett's own "not known" for 46 BC), the feature was
   *refused*, with the reason documented, rather than invented.
2. **Natural-language test-driven development.** For everything a human
   types or says, the test corpus came first: thousands of real
   phrases with hand-derived expected spans, in every supported
   language, including adversarial cases written to break the code.
   Any wrong answer became the top-priority bug before any new
   feature.
3. **Structural ratchets.** Wherever a quality bar was declared, a test
   was written that *walks the data* and fails on any gap: every
   holiday rule must have a gold; every language must have a corpus
   and a semantic-parity block matching English span-for-span; every
   code example in every documentation page is executed on every test
   run. Quality is enforced by the suite, not by promises.

Cross-validation ran throughout: our calendars against an independent
open-source implementation (Chinese and Hebrew agreed exactly, 66/66
and 16/16 — mutual corroboration), our extraction against `dateparser`
and `dateutil`, our Easter against published tables, our prayer times
against published timetables, our Mars dates against NASA's own worked
examples.

## What the process found in the world

Verification pointed both ways. Along the way this process found: a
transcription error in a widely-mirrored Umm al-Qura data table (an
impossible 28-day lunar month, corrected against the 29/30 invariant);
that a commonly-published Solar Hijri leap-cycle variant mispredicts
Nowruz in some years (the corrected variant was verified against twelve
documented Nowruz dates and shipped instead, with the discrepancy
documented); and several long-standing bugs in the predecessor parser's
own languages, including entire missing grammatical features.

## Why this disclosure

AI-written code at this scale is new enough that readers should not
have to guess. The honest summary: the *architecture and judgment* in
this library — its founding design, what it should be, what it must
refuse to do, whose names things carry, which sources count — are
human. The *labor* — tens of thousands of lines of arithmetic, data
transcription, tests, and prose — is AI,
verified by machine-checkable gates and spot-audited by the
orchestrator at every merge. Where those gates could not reach
(translation quality across scripts, contested historical claims), the
work was scoped down to what could be verified rather than shipped on
confidence.

The test suite, the citations in every module, and the executable
documentation are the parts of this story you can check yourself —
which is exactly why they exist.

## The numbers (at the time of writing)

| | |
|---|---|
| Pull requests merged into this repository | 74 |
| Tests | ~27,400 (plus 121 language-parity checks) |
| Natural-language corpus cases | ~9,100 across 42 languages |
| Calendars | 17 (+ zone/timeline adapters) |
| Holiday jurisdictions | 260 (247 countries/territories, subdivisions, 14 financial markets) · ~4,750 rules · every rule golded |
| Holiday name translations | 1,394 rows |
| Documentation pages | 15, every code example executed by the suite |
| Externally-found data errors | 2 (reported in module docstrings) |
