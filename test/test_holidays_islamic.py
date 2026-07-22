"""Islamic-calendar-breadth national differentials (EG / MA / PK / ID / MY).

Per-holiday gold dates live in the shared HOLIDAY_GOLDS registry
(test_holiday_golds.py), where the tabular-Hijri dates are re-derived by a
standalone arithmetic formula (independent of the engine). This module carries
the national public differential against vacanza/holidays, year by year.

Adjudication — the distribution of estimated-vs-tabulated disagreements
----------------------------------------------------------------------
chronologia resolves every Islamic holiday through the ARITHMETIC tabular Hijri
calendar (islamic_civil): a single deterministic model with no per-country moon
sighting. The reference package, and each country's actual observance, use
ASTRONOMICAL ESTIMATES / official sightings, so the two disagree on the Islamic
holidays by a small, bounded offset — almost always ±1 day, occasionally ±2 at
the far end of an Eid span. Every disagreement below is one of:

* Tabulated-vs-estimated Islamic offset (the dominant case): our arithmetic
  date sits ±1-2 days from the reference's estimate. e.g. every country's
  Islamic New Year (our tabular 8 Jul 2024 vs reference 7 Jul), Mawlid
  (16 Sep 2024 vs 15 Sep in EG/MA), Ashura (PK 17 Jul vs 15 Jul).
* Egypt-specific "يوم تعويضي" compensatory-day shifts: Egypt moves a holiday
  that lands on the Fri/Sat weekend to a compensating weekday, which
  chronologia does NOT model — so several EG civil days differ too (this makes
  Egypt by far the noisiest of the five).
* Reference-only "Cuti" / substitute leave days and one-off electoral or
  observed days that chronologia does not model (MY extra CNY/Raya leave days,
  ID election days already carried, etc.).
* Our-only Deepavali (MY): federally gazetted but placed at state level by the
  reference (11-12 2023, 10-31 2024, 10-20 2025).

The offsets are catalogued EXACTLY (not waved away) so the test fails if the
tabulated model ever drifts. The Eid al-Fitr first day, which the arithmetic
table happens to place on the same 10 Apr 2024 the whole region observed, is an
agreement and is absent below.
"""
import os
from datetime import timedelta

import pytest

from chronologia import AstroDate, holidays_for
from chronologia.civil_holidays import _DATA_DIR
from holiday_testkit import assert_national_differential


# ==========================================================================
# TR — the COUNTER-example to tabular routing. Turkey's two Islamic feasts are
# fixed years ahead by the Diyanet CALCULATED calendar and gazetted under Act
# 2429, so they are exact legal dates, NOT moon-sighting estimates. They are
# modelled as `decree` rows, not islamic_civil tabular routing. These golds are
# hand-typed from Turkey's official resmî tatil / Diyanet listings (2024-2027),
# NOT read from the .tab (independent witness), and assert the exact spans.
#
# Regression: the earlier islamic_civil routing emitted Kurban 2024 on
# 06-17..06-20 (off by +1) with a GAP at 06-16 (which Turkey actually observed)
# and a half-day eve stranded on 06-15 — a malformed span. Turkey observed
# Kurban Bayramı 2024 on 06-16..06-19. (Sources: takvim.com, momento.com.tr,
# vodafone.com.tr, turkcell.com.tr, yenisafak.com resmî-tatil listings.)
# --- Ramazan Bayramı (Eid al-Fitr): arefe half-day + 3 full days ---
_TR_RAMAZAN = {
    2024: (AstroDate(2024, 4, 9), AstroDate(2024, 4, 10)),
    2025: (AstroDate(2025, 3, 29), AstroDate(2025, 3, 30)),
    2026: (AstroDate(2026, 3, 19), AstroDate(2026, 3, 20)),
    2027: (AstroDate(2027, 3, 8), AstroDate(2027, 3, 9)),
}
# --- Kurban Bayramı (Eid al-Adha): arefe half-day + 4 full days ---
_TR_KURBAN = {
    2024: (AstroDate(2024, 6, 15), AstroDate(2024, 6, 16)),
    2025: (AstroDate(2025, 6, 5), AstroDate(2025, 6, 6)),
    2026: (AstroDate(2026, 5, 26), AstroDate(2026, 5, 27)),
    2027: (AstroDate(2027, 5, 15), AstroDate(2027, 5, 16)),
}


def _tr_feast(year, name):
    return sorted((h for h in holidays_for("TR", year) if h.name == name),
                  key=lambda h: h.date)


def _ymd(d):
    return (d.year, d.month, d.day)


@pytest.mark.skipif(not os.path.exists(os.path.join(_DATA_DIR, "tr.tab")),
                    reason="tr.tab not present")
@pytest.mark.parametrize("year", (2024, 2025, 2026, 2027))
def test_tr_ramazan_bayrami_gazette_span(year):
    eve_d, first_d = _TR_RAMAZAN[year]
    eve = _tr_feast(year, "Ramazan Bayramı (saat 13.00'ten)")
    assert [_ymd(h.date) for h in eve] == [_ymd(eve_d)]
    assert eve[0].span.width == timedelta(hours=12)          # half-day eve
    full = _tr_feast(year, "Ramazan Bayramı")
    expected = [first_d + timedelta(days=i) for i in range(3)]  # 3 full days
    assert [_ymd(h.date) for h in full] == [_ymd(e) for e in expected]
    assert eve_d + timedelta(days=1) == first_d              # eve abuts day 1, no gap


@pytest.mark.skipif(not os.path.exists(os.path.join(_DATA_DIR, "tr.tab")),
                    reason="tr.tab not present")
@pytest.mark.parametrize("year", (2024, 2025, 2026, 2027))
def test_tr_kurban_bayrami_gazette_span(year):
    eve_d, first_d = _TR_KURBAN[year]
    eve = _tr_feast(year, "Kurban Bayramı (saat 13.00'ten)")
    assert [_ymd(h.date) for h in eve] == [_ymd(eve_d)]
    assert eve[0].span.width == timedelta(hours=12)          # half-day eve
    full = _tr_feast(year, "Kurban Bayramı")
    expected = [first_d + timedelta(days=i) for i in range(4)]  # 4 CONTIGUOUS days
    assert [_ymd(h.date) for h in full] == [_ymd(e) for e in expected]
    assert eve_d + timedelta(days=1) == first_d              # eve abuts day 1, no gap


def test_tr_kurban_2024_regression_no_gap_no_offset():
    """Pin the exact bug: Kurban 2024 must be 06-16..06-19 (contiguous), NOT
    the old tabular 06-17..06-20 with a 06-16 gap."""
    dates = [h.date for h in _tr_feast(2024, "Kurban Bayramı")]
    assert dates == [AstroDate(2024, 6, 16), AstroDate(2024, 6, 17),
                     AstroDate(2024, 6, 18), AstroDate(2024, 6, 19)]
    assert AstroDate(2024, 6, 20) not in dates    # old tabular over-run gone
    # the day Turkey actually observed as day 1 is present (was the gap)
    assert AstroDate(2024, 6, 16) in dates


def _have(cc):
    return os.path.exists(os.path.join(_DATA_DIR, f"{cc.lower()}.tab"))


_EG_DIS = {
    2023: {"our_only": {(4, 23), (7, 1), (5, 1), (4, 25), (7, 19), (1, 7), (9, 27), (1, 25)},
           "ref_only": {(7, 20), (5, 4), (1, 8), (9, 28), (6, 27), (7, 3), (4, 21), (4, 24), (1, 26), (7, 2), (4, 27)}},
    2024: {"our_only": {(9, 16), (7, 23), (5, 1), (6, 19), (7, 8)},
           "ref_only": {(5, 5), (6, 15), (9, 15), (7, 25), (7, 11)}},
    2025: {"our_only": {(7, 23), (6, 9), (6, 30), (6, 27), (9, 5), (10, 6), (4, 1)},
           "ref_only": {(3, 30), (6, 5), (7, 3), (6, 26), (10, 9), (7, 24), (9, 4)}},
}
_MA_DIS = {
    2023: {"our_only": {(6, 30), (4, 23)}, "ref_only": {(4, 21), (6, 28)}},
    2024: {"our_only": {(6, 18), (9, 17), (7, 8)}, "ref_only": {(7, 7), (6, 16), (9, 15)}},
    2025: {"our_only": {(6, 8), (4, 1), (6, 27), (9, 6)}, "ref_only": {(6, 6), (3, 30), (6, 26), (9, 4)}},
}
_PK_DIS = {
    2023: {"our_only": {(9, 27)}, "ref_only": {(9, 29)}},
    2024: {"our_only": {(9, 16), (7, 17)}, "ref_only": {(7, 15), (9, 17)}},
    2025: {"our_only": {(9, 5)}, "ref_only": {(9, 4)}},
}
_ID_DIS = {
    2023: {"our_only": {(9, 27)}, "ref_only": {(9, 28)}},
    2024: {"our_only": {(7, 8), (2, 7)}, "ref_only": {(7, 7), (2, 8)}},
    2025: {"our_only": {(6, 7)}, "ref_only": {(6, 6)}},
}
_MY_DIS = {
    2023: {"our_only": {(9, 27), (11, 12)}, "ref_only": {(4, 21), (1, 24), (9, 28), (4, 24)}},
    2024: {"our_only": {(7, 8), (10, 31)}, "ref_only": {(2, 12), (7, 7)}},
    2025: {"our_only": {(10, 20)}, "ref_only": {(9, 1), (9, 15)}},
}


@pytest.mark.skipif(not _have("EG"), reason="eg.tab not present")
def test_eg_differential():
    assert_national_differential("EG", (2023, 2024, 2025), _EG_DIS)


@pytest.mark.skipif(not _have("MA"), reason="ma.tab not present")
def test_ma_differential():
    assert_national_differential("MA", (2023, 2024, 2025), _MA_DIS)


@pytest.mark.skipif(not _have("PK"), reason="pk.tab not present")
def test_pk_differential():
    assert_national_differential("PK", (2023, 2024, 2025), _PK_DIS)


@pytest.mark.skipif(not _have("ID"), reason="id.tab not present")
def test_id_differential():
    assert_national_differential("ID", (2023, 2024, 2025), _ID_DIS)


@pytest.mark.skipif(not _have("MY"), reason="my.tab not present")
def test_my_differential():
    assert_national_differential("MY", (2023, 2024, 2025), _MY_DIS)
