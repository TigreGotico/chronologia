# -*- coding: utf-8 -*-
"""Greece national differential — the Orthodox-Easter computus meets its users.

Source: Ν. 4808/2021 / Β.Δ. 748/1966 (papers/holidays/gr_holidays.md). Per-holiday
gold dates live in the shared HOLIDAY_GOLDS registry (test_holiday_golds.py); this
module owns the national differential against the independent reference package
and the Orthodox-Easter behavioural checks.

Every Easter-relative Greek holiday is reckoned on the ORTHODOX (Julian) computus
via method='julian_gregorian_date'. This is the interesting differential: our
Orthodox computus vs the reference package's own Orthodox-Easter code. They agree
to the day across 2023-2025 (Clean Monday, Good Friday, Easter Monday, Holy
Spirit), so the only disagreement is a one-year civil decree:

* 2024 our-only 1 May / ref-only 7 May: Εργατική Πρωτομαγιά (Labour Day) is
  statutorily 1 May, but in 2024 it collided with Orthodox Holy Week (Orthodox
  Easter 5 May), so the government relocated its observance to Tuesday 7 May by
  annual ministerial decision. We keep the statutory 1 May date and document the
  reference's decree relocation. 2023 and 2025 (Labour Day on 1 May) agree.
"""
from chronologia import AstroDate, holidays_for
from chronologia.computus import easter
from datetime import timedelta
from holiday_testkit import assert_national_differential

_J = "GR"
_DISAGREEMENTS = {
    2024: {"our_only": {(5, 1)}, "ref_only": {(5, 7)}},
}


def test_national_differential_2023_2025():
    assert_national_differential(_J, (2023, 2024, 2025), _DISAGREEMENTS)


def test_orthodox_easter_2024_flows_through_computus():
    # Orthodox Easter 2024 is 5 May; verify each derived movable day.
    dates = {h.name: h.date for h in holidays_for(_J, 2024)}
    assert dates["Καθαρά Δευτέρα"] == AstroDate(2024, 3, 18)       # -48
    assert dates["Μεγάλη Παρασκευή"] == AstroDate(2024, 5, 3)      # -2
    assert dates["Δευτέρα του Πάσχα"] == AstroDate(2024, 5, 6)     # +1
    assert dates["Δευτέρα του Αγίου Πνεύματος"] == AstroDate(2024, 6, 24)  # +50


def test_uses_orthodox_not_western_easter():
    # Western Easter 2024 is 31 Mar; Orthodox is 5 May. Greek Good Friday lands on
    # the Orthodox one (3 May), proving the julian_gregorian_date method is used —
    # the Western Good Friday would be 29 Mar.
    assert easter(2024, "julian_gregorian_date").date() != \
        easter(2024, "gregorian").date()
    gf = {h.name: h.date for h in holidays_for(_J, 2024)}["Μεγάλη Παρασκευή"]
    assert gf == AstroDate(2024, 5, 3)
    assert gf != AstroDate(2024, 3, 29)
