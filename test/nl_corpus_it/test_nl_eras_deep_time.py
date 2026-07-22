"""Italian eras and deep time: BC/AD ("avanti/dopo Cristo", "a.c./d.c."),
the "l'anno" year reference, and "N milioni/miliardi di anni fa"."""
import pytest

from ._corpus import span, start, nomatch

_BP_EPOCH = 1950


@pytest.mark.parametrize("text,year", [
    ("44 a.c.", -43),
    ("44 avanti cristo", -43),
    ("753 a.c.", -752),
    ("2020 dopo cristo", 2020),
    ("2020 d.c.", 2020),
])
def test_era_year(text, year):
    assert start(text).year == year


def test_bc_is_year_wide():
    s = span("44 a.c.")
    assert s.end.year - s.start.year == 1


@pytest.mark.parametrize("text,year", [
    ("nell'anno 2000", 2000),
    ("l'anno 1789", 1789),
])
def test_year_reference(text, year):
    assert start(text).year == year


@pytest.mark.parametrize("text,years_ago", [
    ("66 milioni di anni fa", 66_000_000),
    ("4 miliardi di anni fa", 4_000_000_000),
    ("250 milioni di anni fa", 250_000_000),
])
def test_deep_time(text, years_ago):
    assert start(text).year == _BP_EPOCH - years_ago


def test_deep_time_needs_marker():
    nomatch("66 milioni di anni")
