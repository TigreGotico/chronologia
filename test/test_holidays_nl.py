"""Netherlands national differential + Koningsdag shift (source: Rijksoverheid).

Per-holiday gold dates live in the shared HOLIDAY_GOLDS registry. The only
documented disagreement is Bevrijdingsdag (5 May): a national commemoration every
year but a work-free day only every five years (lustrum). The reference lists it
in 2025 (80th anniversary) only, which we do not model as a recurring holiday.
"""
from chronologia import AstroDate, holidays_for
from holiday_testkit import assert_national_differential

_J = "NL"
_DISAGREEMENTS = {
    2025: {"ref_only": {(5, 5)}},   # Bevrijdingsdag lustrum year
}


def test_national_differential_2023_2025():
    assert_national_differential(_J, (2023, 2024, 2025), _DISAGREEMENTS)


def test_koningsdag_normal_and_sunday_shift():
    # 2024: 27 Apr is a Saturday -> stays 27 Apr.
    d2024 = {h.name: h.date for h in holidays_for(_J, 2024)}["Koningsdag"]
    assert d2024 == AstroDate(2024, 4, 27)
    # 2025: 27 Apr is a Sunday -> brought forward to Saturday 26 Apr.
    d2025 = {h.name: h.date for h in holidays_for(_J, 2025)}["Koningsdag"]
    assert d2025 == AstroDate(2025, 4, 26)
