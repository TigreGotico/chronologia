"""Italy national differential + regional-capital patron behaviour.

Source: Legge 27 maggio 1949, n. 260 (papers/holidays/it_holidays.md). Per-holiday
gold dates live in the shared HOLIDAY_GOLDS registry (test_holiday_golds.py); this
module owns the national differential against the independent reference package
and the municipal patron-saint behaviour.

Documented differential (reference lists, we deliberately omit):

* ref-only, first Sunday of November each year (2023-11-05, 2024-11-03,
  2025-11-02): the "Giornata dell'Unità Nazionale e delle Forze Armate", a solemn
  commemoration celebrated the first Sunday of November. It is NOT one of the
  twelve work-free civil festività listed by L. 260/1949, so we omit it while the
  reference includes it. This is the sole national disagreement.
"""
from chronologia import AstroDate, holidays_for
from holiday_testkit import assert_national_differential

_J = "IT"
_DISAGREEMENTS = {
    2023: {"ref_only": {(11, 5)}},
    2024: {"ref_only": {(11, 3)}},
    2025: {"ref_only": {(11, 2)}},
}


def test_national_differential_2023_2025():
    assert_national_differential(_J, (2023, 2024, 2025), _DISAGREEMENTS)


def test_national_set_has_twelve_festivita_2024():
    nat = [h for h in holidays_for(_J, 2024) if h.subdiv is None]
    assert len(nat) == 12


def test_rome_patron_santi_pietro_e_paolo_is_municipal():
    rome = holidays_for(_J, 2024, subdiv="IT-RM")
    hit = [h for h in rome if h.name == "Santi Pietro e Paolo"]
    assert hit and hit[0].date == AstroDate(2024, 6, 29)
    assert "municipal" in hit[0].categories
    # The patron day is scoped to its province, not nationwide.
    assert "Santi Pietro e Paolo" not in {h.name for h in holidays_for(_J, 2024)}


def test_milan_and_naples_have_distinct_patrons():
    mi = {h.name: h.date for h in holidays_for(_J, 2024, subdiv="IT-MI")}
    na = {h.name: h.date for h in holidays_for(_J, 2024, subdiv="IT-NA")}
    assert mi["Sant'Ambrogio"] == AstroDate(2024, 12, 7)
    assert na["San Gennaro"] == AstroDate(2024, 9, 19)
    assert "Sant'Ambrogio" not in na and "San Gennaro" not in mi
