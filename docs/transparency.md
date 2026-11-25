# Transparency: how correctness is checked

<!-- agent-hint
covers: the checks that decide whether answers are right and the provenance tiers of holiday golds
source: test/test_holiday_golds.py, test/holiday_golds/_tier_floor.json, test/test_language_parity.py, test/test_docs_examples.py
generated: no
verify: diff <(sed -n 's/^- \*\*\([a-z-]*\)\*\*:.*/\1/p' docs/transparency.md) <(.venv/bin/python -c "import re;print(*re.search(r'_TIERS = \((.*?)\)',open('test/test_holiday_golds.py').read())[1].replace('\"','').replace(' ','').split(','),sep='\n')") && .venv/bin/python -c 'exec("import os,re\nt=open(\"docs/transparency.md\").read()\nm=re.search(r\"MIN_CASES = (\\d+)\",open(\"test/test_language_parity.py\").read())[1]\nassert \"at least \"+m+\" cases\" in t\nfor q in set(re.findall(r\"\\x60((?:test|chronologia)/[^\\x60<>*]+)\\x60\",t)): assert os.path.exists(q.rstrip(\"/\")),q\n")'
see: docs/civil-holidays.md, docs/benchmarks.md
-->

The library is written by AI and directed and reviewed by a human maintainer. This page lists the checks that decide whether its answers are right, so a reader can judge the work without trusting either party.

## The method

**Cite or refuse**. Every algorithm is transcribed from a named source, and every holiday rule cites a law, a gazette or an official listing. Every gold test value is derived by hand or taken from an independent source, never from the code under test. Where no citable source exists, such as the contested leap pattern of the Javanese calendar, the feature is refused and the reason is documented.

**Natural-language test-driven development**. Each language has a corpus package `test/nl_corpus_<code>/` of real phrases with hand-derived expected spans. `test/test_language_parity.py` requires at least 100 cases per corpus. It also requires a semantic-parity block that asserts the same spans as the English corpus.

**Structural checks**. A test walks the data and fails on a gap. Every holiday rule needs a gold value. Every code block in `README.md` and `docs/` runs in `test/test_docs_examples.py`.

## Holiday gold provenance

Each holiday rule is checked against a frozen gold value in `test/holiday_golds/<cc>.tab`, one file per jurisdiction. A single parameterised walker in `test/test_holiday_golds.py` runs every gold against the engine. A structural test reads the same files and requires at least one gold per shipped rule.

Each gold carries a provenance tier, because not every passing test proves the same thing.

- **primary**: the expected date is restated from a cited primary source, such as a statute, a gazette or an official listing. A wrong engine result fails against the source. This is the strongest tier.
- **computed**: an independent in-test calculation produces the expected date. Examples are Easter plus a documented offset, an nth-weekday calculation, or a standalone Julian-day or Hijri conversion. It proves the engine agrees with a second, separately written calculation.
- **witnessed**: the expected date is the output of the independent `holidays` package from vacanza, captured once and frozen with the package version. It proves agreement with an outside witness, not correctness against the statute. If a date or subdivision in a `.tab` file is mistranscribed, the engine output diverges from the frozen value and the test fails.
- **self-evident**: the expected date is the rule's own argument. Examples are the month and day of a fixed row or a listed gazette date of a decree row. It guarantees that the rule has a gold. It does not prove the date is correct.

The suite prints the counts per jurisdiction and tier. `test/holiday_golds/_tier_floor.json` holds a frozen floor, and a test fails when a tier count falls below it.

## Cross-checks against other implementations

The calendars were compared with an independent open-source implementation, and extraction was compared with `dateparser` and `dateutil` in the [benchmark](benchmarks.md). Easter dates are checked against published tables, prayer times against published timetables, and Mars dates against worked examples from NASA.

---
[← Benchmarking chronologia against other date parsers](benchmarks.md) · [Home](index.md) · [Language provenance pages →](languages/index.md)
