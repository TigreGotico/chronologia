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

import pytest

from chronologia.civil_holidays import _DATA_DIR
from holiday_testkit import assert_national_differential


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
