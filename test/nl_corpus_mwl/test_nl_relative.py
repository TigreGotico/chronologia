# -*- coding: utf-8 -*-
"""Relative day words, past offsets and weekdays in Mirandese.

Only a PAST-offset marker is citable: hai ("... ago", from *haber*).  No
forward-offset ("in N ...") or weekday next/last marker was found in the
sources, so those are intentionally absent -- an honest gap, not a fake."""
from datetime import timedelta
import pytest
from ._corpus import ANCHOR, start

A = ANCHOR


@pytest.mark.parametrize("text,days", [
    ("hoije", 0), ("manhana", 1), ("onte", -1), ("trasdonte", -2)])
def test_named_days(text, days):
    exp = (A + timedelta(days=days)).date()
    assert (start(text).month, start(text).day) == (exp.month, exp.day)


@pytest.mark.parametrize("text,days", [
    ("hai 3 dies", -3), ("hai 1 die", -1), ("hai 10 dies", -10),
    ("hai 5 dies", -5), ("hai 2 dies", -2), ("hai 7 dies", -7)])
def test_past_day_offsets(text, days):
    exp = (A + timedelta(days=days)).date()
    assert (start(text).month, start(text).day) == (exp.month, exp.day)


@pytest.mark.parametrize("text,weeks", [
    ("hai 1 sumana", -1), ("hai 2 sumanas", -2), ("hai 3 sumanas", -3),
    ("hai 4 sumanas", -4)])
def test_past_week_offsets(text, weeks):
    exp = (A + timedelta(weeks=weeks)).date()
    assert (start(text).month, start(text).day) == (exp.month, exp.day)


@pytest.mark.parametrize("text,wd", [
    ("segunda feira", None), ("terça feira", None), ("sábado", None),
    ("demingo", None)])
def test_weekday_names_tokenize(text, wd):
    # bare weekday names have no citable next/last marker in mwl, so they do
    # not resolve to a span on their own; assert the engine returns cleanly.
    from ._corpus import parse
    assert parse(text) is None
