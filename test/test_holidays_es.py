"""Spain national traslado + autonomous-community layer (source: BOE resolutions).

Per-holiday gold dates for ES live in the shared HOLIDAY_GOLDS registry
(test_holiday_golds.py); the regional golds are parsed there from the four cited
BOE "relación de fiestas laborales" tables (2023-2026).

National Sunday traslado (Estatuto art. 37.2): a national fiesta falling on a
Sunday is moved to the following Monday (modelled with the sun_mon shift). This
reproduces every BOE "Lunes siguiente a ..." national entry 2023-2026. The
vacanza/holidays reference package instead DROPS a Sunday national holiday, so the
BOE-shifted Mondays are documented our-only differential entries (we follow the
primary source; accuracy over parity):

* 2023 our-only 2 Jan: Año Nuevo (Sun 1 Jan) shifted to Mon 2 Jan per BOE.
* 2024 our-only 9 Dec: Inmaculada Concepción (Sun 8 Dec) shifted to Mon 9 Dec.
* 2025 our-only 13 Oct: Fiesta Nacional (Sun 12 Oct) shifted to Mon 13 Oct.
* 2026 our-only 2 Nov + 7 Dec: Todos los Santos (Sun 1 Nov) and Día de la
  Constitución (Sun 6 Dec) shifted to the following day per BOE.
"""
from chronologia import AstroDate, holidays_for
from holiday_testkit import assert_national_differential

_J = "ES"
_DISAGREEMENTS = {
    2023: {"our_only": {(1, 2)}},
    2024: {"our_only": {(12, 9)}},
    2025: {"our_only": {(10, 13)}},
    2026: {"our_only": {(11, 2), (12, 7)}},
}


def test_national_differential_2023_2026():
    assert_national_differential(_J, (2023, 2024, 2025, 2026), _DISAGREEMENTS)


def test_national_sunday_traslado_shifts_to_monday():
    # Inmaculada Concepción 2024: nominal 8 Dec is a Sunday -> observed 9 Dec.
    got = {h.name: h.date for h in holidays_for(_J, 2024) if h.subdiv is None}
    assert got["Inmaculada Concepción"] == AstroDate(2024, 12, 9)
    # A weekday national holiday is unshifted.
    assert got["Fiesta del Trabajo"] == AstroDate(2024, 5, 1)


def test_regional_layer_present_for_all_communities():
    codes = ["ES-AN", "ES-AR", "ES-AS", "ES-IB", "ES-CN", "ES-CB", "ES-CM",
             "ES-CL", "ES-CT", "ES-EX", "ES-GA", "ES-MD", "ES-MC", "ES-NC",
             "ES-PV", "ES-RI", "ES-VC", "ES-CE", "ES-ML"]
    for code in codes:
        regional = [h for h in holidays_for(_J, 2024, subdiv=code)
                    if h.subdiv == code]
        assert regional, f"no 2024 regional holiday for {code}"


def test_regional_own_day_traslado_merged():
    # Día de Asturias fell on Sunday 8 Sep 2024 -> BOE moved it to Mon 9 Sep.
    asturias = {h.name: h.date for h in holidays_for(_J, 2024, subdiv="ES-AS")
                if h.subdiv == "ES-AS"}
    assert asturias["Día de Asturias"] == AstroDate(2024, 9, 9)


def test_catalonia_sant_esteve_every_year():
    for year in (2023, 2024, 2025, 2026):
        ct = {(h.name, h.date) for h in holidays_for(_J, year, subdiv="ES-CT")}
        assert ("San Esteban", AstroDate(year, 12, 26)) in ct
