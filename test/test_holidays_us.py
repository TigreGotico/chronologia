"""US national (federal) differential + state-layer coverage sanity.

Per-holiday gold dates for US (federal + every subdivision rule) live in the
shared HOLIDAY_GOLDS registry (test_holiday_golds.py). This module carries the
national differential against the frozen reference snapshot and a couple of
state-layer coverage checks.

National differential (2023-2025) adjudication
----------------------------------------------
chronologia models the 5 U.S.C. 6103 weekend rule as a *relocating*
ObservedShift: a federal holiday on a Saturday is observed the preceding
Friday, on a Sunday the following Monday, and the nominal weekend date is
*not* also emitted (the day off is the observed day). The reference snapshot,
taken with ``observed=True``, keeps BOTH the nominal weekend date and its observed
weekday. So in any year a federal holiday falls on a weekend the reference has
a nominal date we do not:

* 2023: New Year's Day 2023-01-01 (Sunday, observed Mon Jan 2) and Veterans
  Day 2023-11-11 (Saturday, observed Fri Nov 10) -- the reference keeps
  (1, 1) and (11, 11); chronologia emits only the observed (1, 2) / (11, 10).
* 2024, 2025: no federal holiday falls on a weekend that produces a
  nominal/observed split in the public set, so the differential is clean.

This is a deliberate, documented modelling difference (relocate vs keep-both),
identical in spirit to the observed-shift handling already used for the other
jurisdictions, so the nominal weekend dates are listed as ref-only.
"""
from chronologia import AstroDate, holidays_for
from holiday_testkit import assert_national_differential

_J = "US"
#: ISO 3166-2:US: the 50 states, DC, the five inhabited territories (AS, GU,
#: MP, PR, VI) and the US Minor Outlying Islands (UM).
_SUBDIVISIONS = {
    "AK", "AL", "AR", "AS", "AZ", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
    "GU", "HI", "IA", "ID", "IL", "IN", "KS", "KY", "LA", "MA", "MD", "ME",
    "MI", "MN", "MO", "MP", "MS", "MT", "NC", "ND", "NE", "NH", "NJ", "NM",
    "NV", "NY", "OH", "OK", "OR", "PA", "PR", "RI", "SC", "SD", "TN", "TX",
    "UM", "UT", "VA", "VI", "VT", "WA", "WI", "WV", "WY",
}
_DISAGREEMENTS = {
    2023: {"ref_only": {(1, 1), (11, 11)}},
}


def test_national_differential_2023_2025():
    assert_national_differential(_J, (2023, 2024, 2025), _DISAGREEMENTS)


def test_state_layer_covers_all_57_subdivisions_minus_two():
    """Every ISO 3166-2:US subdivision except ND and UM (federal-only) carries
    at least one beyond-federal rule."""
    covered = {h.subdiv.split("-", 1)[1]
               for sub in _SUBDIVISIONS
               for h in holidays_for("US", 2024, subdiv=f"US-{sub}")
               if h.subdiv is not None}
    missing = _SUBDIVISIONS - covered
    assert missing == {"ND", "UM"}, missing


def test_distinctive_state_holidays_present_2024():
    """Spot-check the flagship distinctive holidays the batch calls out."""
    def has(subdiv, name, y, m, d):
        return any(h.name == name and h.date == AstroDate(y, m, d)
                   for h in holidays_for("US", y, subdiv=subdiv))
    assert has("US-TX", "Texas Independence Day", 2024, 3, 2)
    assert has("US-MA", "Patriots' Day", 2024, 4, 15)
    assert has("US-LA", "Mardi Gras", 2024, 2, 13)
    assert has("US-CA", "Cesar Chavez Day", 2024, 3, 31)
    assert has("US-UT", "Pioneer Day", 2024, 7, 24)
    assert has("US-AK", "Alaska Day", 2024, 10, 18)
