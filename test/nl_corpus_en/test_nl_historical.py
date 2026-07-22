"""Historical references: Roman-numeral centuries, ab urbe condita, Olympiads,
Attic archonships, and the classical (raw-Latin) date-formula group flag.

Golds are hand-derived from the conventions each construction cites:

* a Roman-numeral century binds only when a century/millennium unit or a year
  marker sits beside it -- a bare or mis-placed numeral (``mix``, ``V for
  Vendetta``) never resolves;
* ab urbe condita is the Varronian epoch (AUC 1 = 753 BC, AUC 753 = 1 BC);
* Olympiad N is the 4-year span opening in Gregorian year 4N-779 at midsummer
  (Olympiad 1 = 776-772 BC); Olympiad 87.2 = 431 BC (the war's outbreak);
* an eponymous archon-year runs midsummer-to-midsummer (Eucleides = 403/402 BC);
* the raw-Latin a.d.-count formula is OFF unless ``enable=('classical',)``.
"""
from datetime import timedelta

import pytest

from chronologia import extract_timespan
from ._corpus import ANCHOR, AstroDate, parse, span, start, nomatch


# -- Roman-numeral centuries / millennia (context-gated) ------------------

@pytest.mark.parametrize("text,y", [
    ("the XII century", 1100), ("the XXI century", 2000),
    ("the IV century", 300), ("the XIX century", 1800),
    ("III millennium", 2000),
])
def test_roman_century_en(text, y):
    s = span(text)
    assert s.start.year == y
    assert parse(text)[1] == ""          # no stranded remainder


def test_roman_century_matches_arabic_reading():
    # the Roman-numeral surface resolves identically to the digit surface
    assert start("the XII century") == start("the 12th century")


# -- explicit Roman-numeral years ("anno MMXX", "year MMXX") --------------

@pytest.mark.parametrize("text,y", [
    ("anno MMXX", 2020), ("year MMXX", 2020),
    ("anno MCMLXXXIV", 1984),
])
def test_roman_year_en(text, y):
    assert start(text).year == y


# -- homograph guard: a numeral out of context NEVER binds ----------------

@pytest.mark.parametrize("text", [
    "mix it up", "V for Vendetta", "I love you", "let us mix",
    "plan C is best", "vitamin D",
    "X", "MMXX",              # bare, no gating neighbour -> never a value
])
def test_roman_confusables_do_not_bind(text):
    nomatch(text)


# -- ab urbe condita (Varronian epoch) ------------------------------------

@pytest.mark.parametrize("text,astro_year", [
    ("auc 1", -752),           # 753 BC
    ("753 ab urbe condita", 0),   # 1 BC (astronomical 0)
    ("AUC 753", 0),
    ("ab urbe condita 754", 1),   # AD 1
])
def test_ab_urbe_condita(text, astro_year):
    assert start(text).year == astro_year
    assert parse(text)[1] == ""


# -- Olympiads (776 BC epoch, 4-year span, midsummer) ---------------------

@pytest.mark.parametrize("text,astro_start,astro_end", [
    ("the first olympiad", -775, -771),      # 776-772 BC
    ("the third olympiad", -767, -763),      # 768-764 BC
    ("olympiad 87", -431, -427),             # 432-428 BC
])
def test_olympiad(text, astro_start, astro_end):
    s = span(text)
    assert s.start == AstroDate(astro_start, 7, 1)
    assert s.end == AstroDate(astro_end, 7, 1)


def test_olympiad_year_narrows_to_single_year():
    # Olympiad 87.2 == 431 BC (astronomical -430): the outbreak of the
    # Peloponnesian War, dated by Thucydides to this exact Olympiad-year.
    s = span("the 2nd year of the 87th olympiad")
    assert s.start == AstroDate(-430, 7, 1)
    assert s.end == AstroDate(-429, 7, 1)


# -- Attic eponymous archonships (attested only) --------------------------

@pytest.mark.parametrize("text,bc", [
    ("in the archonship of eucleides", 403),   # restoration of the democracy
    ("the archonship of solon", 594),
    ("archonship of pythodorus", 432),         # eve of the Peloponnesian War
    ("archon themistocles", 493),
])
def test_archonship(text, bc):
    s = span(text)
    assert s.start == AstroDate(-(bc - 1), 7, 1)
    assert s.end == AstroDate(-(bc - 1) + 1, 7, 1)


def test_unattested_archon_does_not_bind():
    # Pericles was never eponymous archon (he held the strategia), so the
    # registry has no entry and the phrase must not resolve to a year.
    nomatch("in the archonship of pericles")


# -- classical (raw-Latin) date-formula group flag ------------------------

def _d(y, m, dd):
    return AstroDate(y, m, dd)


@pytest.mark.parametrize("text,iso", [
    ("ante diem III kalendas apriles", (2017, 3, 30)),   # a.d. III Kal. Apr.
    ("ante diem IV idus martias", (2017, 3, 12)),        # a.d. IV Id. Mart.
    ("ante diem III kalends of april", (2017, 3, 30)),
])
def test_classical_formula_on(text, iso):
    r = extract_timespan(text, "en", ANCHOR, enable=("classical",))
    assert r is not None
    assert r[0].start == _d(*iso)


@pytest.mark.parametrize("text", [
    "ante diem III kalendas apriles",
    "ante diem IV idus martias",
])
def test_classical_formula_off_by_default(text):
    # the raw-Latin a.d.-count formula is gated OFF unless explicitly enabled
    assert extract_timespan(text, "en", ANCHOR) is None


def test_everyday_roman_surfaces_stay_on():
    # items 1-5 (centuries, AUC, Olympiads, archons) are unambiguous everyday
    # surfaces -- always on, no flag needed
    assert extract_timespan("the XII century", "en", ANCHOR) is not None
    assert extract_timespan("olympiad 87", "en", ANCHOR) is not None
