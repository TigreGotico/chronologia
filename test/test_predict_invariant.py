"""A decree table's ``predict`` bridge must agree with the table it extends.

``HolidayRule`` may carry a ``predict`` key so a decree-tabulated holiday keeps
resolving past the last year it tabulates, via a computable well-known rule. The
bridge is only honest when that computable rule reproduces the table's OWN dates
for every tabulated year -- otherwise extrapolating past the horizon fabricates a
date the table itself contradicts. This is enforced at construction (load) time.
"""
import pytest

from chronologia.civil_holidays.model import HolidayRule
from chronologia.civil_holidays.rules import DecreeTableRule

# all_saints is a fixed 1 November feast, so its computable rule yields 11-01
# for any year -- a clean fixture for agree/disagree cases.
_CATS = frozenset({"catholic"})


def test_predict_agreeing_with_table_loads():
    rule = HolidayRule(
        name="All Saints (decreed table)",
        kind=DecreeTableRule(dates=((2024, (11, 1)), (2025, (11, 1)))),
        categories=_CATS,
        predict="all_saints",
    )
    assert rule.predict == "all_saints"


def test_predict_disagreeing_with_table_is_a_load_error():
    with pytest.raises(ValueError, match="disagrees with the tabulated"):
        HolidayRule(
            name="All Saints (mis-tabulated)",
            # 2025 tabulated as 11-02, but all_saints computes 11-01 -> mismatch
            kind=DecreeTableRule(dates=((2024, (11, 1)), (2025, (11, 2)))),
            categories=_CATS,
            predict="all_saints",
        )


def test_predict_unknown_key_is_a_load_error():
    with pytest.raises(ValueError, match="unknown well-known key"):
        HolidayRule(
            name="Bad predict key",
            kind=DecreeTableRule(dates=((2025, (1, 1)),)),
            categories=_CATS,
            predict="not_a_real_feast",
        )
