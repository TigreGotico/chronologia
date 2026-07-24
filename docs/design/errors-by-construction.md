# Design north star: make the error classes unrepresentable

This is a forward-looking design note, not a description of the code as it
stands today. It names the recurring *kinds* of bug this extractor produces,
and for each one it asks the only question worth asking before a 1.0 freeze:
**can the engine be shaped so that bug cannot be written at all?**

The guiding value is simple. A test proves one wrong answer is now right. A
construction proves a whole *class* of wrong answers can never occur. Where the
two cost about the same, prefer construction — a passing test is a fact about
today's code, an invariant is a fact about all future code. This note is the
plan for turning the lessons of a long adversarial-audit campaign into
invariants, so the 1.0 engine (the declarative engine on `feat/declarative-engine`)
carries them from the start.

It deliberately does **not** propose a ground-up rewrite. Every change below is
an invariant added to the declarative engine incrementally, behind a frozen
public API, each one provable against the existing test corpus. The corpus is
not just a safety net here: because every fixed bug in the campaign left a
signature, the corpus is the *evidence* that each invariant would have caught
what we caught by hand.

## The five error classes, and how each stops being writable

### 1. Silent-wrong — a partial parse returns a plausible wrong span

This was the dominant defect for the whole campaign. A construction matched
part of an utterance, the qualifier it could not use fell to the remainder, and
a confident, wrong-but-plausible span came back. `2026-W1` returned the whole
year and dropped `W1`. `15.06.2020` returned all of 2020 and dropped the day and
month. Romance ranges returned one endpoint and dropped `del 5 al`. The Slavic
spelled ordinal returned the whole month and dropped `trzeciego`. The Portuguese
`segunda semana` bound the weekday and dropped `semana de março`.

Look at what every one of those has in common: **the evidence of the bug was
sitting in the remainder.** The engine computes that remainder today — in
`extract/__init__` the shape is literally `span, consumed = core` and then the
remainder is "every token whose index is not in `consumed`" — and then emits the
result without ever looking at it.

**By construction:** the remainder is not free text, it is a *typed residue*,
and it is an invariant of a successful parse that no residue token is
temporal-shaped. A bare numeral, a stranded ordinal, an unconsumed month or
weekday or qualifier adjacent to the match is not leftover prose — it is proof
the reading is incomplete, and an incomplete reading yields `None`, never a
guess. The selector cannot emit a parse that strands temporal material; the
result type has no inhabitant that carries a wrong-but-plausible span next to a
dropped `W1`.

This is the highest-leverage single change in this document. It is a property of
the selector, not a rewrite, and it is testable against the whole campaign: the
seventeen fixes that stranded something in the remainder are a ready-made
oracle for "does the residue invariant refuse exactly what we refused by hand?"

### 2. Number-word / date-word collision — the fold eats a weekday

The single most *recurring* root cause, across five unrelated language
families. Hebrew `שני` is both "two" and "Monday"; Indonesian `hari` is the
weekday classifier; the Slavic ordinals, the Romance decade numerals, and
Portuguese `segunda` are all numbers that are also dates. In each case the
number-folding stage — an eager pre-pass, `fold_tokens`, that runs *before* the
matcher — rewrote the token to a digit and destroyed the date reading before the
grammar ever saw it.

Each instance was fixed by hand with positional licensing and vocabulary. That
works, but it is patching a leak whose source is the eager fold: a stage that
commits a lexical decision the grammar has not yet earned the right to make.

**By construction:** folding stops being a destructive pre-pass. A surface that
is simultaneously a numeral and a weekday is *one lexical item carrying both
categories*, and which category wins is decided by the parse that consumes it,
not by a stage that runs first and picks blind. Lexical ambiguity is
represented and carried into matching, never resolved away early. There is no
stage that can turn `שני` into `2` before the "every Monday" reading has had its
say, because no stage resolves a numeral's category in isolation.

This is the one change that touches the core representation rather than a guard,
and it is why the declarative engine — with an explicit token model and a
matcher that sees categories — is the right vehicle. It is also what makes
class 1's residue invariant honest: a token can only be "non-temporal residue"
once the grammar, not the fold, has declined every temporal reading of it.

### 3. Dead vocabulary — a shipped surface the tokenizer can never produce

Greek `μ.μ.` shipped as p.m. vocabulary the tokenizer could never emit, because
it drops dots. `week-end` never registered because the loader's canonicalisation
rewrote dotted surfaces but not hyphenated ones. Catalan interpunct forms were
dead the same way. In each case a `.voc` entry sat in the tree looking like
coverage and matching nothing.

**By construction:** a vocabulary surface and the tokenizer share *one*
canonicalisation function, and the loader defines a surface's canonical form as
"what the tokenizer produces for this string." A surface that does not tokenise
to itself is a load-time error, not silent dead data. "Unmatchable vocabulary"
becomes unrepresentable because the only way to register a surface is through
the tokeniser that will later have to match it. The bug that took three separate
audits to notice becomes impossible to commit.

### 4. English-shaped coverage — a locale silently under-implements

English declares 46 constructions; the median locale declares 22; Kabyle
declares 11. Nothing in the design makes that gap *visible* — a locale can ship
without a construction and every test still passes, because absence asserts
nothing. Persian having no weekend construction, Portuguese having no
`weekend_ref` at all: both were discovered by adversarial audit months later,
not flagged by the system.

**By construction:** the construction registry is a *total* function over
`(locale × construction)`. Every cell is one of `supported` (with data),
`not-applicable` (with a cited reason — the language genuinely lacks the form),
or `not-yet` (a tracked gap). There is no `absent`. A locale that fails to
decide a construction fails validation. "Silently missing" stops being
expressible: a gap is either a documented `not-applicable` or a visible
`not-yet`, never a surprise.

### 5. Unrepresentable value — a crash or a layering bypass

Two shapes here. `extract_duration('9'*20 + ' days')` raised `OverflowError`,
because a parsed count flowed straight into a `timedelta` C-int argument with no
guard, breaking the contract that these functions return or refuse but never
raise. And French could not count past thirty (`quatre-vingt-dix` → 34) because
the fold reached the shared Romance number extractor *directly*, bypassing the
`extract_number_fr` wrapper that knows the vigesimal collapse — two number
back-ends, and the fold called the wrong one.

**By construction:** every parsed count reaches a `timedelta` through one smart
constructor that returns `Optional` and refuses the unrepresentable; raw
`timedelta(...)` from a parsed count appears nowhere else, so the crash has no
site to occur at. And each language exposes exactly one number-reading entry
point; the direct call into the shared extractor that skipped the French wrapper
is made private, so "call the wrong back-end" is not a reachable state.

## Emitting an incomplete reading: residue, not a low score

A fair objection to the veto: refusing outright throws away information. If a
parse bound most of an utterance and stranded one qualifier, some consumer — a
search index that wants recall, not precision — might still want the partial
answer. Why not emit the span with a very low confidence score and let the
consumer filter by threshold?

Because a stranded reading is not a *less certain* answer, it is a *wrong-scoped*
one, and a single scalar cannot say which. `2026-W1` that strands `W1` does not
mean "probably 2026"; it means **all of 2026** — a span fifty times too wide that
merely happens to contain the right one. Scoring that 0.1 does not turn a wrong
boundary into an uncertain right one; it lets a wrong boundary survive at a
discount, and the consumer that keeps it is not getting a fuzzy answer, it is
getting a confidently wrong one.

Worse, one number would have to carry two opposite situations. Genuine ambiguity
among *complete* readings ("tomorrow at 3pm" has several valid candidates) and an
*incomplete* parse that dropped a narrowing qualifier are not points on the same
scale — the first says "pick the best or ask", the second says "the scope is
wrong". A consumer thresholding on a scalar cannot tell them apart, and folding
incompleteness into the score re-commits the exact mistake the confidence rework
just undid: coverage leaking into certainty.

So the two signals stay separate, and the consumer's real need is met with
structure rather than a smeared number:

- **Confidence** measures ambiguity among *complete* readings, and nothing else.
  A homograph with two valid readings scores lower; an incomplete parse does not
  touch it.
- **Residue** is the typed record of what a reading could not account for. It is
  not free text and it is not a score — it is the classified leftover, and its
  being non-empty *is* the "incomplete" signal.

The default single-best entry point vetoes: it returns the honest answer or
`None`, and that is what makes the wrong-scope class unwritable for the majority
of callers who want exactly that. The richer entry point (`extract_candidates`)
exposes the partial reading **and its residue together** — the span it could bind
next to the `W1` it could not. A recall-oriented consumer opts in and uses the
partial span *knowing* temporal material was left over; a precision-oriented one
sees a non-empty residue and discards. Neither has to guess a threshold to
distinguish stranding from ambiguity, because stranding is represented as
residue, not as a low score. The information the veto would otherwise discard is
preserved — just in the shape that says what it actually is.

## The selector is the real work

A prototype of the two invariants — ambiguity-preserving lexing and the residue
veto — was built as a 466-line miniature over five languages and four
constructions, and both held cleanly with no per-language special-casing: the
Hebrew/Indonesian/Portuguese collisions resolved by construction, and a
deliberate attempt to construct the `2026 + stranded W1` answer refused at
instantiation time. That is the encouraging half.

The instructive half is what the miniature had to simplify, because it names
where the cost actually is. The veto eliminates *wrong* readings but does not
*pick* among the surviving *valid* ones — that is the selector, and at the full
set of constructions the selector is where ambiguity really lives, covered by
neither headline invariant. And the miniature's "any temporal residue anywhere"
veto does not survive a multi-mention utterance; the real engine needs the veto
scoped to material *adjacent* to the match. Those two — a principled selector and
local veto scoping — are the genuine unsolved work, not the invariants that
frame them.

This is why the sequencing below is staged and why the veto's arrival is
budgeted rather than cheap: turning it on flips currently-green *lossy* spans to
`None`, and each of those is a hand adjudication, not an automatic win.

The bones are good and the freeze should keep them. The **JDN hub** — every
calendar, era and timeline converting only to and from a single integer line —
is the one genuinely elegant idea in the system and the reason calendar
conversions compose and duration math is always safe. **AstroDate** escaping
`datetime`'s year bounds by duck-typing rather than subclassing is right. The
**data/engine split** — per-locale `.voc` plus `lang.json`, math in the engine —
is right; the problem was never the split but the missing validation around it
(class 3) and the eager fold beside it (class 2). And **"silent-wrong becomes
honest-None"** as the governing value is already the house rule; classes 1 and 2
are just the plan to make the engine *enforce* it instead of relying on audits
to find where it was violated.

## Sequencing — behind a frozen API, not a big bang

The public surface freezes at 1.0; the engine behind it does not have to. So the
order is chosen to spend the scarce resource — pre-public API runway — on the
API, and to land the structural invariants where they are cheap.

**Before 1.0 (cheap, high-value, no rewrite):**

- Class 1, the residue invariant, at the selector. It is a property added to one
  decision point and it collapses the largest defect class. Prove it against the
  campaign corpus.
- Class 3, tokeniser-validated vocabulary, at the loader. A load-time check, a
  handful of lines, closes dead-data forever.
- Class 5, the duration smart constructor and the single number entry point.
  Small, local, and one of them is a live crash.
- The **API-freeze audit** itself: names, parameter order, keyword-only-ness, the
  result NamedTuple field names, required-versus-optional — the things that
  genuinely cannot change after v1. This is the real now-or-never work.

**At and after 1.0, on `feat/declarative-engine`:**

- Class 2, ambiguity-preserving lexing, is the deep one. It is the core-
  representation change, and it is exactly what the declarative engine is for.
  It lands as that engine matures, behind the now-frozen API, proven step by step
  against the corpus — the redesign without the big bang.
- The **selector and local veto scoping** — the work the prototype deferred. This
  is the true cost centre (an estimated month against the full corpus), and it is
  what makes the residue veto and ambiguity-preserving lexing usable at 46
  constructions rather than at 4. It ships alongside class 2, one construction
  family at a time.
- Class 4, the total construction matrix, ships with the engine's schema so a new
  locale cannot under-implement silently.

The prototype lives on the throwaway `experiment/pure-engine-spike` branch under
`experiments/pure_engine/` — 466 lines, a runnable `evaluate.py`, and a
`FINDINGS.md`. It is evidence, not a foundation: keep it as the thing that proved
the invariants hold and located the selector as the real work, and build the
production version into the declarative engine rather than growing the miniature.

The test is not whether the engine is beautiful. It is whether, a year after
1.0, the adversarial audit that found twelve defects in an afternoon finds
none — because the shapes it hunts for can no longer be written.
