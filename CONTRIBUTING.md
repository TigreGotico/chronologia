# Contributing

The most valuable thing you can send is a phrase this library reads wrongly.

## Reporting a wrong answer

Open an issue with the phrase, the language code, the anchor you used, what
you expected, and what you got:

```python
from chronologia import extract_timespan
from datetime import datetime

print(extract_timespan("de quinze em quinze dias", "pt", datetime(2026, 8, 14, 10, 0)))
```

Two kinds of report are worth separating, because they get fixed differently.
A **wrong answer** — a plausible-looking span that is not what the phrase
means — is the top-priority bug class here, above any missing feature. A
**refusal** — `None`, or a correct span with your phrase left over in the
remainder — usually means a word is missing from a vocabulary file, which is
a much smaller fix and an easy first contribution.

If you speak a language in the second or third band of the coverage table in
the README, reading its vocabulary files is high-leverage work. Nobody on the
project speaks forty languages, so a native reader finds things no test can.

## Setting up

```bash
git clone https://github.com/TigreGotico/chronologia
cd chronologia
python -m venv .venv && . .venv/bin/activate
pip install -e ".[test]"
```

## Running tests

The suite is large — over 150,000 checks — because every language carries its
own corpus of real phrases. Run the part you touched, not the whole thing:

```bash
pytest test/nl_corpus_pt              # one language's corpus
pytest test/ --ignore-glob="test/nl_corpus_*"   # engine, calendars, packaging
pytest test/test_docs_examples.py     # every code block in README and docs/
```

The full suite takes roughly twenty minutes on a laptop; CI runs it on every
pull request across Python 3.10 through 3.13, so you do not have to.

## How changes are expected to arrive

**Tests come first, and they must fail before your fix.** For anything that
reads human text, write the phrase and its expected span before touching the
parser, and check that the new test genuinely fails against unfixed code — a
regression test that passes either way proves nothing.

**Derive gold values independently.** Compute the expected date by hand or
from a source that is not this library. A test whose expectation was copied
from the parser's own output only pins current behaviour, including its bugs.

**Cite linguistic and calendrical facts.** Vocabulary additions should say
where the surface came from — a dictionary, a grammar, a standards body, or
your own native knowledge stated as such. Where sources disagree, both
readings can ship under different names; where no source exists, the library
refuses rather than guesses, and that refusal is the correct outcome.

**Prefer refusal to a confident guess.** If a construction cannot be
represented faithfully, returning nothing is right. Silently answering with a
span that means something else is the one outcome this project treats as
unacceptable.

Commit messages follow [conventional commits](https://www.conventionalcommits.org)
(`fix:`, `feat:`, `docs:`, `chore:`); `feat:` is reserved for user-visible
features, since the release automation reads these to pick the next version.

## Adding a language

[docs/adding-a-language.md](docs/adding-a-language.md) is the complete
walkthrough: which vocabulary files exist, what each slot means, how the
grammar orders are declared, and how to build the test corpus. The engine
itself is language-independent, so most new languages are vocabulary and
grammar-order work rather than code.

## License

By contributing you agree that your contributions are licensed under
Apache-2.0, the same licence as the project.
