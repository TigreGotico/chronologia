"""Tests for the ``python -m chronologia`` command line (via ``main()``)."""
import pytest

from chronologia.__main__ import main


def _run(capsys, argv):
    code = main(argv)
    out = capsys.readouterr().out
    return code, out


# -- convert ----------------------------------------------------------------
def test_convert_gregorian_to_hebrew(capsys):
    code, out = _run(capsys, ["convert", "2024-06-01", "--to", "hebrew"])
    assert code == 0
    assert "hebrew 5784" in out


def test_convert_from_julian_to_gregorian(capsys):
    code, out = _run(capsys, ["convert", "1752-09-02",
                              "--from", "julian", "--to", "gregorian"])
    assert code == 0
    assert out.startswith("julian 1752-09-02 = gregorian")


def test_convert_bc_year_with_separator(capsys):
    code, out = _run(capsys, ["convert", "--from", "julian", "--to",
                              "gregorian", "--", "-0043-03-15"])
    assert code == 0
    assert "gregorian -43-03-13" in out


def test_convert_unknown_source_calendar(capsys):
    code, out = _run(capsys, ["convert", "2024-06-01",
                              "--from", "nope", "--to", "hebrew"])
    assert code == 2
    assert "unknown source calendar" in out


def test_convert_unknown_target_calendar(capsys):
    code, out = _run(capsys, ["convert", "2024-06-01", "--to", "nope"])
    assert code == 2
    assert "unknown target calendar" in out


def test_convert_bad_date_raises(capsys):
    with pytest.raises(ValueError):
        main(["convert", "not-a-date-here-xyz", "--to", "hebrew"])


# -- extract ----------------------------------------------------------------
def test_extract_finds_span(capsys):
    code, out = _run(capsys, ["extract", "june 1984"])
    assert code == 0
    assert "1984-06-01" in out


def test_extract_reports_no_match(capsys):
    code, out = _run(capsys, ["extract", "asdfghjkl qwerty"])
    assert code == 0
    assert "no date found" in out


def test_extract_lang_flag(capsys):
    code, out = _run(capsys, ["extract", "in 2024", "--lang", "en-us"])
    assert code == 0
    assert "2024-01-01" in out


# -- holidays ---------------------------------------------------------------
def test_holidays_lists_new_year(capsys):
    code, out = _run(capsys, ["holidays", "US", "2024"])
    assert code == 0
    assert "2024-01-01" in out
    assert "New Year" in out


def test_holidays_unknown_jurisdiction(capsys):
    code, out = _run(capsys, ["holidays", "ZZ", "2024"])
    assert code == 2
    assert "no holiday data" in out


# -- easter -----------------------------------------------------------------
def test_easter_gregorian(capsys):
    code, out = _run(capsys, ["easter", "2024"])
    assert code == 0
    assert "2024-03-31" in out


def test_easter_method_flag(capsys):
    code, out = _run(capsys, ["easter", "2024", "--method", "gregorian"])
    assert code == 0
    assert "2024-03-31" in out


# -- when (EDTF) ------------------------------------------------------------
def test_when_resolves_month(capsys):
    code, out = _run(capsys, ["when", "1984-06"])
    assert code == 0
    assert "1984-06-01" in out and "1984-07-01" in out


def test_when_uncertain_qualifier(capsys):
    code, out = _run(capsys, ["when", "1984?"])
    assert code == 0
    assert "[?]" in out


def test_when_invalid_edtf(capsys):
    code, out = _run(capsys, ["when", "!!!not-edtf!!!"])
    assert code == 2
    assert "could not parse" in out


# -- top level --------------------------------------------------------------
def test_no_command_errors(capsys):
    with pytest.raises(SystemExit):
        main([])
