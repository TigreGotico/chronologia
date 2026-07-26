# -*- coding: utf-8 -*-
"""A pathological digit run must not crash the tokenizer (CPython caps
int(str) at 4300 digits). Regression for the persona-review fuzz finding."""
from datetime import datetime
from chronologia import extract_timespan, extract_duration


def test_huge_digit_run_no_crash():
    anc = datetime(2017, 6, 27, 13, 4)
    for n in (4300, 4400, 10000):
        s = "in " + "1" * n + " days"
        assert extract_timespan(s, "en", anc) is None  # withdrawn, not raised
        extract_duration(s, "en")  # must not raise


def test_normal_numbers_unaffected():
    anc = datetime(2017, 6, 27, 13, 4)
    r = extract_timespan("15 April 2020", "en", anc)
    assert r[0].start_datetime.date().isoformat() == "2020-04-15"
