# Rules for AI agents working in this repository

Read [CONTRIBUTING.md](CONTRIBUTING.md) first — everything there applies. This
file adds the constraints that exist because agents, not humans, do most of
the work here, and because the failure modes differ.

## The one rule everything else serves

A wrong answer is worse than no answer. This library is used to decide what a
person meant by a date, and a plausible-but-wrong span propagates silently
into whatever consumes it. When a construction cannot be represented
faithfully, return nothing. Never widen a span, never round a value, and never
pick the likelier of two readings to avoid returning `None`.

## Never invent a linguistic fact

Do not add a vocabulary surface, an inflection, or a grammar order that you
have not verified against a real source: a dictionary, a grammar, a standards
body, or an existing attested phrase in that language's test corpus. Guessed
surfaces have repeatedly looked plausible, passed review, and been wrong.

If you are uncertain about a form, leave it out and say so in your report as
needing a native speaker. An honest gap is a contribution; a confident guess
is a defect with a test pinning it in place.

## Tests

Write the test before the fix, and prove it fails against unfixed code by
reverting your source change with a patch file (`git diff > /tmp/x.patch;
git apply -R /tmp/x.patch`), running the test, then reapplying. Do not use
`git stash` for this: stash state is shared across worktrees and corrupts
concurrent work.

Derive every expected value independently — by hand, or with a library that
is not this one. Never copy an expectation out of the parser's output.

Do not weaken an existing test to make a change pass. A pinned expectation may
only change when it pinned a defect, and the pull request must say so
explicitly and explain why the old expectation was wrong.

## Scope

Fix the defect in front of you. Do not refactor surrounding code toward a
convention, rename for consistency, or restructure a module you were not asked
to touch — those changes bury the actual fix and make review expensive.

If you discover a second, unrelated defect while working, report it rather
than fixing it in the same change.

## Comments and commit messages

Comments state invariants and cite sources: why a band is `[06:00, 12:00)`,
which dictionary attests a surface, what a guard protects against. They never
narrate the change itself — no review-round tags, no "fixed per feedback", no
before-and-after history. That belongs in the commit message, which is where
a reader goes looking for it.

Match the surrounding code's idiom, including whether it uses type
annotations. Do not add defensive `getattr`/`hasattr` layers or compatibility
shims for cases that cannot occur.

## Verifying before you report

Run the tests you claim to have run, and quote real output. If a run was
interrupted or you are unsure whether it completed, say so — an unverified
claim of a green suite is worse than an honest "I could not finish this",
because the next step depends on it being true.
