# Transparency: how this library was built

This library was written by AI, orchestrated by AI, and directed by a
human — most of it in one very long working session. You deserve to know
that, to know how it worked, and to know what went wrong along the way.
This page is the honest account.

## Who did what

**The human maintainer** set the direction and made every decision that
shaped the library: that results must be *spans* with honest widths
rather than fake-precise instants; that `AstroDate` must speak
`datetime`'s language; that holiday data must be built clean-room from
primary sources; that every holiday needs its own "when is X" test;
that holiday names belong to the countries that own them; that ugly
APIs get rewritten ("anyone who reads this will close the tab" — they
were right). The maintainer also contributed data directly — the
Portuguese municipal holiday tables here began as their hand-curated
research — and handled every relationship with human contributors.

**An orchestrating AI** (Anthropic's Claude) planned the work, split it
into missions, reviewed every result, and merged nothing it had not
independently re-verified. **Dozens of subordinate AI agents** each
executed one mission — one language, one calendar family, one country
batch, one documentation pass — in isolated git worktrees, under
written rules, with their work gated by tests before merging.

**A human domain expert** (the author of the Aragonese grammar)
reviewed the Aragonese language work in the neighbouring parser project
and contributed corrections. Those corrections were treated as
reference material — his contribution remains his; nothing here was
pushed onto his work.

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

## What went wrong — and was caught

An honest account includes the failures. All of these happened, and all
were caught by the same discipline that built the rest:

- **A blind merge-conflict script produced invalid TOML**, silently
  breaking the build in a way that masked test results for two rounds
  until the missing output was chased down. Lesson: structured files
  are validated after every conflict resolution, always.
- **A test baseline went stale** and 100 differences appeared. Forensics
  showed every single one was a documented, intentional bug fix and
  zero were regressions — but proving that required categorizing all
  100 rather than regenerating the baseline and hoping.
- **A branch was merged while red** because a shell construct swallowed
  the test runner's exit code. The failures turned out to be a naming
  mismatch between two agents' conventions, fixed by raising coverage
  to the stricter floor — but the merge should not have happened, and
  merge commands now guard on the gate's recorded result.
- **A coordination message was routed to the wrong agent**, which
  correctly recognized the mismatch and refused to act on it — while
  the intended recipient, never receiving it, did work that then had to
  be unwound by hand.
- **An agent was dispatched to push fixes onto a human contributor's
  pull request.** The maintainer stopped it — nothing was pushed, and
  the rule is now permanent: community contributions are reference
  material, never edited by AI. The contributor's corrections were
  preserved as cited notes instead.
- **A claimed fact was published without checking** ("it was a
  Wednesday") and failed its own verification script; the corrected
  example became a better teaching moment than the wrong one would
  have been. Every claimed output in these docs is now executed.

## Why this disclosure

AI-written code at this scale is new enough that readers should not
have to guess. The honest summary: the *judgment* in this library —
what it should be, what it must refuse to do, whose names things carry,
which sources count — is human. The *labor* — tens of thousands of
lines of arithmetic, data transcription, tests, and prose — is AI,
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
| Pull requests merged into this repository | 59 |
| Tests | ~9,200 (plus ~450 language-parity checks) |
| Natural-language corpus cases | ~5,000 across 27 languages |
| Calendars | 17 (+ zone/timeline adapters) |
| Holiday jurisdictions | 45 · 1,182 rules · every rule golded |
| Holiday name translations | 1,007 rows, 5 languages |
| Documentation pages | 13, every code example executed by the suite |
| Externally-found data errors | 2 (reported in module docstrings) |
