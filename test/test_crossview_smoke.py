"""The cross-view harness runs end to end and normalises results exactly."""
import pytest

from benchmark.crossview import (ANCHORS, SEEDS, VIEWS, MODES, diff, disagreements,
                                 grid_inputs, read_rows, run, write_rows)

INPUTS = set(SEEDS) | {("en", "tomorrow"), ("en", "every friday"),
                       ("en", "the 30th of february"), ("en", "next friday"),
                       ("en", "every easter"), ("en", "no date here"),
                       ("en", "lunch every friday at noon for 2 hours"),
                       ("en", "monday to friday")}
WHEN = "2026-11-22T09:00"


@pytest.fixture(scope="module")
def rows():
    return run(INPUTS, ANCHORS[:1])


def test_exact_normalised_values(rows):
    got = {row[:5]: row[5] for row in rows}
    assert got[("en", "tomorrow", "timespan", "none", WHEN)] == \
        "2026-11-23T00:00:00/2026-11-24T00:00:00 exact | "
    assert got[("en", "every friday", "recurrence", "none", WHEN)] == \
        "FREQ=WEEKLY;BYDAY=FR | "
    assert got[("en", "the 30th of february", "event", "raise", WHEN)] == \
        "raise February has no 30th | en | the 30th of february"
    assert got[("en", "next friday", "candidates", "none", WHEN)] == \
        ("2026-11-27T00:00:00/2026-11-28T00:00:00 exact |  | weekday_ref | 0.8833 ; "
         "2026-11-27T00:00:00/2026-11-28T00:00:00 exact | next | weekday_ref | 0.4417")
    assert got[("en", "lunch every friday at noon for 2 hours", "event", "none", WHEN)] == \
        ("lunch | 2026-11-27T12:00:00/2026-11-27T14:00:00 exact | 2:00:00 | "
         "FREQ=WEEKLY;BYDAY=FR;BYHOUR=12 | 1.0000")
    assert got[("en", "every easter", "recurrence", "none", WHEN)].startswith(
        "error ValueError holiday recurrence 'easter' is a movable feast with no RFC 5545 RRULE")
    assert got[("en", "the 30th of february", "event", "none", WHEN)] == "none"


def test_run_is_sorted_with_one_row_per_call(rows):
    assert len(rows) == len(INPUTS) * len(VIEWS) * len(MODES)
    assert rows == sorted(rows, key=lambda row: row[:5])


def test_seeded_rows_are_reported_as_disagreements(rows):
    found = disagreements([row for row in rows if (row[0], row[1]) in SEEDS])
    listed = {text for keys in found.values() for _, text, _ in keys}
    assert listed == {text for _, text in SEEDS}


def test_diff_reports_duplicate_and_missing_rows(rows, capsys):
    assert diff(rows, rows + rows[:1], 5) == 1
    out = capsys.readouterr().out
    assert f"{len(rows)} in, {len(rows) + 1} out" in out
    assert "0 duplicate keys in base, 1 in head" in out
    assert diff(rows, rows[1:], 5) == 1
    out = capsys.readouterr().out
    assert f"{len(rows)} in, {len(rows) - 1} out" in out
    assert "1 rows only in base" in out


def test_diff_counts_and_classes(rows, tmp_path, capsys):
    head = [row[:5] + ("none",) + row[6:] if row[2] == "timespan" and row[3] == "none"
            and row[1] == "tomorrow" else row for row in rows]
    path = tmp_path / "base.tsv"
    write_rows(str(path), rows)
    assert read_rows([str(path)]) == rows
    assert diff(rows, head, 5) == 1
    out = capsys.readouterr().out
    assert out.startswith(f"{len(rows)} in, {len(rows)} out\n")
    assert "timespan none read>none: 1" in out


def test_grid_covers_the_bound_languages():
    langs = {lang for lang, _ in grid_inputs()}
    assert {"en", "pt", "es", "de", "fr", "it", "nl", "ca", "gl"} <= langs
