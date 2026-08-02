# -*- coding: utf-8 -*-
"""A plural COUNT ("the two days of March") must not be fabricated into an
ordinal date (ca): the scoped-ordinal plural-unit veto rejects it. Regression:
ca shipped no unit1_<kind>.voc, so its derived plural_units missed the irregular
plurals and the veto never fired, inventing March 2."""
import datetime

import pytest

from chronologia import extract_timespan

_A = datetime.datetime(2017, 6, 27, 13, 4)


@pytest.mark.parametrize("text", [
    "els dos dies de març",       # two days of March
    "les dues setmanes de març",  # two weeks of March
])
def test_plural_count_is_nomatch(text):
    assert extract_timespan(text, "ca", _A) is None


def test_true_ordinal_still_resolves():
    r = extract_timespan("el segon dia de març", "ca", _A)   # the 2nd of March
    assert r is not None and (r.span.start.month, r.span.start.day) == (3, 2)
