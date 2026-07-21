"""Cyclic year labels: the year-axis generalisation of ``cycles.DayCycle``.

Gold values (cited in ``chronologia/cycles.py``):

* Sexagenary/zodiac anchor: 1984 == jiazi (jia-zi) / rat, position 0
  (Wikipedia, "Sexagenary cycle").
* 2024-02-10 (Chinese New Year) onward == jia-chen / wood dragon; 2024-01-15
  (before that CNY) is still gui-mao / rabbit -- the boundary a naive
  ``gregorian_year % 12`` gets wrong.
* 2000 == geng-chen / golden dragon (same zodiac animal as 2024, different
  sexagenary term -- 12 and 60 don't share a period).
* Indiction of AD 2024: Jan-Aug == 2, Sept-Dec == 3 (the Constantinopolitan
  1-September edge); 2017 == 10 (Wikipedia's worked example).
"""
import pytest

from chronologia.astrodate import AstroDate
from chronologia.calendars import CalendarRangeError
from chronologia.cycles import YEAR_CYCLES, year_cycle_label, years_of

# --------------------------------------------------------------------------
# registry facts
# --------------------------------------------------------------------------

def test_sexagenary_is_60_term():
    assert YEAR_CYCLES["sexagenary"].length == 60
    assert len(set(YEAR_CYCLES["sexagenary"].names)) == 60


def test_chinese_zodiac_is_12_term():
    assert YEAR_CYCLES["chinese_zodiac"].length == 12
    assert YEAR_CYCLES["chinese_zodiac"].names[0] == "rat"


def test_indiction_is_15_term():
    assert YEAR_CYCLES["indiction"].length == 15
    assert YEAR_CYCLES["indiction"].names == tuple(str(n) for n in range(1, 16))


# --------------------------------------------------------------------------
# sexagenary / zodiac golds
# --------------------------------------------------------------------------

def test_1984_is_jiazi_rat():
    assert year_cycle_label(AstroDate(1984, 6, 1), "sexagenary") == "jia-zi"
    assert year_cycle_label(AstroDate(1984, 6, 1), "chinese_zodiac") == "rat"


def test_2024_after_cny_is_jiachen_dragon():
    assert year_cycle_label(AstroDate(2024, 2, 10), "sexagenary") == "jia-chen"
    assert year_cycle_label(AstroDate(2024, 2, 10), "chinese_zodiac") == "dragon"
    assert year_cycle_label(AstroDate(2024, 6, 1), "chinese_zodiac") == "dragon"


def test_2024_before_cny_is_still_guimao_rabbit():
    # 2024-01-15 precedes Chinese New Year 2024-02-10: still the rabbit
    # year, gui-mao -- THE test a naive gregorian_year % 12 fails.
    assert year_cycle_label(AstroDate(2024, 1, 15), "sexagenary") == "gui-mao"
    assert year_cycle_label(AstroDate(2024, 1, 15), "chinese_zodiac") == "rabbit"


def test_day_before_cny_2024_boundary():
    assert year_cycle_label(AstroDate(2024, 2, 9), "chinese_zodiac") == "rabbit"
    assert year_cycle_label(AstroDate(2024, 2, 10), "chinese_zodiac") == "dragon"


def test_2000_is_gengchen_golden_dragon():
    assert year_cycle_label(AstroDate(2000, 6, 1), "sexagenary") == "geng-chen"
    assert year_cycle_label(AstroDate(2000, 6, 1), "chinese_zodiac") == "dragon"


# --------------------------------------------------------------------------
# cycle arithmetic over centuries
# --------------------------------------------------------------------------

def test_sexagenary_repeats_every_60_native_years():
    cycle = YEAR_CYCLES["sexagenary"]
    assert cycle.name_at(1984) == cycle.name_at(1984 + 60) == cycle.name_at(1984 - 60)
    assert cycle.name_at(1864) == "jia-zi"           # two cycles before 1984
    assert cycle.name_at(2104) == "jia-zi"           # two cycles after 1984


def test_zodiac_repeats_every_12_native_years():
    cycle = YEAR_CYCLES["chinese_zodiac"]
    for offset in (-120, -12, 0, 12, 120):
        assert cycle.name_at(1984 + offset) == "rat"


def test_zodiac_and_sexagenary_share_animal_every_60_but_not_12():
    # 2000 and 2024 are both dragon years (12 apart is not enough in
    # general -- they happen to be a multiple of 12 apart here -- but they
    # carry different sexagenary terms since 24 is not a multiple of 60.
    assert (YEAR_CYCLES["chinese_zodiac"].name_at(2000)
            == YEAR_CYCLES["chinese_zodiac"].name_at(2024) == "dragon")
    assert (YEAR_CYCLES["sexagenary"].name_at(2000)
            != YEAR_CYCLES["sexagenary"].name_at(2024))


def test_indiction_repeats_every_15_years():
    cycle = YEAR_CYCLES["indiction"]
    assert cycle.name_at(2024) == cycle.name_at(2024 + 15) == cycle.name_at(2024 - 15)


def test_indiction_2017_is_10():
    # Wikipedia's own worked example: (2017 + 3) mod 15 == 10.
    assert year_cycle_label(AstroDate(2017, 5, 1), "indiction") == "10"


# --------------------------------------------------------------------------
# indiction: the September year-start edge
# --------------------------------------------------------------------------

def test_indiction_2024_january_to_august_is_2():
    for month, day in ((1, 1), (5, 7), (8, 31)):
        assert year_cycle_label(AstroDate(2024, month, day), "indiction") == "2"


def test_indiction_2024_september_to_december_is_3():
    for month, day in ((9, 1), (10, 1), (12, 31)):
        assert year_cycle_label(AstroDate(2024, month, day), "indiction") == "3"


def test_indiction_august_vs_october_same_gregorian_year_differ():
    august = year_cycle_label(AstroDate(2024, 8, 15), "indiction")
    october = year_cycle_label(AstroDate(2024, 10, 15), "indiction")
    assert august != october
    assert (august, october) == ("2", "3")


def test_indiction_day_before_september_boundary():
    assert year_cycle_label(AstroDate(2024, 8, 31), "indiction") == "2"
    assert year_cycle_label(AstroDate(2024, 9, 1), "indiction") == "3"


# --------------------------------------------------------------------------
# years_of: "which recent years were dragon years"
# --------------------------------------------------------------------------

def test_years_of_dragon_years_gold():
    spans = years_of("chinese_zodiac", "dragon", 1990, 2025)
    assert [start.year for start, end in spans] == [2000, 2012, 2024]


def test_years_of_dragon_year_spans_start_at_chinese_new_year():
    spans = years_of("chinese_zodiac", "dragon", 2024, 2024)
    (start, end), = spans
    assert (start.year, start.month, start.day) == (2024, 2, 10)
    assert start < end


def test_years_of_rat_years_include_1984():
    spans = years_of("chinese_zodiac", "rat", 1980, 1990)
    assert [s.year for s, _ in spans] == [1984]


def test_years_of_indiction_spans_tile_at_september():
    # indiction-2 (2024) should run from 1 Sept 2023 to 1 Sept 2024.
    (start, end), = years_of("indiction", "2", 2024, 2024)
    assert (start.year, start.month, start.day) == (2023, 9, 1)
    assert (end.year, end.month, end.day) == (2024, 9, 1)


def test_years_of_empty_when_no_year_in_range_matches():
    assert years_of("chinese_zodiac", "dragon", 2001, 2011) == []


# --------------------------------------------------------------------------
# adversarial
# --------------------------------------------------------------------------

def test_unknown_cycle_key_raises():
    with pytest.raises(KeyError):
        year_cycle_label(AstroDate(2024, 1, 1), "aztec_tonalpohualli")
    with pytest.raises(KeyError):
        years_of("aztec_tonalpohualli", "dragon", 2000, 2010)


def test_unknown_name_in_known_cycle_raises():
    with pytest.raises(ValueError):
        years_of("chinese_zodiac", "unicorn", 2000, 2010)
    with pytest.raises(ValueError):
        years_of("sexagenary", "rat", 2000, 2010)     # zodiac name, wrong cycle


def test_sexagenary_out_of_table_range_raises_calendar_range_error():
    # the Chinese calendar table covers lunar years 1901..2099
    with pytest.raises(CalendarRangeError):
        year_cycle_label(AstroDate(1500, 1, 1), "sexagenary")
    with pytest.raises(CalendarRangeError):
        year_cycle_label(AstroDate(2200, 1, 1), "chinese_zodiac")


def test_indiction_never_raises_calendar_range_error():
    # indiction is not calendar-backed: any Gregorian year resolves.
    assert year_cycle_label(AstroDate(500, 1, 1), "indiction") is not None
    assert year_cycle_label(AstroDate(3000, 1, 1), "indiction") is not None


def test_name_at_and_year_cycle_label_agree():
    cycle = YEAR_CYCLES["chinese_zodiac"]
    moment = AstroDate(2024, 6, 1)
    assert year_cycle_label(moment, cycle) == cycle.name_at(cycle.native_year(moment))
