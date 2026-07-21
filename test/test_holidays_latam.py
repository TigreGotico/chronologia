"""Latin America national differentials (MX / AR / CL / CO / PE / UY).

Per-holiday gold dates live in the shared HOLIDAY_GOLDS registry
(test_holiday_golds.py). This module carries the national public differential
against vacanza/holidays, year by year.

Adjudications
-------------
* MX / AR / CL / CO / PE: clean for 2023-2025. Mexico's art.74 Monday-moving
  holidays and Colombia's Emiliani next-Monday holidays resolve to the same
  moved dates the reference gives (chronologia models them as nth_weekday /
  weekday_onafter / exact Easter offsets rather than shifts, so no nominal
  duplicate is emitted). Chile's traslado / solstice / one-off feriados and
  Argentina's trasladables + tourism bridges are decree-tabulated to the
  gazetted dates.
* UY: four our-only rows — Carnaval (Mon/Tue before Ash Wednesday) and Semana
  de Turismo (Holy Thursday/Friday). These are Uruguayan "feriados no
  laborables" under Ley 16.805 art.18; the reference carries only the five
  "laborables", so they are documented our-only additions (they exercise the
  southern-hemisphere Easter offsets).
"""
import os

import pytest

from chronologia import AstroDate, holidays_for
from chronologia.civil_holidays import _DATA_DIR
from holiday_testkit import assert_national_differential

_CLEAN = {}


def _have(cc):
    return os.path.exists(os.path.join(_DATA_DIR, f"{cc.lower()}.tab"))


@pytest.mark.skipif(not _have("MX"), reason="mx.tab not present")
def test_mx_differential():
    assert_national_differential("MX", (2023, 2024, 2025), _CLEAN)


@pytest.mark.skipif(not _have("AR"), reason="ar.tab not present")
def test_ar_differential():
    assert_national_differential("AR", (2023, 2024, 2025), _CLEAN)


@pytest.mark.skipif(not _have("CL"), reason="cl.tab not present")
def test_cl_differential():
    assert_national_differential("CL", (2023, 2024, 2025), _CLEAN)


@pytest.mark.skipif(not _have("CO"), reason="co.tab not present")
def test_co_differential():
    assert_national_differential("CO", (2023, 2024, 2025), _CLEAN)


@pytest.mark.skipif(not _have("PE"), reason="pe.tab not present")
def test_pe_differential():
    assert_national_differential("PE", (2023, 2024, 2025), _CLEAN)


@pytest.mark.skipif(not _have("UY"), reason="uy.tab not present")
def test_uy_differential():
    def carnaval_turismo(year):
        from chronologia.computus import easter
        from datetime import timedelta
        e = easter(year, "gregorian")
        return {((e + timedelta(days=o)).month, (e + timedelta(days=o)).day)
                for o in (-48, -47, -3, -2)}
    dis = {y: {"our_only": carnaval_turismo(y)} for y in (2023, 2024, 2025)}
    assert_national_differential("UY", (2023, 2024, 2025), dis)


@pytest.mark.skipif(not _have("CO"), reason="co.tab not present")
def test_co_emiliani_moves_to_next_monday():
    """Reyes Magos: unmoved when 6 Jan is a Monday (2025), else next Monday."""
    d = lambda y: {h.name: h.date for h in holidays_for("CO", y)}
    assert d(2024)["Día de los Reyes Magos"] == AstroDate(2024, 1, 8)   # Sat->Mon
    assert d(2025)["Día de los Reyes Magos"] == AstroDate(2025, 1, 6)   # already Mon
