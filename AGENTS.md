# AGENTS.md

<!-- agent-hint
covers: what chronologia is, how the repository is laid out, how to set it up and test it, and the rules that tests and docs enforce
source: pyproject.toml, test/test_docs_examples.py, test/test_language_parity.py, test/test_holiday_golds.py, test/test_impossible_date_error.py, CONTRIBUTING.md
generated: no
verify: .venv/bin/python -c 'exec("import os,re,glob\nfrom chronologia import CALENDARS\nfrom chronologia.extract.numlayer import NUMTAG_LANGS as N\nt=open(\"AGENTS.md\").read()\nfor q in set(re.findall(r\"\\x60((?:chronologia|test|docs|benchmark|examples|\\.github)/[^\\x60<>*{}]+)\\x60\",t)): assert os.path.exists(q.rstrip(\"/\")),q\nc=len(glob.glob(\"chronologia/locale/*/lang.json\"))\nassert \"in %d languages\"%c in t and \"across %d calendars\"%len(CALENDARS) in t and \"other %d locales\"%(c-len(N)) in t\n")'
see: README.md, CONTRIBUTING.md, docs/index.md
-->

chronologia reads dates that people write in 61 languages and computes across 18 calendars, timelines, holidays, the sun and the moon. Its answers are spans with a width and a basis, and the library returns nothing where it cannot be right.

## Map

| Path | Holds |
|---|---|
| `chronologia/` | the calendar, holiday, sky and span code behind `chronologia.__all__` |
| `chronologia/extract/` | `extract_timespan`: loader, matcher, resolver, tokenizer and the number readers |
| `chronologia/locale/<code>/` | `lang.json` and the `*.voc` word lists of one language |
| `chronologia/holiday_data/` | one `<code>.tab` file of holiday rules per jurisdiction |
| `test/` | engine tests, `nl_corpus_<code>/` phrase corpora, `holiday_golds/`, `holiday_sources/` |
| `benchmark/` | the differential benchmark and its generated `SCOREBOARD.md` |
| `docs/`, `examples/` | the guides ([index](docs/index.md)) and eight runnable scripts |

## Setup and tests

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[test]"
pytest test/test_docs_examples.py                  # every python block in README.md and docs/
pytest test/nl_corpus_pt                           # one language corpus
pytest test/ --ignore-glob="test/nl_corpus_*"      # engine, calendars, holidays, packaging
```

The full suite is large, so run the tests for the code you touched. CI runs all of it on Python 3.11, 3.12 and 3.13.

## Rules the repository enforces

A wrong span is worse than no span. Where sources conflict or say nothing, a locale ships nothing. The phrase then returns `None`, or a narrower span with the unreadable words in the remainder. To tell a refusal from a bug, read [when a language declines a phrase](docs/extraction.md#when-a-language-declines-a-phrase).

Cite every linguistic and calendrical fact. A word list entry says where the surface came from: a dictionary, a grammar, a standards body, or your own native knowledge stated as such. Where no source exists, the library refuses rather than guesses ([CONTRIBUTING.md](CONTRIBUTING.md)).

Write the test first and check that it fails before the fix. Derive every expected value without this library, by hand or from another source ([CONTRIBUTING.md](CONTRIBUTING.md)). Each language needs a corpus of at least 100 cases. It also needs a block that asserts the same spans as English. `test/test_language_parity.py` enforces both ([docs/adding-a-language.md](docs/adding-a-language.md)).

Every holiday rule needs a frozen gold value in `test/holiday_golds/`. A tier floor stops the provenance counts from shrinking ([docs/transparency.md](docs/transparency.md)).

Numbers: numtag reads the numbers of the languages in `NUMTAG_LANGS` in `chronologia/extract/numlayer.py`. The other 21 locales use their own `numfold_*` module. The table is in [docs/languages/index.md](docs/languages/index.md).

Ambiguous phrases follow [docs/rulings.md](docs/rulings.md). A change to a ruling changes that page. `test/ruling17_pins.txt` and `test/ruling23_pins.txt` list the tests whose expected value a ruling changed.

Every python block in `README.md` and `docs/*.md` must run. `test/test_docs_examples.py` runs them ([CONTRIBUTING.md](CONTRIBUTING.md)). Mark an illustrative block with `# doctest: skip`.

A phrase that names a date the calendar rejects ("29 February 2017", "every 31st of April") returns `None`. Pass `impossible="raise"` to get an `ImpossibleDateError` instead ([docs/extraction.md](docs/extraction.md#impossible-dates-and-out-of-range-ordinals)). `test/test_impossible_date_error.py` covers it.

Pull request titles follow [conventional commits](CONTRIBUTING.md). `.github/workflows/conventional-label.yaml` labels the pull request from its title. The release workflow picks the version bump from the labels. `feat:` is for user-visible features.

## Before a push

1. Run the tests for the code you touched.
2. Run `pytest test/test_docs_examples.py` after any change to a docs page or a public name.
3. Run the `verify` command in the agent hint of each docs page you changed ([docs/index.md](docs/index.md)).
4. After a change to an extractor, compare two trees with `python -m benchmark.crossview` ([docs/benchmarks.md](docs/benchmarks.md#comparing-two-trees)).
5. Add a language only through [docs/adding-a-language.md](docs/adding-a-language.md).
