"""Smoke coverage for the differential benchmark (``benchmark/``).

The full benchmark run (``python benchmark/run.py``, ~1000 gold cases
across 21 languages) is a manual, documented command (see
``docs/benchmarks.md``) -- it is a snapshot tool, not a CI gate, so it
stays out of the default test run's time budget.  This module instead
asserts the two things that *would* silently rot without any coverage:

* the committed scoreboard snapshot exists and looks like a real report;
* the adapter + scorer plumbing itself still runs end-to-end on a small,
  seeded sample (fast: a few dozen cases, well under a second of engine
  time plus one pytest sub-collection pass).
"""
import os

from benchmark.adapter import collect_gold_cases
from benchmark.run import ENGINES, run_benchmark

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCOREBOARD = os.path.join(_REPO_ROOT, "benchmark", "SCOREBOARD.md")


def test_scoreboard_file_exists_and_looks_real():
    assert os.path.exists(_SCOREBOARD), (
        "benchmark/SCOREBOARD.md is missing -- regenerate it with "
        "`python benchmark/run.py --out benchmark/SCOREBOARD.md`")
    text = open(_SCOREBOARD).read()
    assert "chronologia" in text
    assert "dateparser" in text
    assert "dateutil" in text
    assert "Overall (all languages combined)" in text
    # a real generation command is documented, not left as a placeholder
    assert "benchmark/run.py" in text


def test_adapter_runs_on_a_fast_seeded_sample():
    """The gold-case adapter + scorers run cleanly on a small sample.

    Restricted to a couple of well-covered languages so this stays a
    genuinely fast smoke test (no full 40-language pytest re-collection).
    """
    import random

    cases = collect_gold_cases(["en", "de"])
    assert len(cases) >= 50, "expected the en/de corpora to yield >=50 cases"
    sample = random.Random(0).sample(cases, 50)

    tallies = run_benchmark(sample)

    # every (lang, engine) tally sums back to the number of cases for that
    # language, and every outcome is one of the three defined buckets.
    langs = {c.lang for c in sample}
    for lang in langs:
        n = sum(1 for c in sample if c.lang == lang)
        for engine in ENGINES:
            t = tallies[(lang, engine)]
            assert set(t) == {"exact", "no-parse", "wrong"}
            assert sum(t.values()) == n

    # chronologia is the engine under active development here -- on its
    # own gold set it should get the large majority right (not asserting
    # against competitors' scores; that table is `benchmark, don't assert`).
    chrono_exact = sum(tallies[(lang, "chronologia")]["exact"] for lang in langs)
    assert chrono_exact / len(sample) >= 0.6
