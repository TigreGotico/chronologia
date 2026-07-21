"""Eponym tables: Roman consular years (a RegnalSequence) and the Olympiad
era (a 4-year-cycle era with a midsummer year-start).

A small demonstrative dataset proving the mechanism -- "the consulship of
<pair>" resolves to that consular year's span, and the Olympiad era uses
item 4's year-span machinery with year_length 4.  Values follow the
downloaded fasti and Olympiad references."""
import pytest
from engine_helpers import ANCHOR, zz_engine

from chronologia.astrodate import AstroDate
from chronologia.eras import ERAS, resolve_era_year_span
from chronologia.regnal import REGNAL_SEQUENCES


def _one(text):
    res = zz_engine().resolve(text, ANCHOR)
    assert len(res) == 1, f"{text!r} -> {res}"
    return res[0]


# -- "the consulship of <pair>" -> that year's span ------------------------

def test_consulship_of_caesar_and_bibulus_is_59_bc():
    r = _one("zconsulship zof zcaesarbibulus")
    assert r.value.start == AstroDate(-58, 1, 1)         # 59 BC (astronomical)
    assert r.value.end == AstroDate(-57, 1, 1)           # one-year span

def test_consulship_of_cicero_is_63_bc():
    assert _one("zconsulship zof zcicero").value.start == AstroDate(-62, 1, 1)

def test_consulship_of_vespasian_is_ad_70():
    r = _one("zconsulship zof zvespasian")
    assert r.value.start == AstroDate(70, 1, 1)
    assert r.value.end == AstroDate(71, 1, 1)


# -- Olympiad era: 4-year cycle, midsummer year-start ----------------------

def test_first_olympiad_is_776_bc_midsummer():
    start, end = resolve_era_year_span("olympiad", 1)
    assert start == AstroDate(-775, 7, 1)                # 776 BC, 1 July
    assert end == AstroDate(-771, 7, 1)                  # four years wide

def test_olympiad_span_is_four_years():
    start, end = resolve_era_year_span("olympiad", 699)
    assert start == AstroDate(2017, 7, 1)
    assert end == AstroDate(2021, 7, 1)

def test_olympiad_era_facts():
    assert ERAS["olympiad"].year_length == 4
    assert ERAS["olympiad"].year_start == (7, 1)


# -- dataset stays small (demonstrative) -----------------------------------

def test_consuls_dataset_is_a_dozen():
    assert len(REGNAL_SEQUENCES["consuls"].segments) == 12


# -- adversarial -----------------------------------------------------------

def test_unknown_consul_never_raises():
    zz_engine().resolve("zconsulship zof zzz", ANCHOR)
