"""Eponym tables: Roman consular years (a RegnalSequence) and the Olympiad
era (a 4-year-cycle era with a midsummer year-start).

Gold values ported from the reckoning-core assertions the parser exercised
through its eponym engine stage, rewritten against ``RegnalSequence.
year_span`` and ``resolve_era_year_span`` directly.  The consul-pair and
Olympiad vocabulary surfaces ("the consulship of ...") are parser-side; the
year spans and era facts are the core (BC years astronomical: 59 BC == -58).
"""
from chronologia.astrodate import AstroDate
from chronologia.eras import ERAS, resolve_era_year_span
from chronologia.regnal import REGNAL_SEQUENCES

CONSULS = REGNAL_SEQUENCES["consuls"]


# -- consular years: one-year spans on the 1 January year label ----------

def test_consulship_of_caesar_and_bibulus_is_59_bc():
    assert CONSULS.year_span("caesar_bibulus", 1) == (AstroDate(-58, 1, 1),
                                                      AstroDate(-57, 1, 1))


def test_consulship_of_cicero_is_63_bc():
    start, _ = CONSULS.year_span("cicero_hybrida", 1)
    assert start == AstroDate(-62, 1, 1)


def test_consulship_of_vespasian_is_ad_70():
    assert CONSULS.year_span("vespasian_titus", 1) == (AstroDate(70, 1, 1),
                                                       AstroDate(71, 1, 1))


def test_consuls_dataset_is_a_dozen():
    assert len(CONSULS.segments) == 12


# -- Olympiad era: 4-year cycle, midsummer year-start --------------------

def test_first_olympiad_is_776_bc_midsummer():
    start, end = resolve_era_year_span("olympiad", 1)
    assert start == AstroDate(-775, 7, 1)            # 776 BC, 1 July
    assert end == AstroDate(-771, 7, 1)             # four years wide


def test_olympiad_span_is_four_years():
    start, end = resolve_era_year_span("olympiad", 699)
    assert start == AstroDate(2017, 7, 1)
    assert end == AstroDate(2021, 7, 1)


def test_olympiad_era_facts():
    assert ERAS["olympiad"].year_length == 4
    assert ERAS["olympiad"].year_start == (7, 1)
