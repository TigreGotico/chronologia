"""The support table in docs/languages/index.md matches the data that writes it."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import language_support  # noqa: E402
import plot_benchmarks  # noqa: E402


def test_index_matches_the_generated_table():
    with open(language_support.INDEX, encoding="utf-8") as f:
        current = f.read()
    assert language_support.rendered_index() == current, (
        "docs/languages/index.md differs from the generated table; "
        "run python tools/language_support.py write")


def test_results_cover_every_locale_and_feature():
    with open(language_support.RESULTS, encoding="utf-8") as f:
        results = json.load(f)
    assert sorted(results) == language_support.locales()
    for code, features in results.items():
        assert sorted(features) == sorted(language_support.COLUMNS + ["ready"]), code


def test_ready_flags_match_the_benchmark():
    with open(language_support.RESULTS, encoding="utf-8") as f:
        results = json.load(f)
    for code in language_support.locales():
        assert results[code]["ready"] == language_support.ready_flags(code), (
            code, "run python tools/language_support.py write")


def test_results_count_the_rows_of_the_mapped_files():
    """A renamed or added test file changes the mapping; measure again."""
    with open(language_support.RESULTS, encoding="utf-8") as f:
        results = json.load(f)
    for code in language_support.locales():
        files = language_support.test_files(code)
        for feature, paths in files.items():
            assert (results[code][feature][1] == 0) == (not paths), (code, feature)


def test_benchmark_table_matches_the_result_file():
    with open(plot_benchmarks.OUT + ".json", encoding="utf-8") as f:
        data = json.load(f)
    with open(plot_benchmarks.PAGE, encoding="utf-8") as f:
        assert plot_benchmarks.rendered_page(data) == f.read(), (
            "docs/benchmarks.md differs from the result file; run tools/plot_benchmarks.py")
