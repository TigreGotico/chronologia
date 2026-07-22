"""Belgium national differential (source: KB 18 April 1974).

Per-holiday gold dates live in the shared HOLIDAY_GOLDS registry. The 10 Belgian
legal holidays do not include Easter Sunday or Whit Sunday (both Sundays, not
distinct legal feestdagen); the reference package lists them, so each year shows
those two Sundays as ref-only:

* 2023: Easter Sun 9 Apr, Whit Sun 28 May.
* 2024: Easter Sun 31 Mar, Whit Sun 19 May.
* 2025: Easter Sun 20 Apr, Whit Sun 8 Jun.
"""
from chronologia import holidays_for
from holiday_testkit import assert_national_differential

_J = "BE"
_DISAGREEMENTS = {
    2023: {"ref_only": {(4, 9), (5, 28)}},
    2024: {"ref_only": {(3, 31), (5, 19)}},
    2025: {"ref_only": {(4, 20), (6, 8)}},
}


def test_national_differential_2023_2025():
    assert_national_differential(_J, (2023, 2024, 2025), _DISAGREEMENTS)


def test_ten_legal_holidays_2024():
    # public only -- this project also carries BE's vacanza-parity `bank`
    # category (Goede Vrijdag/Vrijdag na O.L.H. Hemelvaart/Banksluitingsdag),
    # a bank-holiday overlay distinct from the 10 statutory feestdagen.
    nat = [h for h in holidays_for(_J, 2024, categories=("public",))
           if h.subdiv is None]
    assert len(nat) == 10
