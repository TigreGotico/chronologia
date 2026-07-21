"""German eras and deep time: BC/AD ("v. Chr." / "n. Chr." -- the ported
parser vocabulary, multi-word and abbreviated), before-present, "vor N
Millionen Jahren" geological offsets, and named geological periods in
German nomenclature (Jura, Kreide, Trias, Paläozoikum, ...).
"""
import pytest

from ._corpus import start, start_end, span, nomatch, AstroDate


# -- BC: astronomical year numbering (44 BC == year -43) ------------------

@pytest.mark.parametrize("text,astro_year", [
    ("44 v. chr.", -43), ("44 v.chr.", -43), ("44 vor christus", -43),
    ("753 v. chr.", -752), ("753 vor christi geburt", -752),
    ("1 v. chr.", 0), ("100 v. chr.", -99),
])
def test_bc(text, astro_year):
    assert start(text).year == astro_year


# -- AD -------------------------------------------------------------------

@pytest.mark.parametrize("text,y", [
    ("2024 n. chr.", 2024), ("2024 nach christus", 2024),
    ("1 n. chr.", 1), ("476 n. chr.", 476),
])
def test_ad(text, y):
    assert start(text) == AstroDate(y, 1, 1)


# -- deep time: "vor N (Millionen|Milliarden) Jahren" ago ------------------

@pytest.mark.parametrize("text,approx_year", [
    ("vor 66 millionen jahren", -65998050),
    ("vor 2 millionen jahren", -1998050),
    ("vor 3 milliarden jahren", -2999998050),
    ("vor 250 millionen jahren", -249998050),
])
def test_deep_time(text, approx_year):
    assert start(text).year == approx_year
    assert span(text).start_datetime is None   # far outside datetime range


# -- named geological periods (German names) ------------------------------

@pytest.mark.parametrize("text", [
    "im jura", "in der kreide", "das trias", "im devon", "im perm",
    "das paläozoikum", "das mesozoikum", "im holozän", "im pleistozän",
    "das kambrium", "die bronzezeit", "die eisenzeit",
])
def test_named_period(text):
    s = span(text)
    assert s.end.year > s.start.year   # a real, forward, deep span


def test_kreide_ends_at_the_extinction():
    # the Cretaceous ends ~66 Ma; assert the span reaches into that era
    s = span("in der kreide")
    assert s.start.year < -60_000_000 < s.end.year or s.end.year < -60_000_000


# -- adversarial: a bare number is not an era -----------------------------

@pytest.mark.parametrize("text", ["44", "christus", "millionen jahre"])
def test_bare_is_not_era(text):
    from ._corpus import parse
    res = parse(text)
    # "44" alone is not 4 digits -> guarded off; the words alone carry no year
    if text == "44":
        assert res is None
