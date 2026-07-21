"""Egyptian civil calendar (the 365-day "vague year") and the New Kingdom
regnal chronology variants.

Sources:

* ``reingold_dershowitz_1990_calendrical_calculations.pdf`` -- Dershowitz &
  Reingold, "Calendrical Calculations", SP&E 20(9):899-928 (1990): the
  Egyptian calendar algorithm and the era-of-Nabonassar epoch (1 Thoth
  year 1 = JDN 1448638), cross-checked here against
  ``julian_to_jdn(-746, 2, 26) == 1448638``.
* Wikipedia's sourced per-ruler chronology sections (a mirror of the
  scholarly high/middle/low debate) for the ``egyptian_high`` /
  ``egyptian_middle`` / ``egyptian_low`` regnal-sequence gold values --
  see ``chronologia/regnal.py`` for the per-ruler citation notes. Ramesses
  II's triple (1304 / 1290 / 1279 BC) is the one directly and consistently
  attested by name across all three variants.
"""
import pytest

from chronologia.calendars import CALENDARS, jdn_to_julian
from chronologia.regnal import REGNAL_SEQUENCES


# -- Egyptian civil calendar -------------------------------------------------

def test_egyptian_epoch():
    c = CALENDARS["egyptian"]
    assert c.epoch_jdn == 1448638
    assert c.to_jdn(1, 1, 1) == 1448638
    # 1 Thoth year 1 (era of Nabonassar) == -746-02-26 proleptic Julian
    assert jdn_to_julian(c.epoch_jdn) == (-746, 2, 26)


def test_egyptian_no_leap_every_year_365_days():
    c = CALENDARS["egyptian"]
    for y in range(1, 2000):
        assert c.to_jdn(y + 1, 1, 1) - c.to_jdn(y, 1, 1) == 365


def test_egyptian_epagomenal_month_13_has_five_days():
    c = CALENDARS["egyptian"]
    assert c.from_jdn(c.to_jdn(5, 13, 5)) == (5, 13, 5)
    # sixth epagomenal day does not exist: (Y,13,5)+1 == (Y+1,1,1)
    assert c.to_jdn(5, 13, 5) + 1 == c.to_jdn(6, 1, 1)


def test_egyptian_epagomenal_day_6_is_a_different_year_not_a_valid_date():
    c = CALENDARS["egyptian"]
    # There is no "day 6" of month 13 -- the arithmetic silently rolls into
    # next year's Thoth 1, so round-tripping (Y, 13, 6) never returns
    # (Y, 13, 6); it normalizes to (Y+1, 1, 1).
    y, m, d = c.from_jdn(c.to_jdn(5, 13, 6))
    assert (y, m, d) != (5, 13, 6)
    assert (y, m, d) == (6, 1, 1)


@pytest.mark.parametrize("year,julian", [
    (1, (-746, 2, 26)),     # epoch, 1 Thoth year 1
    (2, (-745, 2, 26)),     # year 2: same Julian month/day (365 vs 365.25)
    # Sothic cycle: 1460 Egyptian vague years == 1461 Julian years, so
    # 1 Thoth year 1461 realigns to the same Julian calendar date as the
    # epoch, shifted 1460 Julian years later.
    (1461, (713, 2, 26)),
])
def test_egyptian_gold_conversions(year, julian):
    c = CALENDARS["egyptian"]
    assert jdn_to_julian(c.to_jdn(year, 1, 1)) == julian


def test_egyptian_round_trip_and_proleptic():
    c = CALENDARS["egyptian"]
    for jd in range(c.epoch_jdn - 30_000, c.epoch_jdn + 600_000, 13):
        y, m, d = c.from_jdn(jd)
        assert c.to_jdn(y, m, d) == jd
        assert 1 <= m <= 13 and 1 <= d <= 30


def test_egyptian_months_group_into_akhet_peret_shemu_thirds():
    # Akhet (Inundation) 1-4, Peret (Emergence) 5-8, Shemu (Harvest) 9-12;
    # month 13 is the epagomenal days, outside the season-thirds.
    c = CALENDARS["egyptian"]
    akhet_start = c.to_jdn(10, 1, 1)
    peret_start = c.to_jdn(10, 5, 1)
    shemu_start = c.to_jdn(10, 9, 1)
    epagomenal_start = c.to_jdn(10, 13, 1)
    assert peret_start - akhet_start == 4 * 30
    assert shemu_start - peret_start == 4 * 30
    assert epagomenal_start - shemu_start == 4 * 30


# -- New Kingdom regnal chronology: high / middle / low variants -----------

@pytest.mark.parametrize("variant,expected", [
    ("egyptian_high", (-1303, -1238)),     # 1304-1238 BC
    ("egyptian_middle", (-1289, -1224)),   # 1290-1224 BC
    ("egyptian_low", (-1278, -1213)),      # 1279-1213 BC
])
def test_ramesses_ii_year_5_per_variant(variant, expected):
    seq = REGNAL_SEQUENCES[variant]
    start, end = seq.year_span("ramesses_ii", 5)
    lo, hi = expected
    assert start.year == lo + 4
    assert end.year == lo + 5


def test_ramesses_ii_accession_diverges_by_over_20_years_high_vs_low():
    high = REGNAL_SEQUENCES["egyptian_high"]
    low = REGNAL_SEQUENCES["egyptian_low"]
    high_start, _ = high._bounds("ramesses_ii")
    low_start, _ = low._bounds("ramesses_ii")
    assert abs(high_start.year - low_start.year) >= 20
    # 1304 BC vs 1279 BC == astronomical years -1303 vs -1278
    assert high_start.year == -1303
    assert low_start.year == -1278


def test_ramesses_ii_middle_lies_between_high_and_low():
    high_start, _ = REGNAL_SEQUENCES["egyptian_high"]._bounds("ramesses_ii")
    mid_start, _ = REGNAL_SEQUENCES["egyptian_middle"]._bounds("ramesses_ii")
    low_start, _ = REGNAL_SEQUENCES["egyptian_low"]._bounds("ramesses_ii")
    # astronomical years: high (earliest calendar date) is most negative,
    # low (latest/closest to present) is least negative.
    assert high_start.year < mid_start.year < low_start.year


@pytest.mark.parametrize("variant", [
    "egyptian_high", "egyptian_middle", "egyptian_low",
])
def test_all_three_variants_share_the_same_ten_rulers(variant):
    names = [name for name, _ in REGNAL_SEQUENCES[variant].segments]
    assert names == [
        "ahmose_i", "amenhotep_i", "thutmose_i", "thutmose_iii",
        "amenhotep_ii", "amenhotep_iii", "akhenaten", "tutankhamun",
        "horemheb", "ramesses_ii",
    ]


def test_unknown_ruler_raises_key_error():
    seq = REGNAL_SEQUENCES["egyptian_low"]
    with pytest.raises(KeyError):
        seq.year_span("cleopatra_vii", 1)


def test_regnal_year_zero_and_negative_are_out_of_range():
    seq = REGNAL_SEQUENCES["egyptian_low"]
    assert seq.year_span("ramesses_ii", 0) is None
    assert seq.year_span("ramesses_ii", -1) is None


def test_regnal_year_far_past_reign_end_is_out_of_range():
    # Ramesses II is the open-ended final segment in these sequences, so an
    # absurdly large regnal year still resolves rather than raising -- but a
    # closed segment's successor bounds it. Use amenhotep_ii (bounded by
    # amenhotep_iii) to exercise the out-of-range clamp.
    seq = REGNAL_SEQUENCES["egyptian_low"]
    # amenhotep_ii: 1427-1391 BC == 36 regnal years; year 100 does not exist.
    assert seq.year_span("amenhotep_ii", 100) is None
