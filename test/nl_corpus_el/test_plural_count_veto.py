# -*- coding: utf-8 -*-
"""A plural COUNT ("the two days of March") must not be fabricated into an
ordinal date (el): the scoped-ordinal plural-unit veto rejects it. Regression:
el shipped no unit1_<kind>.voc, so its derived plural_units missed the irregular
plurals and the veto never fired, inventing March 2."""
import datetime

import pytest

from chronologia import extract_timespan

_A = datetime.datetime(2017, 6, 27, 13, 4)


@pytest.mark.parametrize("text", [
    "οι δύο μέρες του Μαρτίου",      # two days of March
    "οι δύο εβδομάδες του Μαρτίου",  # two weeks of March
])
def test_plural_count_is_nomatch(text):
    assert extract_timespan(text, "el", _A) is None


def test_true_ordinal_still_resolves():
    r = extract_timespan("η δεύτερη μέρα του Μαρτίου", "el", _A)  # the 2nd day of March
    assert r is not None and r.span.start.month == 3
